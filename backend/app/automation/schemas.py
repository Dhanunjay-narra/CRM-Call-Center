from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.automation.models import WorkflowTriggerType, WorkflowActionType, ExecutionStatus


class WorkflowCondition(BaseModel):
    field: str
    operator: str  # "equals", "greater_than", "less_than", "contains", "in"
    value: Any


class WorkflowAction(BaseModel):
    action_type: WorkflowActionType
    params: Dict[str, Any] = {}


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: WorkflowTriggerType
    conditions: List[WorkflowCondition] = []
    actions: List[WorkflowAction] = []
    canvas_graph: Optional[Dict[str, Any]] = None
    is_active: bool = True


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[WorkflowTriggerType] = None
    conditions: Optional[List[WorkflowCondition]] = None
    actions: Optional[List[WorkflowAction]] = None
    canvas_graph: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    trigger_type: WorkflowTriggerType
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    canvas_graph: Dict[str, Any]
    is_active: bool
    execution_count: int
    last_executed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    trigger_event_type: str
    entity_id: str
    entity_type: str
    status: ExecutionStatus
    logs: List[str]
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
