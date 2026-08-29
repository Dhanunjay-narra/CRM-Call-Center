from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum
import enum
from datetime import datetime, timezone
from app.core.database import Base

class AgentStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    WRAP_UP = "WRAP_UP"
    OFFLINE = "OFFLINE"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    skills = Column(String, default="GENERAL,BILLING,TECHNICAL")
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.OFFLINE)
    active_call_id = Column(String, nullable=True)
    total_calls_handled = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
