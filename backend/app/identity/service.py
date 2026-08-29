import re
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    generate_otp,
    SystemRole,
    ROLE_PERMISSIONS,
    TokenPayload
)
from app.identity.models import Organization, Department, Team, User, UserSession, OTPCode, UserStatus
from app.identity.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserCreate,
    UserUpdate,
    OrganizationCreate,
    OrganizationUpdate,
    DepartmentCreate,
    TeamCreate
)


def slugify(text: str) -> str:
    text = text.lower().strip()
    return re.sub(r'[\s\W-]+', '-', text)


class IdentityService:
    @staticmethod
    async def register_tenant(db: AsyncSession, req: UserRegisterRequest) -> dict:
        """Register new multi-tenant organization, default admin user, and sales/support departments"""
        # Check if email already exists
        existing_user = await db.execute(select(User).where(User.email == req.email))
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{req.email}' already exists."
            )

        # Create Organization
        base_slug = slugify(req.organization_name)
        slug = base_slug
        counter = 1
        while (await db.execute(select(Organization).where(Organization.slug == slug))).scalar_one_or_none():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Default business hours (9 AM - 6 PM Mon-Fri)
        default_hours = {
            "monday": {"open": "09:00", "close": "18:00", "closed": False},
            "tuesday": {"open": "09:00", "close": "18:00", "closed": False},
            "wednesday": {"open": "09:00", "close": "18:00", "closed": False},
            "thursday": {"open": "09:00", "close": "18:00", "closed": False},
            "friday": {"open": "09:00", "close": "18:00", "closed": False},
            "saturday": {"open": "10:00", "close": "14:00", "closed": False},
            "sunday": {"open": "00:00", "close": "00:00", "closed": True}
        }

        org = Organization(
            name=req.organization_name,
            slug=slug,
            time_zone=req.time_zone,
            business_hours=default_hours,
            holiday_calendar=[],
            settings={"call_recording_enabled": True, "sla_escalation_enabled": True}
        )
        db.add(org)
        await db.flush()

        # Create Default Departments
        sales_dept = Department(organization_id=org.id, name="Sales & Telemarketing", code="SALES")
        support_dept = Department(organization_id=org.id, name="Customer Support", code="SUPPORT")
        db.add_all([sales_dept, support_dept])
        await db.flush()

        # Create Default Teams
        sales_team = Team(organization_id=org.id, department_id=sales_dept.id, name="Outbound Sales Team")
        support_team = Team(organization_id=org.id, department_id=support_dept.id, name="Tier 1 Support Team")
        db.add_all([sales_team, support_team])
        await db.flush()

        # Create Admin User
        user = User(
            organization_id=org.id,
            email=req.email,
            hashed_password=get_password_hash(req.password),
            full_name=req.full_name,
            phone_number=req.phone_number,
            role=SystemRole.ORGANIZATION_ADMIN,
            custom_permissions=ROLE_PERMISSIONS.get(SystemRole.ORGANIZATION_ADMIN, []),
            status=UserStatus.ACTIVE,
            timezone=req.time_zone,
            is_verified=True,
            is_superadmin=False
        )
        db.add(user)
        await db.flush()

        # Generate tokens
        token_data = {
            "sub": user.id,
            "organization_id": org.id,
            "email": user.email,
            "role": user.role,
            "permissions": user.custom_permissions
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Track session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        )
        db.add(session)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    async def login_user(db: AsyncSession, req: UserLoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
        """Authenticate user with email and password"""
        query = await db.execute(select(User).where(and_(User.email == req.email, User.is_deleted == False)))
        user = query.scalar_one_or_none()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User account is {user.status.value.lower()}."
            )

        permissions = user.custom_permissions or ROLE_PERMISSIONS.get(user.role, [])
        token_data = {
            "sub": user.id,
            "organization_id": user.organization_id,
            "email": user.email,
            "role": user.role,
            "permissions": permissions
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Record active session
        session = UserSession(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        )
        db.add(session)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }

    @staticmethod
    async def request_otp(db: AsyncSession, email: Optional[str], phone: Optional[str], purpose: str = "login") -> str:
        """Generate and save numeric OTP code"""
        code = generate_otp(6)
        expires = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
        otp = OTPCode(
            email=email,
            phone_number=phone,
            code=code,
            purpose=purpose,
            expires_at=expires,
            is_used=False
        )
        db.add(otp)
        await db.commit()
        return code

    @staticmethod
    async def verify_otp(db: AsyncSession, email: Optional[str], phone: Optional[str], code: str, purpose: str = "login") -> bool:
        """Verify submitted OTP code"""
        conditions = [OTPCode.code == code, OTPCode.purpose == purpose, OTPCode.is_used == False]
        if email:
            conditions.append(OTPCode.email == email)
        if phone:
            conditions.append(OTPCode.phone_number == phone)

        res = await db.execute(select(OTPCode).where(and_(*conditions)).order_by(OTPCode.created_at.desc()))
        otp = res.scalars().first()

        if not otp:
            return False

        if datetime.fromisoformat(otp.expires_at) < datetime.now(timezone.utc):
            return False

        otp.is_used = True
        await db.commit()
        return True
