from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.communications.models import ChannelType, MessageDirection, MessageStatus, ConversationStatus


# Message Schemas
class MessageSendRequest(BaseModel):
    conversation_id: Optional[str] = None
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: ChannelType
    recipient_identifier: str  # email or phone number
    sender_identifier: Optional[str] = None
    subject: Optional[str] = None
    body: str
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class InboundWebhookMessage(BaseModel):
    channel: ChannelType
    from_identifier: str
    to_identifier: str
    body: str
    subject: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    customer_id: Optional[str] = None
    direction: MessageDirection
    channel: ChannelType
    status: MessageStatus
    sender_identifier: str
    recipient_identifier: str
    subject: Optional[str] = None
    body: str
    attachments: List[Dict[str, Any]]
    sent_by_user_id: Optional[str] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Conversation Schemas
class ConversationCreate(BaseModel):
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: ChannelType
    subject: Optional[str] = None
    assigned_agent_id: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    organization_id: str
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    channel: ChannelType
    subject: Optional[str] = None
    status: ConversationStatus
    assigned_agent_id: Optional[str] = None
    last_message_at: datetime
    unread_agent_count: int
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Template Schemas
class MessageTemplateCreate(BaseModel):
    name: str
    channel: ChannelType
    category: str = "General"
    subject: Optional[str] = None
    body_template: str
    variables: List[str] = []


class MessageTemplateResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    channel: ChannelType
    category: str
    subject: Optional[str] = None
    body_template: str
    variables: List[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
