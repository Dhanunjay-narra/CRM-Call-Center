from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.communications.models import Conversation, Message, MessageTemplate, ChannelType
from app.communications.schemas import (
    MessageSendRequest, MessageResponse, InboundWebhookMessage,
    ConversationCreate, ConversationResponse,
    MessageTemplateCreate, MessageTemplateResponse
)
from app.communications.service import CommunicationsService

router = APIRouter()


# ----------------------------------------------------
# Unified Inbox & Conversations Endpoints
# ----------------------------------------------------

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    channel: Optional[ChannelType] = None,
    customer_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["message.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List unified inbox conversations across all channels (WhatsApp, SMS, Email)"""
    conditions = [Conversation.organization_id == auth.organization_id, Conversation.is_deleted == False]
    if channel:
        conditions.append(Conversation.channel == channel)
    if customer_id:
        conditions.append(Conversation.customer_id == customer_id)

    res = await db.execute(select(Conversation).where(and_(*conditions)).order_by(desc(Conversation.last_message_at)))
    return res.scalars().all()


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def list_conversation_messages(
    conversation_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["message.read"])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch message history for a specific unified inbox conversation"""
    res = await db.execute(
        select(Message).where(
            and_(Message.conversation_id == conversation_id, Message.organization_id == auth.organization_id)
        ).order_by(Message.created_at.asc())
    )
    return res.scalars().all()


@router.post("/messages/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    req: MessageSendRequest,
    auth: TokenPayload = Depends(PermissionChecker(["message.send"])),
    db: AsyncSession = Depends(get_db)
):
    """Send outbound message (WhatsApp, SMS, Email) via provider abstraction layer"""
    return await CommunicationsService.send_message(db, auth.organization_id, req, user_id=auth.sub)


# ----------------------------------------------------
# Message Templates Endpoints
# ----------------------------------------------------

@router.get("/templates", response_model=List[MessageTemplateResponse])
async def list_templates(
    channel: Optional[ChannelType] = None,
    auth: TokenPayload = Depends(PermissionChecker(["template.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """List reusable message templates with dynamic variable substitution"""
    conditions = [MessageTemplate.organization_id == auth.organization_id, MessageTemplate.is_deleted == False]
    if channel:
        conditions.append(MessageTemplate.channel == channel)

    res = await db.execute(select(MessageTemplate).where(and_(*conditions)))
    return res.scalars().all()


@router.post("/templates", response_model=MessageTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    req: MessageTemplateCreate,
    auth: TokenPayload = Depends(PermissionChecker(["template.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new reusable message template"""
    template = MessageTemplate(
        organization_id=auth.organization_id,
        name=req.name,
        channel=req.channel,
        category=req.category,
        subject=req.subject,
        body_template=req.body_template,
        variables=req.variables
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


# ----------------------------------------------------
# Inbound Webhook Receiver
# ----------------------------------------------------

@router.post("/webhooks/{channel}", response_model=MessageResponse)
async def inbound_webhook(
    channel: ChannelType,
    req: InboundWebhookMessage,
    org_id: str = Query(default="default-org"),
    db: AsyncSession = Depends(get_db)
):
    """Inbound webhook receiver for Twilio/Meta/WhatsApp/SendGrid incoming messages"""
    req.channel = channel
    return await CommunicationsService.process_inbound_webhook(db, org_id, req)
