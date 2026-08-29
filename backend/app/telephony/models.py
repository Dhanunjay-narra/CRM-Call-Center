import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class AgentState(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    ON_CALL = "ON_CALL"
    AFTER_CALL_WORK = "AFTER_CALL_WORK"
    BREAK = "BREAK"
    TRAINING = "TRAINING"
    OFFLINE = "OFFLINE"


class BreakType(str, enum.Enum):
    LUNCH = "LUNCH"
    TEA = "TEA"
    PERSONAL = "PERSONAL"
    TRAINING = "TRAINING"
    MEETING = "MEETING"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    OTHER = "OTHER"


class CallDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class CallStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RINGING = "RINGING"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    WRAP_UP = "AFTER_CALL_WORK"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"
    ABANDONED = "ABANDONED"
    BUSY = "BUSY"
    FAILED = "FAILED"


class TransferType(str, enum.Enum):
    COLD = "COLD"
    WARM = "WARM"


class AgentProfile(TenantBaseModel):
    """Workforce Agent profile with skills, languages, and presence tracking"""
    __tablename__ = "cc_agent_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    employee_id = Column(String(50), nullable=True)
    
    # Skills & Languages for Intelligent Routing
    skills = Column(JSON, default=lambda: ["General Support"], nullable=False) # e.g. ["Sales", "Telugu", "VIP", "Tech Support"]
    languages = Column(JSON, default=lambda: ["en"], nullable=False)           # e.g. ["en", "te", "hi", "es"]
    proficiency_level = Column(Integer, default=3, nullable=False)              # 1 to 5
    
    current_state = Column(Enum(AgentState), default=AgentState.OFFLINE, nullable=False, index=True)
    current_break_type = Column(Enum(BreakType), nullable=True)
    state_changed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Telephony extension
    sip_extension = Column(String(20), nullable=True)
    max_concurrent_calls = Column(Integer, default=1, nullable=False)
    max_concurrent_chats = Column(Integer, default=3, nullable=False)
    
    # Performance telemetry metrics
    total_calls_handled_today = Column(Integer, default=0, nullable=False)
    total_talk_time_seconds = Column(Integer, default=0, nullable=False)
    total_acw_time_seconds = Column(Integer, default=0, nullable=False)
    total_break_time_seconds = Column(Integer, default=0, nullable=False)
    occupancy_rate = Column(Float, default=0.0, nullable=False)

    state_logs = relationship("AgentStateLog", back_populates="agent", cascade="all, delete-orphan")


class AgentStateLog(TenantBaseModel):
    """Historical audit log of agent workforce state changes and break durations"""
    __tablename__ = "cc_agent_state_logs"

    agent_id = Column(String(36), ForeignKey("cc_agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    previous_state = Column(String(50), nullable=False)
    new_state = Column(String(50), nullable=False)
    break_type = Column(String(50), nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    agent = relationship("AgentProfile", back_populates="state_logs")


class CallRecord(TenantBaseModel):
    """Comprehensive Inbound/Outbound Call lifecycle entity"""
    __tablename__ = "cc_calls"

    direction = Column(Enum(CallDirection), default=CallDirection.INBOUND, nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.QUEUED, nullable=False, index=True)
    
    from_number = Column(String(50), nullable=False, index=True)
    to_number = Column(String(50), nullable=False, index=True)
    caller_name = Column(String(150), nullable=True)
    
    customer_id = Column(String(36), ForeignKey("crm_customers.id"), nullable=True, index=True)
    contact_id = Column(String(36), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    lead_id = Column(String(36), ForeignKey("crm_leads.id"), nullable=True, index=True)
    
    queue_id = Column(String(36), nullable=True, index=True)
    agent_id = Column(String(36), ForeignKey("cc_agent_profiles.id"), nullable=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)  # agent's user_id
    
    # Timestamps & Call KPI metrics
    queued_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    ringing_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    queue_wait_duration_seconds = Column(Integer, default=0, nullable=False) # ASA metric
    talk_duration_seconds = Column(Integer, default=0, nullable=False)       # Talk time
    hold_duration_seconds = Column(Integer, default=0, nullable=False)       # Hold time
    wrap_up_duration_seconds = Column(Integer, default=0, nullable=False)    # ACW time
    total_handle_time_seconds = Column(Integer, default=0, nullable=False)   # AHT metric
    
    # Routing telemetry
    skills_required = Column(JSON, default=list, nullable=False)
    language_required = Column(String(10), default="en", nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    
    # Recording reference
    recording_url = Column(String(500), nullable=True)
    recording_duration_seconds = Column(Integer, default=0, nullable=False)

    disposition = relationship("CallDisposition", back_populates="call", uselist=False, cascade="all, delete-orphan")


class CallDisposition(TenantBaseModel):
    """Post-call outcome disposition and agent summary"""
    __tablename__ = "cc_call_dispositions"

    call_id = Column(String(36), ForeignKey("cc_calls.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    agent_user_id = Column(String(36), nullable=False)
    
    disposition_code = Column(String(100), nullable=False)  # e.g. "INTERESTED", "RESOLVED", "CALLBACK_REQUESTED"
    category = Column(String(100), default="General", nullable=False)
    summary_notes = Column(Text, nullable=True)
    
    follow_up_required = Column(Boolean, default=False, nullable=False)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(JSON, default=list, nullable=False)

    call = relationship("CallRecord", back_populates="disposition")
