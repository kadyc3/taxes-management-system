"""Service for writing audit log entries."""
from typing import Optional

from Infrastructure.repositories.audit_repository import AuditRepository
from Kernel.models.audit_log import AuditLog, AuditAction


class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self._repo = audit_repo

    def log(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        return self._repo.create(entry)

    def get_recent(self, limit: int = 20):
        return self._repo.find_recent(limit)