import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class TicketStatus(str, enum.Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SLAStatus(str, enum.Enum):
    WITHIN_SLA = "WITHIN_SLA"
    WARNING_80_PERCENT = "WARNING_80_PERCENT"
    BREACHED = "BREACHED"
    PAUSED = "PAUSED"


class SLAPolicy(TenantBaseModel):
    """SLA Policy definitions for support tiers and priority matrix"""
    __tablename__ = "support_sla_policies"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False, unique=False)
    
    first_response_time_minutes = Column(Integer, default=60, nullable=False) # e.g. Critical: 15m, High: 30m, Med: 60m
    resolution_time_minutes = Column(Integer, default=480, nullable=False)    # e.g. Critical: 120m, High: 240m
    warning_threshold_percent = Column(Integer, default=80, nullable=False)  # 80% triggers supervisor warning
    
    escalate_to_manager_on_breach = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class SupportTicket(TenantBaseModel):
    """Customer Support Ticket entity with integrated SLA tracking"""
    __tablename__ = "support_tickets"

    ticket_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(String(36), ForeignKey("crm_customers.id"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Technical Support", nullable=False, index=True)
    
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False, index=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.NEW, nullable=False, index=True)
    
    assigned_user_id = Column(String(36), nullable=True, index=True)
    assigned_team_id = Column(String(36), nullable=True)
    
    # SLA Metrics
    sla_policy_id = Column(String(36), ForeignKey("support_sla_policies.id"), nullable=True)
    sla_status = Column(Enum(SLAStatus), default=SLAStatus.WITHIN_SLA, nullable=False, index=True)
    
    first_response_due_at = Column(DateTime(timezone=True), nullable=True)
    resolution_due_at = Column(DateTime(timezone=True), nullable=True)
    first_responded_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    is_sla_breached = Column(Boolean, default=False, nullable=False)
    sla_warning_sent = Column(Boolean, default=False, nullable=False)
    escalated_to_user_id = Column(String(36), nullable=True)
    
    resolution_code = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    csat_score = Column(Integer, nullable=True)  # 1 to 5
    
    tags = Column(JSON, default=list, nullable=False)
    custom_fields = Column(JSON, default=dict, nullable=False)

    comments = relationship("TicketComment", back_populates="ticket", order_by="TicketComment.created_at", cascade="all, delete-orphan")


class TicketComment(TenantBaseModel):
    """Internal notes and public replies on support ticket"""
    __tablename__ = "support_ticket_comments"

    ticket_id = Column(String(36), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    author_name = Column(String(150), default="Agent", nullable=False)
    
    is_internal_note = Column(Boolean, default=False, nullable=False) # True = internal agent note, False = visible to customer
    body = Column(Text, nullable=False)
    attachments = Column(JSON, default=list, nullable=False)

    ticket = relationship("SupportTicket", back_populates="comments")


class KnowledgeCategory(TenantBaseModel):
    """Knowledge base category"""
    __tablename__ = "kb_categories"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), default="folder", nullable=False)
    order = Column(Integer, default=0, nullable=False)

    articles = relationship("KnowledgeArticle", back_populates="category", cascade="all, delete-orphan")


class KnowledgeArticle(TenantBaseModel):
    """Knowledge base articles, FAQs, troubleshooting guides, and agent call scripts"""
    __tablename__ = "kb_articles"

    category_id = Column(String(36), ForeignKey("kb_categories.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, index=True)
    
    content_markdown = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    
    is_public = Column(Boolean, default=True, nullable=False)       # Public FAQ vs Agent-only internal script
    is_call_script = Column(Boolean, default=False, nullable=False) # Marked as active agent talking script
    
    view_count = Column(Integer, default=0, nullable=False)
    helpful_upvotes = Column(Integer, default=0, nullable=False)
    helpful_downvotes = Column(Integer, default=0, nullable=False)
    
    tags = Column(JSON, default=list, nullable=False)
    created_by_user_id = Column(String(36), nullable=False)

    category = relationship("KnowledgeCategory", back_populates="articles")
