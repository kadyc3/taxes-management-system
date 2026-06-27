from typing import List
from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.audit_log import AuditLog, AuditSeverity


class AuditRepository:
    def __init__(self) -> None:
        self._db = DatabaseConnection.get_instance()

    def _row_to_log(self, row) -> AuditLog:
        return AuditLog(
            id=row["id"],
            date=row["date"],
            user=row["user"],
            action=row["action"],
            entity=row["entity"],
            description=row["description"],
            severity=AuditSeverity(row["severity"]),
        )

    def get_all(self) -> List[AuditLog]:
        conn = self._db.connect()
        rows = conn.execute(
            "SELECT * FROM audit_logs ORDER BY date DESC"
        ).fetchall()
        return [self._row_to_log(r) for r in rows]

    def search(self, query: str = "", severity: str = "all") -> List[AuditLog]:
        conn = self._db.connect()
        sql = "SELECT * FROM audit_logs WHERE 1=1"
        params: list = []
        if query:
            sql += " AND (user LIKE ? OR action LIKE ? OR entity LIKE ? OR description LIKE ?)"
            like = f"%{query}%"
            params += [like, like, like, like]
        if severity != "all":
            sql += " AND severity = ?"
            params.append(severity)
        sql += " ORDER BY date DESC"
        rows = conn.execute(sql, params).fetchall()
        return [self._row_to_log(r) for r in rows]

    def create(self, log: AuditLog) -> None:
        conn = self._db.connect()
        conn.execute(
            """INSERT INTO audit_logs
               (id, date, user, action, entity, description, severity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (log.id, log.date, log.user, log.action,
             log.entity, log.description, log.severity.value),
        )
        conn.commit()