from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.core.security import (
    PermissionChecker,
    TokenPayload,
    decode_token,
    create_access_token,
    get_password_hash,
    SystemRole,
    ROLE_PERMISSIONS
)
from app.identity.models import Organization, Department, Team, User, UserStatus
from app.telephony.models import AgentProfile, AgentState
from app.identity.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    OTPRequest,
    OTPVerifyRequest,
    UserResponse,
    UserCreate,
    UserUpdate,
    OrganizationResponse,
    OrganizationUpdate,
    DepartmentResponse,
    DepartmentCreate,
    TeamResponse,
    TeamCreate
)
from app.identity.service import IdentityService

router = APIRouter()


# ----------------------------------------------------
# Authentication Endpoints
# ----------------------------------------------------

@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register new tenant organization and primary administrator"""
    return await IdentityService.register_tenant(db, req)


@router.post("/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password"""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await IdentityService.login_user(db, req, ip_address=ip, user_agent=user_agent)


@router.post("/auth/refresh")
async def refresh_token(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using valid refresh token"""
    payload = decode_token(req.refresh_token)
    user_query = await db.execute(select(User).where(User.id == payload.sub))
    user = user_query.scalar_one_or_none()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    token_data = {
        "sub": user.id,
        "organization_id": user.organization_id,
        "email": user.email,
        "role": user.role,
        "permissions": user.custom_permissions or ROLE_PERMISSIONS.get(user.role, [])
    }
    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer"
    }


@router.post("/auth/otp/request")
async def request_otp(req: OTPRequest, db: AsyncSession = Depends(get_db)):
    """Request OTP for login or verification"""
    code = await IdentityService.request_otp(db, req.email, req.phone_number, req.purpose)
    return {"message": "OTP sent successfully", "debug_code": code}


@router.post("/auth/otp/verify")
async def verify_otp(req: OTPVerifyRequest, db: AsyncSession = Depends(get_db)):
    """Verify OTP code"""
    is_valid = await IdentityService.verify_otp(db, req.email, req.phone_number, req.code, req.purpose)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP code")
    return {"message": "OTP verified successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch profile of authenticated user"""
    res = await db.execute(select(User).where(User.id == auth.sub))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# ----------------------------------------------------
# Organization Endpoints
# ----------------------------------------------------

@router.get("/organizations/me", response_model=OrganizationResponse)
async def get_my_organization(
    auth: TokenPayload = Depends(PermissionChecker(["org.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details and business hours of current tenant organization"""
    res = await db.execute(select(Organization).where(Organization.id == auth.organization_id))
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


@router.patch("/organizations/me", response_model=OrganizationResponse)
async def update_my_organization(
    req: OrganizationUpdate,
    auth: TokenPayload = Depends(PermissionChecker(["org.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Update tenant organization settings, business hours, and holiday calendar"""
    res = await db.execute(select(Organization).where(Organization.id == auth.organization_id))
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(org, field, val)

    await db.commit()
    await db.refresh(org)
    return org


# ----------------------------------------------------
# Department & Team Endpoints
# ----------------------------------------------------

@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """List departments for current organization"""
    res = await db.execute(
        select(Department).where(
            and_(Department.organization_id == auth.organization_id, Department.is_deleted == False)
        )
    )
    return res.scalars().all()


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    req: DepartmentCreate,
    auth: TokenPayload = Depends(PermissionChecker(["org.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new department"""
    dept = Department(
        organization_id=auth.organization_id,
        name=req.name,
        code=req.code,
        description=req.description,
        head_user_id=req.head_user_id
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    department_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """List teams in the organization, optionally filtered by department"""
    conditions = [Team.organization_id == auth.organization_id, Team.is_deleted == False]
    if department_id:
        conditions.append(Team.department_id == department_id)

    res = await db.execute(select(Team).where(and_(*conditions)))
    return res.scalars().all()


@router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    req: TeamCreate,
    auth: TokenPayload = Depends(PermissionChecker(["org.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new team"""
    team = Team(
        organization_id=auth.organization_id,
        name=req.name,
        department_id=req.department_id,
        lead_user_id=req.lead_user_id,
        description=req.description
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


# ----------------------------------------------------
# Users & Workforce Endpoints
# ----------------------------------------------------

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[str] = None,
    team_id: Optional[str] = None,
    department_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["user.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """List users in tenant organization with filters"""
    conditions = [User.organization_id == auth.organization_id, User.is_deleted == False]
    if role:
        conditions.append(User.role == role)
    if team_id:
        conditions.append(User.team_id == team_id)
    if department_id:
        conditions.append(User.department_id == department_id)

    res = await db.execute(select(User).where(and_(*conditions)))
    return res.scalars().all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    req: UserCreate,
    auth: TokenPayload = Depends(PermissionChecker(["user.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user account with assigned role and department, and initialize Agent Profile if agent"""
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User email already exists")

    perms = ROLE_PERMISSIONS.get(req.role, [])
    user = User(
        organization_id=auth.organization_id,
        department_id=req.department_id,
        team_id=req.team_id,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        phone_number=req.phone_number,
        role=req.role,
        custom_permissions=perms,
        status=UserStatus.ACTIVE,
        timezone=req.timezone,
        language=req.language,
        is_verified=True
    )
    db.add(user)
    await db.flush()

    # Automatically provision AgentProfile for agent/supervisor/admin roles
    agent_prof = AgentProfile(
        organization_id=auth.organization_id,
        user_id=user.id,
        skills=["Sales", "General Support"],
        languages=["en", req.language],
        current_state=AgentState.AVAILABLE,
        state_changed_at=datetime.now(timezone.utc)
    )
    db.add(agent_prof)

    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    req: UserUpdate,
    auth: TokenPayload = Depends(PermissionChecker(["user.manage"])),
    db: AsyncSession = Depends(get_db)
):
    """Update user information, role, or team assignment"""
    res = await db.execute(select(User).where(and_(User.id == user_id, User.organization_id == auth.organization_id)))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(user, field, val)

    await db.commit()
    await db.refresh(user)
    return user
