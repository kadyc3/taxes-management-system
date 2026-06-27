from datetime import datetime
from typing import List, Dict, Any
from ..models.audit_log import AuditLog

class DashboardService:
    def __init__(self, taxpayer_repo, declaration_repo, audit_repo):
        self.taxpayer_repo = taxpayer_repo
        self.declaration_repo = declaration_repo
        self.audit_repo = audit_repo

    def get_kpis(self) -> Dict[str, Any]:
        """Gathers counts and totals for dashboard widgets."""
        taxpayer_kpis = self.taxpayer_repo.get_kpi_counts()
        declaration_kpis = self.declaration_repo.get_kpi_counts()
        total_revenue = self.declaration_repo.get_total_revenue()

        return {
            "taxpayers": {
                "total": taxpayer_kpis.get("total", 0),
                "active": taxpayer_kpis.get("active", 0),
                "suspended": taxpayer_kpis.get("suspended", 0),
                "deregistered": taxpayer_kpis.get("deregistered", 0)
            },
            "declarations": {
                "total": declaration_kpis.get("total", 0),
                "draft": declaration_kpis.get("draft", 0),
                "submitted": declaration_kpis.get("submitted", 0),
                "validated": declaration_kpis.get("validated", 0),
                "rejected": declaration_kpis.get("rejected", 0)
            },
            "total_revenue": total_revenue
        }

    def get_recent_activity(self, limit: int = 10) -> List[AuditLog]:
        """Fetches last N audit logs, mapped to Domain Models."""
        rows = self.audit_repo.get_recent(limit)
        activities = []
        for row in rows:
            try:
                created_at = datetime.fromisoformat(row["created_at"])
            except ValueError:
                created_at = datetime.now()

            activities.append(
                AuditLog(
                    id=row["id"],
                    username=row["username"],
                    action=row["action"],
                    entity_type=row["entity_type"],
                    entity_id=row["entity_id"],
                    details=row["details"],
                    created_at=created_at
                )
            )
        return activities

    def get_revenue_by_year(self) -> List[Dict[str, Any]]:
        """Returns validated revenue grouped by fiscal year for charting."""
        return self.declaration_repo.get_revenue_by_year()
