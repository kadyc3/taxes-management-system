"""Business logic for declaration management."""
from datetime import datetime
from typing import List, Optional

from Infrastructure.repositories.declaration_repository import DeclarationRepository
from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Kernel.models.declaration import Declaration, DeclarationStatus, TAX_RATES
from Kernel.models.audit_log import AuditAction
from Kernel.exceptions.exceptions import ValidationError, NotFoundError
from Kernel.services.audit_service import AuditService


class DeclarationService:
    def __init__(
        self,
        declaration_repo: DeclarationRepository,
        taxpayer_repo: TaxpayerRepository,
        audit_service: AuditService,
    ):
        self._repo = declaration_repo
        self._taxpayer_repo = taxpayer_repo
        self._audit = audit_service

    # ---------------------------------------------------------------- validation
    def _validate(self, declaration: Declaration) -> None:
        errors = []
        if not declaration.taxpayer_id:
            errors.append("Taxpayer is required.")
        else:
            taxpayer = self._taxpayer_repo.find_by_id(declaration.taxpayer_id)
            if not taxpayer:
                errors.append("Selected taxpayer does not exist.")

        current_year = datetime.now().year
        if not (2000 <= declaration.fiscal_year <= current_year + 1):
            errors.append(f"Fiscal year must be between 2000 and {current_year + 1}.")

        if declaration.gross_amount < 0:
            errors.append("Gross amount cannot be negative.")

        if declaration.penalties < 0:
            errors.append("Penalties cannot be negative.")

        if errors:
            raise ValidationError("\n".join(errors))

    # ---------------------------------------------------------------- CRUD
    def create(self, declaration: Declaration, user_id: Optional[int] = None) -> Declaration:
        declaration.calculate_tax()
        self._validate(declaration)
        saved = self._repo.create(declaration)
        self._audit.log(
            AuditAction.CREATE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=saved.id,
            details=f"Created {saved.declaration_type.value} declaration for year {saved.fiscal_year}",
        )
        return saved

    def update(self, declaration: Declaration, user_id: Optional[int] = None) -> Declaration:
        if not self._repo.find_by_id(declaration.id):
            raise NotFoundError(f"Declaration #{declaration.id} not found.")
        declaration.calculate_tax()
        self._validate(declaration)
        saved = self._repo.update(declaration)
        self._audit.log(
            AuditAction.UPDATE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=saved.id,
            details=f"Updated declaration #{saved.id}",
        )
        return saved

    def delete(self, declaration_id: int, user_id: Optional[int] = None) -> None:
        decl = self._repo.find_by_id(declaration_id)
        if not decl:
            raise NotFoundError(f"Declaration #{declaration_id} not found.")
        self._repo.delete(declaration_id)
        self._audit.log(
            AuditAction.DELETE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=declaration_id,
            details=f"Deleted declaration #{declaration_id}",
        )

    def submit(self, declaration_id: int, user_id: Optional[int] = None) -> Declaration:
        decl = self._repo.find_by_id(declaration_id)
        if not decl:
            raise NotFoundError(f"Declaration #{declaration_id} not found.")
        if decl.status != DeclarationStatus.DRAFT:
            raise ValidationError("Only draft declarations can be submitted.")
        decl.status = DeclarationStatus.SUBMITTED
        decl.submitted_at = datetime.now()
        return self._repo.update(decl)

    def validate(self, declaration_id: int, user_id: Optional[int] = None) -> Declaration:
        decl = self._repo.find_by_id(declaration_id)
        if not decl:
            raise NotFoundError(f"Declaration #{declaration_id} not found.")
        if decl.status != DeclarationStatus.SUBMITTED:
            raise ValidationError("Only submitted declarations can be validated.")
        decl.status = DeclarationStatus.VALIDATED
        decl.validated_at = datetime.now()
        return self._repo.update(decl)

    def reject(self, declaration_id: int, user_id: Optional[int] = None) -> Declaration:
        decl = self._repo.find_by_id(declaration_id)
        if not decl:
            raise NotFoundError(f"Declaration #{declaration_id} not found.")
        decl.status = DeclarationStatus.REJECTED
        return self._repo.update(decl)

    def get_by_id(self, declaration_id: int) -> Declaration:
        d = self._repo.find_by_id(declaration_id)
        if not d:
            raise NotFoundError(f"Declaration #{declaration_id} not found.")
        return d

    def get_all(self) -> List[Declaration]:
        return self._repo.find_all()

    def get_by_taxpayer(self, taxpayer_id: int) -> List[Declaration]:
        return self._repo.find_by_taxpayer(taxpayer_id)

    def search(self, query: str) -> List[Declaration]:
        if not query or not query.strip():
            return self.get_all()
        return self._repo.search(query.strip())

    def get_stats(self) -> dict:
        counts = self._repo.count_by_status()
        total = sum(counts.values())
        return {
            "total": total,
            "draft": counts.get("draft", 0),
            "submitted": counts.get("submitted", 0),
            "validated": counts.get("validated", 0),
            "rejected": counts.get("rejected", 0),
            "total_amount_due": self._repo.total_amount_due(),
        }

    def get_recent(self, limit: int = 10) -> List[Declaration]:
        return self._repo.recent(limit)

    @staticmethod
    def get_tax_rates() -> dict:
        return {k.value: v for k, v in TAX_RATES.items()}