from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.telephony.models import AgentProfile, CallRecord, CallDisposition, CallStatus
from app.telephony.schemas import (
    AgentProfileCreate, AgentProfileUpdate, AgentProfileResponse, AgentStateChangeRequest,
    CallInitiateRequest, CallTransferRequest, CallRecordResponse,
    CallDispositionRequest, CallDispositionResponse
)
from app.telephony.service import TelephonyService

router = APIRouter()


# ----------------------------------------------------
# Agent Profile & Workforce States Endpoints
# ----------------------------------------------------

@router.get("/agents/profile", response_model=AgentProfileResponse)
async def get_my_agent_profile(
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch profile and current workforce state of logged-in agent"""
    return await TelephonyService.get_or_create_agent_profile(db, auth.organization_id, auth.sub)


@router.post("/agents/state", response_model=AgentProfileResponse)
async def set_my_agent_state(
    req: AgentStateChangeRequest,
    auth: TokenPayload = Depends(PermissionChecker(["agent.manage_status"])),
    db: AsyncSession = Depends(get_db)
):
    """Change agent workforce state (Available, Break, Training, Offline)"""
    return await TelephonyService.set_agent_state(db, auth.organization_id, auth.sub, req)


@router.get("/agents/all", response_model=List[AgentProfileResponse])
async def list_all_agents(
    auth: TokenPayload = Depends(PermissionChecker(["agent.view"])),
    db: AsyncSession = Depends(get_db)
):
    """Supervisor view of all agents in organization"""
    res = await db.execute(
        select(AgentProfile).where(
            and_(AgentProfile.organization_id == auth.organization_id, AgentProfile.is_deleted == False)
        )
    )
    return res.scalars().all()


# ----------------------------------------------------
# Softphone Dialer & Call Lifecycle Endpoints
# ----------------------------------------------------

@router.post("/calls/initiate", response_model=CallRecordResponse, status_code=status.HTTP_201_CREATED)
async def initiate_call(
    req: CallInitiateRequest,
    auth: TokenPayload = Depends(PermissionChecker(["call.make"])),
    db: AsyncSession = Depends(get_db)
):
    """Initiate an outbound call or simulate incoming call"""
    return await TelephonyService.initiate_call(db, auth.organization_id, req, user_id=auth.sub)


@router.post("/calls/{call_id}/answer", response_model=CallRecordResponse)
async def answer_call(
    call_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["call.answer"])),
    db: AsyncSession = Depends(get_db)
):
    """Answer ringing softphone call"""
    return await TelephonyService.answer_call(db, auth.organization_id, call_id, user_id=auth.sub)


@router.post("/calls/{call_id}/hold", response_model=CallRecordResponse)
async def hold_call(
    call_id: str,
    hold: bool = Query(default=True),
    auth: TokenPayload = Depends(PermissionChecker(["call.answer"])),
    db: AsyncSession = Depends(get_db)
):
    """Hold or resume active softphone call"""
    return await TelephonyService.hold_call(db, auth.organization_id, call_id, hold=hold, user_id=auth.sub)


@router.post("/calls/{call_id}/end", response_model=CallRecordResponse)
async def end_call(
    call_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["call.answer"])),
    db: AsyncSession = Depends(get_db)
):
    """End active call and enter After Call Work (ACW) wrap-up"""
    return await TelephonyService.end_call(db, auth.organization_id, call_id, user_id=auth.sub)


@router.post("/calls/{call_id}/disposition", response_model=CallDispositionResponse, status_code=status.HTTP_201_CREATED)
async def submit_call_disposition(
    call_id: str,
    req: CallDispositionRequest,
    auth: TokenPayload = Depends(PermissionChecker(["call.disposition"])),
    db: AsyncSession = Depends(get_db)
):
    """Submit post-call outcome disposition and wrap-up notes to Customer 360 timeline"""
    return await TelephonyService.submit_disposition(db, auth.organization_id, call_id, req, user_id=auth.sub)


@router.get("/calls/history", response_model=List[CallRecordResponse])
async def list_call_history(
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    status: Optional[CallStatus] = None,
    auth: TokenPayload = Depends(PermissionChecker(["call.recording.listen"])),
    db: AsyncSession = Depends(get_db)
):
    """List call history with filters"""
    conditions = [CallRecord.organization_id == auth.organization_id, CallRecord.is_deleted == False]
    if customer_id:
        conditions.append(CallRecord.customer_id == customer_id)
    if agent_id:
        conditions.append(CallRecord.agent_id == agent_id)
    if status:
        conditions.append(CallRecord.status == status)

    res = await db.execute(select(CallRecord).where(and_(*conditions)).order_by(desc(CallRecord.queued_at)))
    return res.scalars().all()
