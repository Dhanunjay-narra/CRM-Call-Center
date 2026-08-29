from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from app.modules.agents.models import AgentStatus

class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    skills: Optional[str] = "GENERAL"

class AgentLogin(BaseModel):
    email: EmailStr
    password: str

class AgentStatusUpdate(BaseModel):
    status: AgentStatus

class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    skills: str
    status: AgentStatus
    total_calls_handled: int
    active_call_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent: AgentResponse
