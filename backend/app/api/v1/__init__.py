from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.identity.router import router as identity_router
from app.crm.router import router as crm_router
from app.sales.router import router as sales_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(identity_router, tags=["Identity & Access Management"])
api_router.include_router(crm_router, tags=["CRM Core"])
api_router.include_router(sales_router, tags=["Sales & Campaigns"])
