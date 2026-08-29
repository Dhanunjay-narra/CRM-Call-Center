from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.routing.models import RoutingStrategy, IVRNodeType


# Queue Schemas
class CallQueueCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy: RoutingStrategy = RoutingStrategy.LONGEST_IDLE
    sla_threshold_seconds: int = 20
    max_queue_size: int = 50
    timeout_seconds: int = 300
    required_skills: List[str] = []
    default_language: str = "en"
    overflow_queue_id: Optional[str] = None
    enable_callback: bool = True


class CallQueueResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    strategy: RoutingStrategy
    sla_threshold_seconds: int
    max_queue_size: int
    timeout_seconds: int
    required_skills: List[str]
    default_language: str
    overflow_queue_id: Optional[str] = None
    enable_callback: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueueMemberAdd(BaseModel):
    agent_id: str
    user_id: str
    priority: int = 1
    weight: int = 100


class QueueMemberResponse(BaseModel):
    id: str
    queue_id: str
    agent_id: str
    user_id: str
    priority: int
    weight: int

    model_config = ConfigDict(from_attributes=True)


# Smart Routing Agent Match Request/Response
class AgentMatchRequest(BaseModel):
    queue_id: Optional[str] = None
    skills_required: List[str] = []
    language_required: str = "en"
    customer_id: Optional[str] = None
    priority: int = 1


class AgentMatchResponse(BaseModel):
    matched: bool
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    strategy_used: RoutingStrategy
    score: float = 0.0
    reason: str


# Visual IVR Schemas
class IVRNodeSchema(BaseModel):
    node_key: str
    node_type: IVRNodeType
    prompt_text: Optional[str] = None
    prompt_audio_url: Optional[str] = None
    tts_voice: str = "female_1"
    dtmf_options: Dict[str, str] = {}
    target_queue_id: Optional[str] = None


class IVRFlowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    entry_node_id: str = "welcome"
    nodes: List[IVRNodeSchema] = []
    flow_data: Optional[Dict[str, Any]] = None


class IVRFlowResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    entry_node_id: Optional[str] = None
    flow_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IVRSimulateRequest(BaseModel):
    flow_id: str
    current_node_key: Optional[str] = None
    digits_pressed: Optional[str] = None
    selected_language: str = "en"


class IVRSimulateResponse(BaseModel):
    flow_id: str
    current_node_key: str
    node_type: IVRNodeType
    prompt_text: Optional[str] = None
    available_dtmf: Dict[str, str] = {}
    is_terminal: bool = False
    routed_queue_id: Optional[str] = None
