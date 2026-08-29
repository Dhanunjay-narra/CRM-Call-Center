from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from datetime import datetime, timezone
from app.core.database import get_db
from app.modules.tickets.models import SupportTicket, TicketStatus, TicketPriority
from app.modules.tickets.schemas import TicketCreate, TicketUpdate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, db: AsyncSession = Depends(get_db)):
    t_num = f"TICK-{int(datetime.now(timezone.utc).timestamp())}"
    ticket = SupportTicket(
        id=str(uuid.uuid4()),
        ticket_number=t_num,
        customer_id=payload.customer_id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority or TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        channel=payload.channel or "VOICE_CALL"
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket

@router.get("", response_model=list[TicketResponse])
async def list_tickets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SupportTicket))
    return result.scalars().all()

@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, payload: TicketUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalars().first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if payload.status:
        ticket.status = payload.status
    if payload.priority:
        ticket.priority = payload.priority
    if payload.assigned_agent_id:
        ticket.assigned_agent_id = payload.assigned_agent_id
    ticket.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(ticket)
    return ticket
