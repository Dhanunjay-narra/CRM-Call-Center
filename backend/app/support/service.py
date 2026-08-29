import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.core.websocket_manager import ws_manager
from app.crm.models import Customer, CustomerTimelineEvent
from app.support.models import (
    SupportTicket, TicketComment, SLAPolicy, KnowledgeCategory, KnowledgeArticle,
    TicketStatus, TicketPriority, SLAStatus
)
from app.support.schemas import (
    SupportTicketCreate, SupportTicketUpdate, TicketResolveRequest,
    TicketCommentCreate, SLAPolicyCreate,
    KnowledgeCategoryCreate, KnowledgeArticleCreate
)


def ensure_utc(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r'[\s\W-]+', '-', text)


class SupportService:
    # ----------------------------------------------------
    # SLA Policies & Ticket Management
    # ----------------------------------------------------
    @staticmethod
    async def init_default_sla_policies(db: AsyncSession, org_id: str) -> None:
        """Initialize standard SLA matrices for tenant"""
        policies = [
            {"name": "Critical SLA", "priority": TicketPriority.CRITICAL, "resp_m": 15, "resol_m": 120},
            {"name": "High SLA", "priority": TicketPriority.HIGH, "resp_m": 30, "resol_m": 240},
            {"name": "Medium SLA", "priority": TicketPriority.MEDIUM, "resp_m": 60, "resol_m": 480},
            {"name": "Low SLA", "priority": TicketPriority.LOW, "resp_m": 120, "resol_m": 1440},
        ]
        for p in policies:
            sla = SLAPolicy(
                organization_id=org_id,
                name=p["name"],
                priority=p["priority"],
                first_response_time_minutes=p["resp_m"],
                resolution_time_minutes=p["resol_m"],
                warning_threshold_percent=80,
                escalate_to_manager_on_breach=True
            )
            db.add(sla)
        await db.commit()

    @classmethod
    async def create_ticket(cls, db: AsyncSession, org_id: str, req: SupportTicketCreate, user_id: str) -> SupportTicket:
        """Create new support ticket and calculate SLA target deadlines"""
        # Ensure default SLA policies exist
        policies_res = await db.execute(
            select(SLAPolicy).where(and_(SLAPolicy.organization_id == org_id, SLAPolicy.priority == req.priority))
        )
        policy = policies_res.scalars().first()
        if not policy:
            await cls.init_default_sla_policies(db, org_id)
            p_res = await db.execute(
                select(SLAPolicy).where(and_(SLAPolicy.organization_id == org_id, SLAPolicy.priority == req.priority))
            )
            policy = p_res.scalars().first()

        now = datetime.now(timezone.utc)
        resp_due = now + timedelta(minutes=policy.first_response_time_minutes if policy else 60)
        resol_due = now + timedelta(minutes=policy.resolution_time_minutes if policy else 480)

        # Generate ticket number (e.g. TIK-847291)
        ticket_number = f"TIK-{uuid.uuid4().hex[:6].upper()}"

        ticket = SupportTicket(
            organization_id=org_id,
            ticket_number=ticket_number,
            customer_id=req.customer_id,
            contact_id=req.contact_id,
            title=req.title,
            description=req.description,
            category=req.category,
            priority=req.priority,
            status=TicketStatus.NEW,
            assigned_user_id=req.assigned_user_id,
            assigned_team_id=req.assigned_team_id,
            sla_policy_id=policy.id if policy else None,
            sla_status=SLAStatus.WITHIN_SLA,
            first_response_due_at=resp_due,
            resolution_due_at=resol_due,
            tags=req.tags or [],
            custom_fields=req.custom_fields or {}
        )
        db.add(ticket)
        await db.flush()

        # Update customer open tickets count
        if req.customer_id:
            cust_res = await db.execute(select(Customer).where(Customer.id == req.customer_id))
            cust = cust_res.scalar_one_or_none()
            if cust:
                cust.open_tickets_count += 1
                cust.last_interaction_at = now

            # Append to Timeline
            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=req.customer_id,
                contact_id=req.contact_id,
                channel="TICKET",
                event_type="TicketCreated",
                title=f"Support Ticket #{ticket.ticket_number}: {ticket.title}",
                description=f"Priority: {ticket.priority.value} | Category: {ticket.category}",
                metadata_json={"ticket_id": ticket.id, "ticket_number": ticket.ticket_number},
                actor_user_id=user_id,
                actor_name="Customer Support"
            )
            db.add(timeline_event)

        await db.commit()
        await db.refresh(ticket)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.TICKET_CREATED,
            organization_id=org_id,
            entity_id=ticket.id,
            entity_type="ticket",
            payload={"ticket_number": ticket.ticket_number, "priority": ticket.priority.value},
            user_id=user_id
        ))

        return ticket

    @classmethod
    async def add_comment(cls, db: AsyncSession, org_id: str, ticket_id: str, req: TicketCommentCreate, user_id: str, author_name: str = "Agent") -> TicketComment:
        """Add internal note or public customer reply to ticket"""
        t_res = await db.execute(select(SupportTicket).where(and_(SupportTicket.id == ticket_id, SupportTicket.organization_id == org_id)))
        ticket = t_res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        now = datetime.now(timezone.utc)
        if not ticket.first_responded_at and not req.is_internal_note:
            ticket.first_responded_at = now
            ticket.status = TicketStatus.IN_PROGRESS

        comment = TicketComment(
            organization_id=org_id,
            ticket_id=ticket_id,
            user_id=user_id,
            author_name=author_name,
            is_internal_note=req.is_internal_note,
            body=req.body,
            attachments=req.attachments or []
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    @classmethod
    async def resolve_ticket(cls, db: AsyncSession, org_id: str, ticket_id: str, req: TicketResolveRequest, user_id: str) -> SupportTicket:
        """Mark support ticket as RESOLVED and check SLA outcome"""
        t_res = await db.execute(select(SupportTicket).where(and_(SupportTicket.id == ticket_id, SupportTicket.organization_id == org_id)))
        ticket = t_res.scalar_one_or_none()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

        now = datetime.now(timezone.utc)
        ticket.status = TicketStatus.RESOLVED
        ticket.resolved_at = now
        ticket.resolution_code = req.resolution_code
        ticket.resolution_notes = req.resolution_notes
        if req.csat_score:
            ticket.csat_score = req.csat_score

        # Check if resolved within SLA
        if ticket.resolution_due_at:
            resol_due = ensure_utc(ticket.resolution_due_at)
            ticket.is_sla_breached = (now > resol_due)

        # Update customer open tickets
        if ticket.customer_id:
            cust_res = await db.execute(select(Customer).where(Customer.id == ticket.customer_id))
            cust = cust_res.scalar_one_or_none()
            if cust and cust.open_tickets_count > 0:
                cust.open_tickets_count -= 1

            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=ticket.customer_id,
                channel="TICKET",
                event_type="TicketResolved",
                title=f"Ticket #{ticket.ticket_number} Resolved",
                description=req.resolution_notes,
                metadata_json={"ticket_id": ticket.id, "resolution_code": req.resolution_code},
                actor_user_id=user_id,
                actor_name="Support Engineer"
            )
            db.add(timeline_event)

        await db.commit()
        await db.refresh(ticket)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.TICKET_RESOLVED,
            organization_id=org_id,
            entity_id=ticket.id,
            entity_type="ticket",
            payload={"ticket_number": ticket.ticket_number, "resolution_code": req.resolution_code},
            user_id=user_id
        ))

        return ticket

    # ----------------------------------------------------
    # SLA Monitoring & Auto-Escalation Engine
    # ----------------------------------------------------
    @classmethod
    async def monitor_sla_breaches(cls, db: AsyncSession, org_id: str) -> Dict[str, Any]:
        """
        Background SLA Monitoring Worker:
        - Detects tickets at 80% SLA threshold -> sets WARNING_80_PERCENT & broadcasts alert
        - Detects tickets past 100% resolution deadline -> sets BREACHED, escalates to Support Manager
        """
        now = datetime.now(timezone.utc)
        open_tickets_res = await db.execute(
            select(SupportTicket).where(
                and_(
                    SupportTicket.organization_id == org_id,
                    SupportTicket.status.in_([TicketStatus.NEW, TicketStatus.ASSIGNED, TicketStatus.IN_PROGRESS])
                )
            )
        )
        tickets = open_tickets_res.scalars().all()

        warnings_triggered = 0
        breaches_triggered = 0

        for t in tickets:
            if not t.resolution_due_at or not t.created_at:
                continue

            created = ensure_utc(t.created_at)
            due = ensure_utc(t.resolution_due_at)
            total_duration = (due - created).total_seconds()
            elapsed = (now - created).total_seconds()

            if total_duration <= 0:
                continue

            percent_consumed = (elapsed / total_duration) * 100.0

            # 1. Breach Trigger (> 100%)
            if percent_consumed >= 100.0 and not t.is_sla_breached:
                t.is_sla_breached = True
                t.sla_status = SLAStatus.BREACHED
                breaches_triggered += 1

                await ws_manager.broadcast_to_supervisors(org_id, {
                    "type": "sla_breached_alert",
                    "ticket_id": t.id,
                    "ticket_number": t.ticket_number,
                    "priority": t.priority.value
                })

                await event_bus.publish(DomainEvent(
                    event_type=EventTypes.TICKET_SLA_BREACHED,
                    organization_id=org_id,
                    entity_id=t.id,
                    entity_type="ticket",
                    payload={"ticket_number": t.ticket_number, "priority": t.priority.value}
                ))

            # 2. Warning Trigger (>= 80% and < 100%)
            elif percent_consumed >= 80.0 and not t.sla_warning_sent and not t.is_sla_breached:
                t.sla_warning_sent = True
                t.sla_status = SLAStatus.WARNING_80_PERCENT
                warnings_triggered += 1

                await ws_manager.broadcast_to_supervisors(org_id, {
                    "type": "sla_warning_alert",
                    "ticket_id": t.id,
                    "ticket_number": t.ticket_number,
                    "percent_consumed": round(percent_consumed, 1)
                })

                await event_bus.publish(DomainEvent(
                    event_type=EventTypes.TICKET_SLA_WARNING,
                    organization_id=org_id,
                    entity_id=t.id,
                    entity_type="ticket",
                    payload={"ticket_number": t.ticket_number, "percent_consumed": percent_consumed}
                ))

        await db.commit()
        return {"warnings_triggered": warnings_triggered, "breaches_triggered": breaches_triggered}

    # ----------------------------------------------------
    # Knowledge Base Engine
    # ----------------------------------------------------
    @classmethod
    async def search_articles(cls, db: AsyncSession, org_id: str, query: str, is_public_only: bool = False) -> List[KnowledgeArticle]:
        """Search knowledge base articles and call scripts by title, content, or tags"""
        conditions = [KnowledgeArticle.organization_id == org_id, KnowledgeArticle.is_deleted == False]
        if is_public_only:
            conditions.append(KnowledgeArticle.is_public == True)

        search_pattern = f"%{query}%"
        conditions.append(
            or_(
                KnowledgeArticle.title.ilike(search_pattern),
                KnowledgeArticle.content_markdown.ilike(search_pattern)
            )
        )
        res = await db.execute(select(KnowledgeArticle).where(and_(*conditions)).order_by(desc(KnowledgeArticle.view_count)))
        return res.scalars().all()
