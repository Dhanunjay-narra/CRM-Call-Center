from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Boolean, JSON, Text, DateTime
from app.core.base_models import TenantBaseModel, utc_now


class AuditLog(TenantBaseModel):
    """Enterprise Immutable Audit Log recording field-level before/after diffs"""
    __tablename__ = "sec_audit_logs"

    actor_user_id = Column(String(36), nullable=False, index=True)
    actor_email = Column(String(255), nullable=True)
    actor_role = Column(String(50), nullable=True)
    
    action = Column(String(100), nullable=False, index=True) # e.g. "CUSTOMER_PHONE_UPDATED", "USER_ROLE_CHANGED"
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    
    diff_before = Column(JSON, default=dict, nullable=False)
    diff_after = Column(JSON, default=dict, nullable=False)
    
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
