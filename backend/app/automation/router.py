from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.core.events import DomainEvent
from app.automation.models import Workflow, WorkflowExecution, WorkflowTriggerType
from app.automation.schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowExecutionResponse
)
from app.automation.service import AutomationService

router = APIRouter()


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    trigger_type: Optional[WorkflowTriggerType] = None,
    auth: TokenPayload = Depends(PermissionChecker(["workflow.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List visual event-driven workflows"""
    conditions = [Workflow.organization_id == auth.organization_id, Workflow.is_deleted == False]
    if trigger_type:
        conditions.append(Workflow.trigger_type == trigger_type)

    res = await db.execute(select(Workflow).where(and_(*conditions)).order_by(desc(Workflow.created_at)))
    return res.scalars().all()


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    req: WorkflowCreate,
    auth: TokenPayload = Depends(PermissionChecker(["workflow.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new event-driven workflow with trigger, conditions, and actions"""
    workflow = Workflow(
        organization_id=auth.organization_id,
        name=req.name,
        description=req.description,
        trigger_type=req.trigger_type,
        conditions=[c.model_dump() for c in req.conditions],
        actions=[a.model_dump() for a in req.actions],
        canvas_graph=req.canvas_graph or {},
        is_active=req.is_active
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


@router.get("/workflows/{workflow_id}/logs", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["workflow.read"])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch run execution logs for a workflow"""
    res = await db.execute(
        select(WorkflowExecution).where(
            and_(WorkflowExecution.workflow_id == workflow_id, WorkflowExecution.organization_id == auth.organization_id)
        ).order_by(desc(WorkflowExecution.started_at)).limit(50)
    )
    return res.scalars().all()


@router.post("/workflows/{workflow_id}/trigger-test")
async def trigger_test_workflow(
    workflow_id: str,
    sample_payload: dict,
    auth: TokenPayload = Depends(PermissionChecker(["workflow.execute"])),
    db: AsyncSession = Depends(get_db)
):
    """Test execution of workflow against a sample payload"""
    w_res = await db.execute(select(Workflow).where(and_(Workflow.id == workflow_id, Workflow.organization_id == auth.organization_id)))
    workflow = w_res.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    event = DomainEvent(
        event_type=workflow.trigger_type.value,
        organization_id=auth.organization_id,
        entity_id="test-entity-123",
        entity_type="lead",
        payload=sample_payload,
        user_id=auth.sub
    )
    results = await AutomationService.evaluate_and_execute_workflows(db, event)
    return {"message": "Workflow test execution completed", "executions_count": len(results)}
