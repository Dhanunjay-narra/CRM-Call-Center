from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.support.models import SupportTicket, TicketComment, SLAPolicy, KnowledgeCategory, KnowledgeArticle, TicketStatus, TicketPriority
from app.support.schemas import (
    SupportTicketCreate, SupportTicketUpdate, SupportTicketResponse, TicketResolveRequest,
    TicketCommentCreate, TicketCommentResponse,
    SLAPolicyCreate, SLAPolicyResponse,
    KnowledgeCategoryCreate, KnowledgeCategoryResponse,
    KnowledgeArticleCreate, KnowledgeArticleResponse
)
from app.support.service import SupportService, slugify

router = APIRouter()


# ----------------------------------------------------
# Support Tickets Endpoints
# ----------------------------------------------------

@router.get("/tickets", response_model=List[SupportTicketResponse])
async def list_tickets(
    status: Optional[TicketStatus] = None,
    priority: Optional[TicketPriority] = None,
    customer_id: Optional[str] = None,
    assigned_user_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List support tickets with status and priority filters"""
    conditions = [SupportTicket.organization_id == auth.organization_id, SupportTicket.is_deleted == False]
    if status:
        conditions.append(SupportTicket.status == status)
    if priority:
        conditions.append(SupportTicket.priority == priority)
    if customer_id:
        conditions.append(SupportTicket.customer_id == customer_id)
    if assigned_user_id:
        conditions.append(SupportTicket.assigned_user_id == assigned_user_id)

    res = await db.execute(select(SupportTicket).where(and_(*conditions)).order_by(desc(SupportTicket.created_at)))
    return res.scalars().all()


@router.post("/tickets", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    req: SupportTicketCreate,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new support ticket and compute SLA target deadlines"""
    return await SupportService.create_ticket(db, auth.organization_id, req, user_id=auth.sub)


@router.get("/tickets/{ticket_id}", response_model=SupportTicketResponse)
async def get_ticket(
    ticket_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get support ticket details"""
    res = await db.execute(
        select(SupportTicket).where(and_(SupportTicket.id == ticket_id, SupportTicket.organization_id == auth.organization_id))
    )
    ticket = res.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.get("/tickets/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def list_ticket_comments(
    ticket_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List comments and internal notes on ticket"""
    res = await db.execute(
        select(TicketComment).where(
            and_(TicketComment.ticket_id == ticket_id, TicketComment.organization_id == auth.organization_id)
        ).order_by(TicketComment.created_at.asc())
    )
    return res.scalars().all()


@router.post("/tickets/{ticket_id}/comments", response_model=TicketCommentResponse, status_code=status.HTTP_201_CREATED)
async def add_ticket_comment(
    ticket_id: str,
    req: TicketCommentCreate,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.update"])),
    db: AsyncSession = Depends(get_db)
):
    """Add an internal note or public customer reply to ticket"""
    return await SupportService.add_comment(db, auth.organization_id, ticket_id, req, user_id=auth.sub, author_name=auth.email or "Agent")


@router.post("/tickets/{ticket_id}/resolve", response_model=SupportTicketResponse)
async def resolve_ticket(
    ticket_id: str,
    req: TicketResolveRequest,
    auth: TokenPayload = Depends(PermissionChecker(["ticket.resolve"])),
    db: AsyncSession = Depends(get_db)
):
    """Mark support ticket as RESOLVED and evaluate SLA outcome"""
    return await SupportService.resolve_ticket(db, auth.organization_id, ticket_id, req, user_id=auth.sub)


# ----------------------------------------------------
# SLA Policies & Monitoring Endpoints
# ----------------------------------------------------

@router.get("/sla/policies", response_model=List[SLAPolicyResponse])
async def list_sla_policies(
    auth: TokenPayload = Depends(PermissionChecker(["sla.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """List SLA policies for tenant organization"""
    res = await db.execute(
        select(SLAPolicy).where(and_(SLAPolicy.organization_id == auth.organization_id, SLAPolicy.is_deleted == False))
    )
    return res.scalars().all()


@router.post("/sla/check")
async def trigger_sla_monitoring_check(
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Trigger background SLA breach and 80% warning monitor"""
    return await SupportService.monitor_sla_breaches(db, auth.organization_id)


# ----------------------------------------------------
# Knowledge Base Endpoints
# ----------------------------------------------------

@router.get("/knowledge/categories", response_model=List[KnowledgeCategoryResponse])
async def list_knowledge_categories(
    auth: TokenPayload = Depends(PermissionChecker(["knowledge.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List knowledge base categories"""
    res = await db.execute(
        select(KnowledgeCategory).where(
            and_(KnowledgeCategory.organization_id == auth.organization_id, KnowledgeCategory.is_deleted == False)
        ).order_by(KnowledgeCategory.order.asc())
    )
    return res.scalars().all()


@router.post("/knowledge/categories", response_model=KnowledgeCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_category(
    req: KnowledgeCategoryCreate,
    auth: TokenPayload = Depends(PermissionChecker(["knowledge.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge base category"""
    cat = KnowledgeCategory(
        organization_id=auth.organization_id,
        name=req.name,
        slug=slugify(req.name),
        description=req.description,
        icon=req.icon,
        order=req.order
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.get("/knowledge/articles", response_model=List[KnowledgeArticleResponse])
async def search_knowledge_articles(
    query: Optional[str] = None,
    category_id: Optional[str] = None,
    is_call_script: Optional[bool] = None,
    auth: TokenPayload = Depends(PermissionChecker(["knowledge.read"])),
    db: AsyncSession = Depends(get_db)
):
    """Search knowledge base articles, call scripts, and FAQs"""
    if query:
        return await SupportService.search_articles(db, auth.organization_id, query)

    conditions = [KnowledgeArticle.organization_id == auth.organization_id, KnowledgeArticle.is_deleted == False]
    if category_id:
        conditions.append(KnowledgeArticle.category_id == category_id)
    if is_call_script is not None:
        conditions.append(KnowledgeArticle.is_call_script == is_call_script)

    res = await db.execute(select(KnowledgeArticle).where(and_(*conditions)).order_by(desc(KnowledgeArticle.view_count)))
    return res.scalars().all()


@router.post("/knowledge/articles", response_model=KnowledgeArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_article(
    req: KnowledgeArticleCreate,
    auth: TokenPayload = Depends(PermissionChecker(["knowledge.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge article or agent call script"""
    article = KnowledgeArticle(
        organization_id=auth.organization_id,
        category_id=req.category_id,
        title=req.title,
        slug=slugify(req.title),
        content_markdown=req.content_markdown,
        is_public=req.is_public,
        is_call_script=req.is_call_script,
        tags=req.tags or [],
        created_by_user_id=auth.sub
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article
