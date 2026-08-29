from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.identity.router import router as identity_router
from app.crm.router import router as crm_router
from app.sales.router import router as sales_router
from app.telephony.router import router as telephony_router
from app.routing.router import router as routing_router
from app.communications.router import router as communications_router
from app.support.router import router as support_router
from app.automation.router import router as automation_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(identity_router, tags=["Identity & Access Management"])
api_router.include_router(crm_router, tags=["CRM Core"])
api_router.include_router(sales_router, tags=["Sales & Campaigns"])
api_router.include_router(telephony_router, tags=["Call Center & Telephony"])
api_router.include_router(routing_router, tags=["Routing & IVR"])
api_router.include_router(communications_router, tags=["Omnichannel Communications"])
api_router.include_router(support_router, tags=["Customer Support & SLA"])
api_router.include_router(automation_router, tags=["Workflow Automation"])
