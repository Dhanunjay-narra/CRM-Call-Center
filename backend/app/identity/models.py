import enum
from sqlalchemy import Column, String, Boolean, JSON, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.base_models import CoreBaseModel, TenantBaseModel
from app.core.security import SystemRole


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class Organization(CoreBaseModel):
    """Multi-tenant Organization entity"""
    __tablename__ = "organizations"

    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(150), nullable=True)
    logo_url = Column(String(500), nullable=True)
    time_zone = Column(String(50), default="UTC", nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    
    # Business hours stored as JSON e.g. {"monday": {"open": "09:00", "close": "18:00", "closed": false}}
    business_hours = Column(JSON, default=dict, nullable=False)
    
    # Holiday calendar as list of date strings ["2026-01-01", "2026-12-25"]
    holiday_calendar = Column(JSON, default=list, nullable=False)
    
    settings = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    departments = relationship("Department", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")


class Department(TenantBaseModel):
    """Department within an Organization (e.g. Sales, Customer Support, Billing)"""
    __tablename__ = "departments"

    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    head_user_id = Column(String(36), nullable=True)

    organization = relationship("Organization", back_populates="departments")
    teams = relationship("Team", back_populates="department", cascade="all, delete-orphan")


class Team(TenantBaseModel):
    """Team within a Department (e.g. Tier 1 Support, Outbound Telesales)"""
    __tablename__ = "teams"

    name = Column(String(100), nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True)
    lead_user_id = Column(String(36), nullable=True)
    description = Column(Text, nullable=True)

    organization = relationship("Organization", back_populates="teams")
    department = relationship("Department", back_populates="teams")
    users = relationship("User", back_populates="team")


class User(CoreBaseModel):
    """User account entity with 11-tier RBAC support and multi-tenant scoping"""
    __tablename__ = "users"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True)
    team_id = Column(String(36), ForeignKey("teams.id"), nullable=True)

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    phone_number = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    role = Column(String(50), default=SystemRole.AGENT, nullable=False, index=True)
    custom_permissions = Column(JSON, default=list, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)

    organization = relationship("Organization", back_populates="users")
    team = relationship("Team", back_populates="users")


class UserSession(CoreBaseModel):
    """Track active user sessions and devices"""
    __tablename__ = "user_sessions"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    refresh_token = Column(String(500), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    device_name = Column(String(100), nullable=True)
    expires_at = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class OTPCode(CoreBaseModel):
    """One-Time Passwords for 2FA / email verification / phone logins"""
    __tablename__ = "otp_codes"

    email = Column(String(255), nullable=True, index=True)
    phone_number = Column(String(50), nullable=True, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), default="login", nullable=False)  # "login", "password_reset", "verify_email"
    expires_at = Column(String(50), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
