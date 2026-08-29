from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Text
import enum
from datetime import datetime, timezone
from app.core.database import Base

class TicketPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TicketStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(String, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    assigned_agent_id = Column(String, nullable=True, index=True)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    channel = Column(String, default="VOICE_CALL")  # VOICE_CALL, CHAT, EMAIL
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
