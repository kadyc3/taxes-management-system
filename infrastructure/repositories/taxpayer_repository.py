from typing import List, Optional
from Infrastructure.database.connection import DatabaseConnection
from Kernel.models.taxpayer import Taxpayer, TaxpayerStatus, TaxpayerType


class TaxpayerRepository:
    def __init__(self) -> None:
        self._db = DatabaseConnection.get_instance()

    def _row_to_taxpayer(self, row) -> Taxpayer:
        return Taxpayer(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row["phone"],
            status=TaxpayerStatus(row["status"]),
            taxpayer_type=TaxpayerType(row["taxpayer_type"]),
            registration_date=row["registration_date"],
            address=row["address"] or "",
            notes=row["notes"] or "",
        )

    def get_all(self) -> List[Taxpayer]:
        conn = self._db.connect()
        rows = conn.execute(
            "SELECT * FROM taxpayers ORDER BY registration_date DESC"
        ).fetchall()
        return [self._row_to_taxpayer(r) for r in rows]

    def get_by_id(self, taxpayer_id: str) -> Optional[Taxpayer]:
        conn = self._db.connect()
        row = conn.execute(
            "SELECT * FROM taxpayers WHERE id = ?", (taxpayer_id,)
        ).fetchone()
        return self._row_to_taxpayer(row) if row else None

    def search(
        self,
        query: str = "",
        status: Optional[str] = None,
        taxpayer_type: Optional[str] = None,
    ) -> List[Taxpayer]:
        conn = self._db.connect()
        sql = "SELECT * FROM taxpayers WHERE 1=1"
        params: list = []
        if query:
            sql += " AND (name LIKE ? OR email LIKE ? OR id LIKE ?)"
            like = f"%{query}%"
            params += [like, like, like]
        if status and status != "all":
            sql += " AND status = ?"
            params.append(status)
        if taxpayer_type and taxpayer_type != "all":
            sql += " AND taxpayer_type = ?"
            params.append(taxpayer_type)
        sql += " ORDER BY registration_date DESC"
        rows = conn.execute(sql, params).fetchall()
        return [self._row_to_taxpayer(r) for r in rows]

    def create(self, taxpayer: Taxpayer) -> None:
        conn = self._db.connect()
        conn.execute(
            """INSERT INTO taxpayers
               (id, name, email, phone, status, taxpayer_type, registration_date, address, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                taxpayer.id, taxpayer.name, taxpayer.email, taxpayer.phone,
                taxpayer.status.value, taxpayer.taxpayer_type.value,
                taxpayer.registration_date, taxpayer.address, taxpayer.notes,
            ),
        )
        conn.commit()

    def update(self, taxpayer: Taxpayer) -> None:
        conn = self._db.connect()
        conn.execute(
            """UPDATE taxpayers SET
               name=?, email=?, phone=?, status=?, taxpayer_type=?,
               registration_date=?, address=?, notes=?
               WHERE id=?""",
            (
                taxpayer.name, taxpayer.email, taxpayer.phone,
                taxpayer.status.value, taxpayer.taxpayer_type.value,
                taxpayer.registration_date, taxpayer.address, taxpayer.notes,
                taxpayer.id,
            ),
        )
        conn.commit()

    def delete(self, taxpayer_id: str) -> None:
        conn = self._db.connect()
        conn.execute("DELETE FROM taxpayers WHERE id = ?", (taxpayer_id,))
        conn.commit()

    def count_by_status(self) -> dict:
        conn = self._db.connect()
        rows = conn.execute(
            "SELECT status, COUNT(*) as n FROM taxpayers GROUP BY status"
        ).fetchall()
        return {r["status"]: r["n"] for r in rows}