from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.crm.models import LeadStatus, LeadSource, ActivityType, ActivityPriority, ActivityStatus, CustomerSentiment


# Lead Schemas
class LeadCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    title: Optional[str] = None
    source: LeadSource = LeadSource.WEBSITE
    estimated_value: float = 0.0
    assigned_user_id: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    title: Optional[str] = None
    source: Optional[LeadSource] = None
    status: Optional[LeadStatus] = None
    score: Optional[int] = None
    estimated_value: Optional[float] = None
    assigned_user_id: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadConvertRequest(BaseModel):
    create_customer: bool = True
    customer_name: Optional[str] = None
    create_opportunity: bool = True
    opportunity_title: Optional[str] = None
    opportunity_amount: Optional[float] = None
    pipeline_id: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    organization_id: str
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    title: Optional[str] = None
    source: LeadSource
    status: LeadStatus
    score: int
    estimated_value: float
    assigned_user_id: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Dict[str, Any]
    is_converted: bool
    converted_at: Optional[datetime] = None
    converted_customer_id: Optional[str] = None
    converted_contact_id: Optional[str] = None
    converted_opportunity_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Contact Schemas
class ContactCreate(BaseModel):
    customer_id: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    secondary_emails: Optional[List[str]] = None
    phone_number: Optional[str] = None
    secondary_phones: Optional[List[str]] = None
    title: Optional[str] = None
    department: Optional[str] = None
    addresses: Optional[List[Dict[str, Any]]] = None
    consent_preferences: Optional[Dict[str, bool]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    customer_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    secondary_emails: Optional[List[str]] = None
    phone_number: Optional[str] = None
    secondary_phones: Optional[List[str]] = None
    title: Optional[str] = None
    department: Optional[str] = None
    addresses: Optional[List[Dict[str, Any]]] = None
    consent_preferences: Optional[Dict[str, bool]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    id: str
    organization_id: str
    customer_id: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    secondary_emails: List[str]
    phone_number: Optional[str] = None
    secondary_phones: List[str]
    title: Optional[str] = None
    department: Optional[str] = None
    addresses: List[Dict[str, Any]]
    consent_preferences: Dict[str, bool]
    tags: List[str]
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Customer Schemas
class CustomerCreate(BaseModel):
    name: str
    account_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    preferred_channel: str = "PHONE"
    assigned_account_manager_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    account_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    health_score: Optional[int] = None
    engagement_score: Optional[int] = None
    sentiment: Optional[CustomerSentiment] = None
    risk_level: Optional[str] = None
    preferred_channel: Optional[str] = None
    lifetime_value: Optional[float] = None
    assigned_account_manager_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CustomerResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    account_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    health_score: int
    engagement_score: int
    sentiment: CustomerSentiment
    risk_level: str
    preferred_channel: str
    lifetime_value: float
    open_opportunities_count: int
    open_tickets_count: int
    last_interaction_at: datetime
    assigned_account_manager_id: Optional[str] = None
    tags: List[str]
    custom_fields: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Activity Schemas
class ActivityCreate(BaseModel):
    customer_id: Optional[str] = None
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    activity_type: ActivityType = ActivityType.TASK
    title: str
    description: Optional[str] = None
    priority: ActivityPriority = ActivityPriority.MEDIUM
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    assigned_user_id: Optional[str] = None
    call_id: Optional[str] = None
    ticket_id: Optional[str] = None
    opportunity_id: Optional[str] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[ActivityPriority] = None
    status: Optional[ActivityStatus] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_user_id: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    organization_id: str
    customer_id: Optional[str] = None
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    activity_type: ActivityType
    title: str
    description: Optional[str] = None
    priority: ActivityPriority
    status: ActivityStatus
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_user_id: Optional[str] = None
    created_by_user_id: str
    call_id: Optional[str] = None
    ticket_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Timeline Schemas
class TimelineEventCreate(BaseModel):
    customer_id: str
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    channel: str
    event_type: str
    title: str
    description: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    actor_user_id: Optional[str] = None
    actor_name: str = "System"
    occurred_at: Optional[datetime] = None


class TimelineEventResponse(BaseModel):
    id: str
    organization_id: str
    customer_id: str
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    channel: str
    event_type: str
    title: str
    description: Optional[str] = None
    metadata_json: Dict[str, Any]
    actor_user_id: Optional[str] = None
    actor_name: str
    occurred_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Customer 360 Aggregated Response
class Customer360Response(BaseModel):
    customer: CustomerResponse
    contacts: List[ContactResponse]
    activities: List[ActivityResponse]
    timeline: List[TimelineEventResponse]
    metrics: Dict[str, Any]
