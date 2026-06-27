import uuid
from datetime import date
from typing import List, Optional

from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Infrastructure.repositories.audit_repository import AuditRepository
from Kernel.models.taxpayer import Taxpayer, TaxpayerStatus
from Kernel.models.audit_log import AuditLog, AuditSeverity


class TaxpayerService:
    def __init__(
        self,
        taxpayer_repo: TaxpayerRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self._repo = taxpayer_repo
        self._audit = audit_repo

    def list_taxpayers(
        self,
        query: str = "",
        status: str = "all",
        taxpayer_type: str = "all",
    ) -> List[Taxpayer]:
        return self._repo.search(query, status, taxpayer_type)

    def get_taxpayer(self, taxpayer_id: str) -> Optional[Taxpayer]:
        return self._repo.get_by_id(taxpayer_id)

    def create_taxpayer(self, taxpayer: Taxpayer, created_by: str = "admin") -> Taxpayer:
        if not taxpayer.id:
            all_ids = [t.id for t in self._repo.get_all()]
            nums = [int(i.replace("TP-", "")) for i in all_ids if i.startswith("TP-")]
            next_num = max(nums, default=10000) + 1
            taxpayer.id = f"TP-{next_num}"
        self._repo.create(taxpayer)
        self._log(
            user=created_by,
            action="Create",
            entity="Taxpayer",
            description=f"New taxpayer {taxpayer.name!r} added",
            severity=AuditSeverity.SUCCESS,
        )
        return taxpayer

    def update_taxpayer(self, taxpayer: Taxpayer, updated_by: str = "admin") -> None:
        self._repo.update(taxpayer)
        self._log(
            user=updated_by,
            action="Update",
            entity="Taxpayer",
            description=f"Taxpayer {taxpayer.id} updated",
            severity=AuditSeverity.INFO,
        )

    def delete_taxpayer(self, taxpayer_id: str, deleted_by: str = "admin") -> None:
        taxpayer = self._repo.get_by_id(taxpayer_id)
        name = taxpayer.name if taxpayer else taxpayer_id
        self._repo.delete(taxpayer_id)
        self._log(
            user=deleted_by,
            action="Delete",
            entity="Taxpayer",
            description=f"Taxpayer {taxpayer_id} ({name}) deleted",
            severity=AuditSeverity.WARNING,
        )

    def count_by_status(self) -> dict:
        return self._repo.count_by_status()

    def _log(
        self,
        user: str,
        action: str,
        entity: str,
        description: str,
        severity: AuditSeverity,
    ) -> None:
        from datetime import datetime
        log = AuditLog(
            id=f"LOG-{uuid.uuid4().hex[:6].upper()}",
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            user=user,
            action=action,
            entity=entity,
            description=description,
            severity=severity,
        )
        self._audit.create(log)