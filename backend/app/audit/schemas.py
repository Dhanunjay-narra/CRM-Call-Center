from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    organization_id: str
    actor_user_id: str
    actor_email: Optional[str] = None
    actor_role: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    diff_before: Dict[str, Any]
    diff_after: Dict[str, Any]
    ip_address: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
