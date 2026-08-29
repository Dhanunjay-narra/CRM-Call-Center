from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.modules.tickets.models import TicketPriority, TicketStatus

class TicketCreate(BaseModel):
    customer_id: str
    subject: str
    description: str
    priority: Optional[TicketPriority] = TicketPriority.MEDIUM
    channel: Optional[str] = "VOICE_CALL"

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_agent_id: Optional[str] = None

class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_number: str
    customer_id: str
    assigned_agent_id: Optional[str] = None
    subject: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    channel: str
