from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.core.websocket_manager import ws_manager
from app.core.redis import redis_manager
from app.crm.models import Customer, Contact, CustomerTimelineEvent
from app.telephony.models import (
    AgentProfile, AgentStateLog, CallRecord, CallDisposition,
    AgentState, BreakType, CallDirection, CallStatus, TransferType
)
from app.telephony.schemas import (
    AgentProfileCreate, AgentStateChangeRequest,
    CallInitiateRequest, CallTransferRequest, CallDispositionRequest
)


def ensure_utc(dt: Optional[datetime]) -> datetime:
    """Ensure datetime has UTC timezone to avoid offset-naive subtraction issues in SQLite"""
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class TelephonyService:
    # ----------------------------------------------------
    # Agent Profile & Workforce States
    # ----------------------------------------------------
    @staticmethod
    async def get_or_create_agent_profile(db: AsyncSession, org_id: str, user_id: str) -> AgentProfile:
        """Fetch existing agent profile or initialize default"""
        res = await db.execute(
            select(AgentProfile).where(and_(AgentProfile.user_id == user_id, AgentProfile.organization_id == org_id))
        )
        agent = res.scalar_one_or_none()
        if not agent:
            agent = AgentProfile(
                organization_id=org_id,
                user_id=user_id,
                skills=["General Support", "Sales"],
                languages=["en"],
                current_state=AgentState.AVAILABLE,
                state_changed_at=datetime.now(timezone.utc)
            )
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
        return agent

    @classmethod
    async def set_agent_state(cls, db: AsyncSession, org_id: str, user_id: str, req: AgentStateChangeRequest) -> AgentProfile:
        """Update agent workforce state with state log history, Redis presence, and WebSocket telemetry"""
        agent = await cls.get_or_create_agent_profile(db, org_id, user_id)
        old_state = agent.current_state
        now = datetime.now(timezone.utc)

        # Log state duration
        changed_at = ensure_utc(agent.state_changed_at)
        duration = int((now - changed_at).total_seconds())
        state_log = AgentStateLog(
            organization_id=org_id,
            agent_id=agent.id,
            user_id=user_id,
            previous_state=old_state.value,
            new_state=req.state.value,
            break_type=req.break_type.value if req.break_type else None,
            duration_seconds=max(0, duration),
            started_at=changed_at,
            ended_at=now
        )
        db.add(state_log)

        agent.current_state = req.state
        agent.current_break_type = req.break_type
        agent.state_changed_at = now

        await db.commit()
        await db.refresh(agent)

        # Update Redis cache
        await redis_manager.set_agent_presence(agent.id, req.state.value, {
            "user_id": user_id,
            "break_type": req.break_type.value if req.break_type else None,
            "updated_at": now.isoformat()
        })

        # Broadcast via WebSocket to Supervisor Command Center
        await ws_manager.broadcast_to_supervisors(org_id, {
            "type": "agent_state_changed",
            "agent_id": agent.id,
            "user_id": user_id,
            "new_state": req.state.value,
            "break_type": req.break_type.value if req.break_type else None,
            "timestamp": now.isoformat()
        })

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.AGENT_STATUS_CHANGED,
            organization_id=org_id,
            entity_id=agent.id,
            entity_type="agent",
            payload={"old_state": old_state.value, "new_state": req.state.value},
            user_id=user_id
        ))

        return agent

    # ----------------------------------------------------
    # Softphone Call Lifecycle Engine
    # ----------------------------------------------------
    @classmethod
    async def initiate_call(cls, db: AsyncSession, org_id: str, req: CallInitiateRequest, user_id: str) -> CallRecord:
        """
        Initiate inbound or outbound call.
        Performs Caller ID lookup to associate with matching Customer / Contact.
        """
        agent = await cls.get_or_create_agent_profile(db, org_id, user_id)
        now = datetime.now(timezone.utc)

        # Automatic Caller ID Resolution
        customer_id = req.customer_id
        contact_id = req.contact_id
        lead_id = req.lead_id
        caller_name = req.caller_name

        if not customer_id:
            search_phone = req.to_number if req.direction == CallDirection.OUTBOUND else req.from_number
            cust_res = await db.execute(
                select(Customer).where(and_(Customer.phone_number == search_phone, Customer.organization_id == org_id))
            )
            matched_cust = cust_res.scalar_one_or_none()
            if matched_cust:
                customer_id = matched_cust.id
                caller_name = caller_name or matched_cust.name

        call = CallRecord(
            organization_id=org_id,
            direction=req.direction,
            status=CallStatus.RINGING,
            from_number=req.from_number,
            to_number=req.to_number,
            caller_name=caller_name,
            customer_id=customer_id,
            contact_id=contact_id,
            lead_id=lead_id,
            queue_id=req.queue_id,
            agent_id=agent.id,
            user_id=user_id,
            queued_at=now,
            ringing_at=now,
            skills_required=req.skills_required or [],
            language_required=req.language_required,
            priority=req.priority
        )
        db.add(call)
        await db.commit()
        await db.refresh(call)

        # Notify Agent & Supervisors via WebSocket
        call_payload = {
            "type": "call_ringing",
            "call_id": call.id,
            "direction": call.direction.value,
            "from_number": call.from_number,
            "to_number": call.to_number,
            "caller_name": call.caller_name,
            "customer_id": call.customer_id
        }
        await ws_manager.send_to_user(user_id, call_payload)
        await ws_manager.broadcast_to_supervisors(org_id, call_payload)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.CALL_INITIATED,
            organization_id=org_id,
            entity_id=call.id,
            entity_type="call",
            payload=call_payload,
            user_id=user_id
        ))

        return call

    @classmethod
    async def answer_call(cls, db: AsyncSession, org_id: str, call_id: str, user_id: str) -> CallRecord:
        """Agent answers ringing call; changes agent state to ON_CALL"""
        res = await db.execute(select(CallRecord).where(and_(CallRecord.id == call_id, CallRecord.organization_id == org_id)))
        call = res.scalar_one_or_none()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

        now = datetime.now(timezone.utc)
        call.status = CallStatus.IN_PROGRESS
        call.answered_at = now
        if call.queued_at:
            queued_at = ensure_utc(call.queued_at)
            call.queue_wait_duration_seconds = int((now - queued_at).total_seconds())

        agent = await cls.get_or_create_agent_profile(db, org_id, user_id)
        agent.current_state = AgentState.ON_CALL
        agent.state_changed_at = now

        await db.commit()
        await db.refresh(call)

        event_data = {"type": "call_connected", "call_id": call.id, "agent_id": agent.id}
        await ws_manager.send_to_user(user_id, event_data)
        await ws_manager.broadcast_to_supervisors(org_id, event_data)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.CALL_ANSWERED,
            organization_id=org_id,
            entity_id=call.id,
            entity_type="call",
            payload=event_data,
            user_id=user_id
        ))

        return call

    @classmethod
    async def hold_call(cls, db: AsyncSession, org_id: str, call_id: str, hold: bool, user_id: str) -> CallRecord:
        """Hold or resume active softphone call"""
        res = await db.execute(select(CallRecord).where(and_(CallRecord.id == call_id, CallRecord.organization_id == org_id)))
        call = res.scalar_one_or_none()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

        if hold:
            call.status = CallStatus.ON_HOLD
        else:
            call.status = CallStatus.IN_PROGRESS

        await db.commit()
        await db.refresh(call)

        await ws_manager.send_to_user(user_id, {"type": "call_hold_toggled", "call_id": call.id, "on_hold": hold})
        return call

    @classmethod
    async def end_call(cls, db: AsyncSession, org_id: str, call_id: str, user_id: str) -> CallRecord:
        """
        Hang up active call.
        Calculates talk duration, sets call status to COMPLETED, and sets agent state to AFTER_CALL_WORK.
        """
        res = await db.execute(select(CallRecord).where(and_(CallRecord.id == call_id, CallRecord.organization_id == org_id)))
        call = res.scalar_one_or_none()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

        now = datetime.now(timezone.utc)
        call.ended_at = now
        call.status = CallStatus.COMPLETED

        if call.answered_at:
            answered_at = ensure_utc(call.answered_at)
            call.talk_duration_seconds = max(0, int((now - answered_at).total_seconds()))
            call.total_handle_time_seconds = call.talk_duration_seconds + call.queue_wait_duration_seconds
        
        # Simulate recording URL
        call.recording_url = f"https://storage.callsphere.local/recordings/call_{call.id}.mp3"
        call.recording_duration_seconds = call.talk_duration_seconds

        # Set agent to AFTER_CALL_WORK
        agent = await cls.get_or_create_agent_profile(db, org_id, user_id)
        agent.current_state = AgentState.AFTER_CALL_WORK
        agent.state_changed_at = now
        agent.total_calls_handled_today += 1
        agent.total_talk_time_seconds += call.talk_duration_seconds

        await db.commit()
        await db.refresh(call)

        event_data = {
            "type": "call_ended",
            "call_id": call.id,
            "talk_duration": call.talk_duration_seconds,
            "recording_url": call.recording_url
        }
        await ws_manager.send_to_user(user_id, event_data)
        await ws_manager.broadcast_to_supervisors(org_id, event_data)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.CALL_COMPLETED,
            organization_id=org_id,
            entity_id=call.id,
            entity_type="call",
            payload=event_data,
            user_id=user_id
        ))

        return call

    @classmethod
    async def submit_disposition(cls, db: AsyncSession, org_id: str, call_id: str, req: CallDispositionRequest, user_id: str) -> CallDisposition:
        """
        Save call disposition and wrap-up notes.
        Appends call event with duration and recording to Customer 360 Timeline.
        Sets agent state back to AVAILABLE.
        """
        res = await db.execute(select(CallRecord).where(and_(CallRecord.id == call_id, CallRecord.organization_id == org_id)))
        call = res.scalar_one_or_none()
        if not call:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

        disposition = CallDisposition(
            organization_id=org_id,
            call_id=call_id,
            agent_user_id=user_id,
            disposition_code=req.disposition_code,
            category=req.category,
            summary_notes=req.summary_notes,
            follow_up_required=req.follow_up_required,
            follow_up_date=req.follow_up_date,
            tags=req.tags or []
        )
        db.add(disposition)

        # Append to Customer Timeline if customer attached
        if call.customer_id:
            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=call.customer_id,
                contact_id=call.contact_id,
                channel="CALL",
                event_type="CallCompleted",
                title=f"{call.direction.value} Call ({call.talk_duration_seconds}s) - {req.disposition_code}",
                description=req.summary_notes or f"Call completed by agent. Disposition: {req.disposition_code}",
                metadata_json={
                    "call_id": call.id,
                    "talk_duration_seconds": call.talk_duration_seconds,
                    "recording_url": call.recording_url,
                    "disposition": req.disposition_code
                },
                actor_user_id=user_id,
                actor_name="Agent"
            )
            db.add(timeline_event)

        # Return agent to AVAILABLE state
        agent = await cls.get_or_create_agent_profile(db, org_id, user_id)
        agent.current_state = AgentState.AVAILABLE
        agent.state_changed_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(disposition)

        await ws_manager.send_to_user(user_id, {"type": "disposition_saved", "call_id": call.id})
        return disposition
