from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.crm.models import (
    Lead, Contact, Customer, Activity, CustomerTimelineEvent,
    LeadStatus, LeadSource, ActivityType, ActivityStatus, CustomerSentiment
)
from app.crm.schemas import (
    LeadCreate, LeadUpdate, LeadConvertRequest,
    ContactCreate, ContactUpdate,
    CustomerCreate, CustomerUpdate,
    ActivityCreate, ActivityUpdate,
    TimelineEventCreate
)


class CRMService:
    # ----------------------------------------------------
    # Lead Management & Scoring Engine
    # ----------------------------------------------------
    @staticmethod
    def calculate_lead_score(lead_data: LeadCreate) -> int:
        """
        Intelligent Lead Scoring Engine:
        Evaluates completeness of contact details, lead source value, and estimated deal size.
        """
        score = 10  # Base score
        if lead_data.email:
            score += 15
        if lead_data.phone_number:
            score += 20
        if lead_data.company_name:
            score += 15
        if lead_data.title:
            score += 10
            
        # Source scoring weights
        source_weights = {
            LeadSource.REFERRAL: 25,
            LeadSource.PHONE: 20,
            LeadSource.WHATSAPP: 15,
            LeadSource.WEBSITE: 10,
            LeadSource.CAMPAIGN: 10,
            LeadSource.SOCIAL_MEDIA: 5
        }
        score += source_weights.get(lead_data.source, 5)

        # Value scoring
        if lead_data.estimated_value > 10000:
            score += 15
        elif lead_data.estimated_value > 1000:
            score += 10

        return min(score, 100)

    @classmethod
    async def create_lead(cls, db: AsyncSession, org_id: str, req: LeadCreate, user_id: str = "system") -> Lead:
        """Create new lead, compute score, and emit LeadCreated event"""
        calculated_score = cls.calculate_lead_score(req)
        
        lead = Lead(
            organization_id=org_id,
            first_name=req.first_name,
            last_name=req.last_name,
            email=req.email,
            phone_number=req.phone_number,
            company_name=req.company_name,
            title=req.title,
            source=req.source,
            status=LeadStatus.NEW,
            score=calculated_score,
            estimated_value=req.estimated_value,
            assigned_user_id=req.assigned_user_id,
            notes=req.notes,
            custom_fields=req.custom_fields or {}
        )
        db.add(lead)
        await db.commit()
        await db.refresh(lead)

        # Publish LeadCreated event
        await event_bus.publish(DomainEvent(
            event_type=EventTypes.LEAD_CREATED,
            organization_id=org_id,
            entity_id=lead.id,
            entity_type="lead",
            payload={"name": f"{lead.first_name} {lead.last_name or ''}".strip(), "score": lead.score},
            user_id=user_id
        ))

        return lead

    @classmethod
    async def check_lead_duplicates(cls, db: AsyncSession, org_id: str, email: Optional[str], phone: Optional[str]) -> List[Lead]:
        """Detect duplicate leads based on email or phone"""
        conditions = []
        if email:
            conditions.append(Lead.email == email)
        if phone:
            conditions.append(Lead.phone_number == phone)

        if not conditions:
            return []

        query = await db.execute(
            select(Lead).where(
                and_(
                    Lead.organization_id == org_id,
                    Lead.is_deleted == False,
                    or_(*conditions)
                )
            )
        )
        return query.scalars().all()

    @classmethod
    async def convert_lead(cls, db: AsyncSession, org_id: str, lead_id: str, req: LeadConvertRequest, user_id: str) -> Dict[str, Any]:
        """
        Convert Lead -> Customer + Contact (+ Opportunity if requested) in a single atomic transaction.
        Creates initial timeline record.
        """
        lead_query = await db.execute(
            select(Lead).where(and_(Lead.id == lead_id, Lead.organization_id == org_id, Lead.is_deleted == False))
        )
        lead = lead_query.scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

        if lead.is_converted:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Lead has already been converted")

        # 1. Create or retrieve Customer Account
        customer_name = req.customer_name or lead.company_name or f"{lead.first_name} {lead.last_name or ''}".strip()
        customer = Customer(
            organization_id=org_id,
            name=customer_name,
            phone_number=lead.phone_number,
            email=lead.email,
            health_score=85,
            engagement_score=75,
            sentiment=CustomerSentiment.POSITIVE,
            preferred_channel="PHONE" if lead.phone_number else "EMAIL",
            lifetime_value=lead.estimated_value,
            assigned_account_manager_id=lead.assigned_user_id
        )
        db.add(customer)
        await db.flush()

        # 2. Create Contact associated with Customer
        contact = Contact(
            organization_id=org_id,
            customer_id=customer.id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone_number=lead.phone_number,
            title=lead.title,
            tags=["Converted Lead"]
        )
        db.add(contact)
        await db.flush()

        # 3. Update Lead Status
        lead.is_converted = True
        lead.converted_at = datetime.now(timezone.utc)
        lead.converted_customer_id = customer.id
        lead.converted_contact_id = contact.id
        lead.status = LeadStatus.WON

        # 4. Record Conversion on Customer Timeline
        timeline_event = CustomerTimelineEvent(
            organization_id=org_id,
            customer_id=customer.id,
            contact_id=contact.id,
            lead_id=lead.id,
            channel="SALES",
            event_type="LeadConverted",
            title=f"Lead Converted: {customer.name}",
            description=f"Lead {lead.first_name} {lead.last_name or ''} successfully converted to Customer account.",
            metadata_json={"lead_id": lead.id, "score": lead.score, "value": lead.estimated_value},
            actor_user_id=user_id,
            actor_name="CRM Agent"
        )
        db.add(timeline_event)
        await db.commit()

        # Publish Event
        await event_bus.publish(DomainEvent(
            event_type=EventTypes.LEAD_CONVERTED,
            organization_id=org_id,
            entity_id=lead.id,
            entity_type="lead",
            payload={"customer_id": customer.id, "contact_id": contact.id},
            user_id=user_id
        ))

        return {
            "lead_id": lead.id,
            "customer_id": customer.id,
            "contact_id": contact.id,
            "status": "CONVERTED"
        }

    # ----------------------------------------------------
    # Customer 360 & Timeline Engine
    # ----------------------------------------------------
    @classmethod
    async def record_timeline_event(cls, db: AsyncSession, org_id: str, req: TimelineEventCreate) -> CustomerTimelineEvent:
        """Append event to unified Customer 360 timeline"""
        event = CustomerTimelineEvent(
            organization_id=org_id,
            customer_id=req.customer_id,
            contact_id=req.contact_id,
            lead_id=req.lead_id,
            channel=req.channel,
            event_type=req.event_type,
            title=req.title,
            description=req.description,
            metadata_json=req.metadata_json or {},
            actor_user_id=req.actor_user_id,
            actor_name=req.actor_name,
            occurred_at=req.occurred_at or datetime.now(timezone.utc)
        )
        db.add(event)

        # Update customer last_interaction_at
        cust_query = await db.execute(select(Customer).where(Customer.id == req.customer_id))
        cust = cust_query.scalar_one_or_none()
        if cust:
            cust.last_interaction_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(event)
        return event

    @classmethod
    async def get_customer_360(cls, db: AsyncSession, org_id: str, customer_id: str) -> Dict[str, Any]:
        """Synthesize unified Customer 360 profile with contacts, activities, timeline, and health metrics"""
        cust_query = await db.execute(
            select(Customer).where(and_(Customer.id == customer_id, Customer.organization_id == org_id, Customer.is_deleted == False))
        )
        customer = cust_query.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        # Contacts
        contacts_query = await db.execute(
            select(Contact).where(and_(Contact.customer_id == customer_id, Contact.is_deleted == False))
        )
        contacts = contacts_query.scalars().all()

        # Activities
        activities_query = await db.execute(
            select(Activity).where(and_(Activity.customer_id == customer_id, Activity.is_deleted == False)).order_by(Activity.due_date.desc())
        )
        activities = activities_query.scalars().all()

        # Timeline
        timeline_query = await db.execute(
            select(CustomerTimelineEvent).where(CustomerTimelineEvent.customer_id == customer_id).order_by(CustomerTimelineEvent.occurred_at.desc()).limit(100)
        )
        timeline = timeline_query.scalars().all()

        metrics = {
            "health_score": customer.health_score,
            "engagement_score": customer.engagement_score,
            "sentiment": customer.sentiment,
            "lifetime_value": customer.lifetime_value,
            "total_contacts": len(contacts),
            "total_activities": len(activities),
            "total_timeline_events": len(timeline),
            "preferred_channel": customer.preferred_channel
        }

        return {
            "customer": customer,
            "contacts": contacts,
            "activities": activities,
            "timeline": timeline,
            "metrics": metrics
        }
