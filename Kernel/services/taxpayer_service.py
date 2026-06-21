"""Business logic for taxpayer management."""
import re
from typing import List, Optional

from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Kernel.models.taxpayer import Taxpayer, TaxpayerStatus, TaxpayerType
from Kernel.models.audit_log import AuditAction
from Kernel.exceptions.exceptions import ValidationError, NotFoundError, DuplicateError
from Kernel.services.audit_service import AuditService
from Kernel.models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus


class TaxpayerService:
    def __init__(self, taxpayer_repo: TaxpayerRepository, audit_service: AuditService):
        self._repo = taxpayer_repo
        self._audit = audit_service
    # ---------------------------------------------------------------- validation
    def _validate(self, taxpayer: Taxpayer, is_update: bool = False) -> None:
        errors = []
        if not taxpayer.tax_id or not taxpayer.tax_id.strip():
            errors.append("Tax ID is required.")
        elif not re.match(r"^[A-Za-z0-9\-]{4,20}$", taxpayer.tax_id.strip()):
            errors.append("Tax ID must be 4–20 alphanumeric characters.")

        if not taxpayer.name or not taxpayer.name.strip():
            errors.append("Name is required.")
        elif len(taxpayer.name.strip()) < 2:
            errors.append("Name must be at least 2 characters.")

        if taxpayer.email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", taxpayer.email):
            errors.append("Invalid email address.")

        if taxpayer.phone and not re.match(r"^[\d\+\-\s\(\)]{6,20}$", taxpayer.phone):
            errors.append("Invalid phone number.")

        if errors:
            raise ValidationError("\n".join(errors))

        # Uniqueness check
        existing = self._repo.find_by_tax_id(taxpayer.tax_id.strip())
        if existing and (not is_update or existing.id != taxpayer.id):
            raise DuplicateError(f"Tax ID '{taxpayer.tax_id}' is already registered.")

    # ---------------------------------------------------------------- CRUD
    def create(self, taxpayer: Taxpayer, user_id: Optional[int] = None) -> Taxpayer:
        taxpayer.tax_id = taxpayer.tax_id.strip().upper()
        taxpayer.name = taxpayer.name.strip()
        self._validate(taxpayer)
        saved = self._repo.create(taxpayer)
        self._audit.log(
            AuditAction.CREATE_TAXPAYER,
            user_id=user_id,
            entity_type="taxpayer",
            entity_id=saved.id,
            details=f"Created taxpayer '{saved.name}' ({saved.tax_id})",
        )
        return saved

    def update(self, taxpayer: Taxpayer, user_id: Optional[int] = None) -> Taxpayer:
        if not self._repo.find_by_id(taxpayer.id):
            raise NotFoundError(f"Taxpayer #{taxpayer.id} not found.")
        taxpayer.tax_id = taxpayer.tax_id.strip().upper()
        taxpayer.name = taxpayer.name.strip()
        self._validate(taxpayer, is_update=True)
        saved = self._repo.update(taxpayer)
        self._audit.log(
            AuditAction.UPDATE_TAXPAYER,
            user_id=user_id,
            entity_type="taxpayer",
            entity_id=saved.id,
            details=f"Updated taxpayer '{saved.name}' ({saved.tax_id})",
        )
        return saved

    def delete(self, taxpayer_id: int, user_id: Optional[int] = None) -> None:
        taxpayer = self._repo.find_by_id(taxpayer_id)
        if not taxpayer:
            raise NotFoundError(f"Taxpayer #{taxpayer_id} not found.")
        self._repo.delete(taxpayer_id)
        self._audit.log(
            AuditAction.DELETE_TAXPAYER,
            user_id=user_id,
            entity_type="taxpayer",
            entity_id=taxpayer_id,
            details=f"Deleted taxpayer '{taxpayer.name}' ({taxpayer.tax_id})",
        )

    def get_by_id(self, taxpayer_id: int) -> Taxpayer:
        t = self._repo.find_by_id(taxpayer_id)
        if not t:
            raise NotFoundError(f"Taxpayer #{taxpayer_id} not found.")
        return t

    def get_all(self) -> List[Taxpayer]:
        return self._repo.find_all()

    def search(self, query: str) -> List[Taxpayer]:
        if not query or not query.strip():
            return self.get_all()
        return self._repo.search(query.strip())

    def get_stats(self) -> dict:
        counts = self._repo.count_by_status()
        total = self._repo.count_total()
        return {
            "total": total,
            "active": counts.get("active", 0),
            "suspended": counts.get("suspended", 0),
            "deregistered": counts.get("deregistered", 0),
        }