import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus
from ..models.user import User, UserRole
from ..exceptions.app_exceptions import ValidationError, PermissionDeniedError, NotFoundError

class TaxpayerService:
    def __init__(self, taxpayer_repo, audit_repo):
        self.taxpayer_repo = taxpayer_repo
        self.audit_repo = audit_repo

    def _verify_write_permission(self, user: Optional[User]):
        if not user:
            raise PermissionDeniedError("Authentication required.")
        if user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            raise PermissionDeniedError("Only Administrators and Editors can modify taxpayer records.")

    def _verify_delete_permission(self, user: Optional[User]):
        if not user:
            raise PermissionDeniedError("Authentication required.")
        if user.role != UserRole.ADMIN:
            raise PermissionDeniedError("Only Administrators can delete records.")

    def _validate_taxpayer_data(self, nin: str, full_name: str, email: str, phone: str):
        if not nin or not nin.strip():
            raise ValidationError("NIN is required.")
        if not full_name or not full_name.strip():
            raise ValidationError("Full name is required.")
        
        # Simple email validation
        if email and email.strip():
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()):
                raise ValidationError("Invalid email address format.")

    def create_taxpayer(
        self,
        nin: str,
        full_name: str,
        taxpayer_type: str,
        status: str,
        email: str,
        phone: str,
        address: str,
        current_user: User
    ) -> Taxpayer:
        self._verify_write_permission(current_user)
        self._validate_taxpayer_data(nin, full_name, email, phone)

        # Check duplicate NIN
        existing = self.taxpayer_repo.get_by_nin(nin.strip())
        if existing:
            raise ValidationError(f"A taxpayer with NIN '{nin}' already exists.")

        now_str = datetime.now().isoformat()
        data = {
            "nin": nin.strip(),
            "full_name": full_name.strip(),
            "taxpayer_type": taxpayer_type,
            "status": status,
            "email": email.strip() if email else "",
            "phone": phone.strip() if phone else "",
            "address": address.strip() if address else "",
            "registration_date": now_str
        }

        new_id = self.taxpayer_repo.create(data)
        
        self.audit_repo.log(
            current_user.username,
            "create_taxpayer",
            "taxpayer",
            new_id,
            f"Created taxpayer '{full_name}' with NIN {nin}"
        )

        return self.get_taxpayer_by_id(new_id)

    def update_taxpayer(
        self,
        taxpayer_id: int,
        nin: str,
        full_name: str,
        taxpayer_type: str,
        status: str,
        email: str,
        phone: str,
        address: str,
        current_user: User
    ) -> Taxpayer:
        self._verify_write_permission(current_user)
        self._validate_taxpayer_data(nin, full_name, email, phone)

        # Check taxpayer exists
        existing = self.taxpayer_repo.get_by_id(taxpayer_id)
        if not existing:
            raise NotFoundError("Taxpayer not found.")

        # Check duplicate NIN if changed
        if existing["nin"].lower() != nin.strip().lower():
            dup = self.taxpayer_repo.get_by_nin(nin.strip())
            if dup:
                raise ValidationError(f"A taxpayer with NIN '{nin}' already exists.")

        data = {
            "nin": nin.strip(),
            "full_name": full_name.strip(),
            "taxpayer_type": taxpayer_type,
            "status": status,
            "email": email.strip() if email else "",
            "phone": phone.strip() if phone else "",
            "address": address.strip() if address else ""
        }

        self.taxpayer_repo.update(taxpayer_id, data)

        self.audit_repo.log(
            current_user.username,
            "update_taxpayer",
            "taxpayer",
            taxpayer_id,
            f"Updated taxpayer '{full_name}' (NIN {nin})"
        )

        return self.get_taxpayer_by_id(taxpayer_id)

    def delete_taxpayer(self, taxpayer_id: int, current_user: User) -> bool:
        self._verify_delete_permission(current_user)

        existing = self.taxpayer_repo.get_by_id(taxpayer_id)
        if not existing:
            raise NotFoundError("Taxpayer not found.")

        success = self.taxpayer_repo.delete(taxpayer_id)
        if success:
            self.audit_repo.log(
                current_user.username,
                "delete_taxpayer",
                "taxpayer",
                taxpayer_id,
                f"Deleted taxpayer '{existing['full_name']}' (NIN {existing['nin']})"
            )
        return success

    def get_taxpayer_by_id(self, taxpayer_id: int) -> Taxpayer:
        row = self.taxpayer_repo.get_by_id(taxpayer_id)
        if not row:
            raise NotFoundError("Taxpayer not found.")
        return self._map_row_to_model(row)

    def search_taxpayers(self, query: str = "", status_filter: Optional[str] = None, type_filter: Optional[str] = None) -> List[Taxpayer]:
        rows = self.taxpayer_repo.search(query, status_filter, type_filter)
        return [self._map_row_to_model(row) for row in rows]

    def _map_row_to_model(self, row: Dict[str, Any]) -> Taxpayer:
        try:
            reg_date = datetime.fromisoformat(row["registration_date"])
        except ValueError:
            reg_date = datetime.now()

        return Taxpayer(
            id=row["id"],
            nin=row["nin"],
            full_name=row["full_name"],
            taxpayer_type=TaxpayerType.from_str(row["taxpayer_type"]),
            status=TaxpayerStatus.from_str(row["status"]),
            email=row["email"] or "",
            phone=row["phone"] or "",
            address=row["address"] or "",
            registration_date=reg_date
        )
