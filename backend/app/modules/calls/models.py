from sqlalchemy import Column, String, DateTime, Integer, Float, Enum as SQLEnum
import enum
from datetime import datetime, timezone
from app.core.database import Base

class CallDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

class CallStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RINGING = "RINGING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    WRAP_UP = "WRAP_UP"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"

class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(String, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=True, index=True)
    direction = Column(SQLEnum(CallDirection), default=CallDirection.INBOUND)
    status = Column(SQLEnum(CallStatus), default=CallStatus.QUEUED)
    queue_name = Column(String, default="General Support")
    priority = Column(Integer, default=1)
    duration_seconds = Column(Integer, default=0)
    hold_duration_seconds = Column(Integer, default=0)
    recording_url = Column(String, nullable=True)
    sentiment_score = Column(Float, default=0.0)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)
