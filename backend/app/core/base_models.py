import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """SQLAlchemy Base Declarative Class"""
    pass


class CoreBaseModel(Base):
    """
    Abstract base model providing:
    - Primary Key (UUID string)
    - Timestamps (created_at, updated_at)
    - Soft delete flag (is_deleted)
    - Optional arbitrary metadata JSON field
    """
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    metadata_json = Column(JSON, default=dict, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            result[c.name] = val
        return result


class TenantBaseModel(CoreBaseModel):
    """
    Base model for all tenant-scoped CRM and Call Center entities.
    Enforces multi-tenancy via organization_id with foreign key.
    """
    __abstract__ = True

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
