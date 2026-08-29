import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class ChannelType(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    VOICE = "VOICE"
    IN_APP = "IN_APP"


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class MessageStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"
    FAILED = "FAILED"


class ConversationStatus(str, enum.Enum):
    OPEN = "OPEN"
    PENDING_AGENT = "PENDING_AGENT"
    PENDING_CUSTOMER = "PENDING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Conversation(TenantBaseModel):
    """Unified omnichannel conversation thread"""
    __tablename__ = "comm_conversations"

    customer_id = Column(String(36), ForeignKey("crm_customers.id"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    channel = Column(Enum(ChannelType), default=ChannelType.WHATSAPP, nullable=False, index=True)
    
    subject = Column(String(255), nullable=True)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.OPEN, nullable=False, index=True)
    
    assigned_agent_id = Column(String(36), nullable=True, index=True)
    last_message_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    unread_agent_count = Column(Integer, default=0, nullable=False)
    
    tags = Column(JSON, default=list, nullable=False)
    custom_fields = Column(JSON, default=dict, nullable=False)

    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at", cascade="all, delete-orphan")


class Message(TenantBaseModel):
    """Individual message (Email, SMS, WhatsApp) within conversation thread"""
    __tablename__ = "comm_messages"

    conversation_id = Column(String(36), ForeignKey("comm_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), nullable=True, index=True)
    
    direction = Column(Enum(MessageDirection), nullable=False)
    channel = Column(Enum(ChannelType), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT, nullable=False)
    
    sender_identifier = Column(String(255), nullable=False)     # email or phone
    recipient_identifier = Column(String(255), nullable=False)  # email or phone
    
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    attachments = Column(JSON, default=list, nullable=False)    # [{filename, url, content_type, size}]
    
    sent_by_user_id = Column(String(36), nullable=True)
    provider_message_id = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    conversation = relationship("Conversation", back_populates="messages")


class MessageTemplate(TenantBaseModel):
    """Reusable message template with dynamic {{variables}}"""
    __tablename__ = "comm_message_templates"

    name = Column(String(150), nullable=False)
    channel = Column(Enum(ChannelType), default=ChannelType.EMAIL, nullable=False)
    category = Column(String(100), default="General", nullable=False)
    subject = Column(String(255), nullable=True)
    body_template = Column(Text, nullable=False)
    variables = Column(JSON, default=list, nullable=False) # e.g. ["customer_name", "order_id", "agent_name"]
    is_active = Column(Boolean, default=True, nullable=False)
