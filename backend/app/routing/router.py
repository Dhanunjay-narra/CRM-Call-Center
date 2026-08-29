from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.routing.models import CallQueue, QueueMember, IVRFlow, IVRNode
from app.routing.schemas import (
    CallQueueCreate, CallQueueResponse,
    QueueMemberAdd, QueueMemberResponse,
    AgentMatchRequest, AgentMatchResponse,
    IVRFlowCreate, IVRFlowResponse,
    IVRSimulateRequest, IVRSimulateResponse
)
from app.routing.service import RoutingService

router = APIRouter()


# ----------------------------------------------------
# Queue Management Endpoints
# ----------------------------------------------------

@router.get("/queues", response_model=List[CallQueueResponse])
async def list_queues(
    auth: TokenPayload = Depends(PermissionChecker(["queue.view"])),
    db: AsyncSession = Depends(get_db)
):
    """List all call queues and SLA configs"""
    res = await db.execute(
        select(CallQueue).where(and_(CallQueue.organization_id == auth.organization_id, CallQueue.is_deleted == False))
    )
    return res.scalars().all()


@router.post("/queues", response_model=CallQueueResponse, status_code=status.HTTP_201_CREATED)
async def create_queue(
    req: CallQueueCreate,
    auth: TokenPayload = Depends(PermissionChecker(["queue.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new call center queue"""
    queue = CallQueue(
        organization_id=auth.organization_id,
        name=req.name,
        description=req.description,
        strategy=req.strategy,
        sla_threshold_seconds=req.sla_threshold_seconds,
        max_queue_size=req.max_queue_size,
        timeout_seconds=req.timeout_seconds,
        required_skills=req.required_skills,
        default_language=req.default_language,
        overflow_queue_id=req.overflow_queue_id,
        enable_callback=req.enable_callback
    )
    db.add(queue)
    await db.commit()
    await db.refresh(queue)
    return queue


# ----------------------------------------------------
# Smart Routing Engine Endpoint
# ----------------------------------------------------

@router.post("/routing/match", response_model=AgentMatchResponse)
async def match_agent(
    req: AgentMatchRequest,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """
    Intelligent Dynamic Agent Routing:
    Matches incoming caller with optimal agent based on Skills, Language, Longest Idle, and Queue SLA.
    """
    return await RoutingService.match_best_agent(db, auth.organization_id, req)


# ----------------------------------------------------
# Visual IVR Flow Builder & Simulator Endpoints
# ----------------------------------------------------

@router.get("/ivr/flows", response_model=List[IVRFlowResponse])
async def list_ivr_flows(
    auth: TokenPayload = Depends(PermissionChecker(["ivr.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """List all visual IVR flows in organization"""
    res = await db.execute(
        select(IVRFlow).where(and_(IVRFlow.organization_id == auth.organization_id, IVRFlow.is_deleted == False))
    )
    flows = res.scalars().all()
    if not flows:
        default_flow = await RoutingService.create_default_ivr_flow(db, auth.organization_id)
        return [default_flow]
    return flows


@router.post("/ivr/simulate", response_model=IVRSimulateResponse)
async def simulate_ivr_navigation(
    req: IVRSimulateRequest,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Interactive visual IVR simulator tool for testing DTMF call trees"""
    return await RoutingService.simulate_ivr_step(db, auth.organization_id, req)
