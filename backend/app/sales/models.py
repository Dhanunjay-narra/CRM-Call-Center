import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class OpportunityStatus(str, enum.Enum):
    OPEN = "OPEN"
    WON = "WON"
    LOST = "LOST"
    ABANDONED = "ABANDONED"


class CampaignType(str, enum.Enum):
    LEAD_GENERATION = "LEAD_GENERATION"
    SALES = "SALES"
    RETENTION = "RETENTION"
    REACTIVATION = "REACTIVATION"
    UPSELL = "UPSELL"
    CROSS_SELL = "CROSS_SELL"
    SURVEY = "SURVEY"
    PROMOTIONAL = "PROMOTIONAL"
    SERVICE_NOTIFICATION = "SERVICE_NOTIFICATION"


class CampaignChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    VOICE_CALL = "VOICE_CALL"
    OMNICHANNEL = "OMNICHANNEL"


class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


class Pipeline(TenantBaseModel):
    """Sales Pipeline entity supporting multiple custom pipelines"""
    __tablename__ = "sales_pipelines"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    stages = relationship("PipelineStage", back_populates="pipeline", order_by="PipelineStage.order", cascade="all, delete-orphan")
    opportunities = relationship("Opportunity", back_populates="pipeline")


class PipelineStage(TenantBaseModel):
    """Stages within a Pipeline with probability weights"""
    __tablename__ = "sales_pipeline_stages"

    pipeline_id = Column(String(36), ForeignKey("sales_pipelines.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    order = Column(Integer, default=0, nullable=False)
    default_probability = Column(Integer, default=20, nullable=False)  # 0 to 100%
    is_won_stage = Column(Boolean, default=False, nullable=False)
    is_lost_stage = Column(Boolean, default=False, nullable=False)

    pipeline = relationship("Pipeline", back_populates="stages")
    opportunities = relationship("Opportunity", back_populates="stage")


class Opportunity(TenantBaseModel):
    """Deal / Sales Opportunity entity"""
    __tablename__ = "sales_opportunities"

    pipeline_id = Column(String(36), ForeignKey("sales_pipelines.id"), nullable=False, index=True)
    stage_id = Column(String(36), ForeignKey("sales_pipeline_stages.id"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("crm_customers.id"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    lead_id = Column(String(36), ForeignKey("crm_leads.id"), nullable=True, index=True)

    title = Column(String(200), nullable=False)
    amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    probability = Column(Integer, default=20, nullable=False)  # 0 to 100%
    
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.OPEN, nullable=False, index=True)
    expected_close_date = Column(DateTime(timezone=True), nullable=True)
    actual_close_date = Column(DateTime(timezone=True), nullable=True)
    
    owner_user_id = Column(String(36), nullable=False, index=True)
    
    products = Column(JSON, default=list, nullable=False)  # [{name, qty, unit_price}]
    competitors = Column(JSON, default=list, nullable=False)
    win_loss_reason = Column(Text, nullable=True)
    next_step = Column(String(255), nullable=True)
    custom_fields = Column(JSON, default=dict, nullable=False)

    pipeline = relationship("Pipeline", back_populates="opportunities")
    stage = relationship("PipelineStage", back_populates="opportunities")


class Campaign(TenantBaseModel):
    """Multi-channel outbound campaign management"""
    __tablename__ = "crm_campaigns"

    name = Column(String(150), nullable=False)
    campaign_type = Column(Enum(CampaignType), default=CampaignType.SALES, nullable=False)
    channel = Column(Enum(CampaignChannel), default=CampaignChannel.EMAIL, nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False, index=True)
    
    description = Column(Text, nullable=True)
    budget = Column(Float, default=0.0, nullable=False)
    actual_cost = Column(Float, default=0.0, nullable=False)
    
    # Message content & Template reference
    template_id = Column(String(36), nullable=True)
    subject = Column(String(255), nullable=True)
    message_body = Column(Text, nullable=True)
    
    # Audience & Filters
    target_segment = Column(String(100), nullable=True)
    filter_criteria = Column(JSON, default=dict, nullable=False)
    
    # Execution & Scheduling
    scheduled_start = Column(DateTime(timezone=True), nullable=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Performance Metrics
    total_audience = Column(Integer, default=0, nullable=False)
    total_sent = Column(Integer, default=0, nullable=False)
    total_delivered = Column(Integer, default=0, nullable=False)
    total_opened = Column(Integer, default=0, nullable=False)
    total_clicked = Column(Integer, default=0, nullable=False)
    total_converted = Column(Integer, default=0, nullable=False)
    revenue_generated = Column(Float, default=0.0, nullable=False)

    created_by_user_id = Column(String(36), nullable=False)
    audience_members = relationship("CampaignAudienceMember", back_populates="campaign", cascade="all, delete-orphan")


class CampaignAudienceMember(TenantBaseModel):
    """Recipient member in a campaign blast"""
    __tablename__ = "crm_campaign_audience"

    campaign_id = Column(String(36), ForeignKey("crm_campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), nullable=True)
    contact_id = Column(String(36), nullable=True)
    lead_id = Column(String(36), nullable=True)
    
    recipient_identifier = Column(String(255), nullable=False)  # email, phone number
    delivery_status = Column(String(50), default="PENDING", nullable=False)  # PENDING, SENT, DELIVERED, FAILED, OPENED, CONVERTED
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)

    campaign = relationship("Campaign", back_populates="audience_members")
