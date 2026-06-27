from typing import List
from Infrastructure.repositories.audit_repository import AuditRepository
from Kernel.models.audit_log import AuditLog


class AuditService:
    def __init__(self, audit_repo: AuditRepository) -> None:
        self._repo = audit_repo

    def list_logs(self, query: str = "", severity: str = "all") -> List[AuditLog]:
        return self._repo.search(query, severity)