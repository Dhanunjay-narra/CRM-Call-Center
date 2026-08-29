from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.modules.agents.models import Agent, AgentStatus
from app.modules.agents.schemas import AgentCreate, AgentLogin, AgentStatusUpdate, AgentResponse, TokenResponse

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Agent email already registered")
    
    agent = Agent(
        id=str(uuid.uuid4()),
        name=payload.name,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        skills=payload.skills or "GENERAL",
        status=AgentStatus.AVAILABLE
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.post("/login", response_model=TokenResponse)
async def login_agent(payload: AgentLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.email == payload.email))
    agent = result.scalars().first()
    if not agent or not verify_password(payload.password, agent.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    agent.status = AgentStatus.AVAILABLE
    await db.commit()
    token = create_access_token(subject=agent.id)
    return TokenResponse(access_token=token, agent=agent)

@router.get("", response_model=list[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent))
    return result.scalars().all()

@router.patch("/{agent_id}/status", response_model=AgentResponse)
async def update_agent_status(agent_id: str, payload: AgentStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = payload.status
    await db.commit()
    await db.refresh(agent)
    return agent
