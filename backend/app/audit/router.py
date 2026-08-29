from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.audit.models import AuditLog
from app.audit.schemas import AuditLogResponse

router = APIRouter()


@router.get("/audit/logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["audit.view"])),
    db: AsyncSession = Depends(get_db)
):
    """List immutable enterprise security audit logs and field diffs"""
    conditions = [AuditLog.organization_id == auth.organization_id, AuditLog.is_deleted == False]
    if entity_type:
        conditions.append(AuditLog.entity_type == entity_type)
    if action:
        conditions.append(AuditLog.action == action)

    res = await db.execute(select(AuditLog).where(and_(*conditions)).order_by(desc(AuditLog.created_at)).limit(100))
    return res.scalars().all()
