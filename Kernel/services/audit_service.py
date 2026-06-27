"""services/audit_service.py"""
from Infrastructure.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    def __init__(self, log_repo: AuditLogRepository):
        self.log_repo = log_repo

    def get_all_logs(self) -> list[dict]:
        return self.log_repo.get_all()

    def get_entity_logs(self, entity_type: str, entity_id: int) -> list[dict]:
        return self.log_repo.get_by_entity(entity_type, entity_id)

    def count_today(self) -> int:
        return self.log_repo.count_today()