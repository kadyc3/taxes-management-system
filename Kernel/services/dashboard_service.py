"""Service that aggregates statistics for the dashboard."""
from Kernel.services.taxpayer_service import TaxpayerService
from Kernel.services.declaration_service import DeclarationService
from Kernel.services.audit_service import AuditService


class DashboardService:
    def __init__(
        self,
        taxpayer_service: TaxpayerService,
        declaration_service: DeclarationService,
        audit_service: AuditService,
    ):
        self._taxpayers = taxpayer_service
        self._declarations = declaration_service
        self._audit = audit_service

    def get_summary(self) -> dict:
        tp_stats = self._taxpayers.get_stats()
        decl_stats = self._declarations.get_stats()
        recent_activity = self._audit.get_recent(10)

        return {
    "taxpayers": {
        "total": tp_stats["total"],
        "active": tp_stats["active"],
        "suspended": tp_stats["suspended"],
        "deregistered": tp_stats["deregistered"],
    },

    "declarations": {
        "total": decl_stats["total"],
        "draft": decl_stats["draft"],
        "submitted": decl_stats["submitted"],
        "validated": decl_stats["validated"],
        "rejected": decl_stats["rejected"],
        "total_due": decl_stats["total_amount_due"],
    },

    "recent_activity": recent_activity,
    "recent_declarations": self._declarations.get_recent(5),
}