"""Repository for audit log persistence."""
from datetime import datetime
from typing import List, Optional

from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.audit_log import AuditLog, AuditAction


class AuditRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    def _row_to_log(self, row) -> AuditLog:
        d = dict(row)
        return AuditLog(
            id=d["id"],
            user_id=d.get("user_id"),
            action=AuditAction(d["action"]) if d.get("action") else None,
            entity_type=d.get("entity_type"),
            entity_id=d.get("entity_id"),
            details=d.get("details"),
            ip_address=d.get("ip_address"),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else None,
        )

    def create(self, log: AuditLog) -> AuditLog:
        now = datetime.now().isoformat()
        conn = self._db.get_connection()
        cur = conn.execute(
            """INSERT INTO audit_log
               (user_id, action, entity_type, entity_id, details, ip_address, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (
                log.user_id,
                log.action.value if log.action else None,
                log.entity_type,
                log.entity_id,
                log.details,
                log.ip_address,
                now,
            ),
        )
        conn.commit()
        log.id = cur.lastrowid
        log.created_at = datetime.fromisoformat(now)
        return log

    def find_recent(self, limit: int = 20) -> List[AuditLog]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._row_to_log(r) for r in rows]

    def find_by_user(self, user_id: int, limit: int = 50) -> List[AuditLog]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [self._row_to_log(r) for r in rows]