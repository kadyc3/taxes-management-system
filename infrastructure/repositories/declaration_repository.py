from typing import List, Optional
from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.declaration import Declaration, DeclarationStatus, DeclarationType


class DeclarationRepository:
    def __init__(self) -> None:
        self._db = DatabaseConnection.get_instance()

    def _row_to_declaration(self, row) -> Declaration:
        return Declaration(
            number=row["number"],
            taxpayer=row["taxpayer"],
            amount=row["amount"],
            status=DeclarationStatus(row["status"]),
            date=row["date"],
            declaration_type=DeclarationType(row["declaration_type"]),
            notes=row["notes"] or "",
        )

    def get_all(self) -> List[Declaration]:
        conn = self._db.connect()
        rows = conn.execute(
            "SELECT * FROM declarations ORDER BY date DESC"
        ).fetchall()
        return [self._row_to_declaration(r) for r in rows]

    def search(
        self,
        query: str = "",
        status: Optional[str] = None,
        declaration_type: Optional[str] = None,
    ) -> List[Declaration]:
        conn = self._db.connect()
        sql = "SELECT * FROM declarations WHERE 1=1"
        params: list = []
        if query:
            sql += " AND (number LIKE ? OR taxpayer LIKE ?)"
            like = f"%{query}%"
            params += [like, like]
        if status and status != "all":
            sql += " AND status = ?"
            params.append(status)
        if declaration_type and declaration_type != "all":
            sql += " AND declaration_type = ?"
            params.append(declaration_type)
        sql += " ORDER BY date DESC"
        rows = conn.execute(sql, params).fetchall()
        return [self._row_to_declaration(r) for r in rows]

    def create(self, declaration: Declaration) -> None:
        conn = self._db.connect()
        conn.execute(
            """INSERT INTO declarations
               (number, taxpayer, amount, status, date, declaration_type, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                declaration.number, declaration.taxpayer, declaration.amount,
                declaration.status.value, declaration.date,
                declaration.declaration_type.value, declaration.notes,
            ),
        )
        conn.commit()

    def update(self, declaration: Declaration) -> None:
        conn = self._db.connect()
        conn.execute(
            """UPDATE declarations SET
               taxpayer=?, amount=?, status=?, date=?, declaration_type=?, notes=?
               WHERE number=?""",
            (
                declaration.taxpayer, declaration.amount, declaration.status.value,
                declaration.date, declaration.declaration_type.value,
                declaration.notes, declaration.number,
            ),
        )
        conn.commit()

    def delete(self, number: str) -> None:
        conn = self._db.connect()
        conn.execute("DELETE FROM declarations WHERE number = ?", (number,))
        conn.commit()

    def count_by_status(self) -> dict:
        conn = self._db.connect()
        rows = conn.execute(
            "SELECT status, COUNT(*) as n FROM declarations GROUP BY status"
        ).fetchall()
        return {r["status"]: r["n"] for r in rows}

    def sum_amounts(self) -> float:
        conn = self._db.connect()
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM declarations WHERE status = 'Validated'"
        ).fetchone()
        return float(row["total"])

    def monthly_stats(self) -> list:
        conn = self._db.connect()
        rows = conn.execute(
            """SELECT strftime('%Y-%m', date) as month,
               COUNT(*) as total,
               SUM(CASE WHEN status='Validated' THEN 1 ELSE 0 END) as validated,
               SUM(amount) as revenue
               FROM declarations
               GROUP BY month
               ORDER BY month DESC
               LIMIT 6"""
        ).fetchall()
        return [dict(r) for r in reversed(rows)]