"""repositories/audit_log_repository.py"""
import sqlite3
from datetime import datetime


class AuditLogRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_dict(self, row) -> dict:
        return dict(row) if row else {}

    def log(
        self,
        action: str,
        entity_type: str = None,
        entity_id: int = None,
        details: str = None,
        username: str = "system",
    ) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO audit_logs (username, action, entity_type, entity_id, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, action, entity_type, entity_id, details, datetime.now().isoformat()),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self, limit: int = 500) -> list[dict]:
        cursor = self.conn.execute(
            "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def get_by_entity(self, entity_type: str, entity_id: int) -> list[dict]:
        cursor = self.conn.execute(
            """
            SELECT * FROM audit_logs
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY created_at DESC
            """,
            (entity_type, entity_id),
        )
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def count_today(self) -> int:
        today = datetime.now().strftime("%Y-%m-%d")
        row = self.conn.execute(
            "SELECT COUNT(*) FROM audit_logs WHERE created_at LIKE ?",
            (f"{today}%",),
        ).fetchone()
        return row[0] if row else 0