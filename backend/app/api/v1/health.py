from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint for container orchestrators and load balancers"""
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
        "services": {
            "telephony": settings.TELEPHONY_PROVIDER,
            "sms": settings.SMS_PROVIDER,
            "whatsapp": settings.WHATSAPP_PROVIDER,
            "email": settings.EMAIL_PROVIDER
        }
    }
