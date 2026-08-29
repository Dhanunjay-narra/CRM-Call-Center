from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.analytics.schemas import (
    CallCenterKPIsResponse, SalesAnalyticsResponse, ExecutiveAnalyticsResponse,
    GlobalSearchResponse
)
from app.analytics.service import AnalyticsService

router = APIRouter()


@router.get("/analytics/operational", response_model=CallCenterKPIsResponse)
async def get_operational_kpis(
    auth: TokenPayload = Depends(PermissionChecker(["analytics.view_calls"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Real-time Contact Center Operational KPIs:
    Calculates AHT, ASA, Service Level %, FCR, Answer/Abandonment rate, and Live Agent Presence.
    """
    return await AnalyticsService.get_operational_kpis(db, auth.organization_id)


@router.get("/analytics/sales", response_model=SalesAnalyticsResponse)
async def get_sales_analytics(
    auth: TokenPayload = Depends(PermissionChecker(["analytics.view_sales"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Sales Pipeline Analytics:
    Calculates Lead conversion rate %, Weighted Pipeline Value, Won Revenue, Win Rate, and Average Deal Size.
    """
    return await AnalyticsService.get_sales_analytics(db, auth.organization_id)


@router.get("/analytics/executive", response_model=ExecutiveAnalyticsResponse)
async def get_executive_summary(
    auth: TokenPayload = Depends(PermissionChecker(["analytics.view_dashboard"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Executive 360 Dashboard:
    Synthesizes Customer Health, CSAT, NPS, Revenue, and SLA Compliance.
    """
    return await AnalyticsService.get_executive_summary(db, auth.organization_id)


@router.get("/search", response_model=GlobalSearchResponse)
async def global_search(
    q: str = Query(..., min_length=1),
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """
    Unified Global Multi-Entity Search:
    Searches across Customers, Leads, Contacts, Opportunities, Tickets, and Knowledge Base.
    """
    return await AnalyticsService.global_search(db, auth.organization_id, q)
