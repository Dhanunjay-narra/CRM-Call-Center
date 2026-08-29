from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.telephony.models import AgentProfile, AgentState, CallRecord, CallStatus
from app.routing.models import (
    CallQueue, QueueMember, IVRFlow, IVRNode,
    RoutingStrategy, IVRNodeType
)
from app.routing.schemas import (
    CallQueueCreate, AgentMatchRequest, AgentMatchResponse,
    IVRFlowCreate, IVRSimulateRequest, IVRSimulateResponse
)


def ensure_utc(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class RoutingService:
    # ----------------------------------------------------
    # Smart Multi-Strategy Routing Engine
    # ----------------------------------------------------
    @classmethod
    async def match_best_agent(cls, db: AsyncSession, org_id: str, req: AgentMatchRequest) -> AgentMatchResponse:
        """
        Intelligent Dynamic Agent Routing Algorithm.
        Evaluates:
        1. Agent workforce state (must be AVAILABLE)
        2. Required Skills match
        3. Language match
        4. Strategy: Longest Idle / Least Busy / Skill Proficiency / Priority
        """
        # Fetch queue strategy if queue_id provided
        strategy = RoutingStrategy.LONGEST_IDLE
        required_skills = req.skills_required.copy()
        required_lang = req.language_required

        if req.queue_id:
            q_res = await db.execute(
                select(CallQueue).where(and_(CallQueue.id == req.queue_id, CallQueue.organization_id == org_id))
            )
            queue = q_res.scalar_one_or_none()
            if queue:
                strategy = queue.strategy
                required_skills.extend(queue.required_skills)
                if queue.default_language:
                    required_lang = queue.default_language

        # Fetch available agents in this organization
        agents_res = await db.execute(
            select(AgentProfile).where(
                and_(
                    AgentProfile.organization_id == org_id,
                    AgentProfile.current_state == AgentState.AVAILABLE,
                    AgentProfile.is_deleted == False
                )
            )
        )
        available_agents = agents_res.scalars().all()

        if not available_agents:
            return AgentMatchResponse(
                matched=False,
                strategy_used=strategy,
                reason="No agents currently in AVAILABLE workforce state. Placed in queue."
            )

        # Filter by language if required
        candidate_agents = []
        for agent in available_agents:
            if required_lang and required_lang not in (agent.languages or ["en"]):
                continue
            # Filter by skills if required
            if required_skills:
                has_all_skills = all(skill.lower() in [s.lower() for s in (agent.skills or [])] for skill in required_skills)
                if not has_all_skills:
                    continue
            candidate_agents.append(agent)

        # If strict matching yields no one, fall back to any available agent
        if not candidate_agents:
            candidate_agents = available_agents

        now = datetime.now(timezone.utc)

        # Rank candidates based on strategy
        if strategy == RoutingStrategy.LONGEST_IDLE:
            # Sort by who has been AVAILABLE the longest (earliest state_changed_at)
            candidate_agents.sort(key=lambda a: ensure_utc(a.state_changed_at))
        elif strategy == RoutingStrategy.LEAST_BUSY:
            # Sort by who handled fewest calls today
            candidate_agents.sort(key=lambda a: a.total_calls_handled_today)
        elif strategy == RoutingStrategy.SKILL_BASED:
            # Sort by proficiency level descending
            candidate_agents.sort(key=lambda a: a.proficiency_level, reverse=True)
        else:
            # Default longest idle
            candidate_agents.sort(key=lambda a: ensure_utc(a.state_changed_at))

        best_agent = candidate_agents[0]

        idle_seconds = int((now - ensure_utc(best_agent.state_changed_at)).total_seconds())

        return AgentMatchResponse(
            matched=True,
            agent_id=best_agent.id,
            user_id=best_agent.user_id,
            strategy_used=strategy,
            score=float(best_agent.proficiency_level * 20),
            reason=f"Matched agent with skills {best_agent.skills}, language '{required_lang}', idle for {idle_seconds}s."
        )

    # ----------------------------------------------------
    # Visual IVR Flow Builder & Simulation Engine
    # ----------------------------------------------------
    @classmethod
    async def create_default_ivr_flow(cls, db: AsyncSession, org_id: str) -> IVRFlow:
        """Create standard multi-lingual visual IVR flow for tenant"""
        flow = IVRFlow(
            organization_id=org_id,
            name="Standard Multi-Lingual IVR Flow",
            description="Welcome menu with Language Selection, Sales, Support, and Billing queues",
            entry_node_id="welcome_menu",
            flow_data={
                "nodes": [
                    {"id": "welcome_menu", "type": "PLAY_MESSAGE", "label": "Welcome to CallSphere"},
                    {"id": "lang_select", "type": "GATHER_DTMF", "label": "Language Selection (1: EN, 2: TE, 3: HI)"},
                    {"id": "main_menu", "type": "GATHER_DTMF", "label": "Main Menu (1: Sales, 2: Support, 3: Billing)"}
                ]
            }
        )
        db.add(flow)
        await db.flush()

        # Nodes
        welcome = IVRNode(
            organization_id=org_id,
            flow_id=flow.id,
            node_key="welcome_menu",
            node_type=IVRNodeType.PLAY_MESSAGE,
            prompt_text="Thank you for calling CallSphere. Please hold while we connect you to our menu.",
            dtmf_options={"default": "lang_select"}
        )
        lang_node = IVRNode(
            organization_id=org_id,
            flow_id=flow.id,
            node_key="lang_select",
            node_type=IVRNodeType.GATHER_DTMF,
            prompt_text="Press 1 for English, 2 for Telugu, 3 for Hindi.",
            dtmf_options={"1": "main_menu", "2": "main_menu", "3": "main_menu"}
        )
        main_node = IVRNode(
            organization_id=org_id,
            flow_id=flow.id,
            node_key="main_menu",
            node_type=IVRNodeType.GATHER_DTMF,
            prompt_text="Press 1 for Sales, 2 for Support, 3 for Billing, or 0 to speak with an operator.",
            dtmf_options={"1": "sales_queue", "2": "support_queue", "3": "billing_queue", "0": "operator_queue"}
        )
        db.add_all([welcome, lang_node, main_node])
        await db.commit()
        await db.refresh(flow)
        return flow

    @classmethod
    async def simulate_ivr_step(cls, db: AsyncSession, org_id: str, req: IVRSimulateRequest) -> IVRSimulateResponse:
        """Interactive visual IVR simulator: navigates the DTMF tree step-by-step"""
        nodes_res = await db.execute(
            select(IVRNode).where(and_(IVRNode.flow_id == req.flow_id, IVRNode.organization_id == org_id))
        )
        nodes = {n.node_key: n for n in nodes_res.scalars().all()}

        if not nodes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IVR Flow has no nodes configured")

        # Determine current node
        curr_key = req.current_node_key
        if not curr_key or curr_key not in nodes:
            curr_key = "welcome_menu" if "welcome_menu" in nodes else list(nodes.keys())[0]

        curr_node = nodes[curr_key]

        # If user pressed digits, navigate to target node
        if req.digits_pressed:
            target_key = curr_node.dtmf_options.get(str(req.digits_pressed))
            if target_key and target_key in nodes:
                curr_node = nodes[target_key]
                curr_key = target_key
            elif target_key and "queue" in target_key:
                # Terminal destination reached (Queue)
                return IVRSimulateResponse(
                    flow_id=req.flow_id,
                    current_node_key=target_key,
                    node_type=IVRNodeType.TRANSFER_QUEUE,
                    prompt_text=f"Connecting you to {target_key}...",
                    available_dtmf={},
                    is_terminal=True,
                    routed_queue_id=target_key
                )

        return IVRSimulateResponse(
            flow_id=req.flow_id,
            current_node_key=curr_node.node_key,
            node_type=curr_node.node_type,
            prompt_text=curr_node.prompt_text,
            available_dtmf=curr_node.dtmf_options or {},
            is_terminal=(curr_node.node_type in [IVRNodeType.TRANSFER_QUEUE, IVRNodeType.DISCONNECT])
        )
