from dataclasses import dataclass
from typing import List

from Infrastructure.repositories.taxpayer_repository import TaxpayerRepository
from Infrastructure.repositories.declaration_repository import DeclarationRepository
from Infrastructure.repositories.audit_repository import AuditRepository
from Kernel.models.audit_log import AuditLog


@dataclass
class DashboardStats:
    total_taxpayers: int
    active_taxpayers: int
    suspended_taxpayers: int
    deregistered_taxpayers: int
    total_declarations: int
    draft_declarations: int
    submitted_declarations: int
    validated_declarations: int
    rejected_declarations: int
    total_taxes_due: float
    recent_logs: List[AuditLog]
    monthly_stats: list


class DashboardService:
    def __init__(
        self,
        taxpayer_repo: TaxpayerRepository,
        declaration_repo: DeclarationRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self._taxpayer_repo = taxpayer_repo
        self._declaration_repo = declaration_repo
        self._audit_repo = audit_repo

    def get_stats(self) -> DashboardStats:
        tp_counts = self._taxpayer_repo.count_by_status()
        dcl_counts = self._declaration_repo.count_by_status()
        recent = self._audit_repo.get_all()[:5]
        monthly = self._declaration_repo.monthly_stats()
        return DashboardStats(
            total_taxpayers=sum(tp_counts.values()),
            active_taxpayers=tp_counts.get("Active", 0),
            suspended_taxpayers=tp_counts.get("Suspended", 0),
            deregistered_taxpayers=tp_counts.get("Deregistered", 0),
            total_declarations=sum(dcl_counts.values()),
            draft_declarations=dcl_counts.get("Draft", 0),
            submitted_declarations=dcl_counts.get("Submitted", 0),
            validated_declarations=dcl_counts.get("Validated", 0),
            rejected_declarations=dcl_counts.get("Rejected", 0),
            total_taxes_due=self._declaration_repo.sum_amounts(),
            recent_logs=recent,
            monthly_stats=monthly,
        )