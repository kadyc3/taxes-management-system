import sqlite3
from typing import Optional, Dict, Any, List
from ..database.connection import DatabaseConnection

class DeclarationRepository:
    def __init__(self):
        pass

    def get_by_id(self, declaration_id: int) -> Optional[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT d.id, d.taxpayer_id, d.reference_number, d.declaration_type, d.fiscal_year, d.period,
                       d.gross_amount, d.deductions, d.penalties, d.total_due, d.status, d.filed_date, d.rejection_reason,
                       t.full_name as taxpayer_name
                FROM declarations d
                JOIN taxpayers t ON d.taxpayer_id = t.id
                WHERE d.id = ?
                """,
                (declaration_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def get_by_reference_number(self, reference_number: str) -> Optional[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT d.id, d.taxpayer_id, d.reference_number, d.declaration_type, d.fiscal_year, d.period,
                       d.gross_amount, d.deductions, d.penalties, d.total_due, d.status, d.filed_date, d.rejection_reason,
                       t.full_name as taxpayer_name
                FROM declarations d
                JOIN taxpayers t ON d.taxpayer_id = t.id
                WHERE d.reference_number = ?
                """,
                (reference_number,)
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
                INSERT INTO declarations (taxpayer_id, reference_number, declaration_type, fiscal_year, period,
                                         gross_amount, deductions, penalties, total_due, status, filed_date, rejection_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["taxpayer_id"],
                    data["reference_number"],
                    data["declaration_type"],
                    data["fiscal_year"],
                    data["period"],
                    data["gross_amount"],
                    data["deductions"],
                    data["penalties"],
                    data["total_due"],
                    data["status"],
                    data["filed_date"],
                    data.get("rejection_reason")
                )
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update(self, declaration_id: int, data: Dict[str, Any]) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE declarations
                SET taxpayer_id = ?, reference_number = ?, declaration_type = ?, fiscal_year = ?, period = ?,
                    gross_amount = ?, deductions = ?, penalties = ?, total_due = ?, status = ?, rejection_reason = ?
                WHERE id = ?
                """,
                (
                    data["taxpayer_id"],
                    data["reference_number"],
                    data["declaration_type"],
                    data["fiscal_year"],
                    data["period"],
                    data["gross_amount"],
                    data["deductions"],
                    data["penalties"],
                    data["total_due"],
                    data["status"],
                    data.get("rejection_reason"),
                    declaration_id
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete(self, declaration_id: int) -> bool:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM declarations WHERE id = ?", (declaration_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def search(self, query: str = "", status_filter: Optional[str] = None, taxpayer_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                SELECT d.id, d.taxpayer_id, d.reference_number, d.declaration_type, d.fiscal_year, d.period,
                       d.gross_amount, d.deductions, d.penalties, d.total_due, d.status, d.filed_date, d.rejection_reason,
                       t.full_name as taxpayer_name
                FROM declarations d
                JOIN taxpayers t ON d.taxpayer_id = t.id
                WHERE 1=1
            """
            params = []

            if query:
                sql += " AND (d.reference_number LIKE ? OR t.full_name LIKE ? OR d.declaration_type LIKE ? OR d.fiscal_year LIKE ?)"
                like_query = f"%{query}%"
                params.extend([like_query, like_query, like_query, like_query])

            if status_filter:
                sql += " AND d.status = ?"
                params.append(status_filter)

            if taxpayer_id is not None:
                sql += " AND d.taxpayer_id = ?"
                params.append(taxpayer_id)

            sql += " ORDER BY d.filed_date DESC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_kpi_counts(self) -> Dict[str, int]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT status, COUNT(*) as count FROM declarations GROUP BY status")
            rows = cursor.fetchall()
            kpis = {"total": 0, "draft": 0, "submitted": 0, "validated": 0, "rejected": 0}
            for row in rows:
                status = row["status"].lower()
                kpis[status] = row["count"]
                kpis["total"] += row["count"]
            return kpis
        finally:
            conn.close()

    def get_total_revenue(self) -> float:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            # Revenue is defined as total_due for validated declarations
            cursor.execute("SELECT SUM(total_due) as total FROM declarations WHERE status = 'Validated'")
            row = cursor.fetchone()
            return row["total"] if row and row["total"] is not None else 0.0
        finally:
            conn.close()
            
    def get_revenue_by_year(self) -> List[Dict[str, Any]]:
        """Used for dashboard charts (shows revenue by fiscal year)."""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT fiscal_year, SUM(total_due) as revenue
                FROM declarations
                WHERE status = 'Validated'
                GROUP BY fiscal_year
                ORDER BY fiscal_year ASC
                LIMIT 5
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
