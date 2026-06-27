import sqlite3
from typing import Optional, Dict, Any
from ..database.connection import DatabaseConnection

class UserRepository:
    def __init__(self):
        pass

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, username, password, salt, role, created_at FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def create(self, user_data: Dict[str, Any]) -> int:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, salt, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    user_data["username"],
                    user_data["password"],
                    user_data["salt"],
                    user_data["role"],
                    user_data["created_at"]
                )
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
