"""Repository for taxpayer persistence."""
from datetime import datetime
from typing import List, Optional

from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.taxpayer import Taxpayer, TaxpayerStatus, TaxpayerType


class TaxpayerRepository:
    def __init__(self, db: DatabaseConnection):
        self._db = db

    @staticmethod
    def _safe_enum(enum_class, value, default):
        try:
            return enum_class(value)
        except Exception:
            return default
    # ------------------------------------------------------------------ helpers
    def _row_to_taxpayer(self, row) -> Taxpayer:
        d = dict(row)
        return Taxpayer(
            id=d["id"],
            tax_id=d["tax_id"],
            name=d["name"],
            taxpayer_type=self._safe_enum(
                TaxpayerType,
                d.get("taxpayer_type"),
                TaxpayerType.PHYSICAL
            ),
            status=self._safe_enum(
            TaxpayerStatus,
                d.get("status"),
                TaxpayerStatus.ACTIVE
            ),
            email=d.get("email"),
            phone=d.get("phone"),
            address=d.get("address"),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else None,
            updated_at=datetime.fromisoformat(d["updated_at"]) if d.get("updated_at") else None,
        )

    # ------------------------------------------------------------------ CRUD
    def create(self, taxpayer: Taxpayer) -> Taxpayer:
        now = datetime.now().isoformat()
        conn = self._db.get_connection()
        cur = conn.execute(
            """INSERT INTO taxpayers
               (tax_id, name, taxpayer_type, status, email, phone, address, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (
                taxpayer.tax_id,
                taxpayer.name,
                taxpayer.taxpayer_type.value,
                taxpayer.status.value,
                taxpayer.email,
                taxpayer.phone,
                taxpayer.address,
                now,
                now,
            ),
        )
        conn.commit()
        taxpayer.id = cur.lastrowid
        taxpayer.created_at = datetime.fromisoformat(now)
        taxpayer.updated_at = taxpayer.created_at
        return taxpayer

    def update(self, taxpayer: Taxpayer) -> Taxpayer:
        now = datetime.now().isoformat()
        conn = self._db.get_connection()
        conn.execute(
            """UPDATE taxpayers SET
               tax_id=?, name=?, taxpayer_type=?, status=?,
               email=?, phone=?, address=?, updated_at=?
               WHERE id=?""",
            (
                taxpayer.tax_id,
                taxpayer.name,
                taxpayer.taxpayer_type.value,
                taxpayer.status.value,
                taxpayer.email,
                taxpayer.phone,
                taxpayer.address,
                now,
                taxpayer.id,
            ),
        )
        conn.commit()
        taxpayer.updated_at = datetime.fromisoformat(now)
        return taxpayer

    def delete(self, taxpayer_id: int) -> bool:
        conn = self._db.get_connection()
        cur = conn.execute("DELETE FROM taxpayers WHERE id=?", (taxpayer_id,))
        conn.commit()
        return cur.rowcount > 0

    def find_by_id(self, taxpayer_id: int) -> Optional[Taxpayer]:
        conn = self._db.get_connection()
        row = conn.execute("SELECT * FROM taxpayers WHERE id=?", (taxpayer_id,)).fetchone()
        return self._row_to_taxpayer(row) if row else None

    def find_by_tax_id(self, tax_id: str) -> Optional[Taxpayer]:
        conn = self._db.get_connection()
        row = conn.execute("SELECT * FROM taxpayers WHERE tax_id=?", (tax_id,)).fetchone()
        return self._row_to_taxpayer(row) if row else None

    def find_all(self) -> List[Taxpayer]:
        conn = self._db.get_connection()
        rows = conn.execute("SELECT * FROM taxpayers ORDER BY name").fetchall()
        return [self._row_to_taxpayer(r) for r in rows]

    def search(self, query: str) -> List[Taxpayer]:
        like = f"%{query}%"
        conn = self._db.get_connection()
        rows = conn.execute(
            """SELECT * FROM taxpayers
               WHERE name LIKE ? OR tax_id LIKE ? OR email LIKE ?
               ORDER BY name""",
            (like, like, like),
        ).fetchall()
        return [self._row_to_taxpayer(r) for r in rows]

    def find_by_status(self, status: TaxpayerStatus) -> List[Taxpayer]:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT * FROM taxpayers WHERE status=? ORDER BY name", (status.value,)
        ).fetchall()
        return [self._row_to_taxpayer(r) for r in rows]

    # ------------------------------------------------------------------ stats
    def count_by_status(self) -> dict:
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM taxpayers GROUP BY status"
        ).fetchall()
        result = {s.value: 0 for s in TaxpayerStatus}
        for r in rows:
            result[r["status"]] = r["cnt"]
        return result

    def count_total(self) -> int:
        conn = self._db.get_connection()
        row = conn.execute("SELECT COUNT(*) FROM taxpayers").fetchone()
        return row[0]