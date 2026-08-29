import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.core.websocket_manager import ws_manager
from app.crm.models import Customer, Contact, CustomerTimelineEvent
from app.communications.models import (
    Conversation, Message, MessageTemplate,
    ChannelType, MessageDirection, MessageStatus, ConversationStatus
)
from app.communications.schemas import (
    MessageSendRequest, InboundWebhookMessage,
    ConversationCreate, MessageTemplateCreate
)
from app.communications.providers import email_provider, sms_provider, whatsapp_provider


def render_template(template_str: str, variables: Dict[str, Any]) -> str:
    """Render dynamic {{variable}} placeholders within template string"""
    result = template_str
    for k, v in variables.items():
        pattern = r"\{\{\s*" + re.escape(k) + r"\s*\}\}"
        result = re.sub(pattern, str(v), result)
    return result


class CommunicationsService:
    # ----------------------------------------------------
    # Outbound Message Sending Engine
    # ----------------------------------------------------
    @classmethod
    async def send_message(cls, db: AsyncSession, org_id: str, req: MessageSendRequest, user_id: str) -> Message:
        """
        Send outbound email, SMS, or WhatsApp message.
        Appends to unified conversation thread and records event on Customer 360 Timeline.
        """
        body_text = req.body
        subject_text = req.subject

        # If template used, render variables
        if req.template_id:
            tpl_res = await db.execute(
                select(MessageTemplate).where(
                    and_(MessageTemplate.id == req.template_id, MessageTemplate.organization_id == org_id)
                )
            )
            tpl = tpl_res.scalar_one_or_none()
            if tpl:
                vars_dict = req.template_variables or {}
                body_text = render_template(tpl.body_template, vars_dict)
                if tpl.subject:
                    subject_text = render_template(tpl.subject, vars_dict)

        # Retrieve or create Conversation thread
        conversation_id = req.conversation_id
        if not conversation_id:
            conv = Conversation(
                organization_id=org_id,
                customer_id=req.customer_id,
                contact_id=req.contact_id,
                channel=req.channel,
                subject=subject_text or f"{req.channel.value} with {req.recipient_identifier}",
                status=ConversationStatus.PENDING_CUSTOMER,
                assigned_agent_id=user_id,
                last_message_at=datetime.now(timezone.utc)
            )
            db.add(conv)
            await db.flush()
            conversation_id = conv.id
        else:
            conv_res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
            conv = conv_res.scalar_one_or_none()
            if conv:
                conv.last_message_at = datetime.now(timezone.utc)
                conv.status = ConversationStatus.PENDING_CUSTOMER

        # Provider delivery
        provider_resp = {}
        if req.channel == ChannelType.EMAIL:
            provider_resp = await email_provider.send_message(req.recipient_identifier, body_text, subject=subject_text)
        elif req.channel == ChannelType.SMS:
            provider_resp = await sms_provider.send_message(req.recipient_identifier, body_text)
        elif req.channel == ChannelType.WHATSAPP:
            provider_resp = await whatsapp_provider.send_message(req.recipient_identifier, body_text)

        # Create Message Record
        msg = Message(
            organization_id=org_id,
            conversation_id=conversation_id,
            customer_id=req.customer_id,
            direction=MessageDirection.OUTBOUND,
            channel=req.channel,
            status=MessageStatus.DELIVERED,
            sender_identifier=req.sender_identifier or "CallSphere",
            recipient_identifier=req.recipient_identifier,
            subject=subject_text,
            body=body_text,
            attachments=req.attachments or [],
            sent_by_user_id=user_id,
            provider_message_id=provider_resp.get("provider_message_id"),
            delivered_at=datetime.now(timezone.utc)
        )
        db.add(msg)

        # Append to Customer Timeline if customer attached
        if req.customer_id:
            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=req.customer_id,
                contact_id=req.contact_id,
                channel=req.channel.value,
                event_type="MessageSent",
                title=f"Outbound {req.channel.value} to {req.recipient_identifier}",
                description=body_text[:200],
                metadata_json={"message_id": msg.id, "conversation_id": conversation_id},
                actor_user_id=user_id,
                actor_name="Agent"
            )
            db.add(timeline_event)

        await db.commit()
        await db.refresh(msg)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.MESSAGE_SENT,
            organization_id=org_id,
            entity_id=msg.id,
            entity_type="message",
            payload={"channel": req.channel.value, "recipient": req.recipient_identifier},
            user_id=user_id
        ))

        return msg

    # ----------------------------------------------------
    # Inbound Webhook Processing
    # ----------------------------------------------------
    @classmethod
    async def process_inbound_webhook(cls, db: AsyncSession, org_id: str, webhook_data: InboundWebhookMessage) -> Message:
        """Process incoming WhatsApp/SMS/Email webhook message, link to customer, and notify agent"""
        # Resolve customer from phone number or email
        cust_query = await db.execute(
            select(Customer).where(
                and_(
                    Customer.organization_id == org_id,
                    or_(
                        Customer.phone_number == webhook_data.from_identifier,
                        Customer.email == webhook_data.from_identifier
                    )
                )
            )
        )
        customer = cust_query.scalar_one_or_none()
        customer_id = customer.id if customer else None

        # Find or create active conversation thread
        conv_query = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.organization_id == org_id,
                    Conversation.channel == webhook_data.channel,
                    Conversation.customer_id == customer_id,
                    Conversation.status.in_([ConversationStatus.OPEN, ConversationStatus.PENDING_AGENT, ConversationStatus.PENDING_CUSTOMER])
                )
            )
        )
        conv = conv_query.scalar_one_or_none()
        if not conv:
            conv = Conversation(
                organization_id=org_id,
                customer_id=customer_id,
                channel=webhook_data.channel,
                subject=webhook_data.subject or f"Inbound {webhook_data.channel.value} from {webhook_data.from_identifier}",
                status=ConversationStatus.PENDING_AGENT,
                last_message_at=datetime.now(timezone.utc),
                unread_agent_count=1
            )
            db.add(conv)
            await db.flush()
        else:
            conv.last_message_at = datetime.now(timezone.utc)
            conv.status = ConversationStatus.PENDING_AGENT
            conv.unread_agent_count += 1

        msg = Message(
            organization_id=org_id,
            conversation_id=conv.id,
            customer_id=customer_id,
            direction=MessageDirection.INBOUND,
            channel=webhook_data.channel,
            status=MessageStatus.DELIVERED,
            sender_identifier=webhook_data.from_identifier,
            recipient_identifier=webhook_data.to_identifier,
            subject=webhook_data.subject,
            body=webhook_data.body,
            attachments=webhook_data.attachments or [],
            delivered_at=datetime.now(timezone.utc)
        )
        db.add(msg)

        if customer_id:
            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=customer_id,
                channel=webhook_data.channel.value,
                event_type="MessageReceived",
                title=f"Inbound {webhook_data.channel.value} from {webhook_data.from_identifier}",
                description=webhook_data.body[:200],
                metadata_json={"message_id": msg.id, "conversation_id": conv.id},
                actor_name=customer.name if customer else "Customer"
            )
            db.add(timeline_event)

        await db.commit()
        await db.refresh(msg)

        # Broadcast via WebSocket to Agent Unified Inbox
        await ws_manager.broadcast_to_org(org_id, {
            "type": "new_message",
            "conversation_id": conv.id,
            "channel": webhook_data.channel.value,
            "from": webhook_data.from_identifier,
            "body": webhook_data.body
        })

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.MESSAGE_RECEIVED,
            organization_id=org_id,
            entity_id=msg.id,
            entity_type="message",
            payload={"channel": webhook_data.channel.value, "from": webhook_data.from_identifier},
            user_id="customer"
        ))

        return msg
