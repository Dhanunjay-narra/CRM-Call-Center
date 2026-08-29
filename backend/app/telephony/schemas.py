from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.telephony.models import AgentState, BreakType, CallDirection, CallStatus, TransferType


# Agent Profile Schemas
class AgentProfileCreate(BaseModel):
    user_id: str
    employee_id: Optional[str] = None
    skills: List[str] = ["General Support"]
    languages: List[str] = ["en"]
    proficiency_level: int = 3
    sip_extension: Optional[str] = None


class AgentProfileUpdate(BaseModel):
    employee_id: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    proficiency_level: Optional[int] = None
    sip_extension: Optional[str] = None


class AgentStateChangeRequest(BaseModel):
    state: AgentState
    break_type: Optional[BreakType] = None


class AgentProfileResponse(BaseModel):
    id: str
    organization_id: str
    user_id: str
    employee_id: Optional[str] = None
    skills: List[str]
    languages: List[str]
    proficiency_level: int
    current_state: AgentState
    current_break_type: Optional[BreakType] = None
    state_changed_at: datetime
    sip_extension: Optional[str] = None
    total_calls_handled_today: int
    total_talk_time_seconds: int
    occupancy_rate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Call Schemas
class CallInitiateRequest(BaseModel):
    direction: CallDirection = CallDirection.OUTBOUND
    from_number: str
    to_number: str
    caller_name: Optional[str] = None
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    queue_id: Optional[str] = None
    skills_required: Optional[List[str]] = None
    language_required: str = "en"
    priority: int = 1


class CallTransferRequest(BaseModel):
    target_agent_id: Optional[str] = None
    target_queue_id: Optional[str] = None
    target_phone_number: Optional[str] = None
    transfer_type: TransferType = TransferType.COLD


class CallDispositionRequest(BaseModel):
    disposition_code: str
    category: str = "General"
    summary_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class CallDispositionResponse(BaseModel):
    id: str
    call_id: str
    agent_user_id: str
    disposition_code: str
    category: str
    summary_notes: Optional[str] = None
    follow_up_required: bool
    follow_up_date: Optional[datetime] = None
    tags: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallRecordResponse(BaseModel):
    id: str
    organization_id: str
    direction: CallDirection
    status: CallStatus
    from_number: str
    to_number: str
    caller_name: Optional[str] = None
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    queue_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    queued_at: datetime
    ringing_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    queue_wait_duration_seconds: int
    talk_duration_seconds: int
    hold_duration_seconds: int
    wrap_up_duration_seconds: int
    total_handle_time_seconds: int
    recording_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
