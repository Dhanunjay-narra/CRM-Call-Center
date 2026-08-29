from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.support.models import TicketStatus, TicketPriority, SLAStatus


# SLA Policy Schemas
class SLAPolicyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM
    first_response_time_minutes: int = 60
    resolution_time_minutes: int = 480
    warning_threshold_percent: int = 80
    escalate_to_manager_on_breach: bool = True


class SLAPolicyResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    priority: TicketPriority
    first_response_time_minutes: int
    resolution_time_minutes: int
    warning_threshold_percent: int
    escalate_to_manager_on_breach: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Comment Schemas
class TicketCommentCreate(BaseModel):
    body: str
    is_internal_note: bool = False
    attachments: Optional[List[Dict[str, Any]]] = None


class TicketCommentResponse(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    author_name: str
    is_internal_note: bool
    body: str
    attachments: List[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Ticket Schemas
class SupportTicketCreate(BaseModel):
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    title: str
    description: str
    category: str = "Technical Support"
    priority: TicketPriority = TicketPriority.MEDIUM
    assigned_user_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class SupportTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_user_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    tags: Optional[List[str]] = None


class TicketResolveRequest(BaseModel):
    resolution_code: str = "RESOLVED_SUCCESSFULLY"
    resolution_notes: str
    csat_score: Optional[int] = None


class SupportTicketResponse(BaseModel):
    id: str
    organization_id: str
    ticket_number: str
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    title: str
    description: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    assigned_user_id: Optional[str] = None
    assigned_team_id: Optional[str] = None
    sla_status: SLAStatus
    first_response_due_at: Optional[datetime] = None
    resolution_due_at: Optional[datetime] = None
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    is_sla_breached: bool
    sla_warning_sent: bool
    resolution_code: Optional[str] = None
    resolution_notes: Optional[str] = None
    csat_score: Optional[int] = None
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Knowledge Base Schemas
class KnowledgeCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: str = "folder"
    order: int = 0


class KnowledgeCategoryResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon: str
    order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeArticleCreate(BaseModel):
    category_id: str
    title: str
    content_markdown: str
    is_public: bool = True
    is_call_script: bool = False
    tags: Optional[List[str]] = None


class KnowledgeArticleResponse(BaseModel):
    id: str
    organization_id: str
    category_id: str
    title: str
    slug: str
    content_markdown: str
    is_public: bool
    is_call_script: bool
    view_count: int
    helpful_upvotes: int
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
