from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.sales.models import OpportunityStatus, CampaignType, CampaignChannel, CampaignStatus


# Pipeline & Stage Schemas
class PipelineStageCreate(BaseModel):
    name: str
    order: int
    default_probability: int = 20
    is_won_stage: bool = False
    is_lost_stage: bool = False


class PipelineStageResponse(BaseModel):
    id: str
    pipeline_id: str
    name: str
    order: int
    default_probability: int
    is_won_stage: bool
    is_lost_stage: bool

    model_config = ConfigDict(from_attributes=True)


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    stages: Optional[List[PipelineStageCreate]] = None


class PipelineResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    stages: List[PipelineStageResponse] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Opportunity Schemas
class OpportunityCreate(BaseModel):
    pipeline_id: str
    stage_id: str
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    title: str
    amount: float = 0.0
    currency: str = "USD"
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    owner_user_id: Optional[str] = None
    products: Optional[List[Dict[str, Any]]] = None
    competitors: Optional[List[str]] = None
    next_step: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class OpportunityUpdate(BaseModel):
    pipeline_id: Optional[str] = None
    stage_id: Optional[str] = None
    title: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    probability: Optional[int] = None
    status: Optional[OpportunityStatus] = None
    expected_close_date: Optional[datetime] = None
    win_loss_reason: Optional[str] = None
    next_step: Optional[str] = None
    products: Optional[List[Dict[str, Any]]] = None
    competitors: Optional[List[str]] = None
    owner_user_id: Optional[str] = None


class OpportunityResponse(BaseModel):
    id: str
    organization_id: str
    pipeline_id: str
    stage_id: str
    customer_id: Optional[str] = None
    contact_id: Optional[str] = None
    lead_id: Optional[str] = None
    title: str
    amount: float
    currency: str
    probability: int
    status: OpportunityStatus
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    owner_user_id: str
    products: List[Dict[str, Any]]
    competitors: List[str]
    win_loss_reason: Optional[str] = None
    next_step: Optional[str] = None
    custom_fields: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Sales Forecast Schemas
class SalesForecastResponse(BaseModel):
    total_pipeline_value: float
    weighted_forecast_value: float
    open_deals_count: int
    won_deals_count: int
    won_revenue: float
    lost_deals_count: int
    win_rate_percent: float
    stage_breakdown: List[Dict[str, Any]]


# Campaign Schemas
class CampaignCreate(BaseModel):
    name: str
    campaign_type: CampaignType = CampaignType.SALES
    channel: CampaignChannel = CampaignChannel.EMAIL
    description: Optional[str] = None
    budget: float = 0.0
    subject: Optional[str] = None
    message_body: Optional[str] = None
    target_segment: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    campaign_type: Optional[CampaignType] = None
    channel: Optional[CampaignChannel] = None
    status: Optional[CampaignStatus] = None
    description: Optional[str] = None
    budget: float = 0.0
    subject: Optional[str] = None
    message_body: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class CampaignResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    campaign_type: CampaignType
    channel: CampaignChannel
    status: CampaignStatus
    description: Optional[str] = None
    budget: float
    actual_cost: float
    subject: Optional[str] = None
    message_body: Optional[str] = None
    target_segment: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    total_audience: int
    total_sent: int
    total_delivered: int
    total_opened: int
    total_clicked: int
    total_converted: int
    revenue_generated: float
    created_by_user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
