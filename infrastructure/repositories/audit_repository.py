import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..database.connection import DatabaseConnection

class AuditRepository:
    def __init__(self):
        pass

    def log(self, username: str, action: str, entity_type: str, entity_id: Optional[int], details: Optional[str]) -> int:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            now_str = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO audit_logs (username, action, entity_type, entity_id, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, action, entity_type, entity_id, details, now_str)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, username, action, entity_type, entity_id, details, created_at
                FROM audit_logs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
