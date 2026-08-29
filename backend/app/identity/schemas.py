from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.core.security import SystemRole
from app.identity.models import UserStatus


# Authentication Schemas
class UserRegisterRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=150)
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: Optional[str] = None
    time_zone: str = "UTC"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    purpose: str = "login"


class OTPVerifyRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    code: str
    purpose: str = "login"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Organization Schemas
class OrganizationCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    domain: Optional[str] = None
    time_zone: str = "UTC"
    currency: str = "USD"
    business_hours: Optional[Dict[str, Any]] = None
    holiday_calendar: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    time_zone: Optional[str] = None
    currency: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    holiday_calendar: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    time_zone: str
    currency: str
    business_hours: Dict[str, Any]
    holiday_calendar: List[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Department & Team Schemas
class DepartmentCreate(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    head_user_id: Optional[str] = None


class DepartmentResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    head_user_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    name: str
    department_id: Optional[str] = None
    lead_user_id: Optional[str] = None
    description: Optional[str] = None


class TeamResponse(BaseModel):
    id: str
    organization_id: str
    department_id: Optional[str] = None
    name: str
    lead_user_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = SystemRole.AGENT
    department_id: Optional[str] = None
    team_id: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[str] = None
    team_id: Optional[str] = None
    status: Optional[UserStatus] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    custom_permissions: Optional[List[str]] = None


class UserResponse(BaseModel):
    id: str
    organization_id: Optional[str] = None
    department_id: Optional[str] = None
    team_id: Optional[str] = None
    email: str
    full_name: str
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    custom_permissions: List[str]
    status: UserStatus
    timezone: str
    language: str
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


TokenResponse.model_rebuild()
