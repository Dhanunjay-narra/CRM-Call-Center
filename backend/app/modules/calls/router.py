from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.modules.calls.models import CallSession, CallStatus, CallDirection
from app.modules.calls.schemas import CallInitiate, CallAction, CallResponse, WebRTCSignalingMessage
from app.modules.agents.models import Agent, AgentStatus

router = APIRouter(prefix="/calls", tags=["Calls & ACD Queue"])

@router.post("/initiate", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def initiate_call(payload: CallInitiate, db: AsyncSession = Depends(get_db)):
    call_id = f"CALL-{int(datetime.now(timezone.utc).timestamp())}"
    
    # ACD routing: search for available agent
    avail_agent = None
    agent_res = await db.execute(select(Agent).where(Agent.status == AgentStatus.AVAILABLE))
    avail_agent = agent_res.scalars().first()

    status_val = CallStatus.RINGING if avail_agent else CallStatus.QUEUED
    agent_id = avail_agent.id if avail_agent else None

    call = CallSession(
        id=str(uuid.uuid4()),
        call_id=call_id,
        customer_id=payload.customer_id,
        agent_id=agent_id,
        direction=payload.direction or CallDirection.INBOUND,
        status=status_val,
        queue_name=payload.queue_name or "General Support",
        priority=payload.priority or 1
    )
    if avail_agent:
        avail_agent.status = AgentStatus.BUSY
        avail_agent.active_call_id = call_id
    
    db.add(call)
    await db.commit()
    await db.refresh(call)

    await ws_manager.broadcast_event("CALL_UPDATE", {"call_id": call_id, "status": status_val.value, "agent_id": agent_id})
    return call

@router.post("/{call_id}/action", response_model=CallResponse)
async def handle_call_action(call_id: str, payload: CallAction, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CallSession).where(CallSession.call_id == call_id))
    call = result.scalars().first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    act = payload.action.upper()
    if act == "ANSWER":
        call.status = CallStatus.ACTIVE
        if payload.agent_id:
            call.agent_id = payload.agent_id
            agent_res = await db.execute(select(Agent).where(Agent.id == payload.agent_id))
            ag = agent_res.scalars().first()
            if ag:
                ag.status = AgentStatus.BUSY
                ag.active_call_id = call_id
    elif act == "HOLD":
        call.status = CallStatus.ON_HOLD
    elif act == "RESUME":
        call.status = CallStatus.ACTIVE
    elif act == "END":
        call.status = CallStatus.COMPLETED
        call.ended_at = datetime.now(timezone.utc)
        call.duration_seconds = 180
        if call.agent_id:
            agent_res = await db.execute(select(Agent).where(Agent.id == call.agent_id))
            ag = agent_res.scalars().first()
            if ag:
                ag.status = AgentStatus.AVAILABLE
                ag.active_call_id = None
                ag.total_calls_handled += 1
    
    await db.commit()
    await db.refresh(call)
    await ws_manager.broadcast_event("CALL_STATUS_CHANGE", {"call_id": call_id, "status": call.status.value})
    return call

@router.get("/queue", response_model=list[CallResponse])
async def get_active_queue(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CallSession).where(CallSession.status.in_([CallStatus.QUEUED, CallStatus.RINGING, CallStatus.ACTIVE, CallStatus.ON_HOLD])))
    return result.scalars().all()

@router.post("/signal")
async def webrtc_signal(payload: WebRTCSignalingMessage):
    # Relay WebRTC SDP offer/answer/ICE candidate
    await ws_manager.broadcast_event("WEBRTC_SIGNAL", payload.model_dump())
    return {"status": "signaling_dispatched", "call_id": payload.call_id}
