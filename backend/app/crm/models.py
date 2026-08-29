import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    NURTURING = "NURTURING"
    OPPORTUNITY = "OPPORTUNITY"
    WON = "WON"
    LOST = "LOST"


class LeadSource(str, enum.Enum):
    WEBSITE = "WEBSITE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    CAMPAIGN = "CAMPAIGN"
    REFERRAL = "REFERRAL"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    ADVERTISEMENT = "ADVERTISEMENT"
    MANUAL_ENTRY = "MANUAL_ENTRY"
    IMPORT = "IMPORT"
    API = "API"


class ActivityType(str, enum.Enum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    MEETING = "MEETING"
    TASK = "TASK"
    NOTE = "NOTE"
    FOLLOW_UP = "FOLLOW_UP"


class ActivityPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class ActivityStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    OVERDUE = "OVERDUE"


class CustomerSentiment(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    CHURN_RISK = "CHURN_RISK"


class Lead(TenantBaseModel):
    """Lead lifecycle entity with scoring, distribution, and conversion"""
    __tablename__ = "crm_leads"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone_number = Column(String(50), nullable=True, index=True)
    company_name = Column(String(150), nullable=True)
    title = Column(String(100), nullable=True)
    
    source = Column(Enum(LeadSource), default=LeadSource.WEBSITE, nullable=False)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True)
    
    score = Column(Integer, default=10, nullable=False)  # 0 to 100
    estimated_value = Column(Float, default=0.0, nullable=False)
    
    assigned_user_id = Column(String(36), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default=dict, nullable=False)
    
    # Conversion references
    is_converted = Column(Boolean, default=False, nullable=False)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_customer_id = Column(String(36), nullable=True)
    converted_contact_id = Column(String(36), nullable=True)
    converted_opportunity_id = Column(String(36), nullable=True)


class Contact(TenantBaseModel):
    """Person associated with a customer account or standalone prospect"""
    __tablename__ = "crm_contacts"

    customer_id = Column(String(36), ForeignKey("crm_customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    secondary_emails = Column(JSON, default=list, nullable=False)
    
    phone_number = Column(String(50), nullable=True, index=True)
    secondary_phones = Column(JSON, default=list, nullable=False)
    
    title = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    addresses = Column(JSON, default=list, nullable=False)
    
    consent_preferences = Column(JSON, default=lambda: {"email": True, "sms": True, "calls": True, "whatsapp": True}, nullable=False)
    tags = Column(JSON, default=list, nullable=False)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="contacts")


class Customer(TenantBaseModel):
    """Central Customer 360 Entity"""
    __tablename__ = "crm_customers"

    name = Column(String(200), nullable=False, index=True)
    account_number = Column(String(50), nullable=True, index=True)
    industry = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    
    # Customer Intelligence
    health_score = Column(Integer, default=85, nullable=False)  # 0 to 100
    engagement_score = Column(Integer, default=70, nullable=False)  # 0 to 100
    sentiment = Column(Enum(CustomerSentiment), default=CustomerSentiment.POSITIVE, nullable=False)
    risk_level = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    
    preferred_channel = Column(String(20), default="PHONE", nullable=False)  # PHONE, EMAIL, WHATSAPP, SMS
    lifetime_value = Column(Float, default=0.0, nullable=False)
    open_opportunities_count = Column(Integer, default=0, nullable=False)
    open_tickets_count = Column(Integer, default=0, nullable=False)
    last_interaction_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    assigned_account_manager_id = Column(String(36), nullable=True, index=True)
    tags = Column(JSON, default=list, nullable=False)
    custom_fields = Column(JSON, default=dict, nullable=False)

    contacts = relationship("Contact", back_populates="customer", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="customer")
    timeline_events = relationship("CustomerTimelineEvent", back_populates="customer", cascade="all, delete-orphan")


class Activity(TenantBaseModel):
    """Unified Activities & Tasks (Call, Email, SMS, WhatsApp, Meeting, Task, Follow-up)"""
    __tablename__ = "crm_activities"

    customer_id = Column(String(36), ForeignKey("crm_customers.id", ondelete="CASCADE"), nullable=True, index=True)
    lead_id = Column(String(36), ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id", ondelete="CASCADE"), nullable=True, index=True)
    
    activity_type = Column(Enum(ActivityType), default=ActivityType.TASK, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    priority = Column(Enum(ActivityPriority), default=ActivityPriority.MEDIUM, nullable=False)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False, index=True)
    
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    assigned_user_id = Column(String(36), nullable=True, index=True)
    created_by_user_id = Column(String(36), nullable=False)
    
    call_id = Column(String(36), nullable=True)
    ticket_id = Column(String(36), nullable=True)
    opportunity_id = Column(String(36), nullable=True)

    customer = relationship("Customer", back_populates="activities")


class CustomerTimelineEvent(TenantBaseModel):
    """
    Unified Customer 360 Chronological Timeline.
    Records every single event: call, WhatsApp, opportunity, quote, support ticket, feedback, notes.
    """
    __tablename__ = "crm_timeline_events"

    customer_id = Column(String(36), ForeignKey("crm_customers.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(36), nullable=True)
    lead_id = Column(String(36), nullable=True)
    
    channel = Column(String(30), nullable=False)  # CALL, WHATSAPP, EMAIL, SMS, TICKET, SALES, SYSTEM
    event_type = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    metadata_json = Column(JSON, default=dict, nullable=False)
    actor_user_id = Column(String(36), nullable=True)
    actor_name = Column(String(150), default="System", nullable=False)
    occurred_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    customer = relationship("Customer", back_populates="timeline_events")
