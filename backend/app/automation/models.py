import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class WorkflowTriggerType(str, enum.Enum):
    LEAD_CREATED = "LeadCreated"
    LEAD_UPDATED = "LeadUpdated"
    CALL_COMPLETED = "CallCompleted"
    TICKET_CREATED = "TicketCreated"
    TICKET_SLA_BREACHED = "SLABreached"
    OPPORTUNITY_CREATED = "OpportunityCreated"
    OPPORTUNITY_STAGE_CHANGED = "OpportunityStageChanged"
    FEEDBACK_SUBMITTED = "FeedbackSubmitted"
    SCHEDULED_CRON = "ScheduledCron"


class WorkflowActionType(str, enum.Enum):
    ASSIGN_AGENT = "ASSIGN_AGENT"
    CREATE_TASK = "CREATE_TASK"
    SEND_EMAIL = "SEND_EMAIL"
    SEND_SMS = "SEND_SMS"
    SEND_WHATSAPP = "SEND_WHATSAPP"
    CREATE_TICKET = "CREATE_TICKET"
    CHANGE_STATUS = "CHANGE_STATUS"
    ADD_TAG = "ADD_TAG"
    CREATE_OPPORTUNITY = "CREATE_OPPORTUNITY"
    NOTIFY_SUPERVISOR = "NOTIFY_SUPERVISOR"


class ExecutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Workflow(TenantBaseModel):
    """Event-Driven Visual Workflow entity"""
    __tablename__ = "auto_workflows"

    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(Enum(WorkflowTriggerType), nullable=False, index=True)
    
    # Conditions: [{"field": "score", "operator": "greater_than", "value": 75}]
    conditions = Column(JSON, default=list, nullable=False)
    
    # Actions: [{"action_type": "CREATE_TASK", "params": {"title": "Call hot lead", "priority": "HIGH"}}]
    actions = Column(JSON, default=list, nullable=False)
    
    # Visual graph structure for UI builder
    canvas_graph = Column(JSON, default=dict, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    execution_count = Column(Integer, default=0, nullable=False)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)

    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(TenantBaseModel):
    """Run log for individual workflow execution instances"""
    __tablename__ = "auto_workflow_executions"

    workflow_id = Column(String(36), ForeignKey("auto_workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_event_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    entity_type = Column(String(50), nullable=False)
    
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False, index=True)
    logs = Column(JSON, default=list, nullable=False)
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow = relationship("Workflow", back_populates="executions")
