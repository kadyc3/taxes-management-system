"""Repository for declaration persistence."""
from datetime import datetime
from typing import List, Optional

from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.declaration import Declaration, DeclarationStatus, DeclarationType


class DeclarationRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    def _row_to_declaration(self, row) -> Declaration:
        d = dict(row)

        def _dt(val):
            return datetime.fromisoformat(val) if val else None

        return Declaration(
            id=d["id"],
            taxpayer_id=d["taxpayer_id"],
            declaration_type=DeclarationType(d.get("declaration_type", "income_tax")),
            fiscal_year=d["fiscal_year"],
            period=d.get("period"),
            gross_amount=float(d.get("gross_amount", 0)),
            tax_rate=float(d.get("tax_rate", 0)),
            tax_amount=float(d.get("tax_amount", 0)),
            penalties=float(d.get("penalties", 0)),
            total_due=float(d.get("total_due", 0)),
            status=DeclarationStatus(d.get("status", "draft")),
            notes=d.get("notes"),
            submitted_at=_dt(d.get("submitted_at")),
            validated_at=_dt(d.get("validated_at")),
            created_at=_dt(d.get("created_at")),
            updated_at=_dt(d.get("updated_at")),
            taxpayer_name=d.get("taxpayer_name"),
        )

    def create(self, declaration: Declaration) -> Declaration:
        now = datetime.now().isoformat()
        conn = self._db.get_connection()
        cur = conn.execute(
            """INSERT INTO declarations
               (taxpayer_id, declaration_type, fiscal_year, period,
                gross_amount, tax_rate, tax_amount, penalties, total_due,
                status, notes, submitted_at, validated_at, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                declaration.taxpayer_id,
                declaration.declaration_type.value,
                declaration.fiscal_year,
                declaration.period,
                declaration.gross_amount,
                declaration.tax_rate,
                declaration.tax_amount,
                declaration.penalties,
                declaration.total_due,
                declaration.status.value,
                declaration.notes,
                declaration.submitted_at.isoformat() if declaration.submitted_at else None,
                declaration.validated_at.isoformat() if declaration.validated_at else None,
                now,
                now,
            ),
        )
        conn.commit()
        declaration.id = cur.lastrowid
        declaration.created_at = datetime.fromisoformat(now)
        declaration.updated_at = declaration.created_at
        return declaration

    def update(self, declaration: Declaration) -> Declaration:
        now = datetime.now().isoformat()
        conn = self._db.get_connection()
        conn.execute(
            """UPDATE declarations SET
               taxpayer_id=?, declaration_type=?, fiscal_year=?, period=?,
               gross_amount=?, tax_rate=?, tax_amount=?, penalties=?, total_due=?,
               status=?, notes=?, submitted_at=?, validated_at=?, updated_at=?
               WHERE id=?""",
            (
                declaration.taxpayer_id,
                declaration.declaration_type.value,
                declaration.fiscal_year,
                declaration.period,
                declaration.gross_amount,
                declaration.tax_rate,
                declaration.tax_amount,
                declaration.penalties,
                declaration.total_due,
                declaration.status.value,
                declaration.notes,
                declaration.submitted_at.isoformat() if declaration.submitted_at else None,
                declaration.validated_at.isoformat() if declaration.validated_at else None,
                now,
                declaration.id,
            ),
        )
        conn.commit()
        declaration.updated_at = datetime.fromisoformat(now)
        return declaration

    def delete(self, declaration_id: int) -> bool:
        conn = self._db.get_connection()
        cur = conn.execute("DELETE FROM declarations WHERE id=?", (declaration_id,))
        conn.commit()
        return cur.rowcount > 0

    def find_by_id(self, declaration_id: int) -> Optional[Declaration]:
        conn = self._db.get_connection()
        row = conn.execute(
            """SELECT d.*, t.name as taxpayer_name FROM declarations d
               LEFT JOIN taxpayers t ON t.id = d.taxpayer_id
               WHERE d.id=?""",
            (declaration_id,),
        ).fetchone()
        return self._row_to_declaration(row) if row else None

    def find_all(self) -> List[Declaration]:
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT d.*, t.name as taxpayer_name FROM declarations d
               LEFT JOIN taxpayers t ON t.id = d.taxpayer_id
               ORDER BY d.created_at DESC"""
        ).fetchall()
        return [self._row_to_declaration(r) for r in rows]

    def find_by_taxpayer(self, taxpayer_id: int) -> List[Declaration]:
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT d.*, t.name as taxpayer_name FROM declarations d
               LEFT JOIN taxpayers t ON t.id = d.taxpayer_id
               WHERE d.taxpayer_id=? ORDER BY d.fiscal_year DESC""",
            (taxpayer_id,),
        ).fetchall()
        return [self._row_to_declaration(r) for r in rows]

    def search(self, query: str) -> List[Declaration]:
        like = f"%{query}%"
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT d.*, t.name as taxpayer_name FROM declarations d
               LEFT JOIN taxpayers t ON t.id = d.taxpayer_id
               WHERE t.name LIKE ? OR t.tax_id LIKE ?
                  OR CAST(d.fiscal_year AS TEXT) LIKE ?
                  OR d.declaration_type LIKE ?
               ORDER BY d.created_at DESC""",
            (like, like, like, like),
        ).fetchall()
        return [self._row_to_declaration(r) for r in rows]

    def count_by_status(self) -> dict:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM declarations GROUP BY status"
        ).fetchall()
        result = {s.value: 0 for s in DeclarationStatus}
        for r in rows:
            result[r["status"]] = r["cnt"]
        return result

    def total_amount_due(self) -> float:
        conn = self._db.get_connection()
        row = conn.execute(
            "SELECT COALESCE(SUM(total_due),0) FROM declarations WHERE status != 'rejected'"
        ).fetchone()
        return float(row[0])

    def recent(self, limit: int = 10) -> List[Declaration]:
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT d.*, t.name as taxpayer_name FROM declarations d
               LEFT JOIN taxpayers t ON t.id = d.taxpayer_id
               ORDER BY d.created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [self._row_to_declaration(r) for r in rows]