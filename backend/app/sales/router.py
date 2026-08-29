from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.sales.models import Pipeline, PipelineStage, Opportunity, Campaign, OpportunityStatus
from app.sales.schemas import (
    PipelineCreate, PipelineResponse,
    PipelineStageCreate, PipelineStageResponse,
    OpportunityCreate, OpportunityUpdate, OpportunityResponse,
    SalesForecastResponse,
    CampaignCreate, CampaignUpdate, CampaignResponse
)
from app.sales.service import SalesService

router = APIRouter()


# ----------------------------------------------------
# Pipelines & Stages Endpoints
# ----------------------------------------------------

@router.get("/pipelines", response_model=List[PipelineResponse])
async def list_pipelines(
    auth: TokenPayload = Depends(PermissionChecker(["opportunity.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List all sales pipelines and their ordered stages"""
    res = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.stages)).where(
            and_(Pipeline.organization_id == auth.organization_id, Pipeline.is_deleted == False)
        )
    )
    pipelines = res.scalars().all()
    
    # If no pipeline exists, initialize default
    if not pipelines:
        default_pipe = await SalesService.create_default_pipeline(db, auth.organization_id)
        return [default_pipe]
    return pipelines


@router.post("/pipelines", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    req: PipelineCreate,
    auth: TokenPayload = Depends(PermissionChecker(["pipeline.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new custom sales pipeline"""
    pipeline = Pipeline(
        organization_id=auth.organization_id,
        name=req.name,
        description=req.description,
        is_default=req.is_default
    )
    db.add(pipeline)
    await db.flush()

    if req.stages:
        for s in req.stages:
            stage = PipelineStage(
                organization_id=auth.organization_id,
                pipeline_id=pipeline.id,
                name=s.name,
                order=s.order,
                default_probability=s.default_probability,
                is_won_stage=s.is_won_stage,
                is_lost_stage=s.is_lost_stage
            )
            db.add(stage)

    await db.commit()
    reloaded = await db.execute(
        select(Pipeline).options(selectinload(Pipeline.stages)).where(Pipeline.id == pipeline.id)
    )
    return reloaded.scalar_one()


# ----------------------------------------------------
# Opportunities & Deals Endpoints
# ----------------------------------------------------

@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    pipeline_id: Optional[str] = None,
    stage_id: Optional[str] = None,
    status: Optional[OpportunityStatus] = None,
    customer_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["opportunity.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List sales deals with stage and pipeline filters"""
    conditions = [Opportunity.organization_id == auth.organization_id, Opportunity.is_deleted == False]
    if pipeline_id:
        conditions.append(Opportunity.pipeline_id == pipeline_id)
    if stage_id:
        conditions.append(Opportunity.stage_id == stage_id)
    if status:
        conditions.append(Opportunity.status == status)
    if customer_id:
        conditions.append(Opportunity.customer_id == customer_id)

    res = await db.execute(select(Opportunity).where(and_(*conditions)).order_by(desc(Opportunity.amount)))
    return res.scalars().all()


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    req: OpportunityCreate,
    auth: TokenPayload = Depends(PermissionChecker(["opportunity.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new sales opportunity"""
    return await SalesService.create_opportunity(db, auth.organization_id, req, user_id=auth.sub)


@router.patch("/opportunities/{opp_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opp_id: str,
    req: OpportunityUpdate,
    auth: TokenPayload = Depends(PermissionChecker(["opportunity.update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update opportunity status or stage"""
    return await SalesService.update_opportunity(db, auth.organization_id, opp_id, req, user_id=auth.sub)


@router.get("/sales/forecast", response_model=SalesForecastResponse)
async def get_sales_forecast(
    auth: TokenPayload = Depends(PermissionChecker(["analytics.view_sales"])),
    db: AsyncSession = Depends(get_db)
):
    """Get weighted sales forecast, pipeline totals, and win rates"""
    return await SalesService.calculate_sales_forecast(db, auth.organization_id)


# ----------------------------------------------------
# Campaigns Endpoints
# ----------------------------------------------------

@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    auth: TokenPayload = Depends(PermissionChecker(["campaign.read"])),
    db: AsyncSession = Depends(get_db)
):
    """List marketing and outbound sales campaigns"""
    res = await db.execute(
        select(Campaign).where(and_(Campaign.organization_id == auth.organization_id, Campaign.is_deleted == False)).order_by(desc(Campaign.created_at))
    )
    return res.scalars().all()


@router.post("/campaigns", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    req: CampaignCreate,
    auth: TokenPayload = Depends(PermissionChecker(["campaign.create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create an outbound marketing/sales campaign"""
    campaign = Campaign(
        organization_id=auth.organization_id,
        name=req.name,
        campaign_type=req.campaign_type,
        channel=req.channel,
        description=req.description,
        budget=req.budget,
        subject=req.subject,
        message_body=req.message_body,
        target_segment=req.target_segment,
        filter_criteria=req.filter_criteria or {},
        scheduled_start=req.scheduled_start,
        scheduled_end=req.scheduled_end,
        created_by_user_id=auth.sub
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/campaigns/{campaign_id}/execute", response_model=CampaignResponse)
async def execute_campaign(
    campaign_id: str,
    auth: TokenPayload = Depends(PermissionChecker(["campaign.execute"])),
    db: AsyncSession = Depends(get_db)
):
    """Execute a campaign blast across target audience"""
    return await SalesService.execute_campaign(db, auth.organization_id, campaign_id, user_id=auth.sub)
