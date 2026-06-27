import sqlite3
from typing import Optional, Dict, Any, List
from ..database.connection import DatabaseConnection

class TaxpayerRepository:
    def __init__(self):
        pass

    def get_by_id(self, taxpayer_id: int) -> Optional[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, nin, full_name, taxpayer_type, status, email, phone, address, registration_date FROM taxpayers WHERE id = ?",
                (taxpayer_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def get_by_nin(self, nin: str) -> Optional[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, nin, full_name, taxpayer_type, status, email, phone, address, registration_date FROM taxpayers WHERE nin = ?",
                (nin,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def create(self, data: Dict[str, Any]) -> int:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO taxpayers (nin, full_name, taxpayer_type, status, email, phone, address, registration_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["nin"],
                    data["full_name"],
                    data["taxpayer_type"],
                    data["status"],
                    data.get("email"),
                    data.get("phone"),
                    data.get("address"),
                    data["registration_date"]
                )
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update(self, taxpayer_id: int, data: Dict[str, Any]) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE taxpayers
                SET nin = ?, full_name = ?, taxpayer_type = ?, status = ?, email = ?, phone = ?, address = ?
                WHERE id = ?
                """,
                (
                    data["nin"],
                    data["full_name"],
                    data["taxpayer_type"],
                    data["status"],
                    data.get("email"),
                    data.get("phone"),
                    data.get("address"),
                    taxpayer_id
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, taxpayer_id: int) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM taxpayers WHERE id = ?", (taxpayer_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def search(self, query: str = "", status_filter: Optional[str] = None, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            sql = "SELECT id, nin, full_name, taxpayer_type, status, email, phone, address, registration_date FROM taxpayers WHERE 1=1"
            params = []

            if query:
                sql += " AND (nin LIKE ? OR full_name LIKE ? OR email LIKE ? OR phone LIKE ? OR address LIKE ?)"
                like_query = f"%{query}%"
                params.extend([like_query] * 5)

            if status_filter:
                sql += " AND status = ?"
                params.append(status_filter)

            if type_filter:
                sql += " AND taxpayer_type = ?"
                params.append(type_filter)

            sql += " ORDER BY registration_date DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_kpi_counts(self) -> Dict[str, int]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status, COUNT(*) as count FROM taxpayers GROUP BY status")
            rows = cursor.fetchall()
            kpis = {"total": 0, "active": 0, "suspended": 0, "deregistered": 0}
            for row in rows:
                status = row["status"].lower()
                kpis[status] = row["count"]
                kpis["total"] += row["count"]
            return kpis
        finally:
            conn.close()
