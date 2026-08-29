import random
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


# 11 Standard System Roles
class SystemRole:
    SUPER_ADMIN = "SUPER_ADMIN"
    ORGANIZATION_ADMIN = "ORGANIZATION_ADMIN"
    CALL_CENTER_MANAGER = "CALL_CENTER_MANAGER"
    SALES_MANAGER = "SALES_MANAGER"
    SUPPORT_MANAGER = "SUPPORT_MANAGER"
    SUPERVISOR = "SUPERVISOR"
    SENIOR_AGENT = "SENIOR_AGENT"
    AGENT = "AGENT"
    QA_ANALYST = "QA_ANALYST"
    ANALYST = "ANALYST"
    READ_ONLY_USER = "READ_ONLY_USER"


# Granular Permission Constants
ALL_PERMISSIONS = [
    # Leads
    "lead.create", "lead.read", "lead.update", "lead.delete", "lead.assign", "lead.export",
    # Contacts
    "contact.create", "contact.read", "contact.update", "contact.delete", "contact.merge",
    # Customers
    "customer.create", "customer.read", "customer.update", "customer.delete", "customer.view_360",
    # Sales & Opportunities
    "opportunity.create", "opportunity.read", "opportunity.update", "opportunity.delete", "pipeline.manage",
    # Calls & Telephony
    "call.make", "call.answer", "call.transfer", "call.recording.listen", "call.recording.download",
    "call.barge", "call.whisper", "call.disposition",
    # Queues & Routing
    "queue.view", "queue.manage", "ivr.manage", "routing.manage",
    # Agents & Workforce
    "agent.view", "agent.manage_status", "agent.manage_skills", "agent.manage_schedule",
    # Omnichannel Messages
    "message.send", "message.read", "template.manage",
    # Tickets & Support
    "ticket.create", "ticket.read", "ticket.update", "ticket.assign", "ticket.resolve", "ticket.delete", "sla.manage",
    # Campaigns
    "campaign.create", "campaign.read", "campaign.update", "campaign.execute", "campaign.delete",
    # Automation & Workflows
    "workflow.create", "workflow.read", "workflow.update", "workflow.execute", "workflow.delete",
    # Knowledge Base
    "knowledge.read", "knowledge.create", "knowledge.update", "knowledge.delete",
    # Quality Assurance
    "qa.evaluate", "qa.view_scorecard", "qa.manage_scorecard", "qa.coach",
    # Feedback
    "feedback.view", "feedback.manage",
    # Analytics & Reports
    "analytics.view_dashboard", "analytics.view_calls", "analytics.view_sales", "analytics.view_agent", "analytics.export",
    # Organization & Admin
    "org.manage", "user.manage", "role.manage", "audit.view", "settings.manage"
]


