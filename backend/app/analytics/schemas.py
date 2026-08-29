from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# Call Center Operational KPIs
class CallCenterKPIsResponse(BaseModel):
    total_calls_today: int
    answered_calls: int
    missed_calls: int
    abandoned_calls: int
    answer_rate_percent: float
    abandonment_rate_percent: float
    service_level_percent: float       # Calls answered within target SLA threshold (e.g. 20s)
    aht_seconds: float                 # Average Handle Time
    asa_seconds: float                 # Average Speed of Answer
    fcr_percent: float                 # First Call Resolution
    occupancy_percent: float           # Agent Occupancy Rate
    active_calls_count: int
    agents_online: int
    agents_available: int
    agents_on_call: int
    agents_on_break: int


# Sales Analytics KPIs
class SalesAnalyticsResponse(BaseModel):
    total_leads: int
    lead_conversion_rate: float
    open_pipeline_value: float
    weighted_pipeline_value: float
    won_revenue_total: float
    win_rate_percent: float
    average_deal_size: float
    sales_velocity_days: float


# Executive 360 Analytics
class ExecutiveAnalyticsResponse(BaseModel):
    total_customers: int
    average_health_score: float
    csat_score: float
    nps_score: float
    open_tickets_count: int
    sla_compliance_percent: float
    total_revenue_generated: float
    active_campaigns_count: int


# Global Multi-Entity Search Response
class SearchResultItem(BaseModel):
    entity_type: str  # "customer", "lead", "contact", "call", "ticket", "opportunity", "article"
    id: str
    title: str
    subtitle: Optional[str] = None
    extra_metadata: Dict[str, Any] = {}
    url: str


class GlobalSearchResponse(BaseModel):
    query: str
    total_matches: int
    results: List[SearchResultItem]
