from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.crm.models import Lead, Contact, Customer, Activity, CustomerTimelineEvent, LeadStatus, ActivityStatus
from app.crm.schemas import (
    LeadCreate, LeadUpdate, LeadResponse, LeadConvertRequest,
    ContactCreate, ContactUpdate, ContactResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse, Customer360Response,
    ActivityCreate, ActivityUpdate, ActivityResponse,
    TimelineEventCreate, TimelineEventResponse
)
from app.crm.service import CRMService

router = APIRouter()


# ----------------------------------------------------
# Leads Endpoints
# ----------------------------------------------------

@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    status: Optional[LeadStatus] = None,
    assigned_user_id: Optional[str] = None,
    search: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["lead.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List leads with filtering and search"""
    conditions = [Lead.organization_id == auth.organization_id, Lead.is_deleted == False]
    if status:
        conditions.append(Lead.status == status)
    if assigned_user_id:
        conditions.append(Lead.assigned_user_id == assigned_user_id)
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Lead.first_name.ilike(search_pattern),
                Lead.last_name.ilike(search_pattern),
                Lead.company_name.ilike(search_pattern),
                Lead.email.ilike(search_pattern),
                Lead.phone_number.ilike(search_pattern)
            )
        )

    res = await db.execute(select(Lead).where(and_(*conditions)).order_by(desc(Lead.score), desc(Lead.created_at)))
    return res.scalars().all()


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    req: LeadCreate,
    auth: TokenPayload = Depends(PermissionChecker(["lead.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead with automated intelligent scoring"""
    return await CRMService.create_lead(db, auth.organization_id, req, user_id=auth.sub)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["lead.read"])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch single lead details"""
    res = await db.execute(
        select(Lead).where(and_(Lead.id == lead_id, Lead.organization_id == auth.organization_id, Lead.is_deleted == False))
    )
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    req: LeadUpdate,
    auth: TokenPayload = Depends(PermissionChecker(["lead.update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update lead fields or status"""
    res = await db.execute(
        select(Lead).where(and_(Lead.id == lead_id, Lead.organization_id == auth.organization_id, Lead.is_deleted == False))
    )
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(lead, k, v)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.post("/leads/{lead_id}/convert")
async def convert_lead_to_customer(
    lead_id: str,
    req: LeadConvertRequest,
    auth: TokenPayload = Depends(PermissionChecker(["lead.update", "customer.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Convert Lead into Customer 360 Account, Contact, and Opportunity"""
    return await CRMService.convert_lead(db, auth.organization_id, lead_id, req, user_id=auth.sub)


# ----------------------------------------------------
# Contacts Endpoints
# ----------------------------------------------------

@router.get("/contacts", response_model=List[ContactResponse])
async def list_contacts(
    customer_id: Optional[str] = None,
    search: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["contact.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List contacts, optionally filtered by customer account"""
    conditions = [Contact.organization_id == auth.organization_id, Contact.is_deleted == False]
    if customer_id:
        conditions.append(Contact.customer_id == customer_id)
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Contact.first_name.ilike(search_pattern),
                Contact.last_name.ilike(search_pattern),
                Contact.email.ilike(search_pattern),
                Contact.phone_number.ilike(search_pattern)
            )
        )

    res = await db.execute(select(Contact).where(and_(*conditions)).order_by(Contact.first_name))
    return res.scalars().all()


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    req: ContactCreate,
    auth: TokenPayload = Depends(PermissionChecker(["contact.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    contact = Contact(
        organization_id=auth.organization_id,
        customer_id=req.customer_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        secondary_emails=req.secondary_emails or [],
        phone_number=req.phone_number,
        secondary_phones=req.secondary_phones or [],
        title=req.title,
        department=req.department,
        addresses=req.addresses or [],
        consent_preferences=req.consent_preferences or {"email": True, "sms": True, "calls": True, "whatsapp": True},
        tags=req.tags or [],
        notes=req.notes
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


# ----------------------------------------------------
# Customers & Customer 360 Endpoints
# ----------------------------------------------------

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    search: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["customer.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List customer accounts"""
    conditions = [Customer.organization_id == auth.organization_id, Customer.is_deleted == False]
    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                Customer.name.ilike(search_pattern),
                Customer.email.ilike(search_pattern),
                Customer.phone_number.ilike(search_pattern),
                Customer.account_number.ilike(search_pattern)
            )
        )

    res = await db.execute(select(Customer).where(and_(*conditions)).order_by(Customer.name))
    return res.scalars().all()


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    req: CustomerCreate,
    auth: TokenPayload = Depends(PermissionChecker(["customer.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new customer profile"""
    customer = Customer(
        organization_id=auth.organization_id,
        name=req.name,
        account_number=req.account_number,
        industry=req.industry,
        website=req.website,
        phone_number=req.phone_number,
        email=req.email,
        preferred_channel=req.preferred_channel,
        assigned_account_manager_id=req.assigned_account_manager_id or auth.sub,
        tags=req.tags or [],
        custom_fields=req.custom_fields or {}
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer


@router.get("/customers/{customer_id}/360", response_model=Customer360Response)
async def get_customer_360_view(
    customer_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["customer.view_360"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full Customer 360 View:
    Includes customer intelligence, health score, contacts, activities, and complete unified timeline.
    """
    return await CRMService.get_customer_360(db, auth.organization_id, customer_id)


# ----------------------------------------------------
# Activities & Tasks Endpoints
# ----------------------------------------------------

@router.get("/activities", response_model=List[ActivityResponse])
async def list_activities(
    customer_id: Optional[str] = None,
    lead_id: Optional[str] = None,
    status: Optional[ActivityStatus] = None,
    assigned_user_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """List activities and tasks"""
    conditions = [Activity.organization_id == auth.organization_id, Activity.is_deleted == False]
    if customer_id:
        conditions.append(Activity.customer_id == customer_id)
    if lead_id:
        conditions.append(Activity.lead_id == lead_id)
    if status:
        conditions.append(Activity.status == status)
    if assigned_user_id:
        conditions.append(Activity.assigned_user_id == assigned_user_id)

    res = await db.execute(select(Activity).where(and_(*conditions)).order_by(Activity.due_date.asc()))
    return res.scalars().all()


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    req: ActivityCreate,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Create a task or follow-up activity"""
    activity = Activity(
        organization_id=auth.organization_id,
        customer_id=req.customer_id,
        lead_id=req.lead_id,
        contact_id=req.contact_id,
        activity_type=req.activity_type,
        title=req.title,
        description=req.description,
        priority=req.priority,
        status=ActivityStatus.PENDING,
        due_date=req.due_date,
        reminder_at=req.reminder_at,
        assigned_user_id=req.assigned_user_id or auth.sub,
        created_by_user_id=auth.sub,
        call_id=req.call_id,
        ticket_id=req.ticket_id,
        opportunity_id=req.opportunity_id
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


# ----------------------------------------------------
# Customer Timeline Endpoints
# ----------------------------------------------------

@router.get("/timeline/{customer_id}", response_model=List[TimelineEventResponse])
async def get_customer_timeline(
    customer_id: str,
    channel: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["customer.view_360"])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch chronological timeline events for a customer"""
    conditions = [
        CustomerTimelineEvent.customer_id == customer_id,
        CustomerTimelineEvent.organization_id == auth.organization_id
    ]
    if channel:
        conditions.append(CustomerTimelineEvent.channel == channel)

    res = await db.execute(
        select(CustomerTimelineEvent).where(and_(*conditions)).order_by(desc(CustomerTimelineEvent.occurred_at))
    )
    return res.scalars().all()


@router.post("/timeline", response_model=TimelineEventResponse, status_code=status.HTTP_201_CREATED)
async def record_timeline_event(
    req: TimelineEventCreate,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Manually append an event or interaction note to customer timeline"""
    req.actor_user_id = auth.sub
    return await CRMService.record_timeline_event(db, auth.organization_id, req)