# Default Role-to-Permissions Mapping
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    SystemRole.SUPER_ADMIN: ALL_PERMISSIONS,
    
    SystemRole.ORGANIZATION_ADMIN: [p for p in ALL_PERMISSIONS if not p.startswith("org.delete")],
    
    SystemRole.CALL_CENTER_MANAGER: [
        "call.make", "call.answer", "call.transfer", "call.recording.listen", "call.recording.download",
        "call.barge", "call.whisper", "call.disposition", "queue.view", "queue.manage", "ivr.manage", "routing.manage",
        "agent.view", "agent.manage_status", "agent.manage_skills", "agent.manage_schedule",
        "customer.read", "customer.view_360", "contact.read", "ticket.read",
        "analytics.view_dashboard", "analytics.view_calls", "analytics.view_agent", "analytics.export",
        "qa.view_scorecard", "qa.evaluate", "feedback.view"
    ],
    
    SystemRole.SALES_MANAGER: [
        "lead.create", "lead.read", "lead.update", "lead.delete", "lead.assign", "lead.export",
        "contact.create", "contact.read", "contact.update", "customer.create", "customer.read", "customer.update", "customer.view_360",
        "opportunity.create", "opportunity.read", "opportunity.update", "opportunity.delete", "pipeline.manage",
        "campaign.create", "campaign.read", "campaign.update", "campaign.execute",
        "message.send", "message.read", "call.make", "call.answer", "call.disposition",
        "analytics.view_dashboard", "analytics.view_sales", "analytics.export"
    ],
    
    SystemRole.SUPPORT_MANAGER: [
        "ticket.create", "ticket.read", "ticket.update", "ticket.assign", "ticket.resolve", "ticket.delete", "sla.manage",
        "customer.read", "customer.view_360", "contact.read", "knowledge.read", "knowledge.create", "knowledge.update",
        "message.send", "message.read", "call.make", "call.answer", "call.transfer", "call.disposition",
        "feedback.view", "feedback.manage", "analytics.view_dashboard", "analytics.export"
    ],
    
    SystemRole.SUPERVISOR: [
        "call.make", "call.answer", "call.transfer", "call.recording.listen", "call.barge", "call.whisper", "call.disposition",
        "queue.view", "agent.view", "agent.manage_status",
        "lead.read", "lead.assign", "contact.read", "customer.read", "customer.view_360",
        "ticket.read", "ticket.assign", "ticket.update",
        "qa.evaluate", "qa.view_scorecard", "qa.coach", "feedback.view",
        "analytics.view_dashboard", "analytics.view_calls", "analytics.view_agent"
    ],
    
    SystemRole.SENIOR_AGENT: [
        "call.make", "call.answer", "call.transfer", "call.disposition", "call.recording.listen",
        "lead.create", "lead.read", "lead.update", "contact.create", "contact.read", "contact.update",
        "customer.read", "customer.update", "customer.view_360", "opportunity.create", "opportunity.read", "opportunity.update",
        "ticket.create", "ticket.read", "ticket.update", "ticket.resolve",
        "message.send", "message.read", "knowledge.read", "agent.manage_status", "feedback.view"
    ],
    
    SystemRole.AGENT: [
        "call.make", "call.answer", "call.transfer", "call.disposition",
        "lead.create", "lead.read", "lead.update", "contact.create", "contact.read", "contact.update",
        "customer.read", "customer.update", "customer.view_360", "opportunity.create", "opportunity.read", "opportunity.update",
        "ticket.create", "ticket.read", "ticket.update", "ticket.resolve",
        "message.send", "message.read", "knowledge.read", "agent.manage_status"
    ],
    
    SystemRole.QA_ANALYST: [
        "call.recording.listen", "qa.evaluate", "qa.view_scorecard", "qa.manage_scorecard", "qa.coach",
        "customer.read", "customer.view_360", "ticket.read", "feedback.view",
        "analytics.view_calls", "analytics.view_dashboard"
    ],
    
    SystemRole.ANALYST: [
        "analytics.view_dashboard", "analytics.view_calls", "analytics.view_sales", "analytics.view_agent", "analytics.export",
        "lead.read", "customer.read", "opportunity.read", "ticket.read", "campaign.read"
    ],
    
    SystemRole.READ_ONLY_USER: [
        "lead.read", "contact.read", "customer.read", "opportunity.read", "ticket.read", "knowledge.read"
    ]
}


class TokenPayload(BaseModel):
    sub: str
    organization_id: Optional[str] = None
    email: Optional[str] = None
    role: str = SystemRole.AGENT
    permissions: List[str] = []
    exp: Optional[int] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with user details, role, and permissions"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create longer-lived refresh token"""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp()), "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_otp(length: int = 6) -> str:
    """Generate numeric one-time password (OTP)"""
    return "".join(random.choices(string.digits, k=length))


class PermissionChecker:
    """Dependency for RBAC & permission checking on FastAPI endpoints"""
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, token: Optional[str] = Depends(oauth2_scheme)) -> TokenPayload:
        if not token:
            # In development/test mode without token, provide default authorized superuser
            if settings.DEBUG:
                return TokenPayload(
                    sub="dev-admin-user-id",
                    organization_id="default-org-id",
                    email="admin@callsphere.local",
                    role=SystemRole.SUPER_ADMIN,
                    permissions=ALL_PERMISSIONS
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_token(token)
        user_role = payload.role
        user_permissions = payload.permissions or ROLE_PERMISSIONS.get(user_role, [])

        if user_role == SystemRole.SUPER_ADMIN:
            return payload

        for perm in self.required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: Requires '{perm}'"
                )
        return payload
