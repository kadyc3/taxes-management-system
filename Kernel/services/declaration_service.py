import uuid
from datetime import datetime
from typing import List

from Infrastructure.repositories.declaration_repository import DeclarationRepository
from Infrastructure.repositories.audit_repository import AuditRepository
from Kernel.models.declaration import Declaration, DeclarationStatus
from Kernel.models.audit_log import AuditLog, AuditSeverity


class DeclarationService:
    def __init__(
        self,
        declaration_repo: DeclarationRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self._repo = declaration_repo
        self._audit = audit_repo

    def list_declarations(
        self,
        query: str = "",
        status: str = "all",
        declaration_type: str = "all",
    ) -> List[Declaration]:
        return self._repo.search(query, status, declaration_type)

    def create_declaration(self, declaration: Declaration, created_by: str = "admin") -> Declaration:
        if not declaration.number:
            year = datetime.now().year
            all_d = self._repo.get_all()
            nums = []
            for d in all_d:
                parts = d.number.split("-")
                if len(parts) == 3:
                    try:
                        nums.append(int(parts[2]))
                    except ValueError:
                        pass
            next_num = max(nums, default=400) + 1
            declaration.number = f"DCL-{year}-{next_num:04d}"
        self._repo.create(declaration)
        self._log(
            user=created_by,
            action="Create",
            entity="Declaration",
            description=f"Draft declaration {declaration.number} created",
            severity=AuditSeverity.INFO,
        )
        return declaration

    def update_declaration(self, declaration: Declaration, updated_by: str = "admin") -> None:
        self._repo.update(declaration)
        self._log(
            user=updated_by,
            action="Update",
            entity="Declaration",
            description=f"Declaration {declaration.number} updated",
            severity=AuditSeverity.INFO,
        )

    def validate_declaration(self, declaration: Declaration, validated_by: str = "admin") -> None:
        declaration.status = DeclarationStatus.VALIDATED
        self._repo.update(declaration)
        self._log(
            user=validated_by,
            action="Validate",
            entity="Declaration",
            description=f"Declaration {declaration.number} validated",
            severity=AuditSeverity.SUCCESS,
        )

    def reject_declaration(self, declaration: Declaration, reason: str, rejected_by: str = "admin") -> None:
        declaration.status = DeclarationStatus.REJECTED
        declaration.notes = reason
        self._repo.update(declaration)
        self._log(
            user=rejected_by,
            action="Reject",
            entity="Declaration",
            description=f"Declaration {declaration.number} rejected — {reason}",
            severity=AuditSeverity.DANGER,
        )

    def delete_declaration(self, number: str, deleted_by: str = "admin") -> None:
        self._repo.delete(number)
        self._log(
            user=deleted_by,
            action="Delete",
            entity="Declaration",
            description=f"Declaration {number} deleted",
            severity=AuditSeverity.WARNING,
        )

    def count_by_status(self) -> dict:
        return self._repo.count_by_status()

    def total_validated_amount(self) -> float:
        return self._repo.sum_amounts()

    def monthly_stats(self) -> list:
        return self._repo.monthly_stats()

    def _log(
        self,
        user: str,
        action: str,
        entity: str,
        description: str,
        severity: AuditSeverity,
    ) -> None:
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