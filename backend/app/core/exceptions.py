from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class DomainException(HTTPException):
    """Base domain exception with structured error details"""
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "A domain error occurred",
        error_code: str = "DOMAIN_ERROR",
        extra_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra_data = extra_data or {}


class EntityNotFoundException(DomainException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with ID '{entity_id}' was not found",
            error_code="ENTITY_NOT_FOUND",
            extra_data={"entity_name": entity_name, "entity_id": entity_id}
        )


class EntityConflictException(DomainException):
    def __init__(self, message: str, conflict_field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
            error_code="ENTITY_CONFLICT",
            extra_data={"conflict_field": conflict_field} if conflict_field else {}
        )


class PermissionDeniedException(DomainException):
    def __init__(self, permission_name: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not possess the required permission: '{permission_name}'",
            error_code="PERMISSION_DENIED",
            extra_data={"permission": permission_name}
        )


class TelephonyException(DomainException):
    def __init__(self, detail: str, call_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Telephony Error: {detail}",
            error_code="TELEPHONY_ERROR",
            extra_data={"call_id": call_id} if call_id else {}
        )
