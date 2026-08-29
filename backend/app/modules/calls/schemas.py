from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.modules.calls.models import CallDirection, CallStatus

class CallInitiate(BaseModel):
    customer_id: str
    direction: Optional[CallDirection] = CallDirection.INBOUND
    queue_name: Optional[str] = "General Support"
    priority: Optional[int] = 1

class CallAction(BaseModel):
    action: str
    agent_id: Optional[str] = None
    target_agent_id: Optional[str] = None

class WebRTCSignalingMessage(BaseModel):
    call_id: str
    type: str
    payload: dict

class CallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    call_id: str
    customer_id: str
    agent_id: Optional[str] = None
    direction: CallDirection
    status: CallStatus
    queue_name: str
    priority: int
    duration_seconds: int
    sentiment_score: float
