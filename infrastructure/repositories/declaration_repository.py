from Kernel.models.declaration import Declaration
class DeclarationRepository:
    def __init__(self, db):
        self._db = db

    def _row(self, r):
        return Declaration(
            id=r["id"],
            taxpayer_id=r["taxpayer_id"],
            taxpayer_name=r["name"] if "name" in r.keys() else None,
            tax_type=r["declaration_type"],
            fiscal_year=r["fiscal_year"],
            fiscal_period=r["period"],
            gross_amount=r["gross_amount"],
            deductions=r.get("deductions", 0),
            penalties=r["penalties"],
            total_due=r["total_due"],
            status=r["status"],
            notes=r["notes"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    def create(self, d: Declaration):
        conn = self._db.get_connection()

        tax = (d.gross_amount - d.deductions) + d.penalties

        cur = conn.execute("""
            INSERT INTO declarations (
                taxpayer_id, declaration_type, fiscal_year, period,
                gross_amount, tax_rate, tax_amount,
                penalties, total_due, status, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d.taxpayer_id,
            d.tax_type,
            d.fiscal_year,
            d.fiscal_period,
            d.gross_amount,
            0,
            tax,
            d.penalties,
            tax,
            d.status,
            d.notes
        ))

        conn.commit()
        d.id = cur.lastrowid
        d.total_due = tax
        return d

    def update(self, d: Declaration):
        conn = self._db.get_connection()

        tax = (d.gross_amount - d.deductions) + d.penalties

        conn.execute("""
            UPDATE declarations SET
                taxpayer_id=?,
                declaration_type=?,
                fiscal_year=?,
                period=?,
                gross_amount=?,
                penalties=?,
                total_due=?,
                status=?,
                notes=?,
                updated_at=datetime('now')
            WHERE id=?
        """, (
            d.taxpayer_id,
            d.tax_type,
            d.fiscal_year,
            d.fiscal_period,
            d.gross_amount,
            d.penalties,
            tax,
            d.status,
            d.notes,
            d.id
        ))

        conn.commit()
        d.total_due = tax
        return d

    def delete(self, decl_id):
        conn = self._db.get_connection()
        conn.execute("DELETE FROM declarations WHERE id=?", (decl_id,))
        conn.commit()

    def find_all(self):
        conn = self._db.get_connection()
        rows = conn.execute("""
            SELECT d.*, t.name
            FROM declarations d
            JOIN taxpayers t ON t.id = d.taxpayer_id
            ORDER BY d.id DESC
        """).fetchall()

        return [self._row(r) for r in rows]

    def find_by_id(self, decl_id):
        conn = self._db.get_connection()
        row = conn.execute("""
            SELECT d.*, t.name
            FROM declarations d
            JOIN taxpayers t ON t.id = d.taxpayer_id
            WHERE d.id=?
        """, (decl_id,)).fetchone()

        return self._row(row) if row else None

    def search(self, q: str):
        like = f"%{q}%"
        conn = self._db.get_connection()

        rows = conn.execute("""
            SELECT d.*, t.name
            FROM declarations d
            JOIN taxpayers t ON t.id = d.taxpayer_id
            WHERE t.name LIKE ? OR d.declaration_type LIKE ? OR d.period LIKE ?
            ORDER BY d.id DESC
        """, (like, like, like)).fetchall()

        return [self._row(r) for r in rows]

    def count_total(self):
        conn = self._db.get_connection()
        return conn.execute("SELECT COUNT(*) FROM declarations").fetchone()[0]

    def count_by_status(self):
        conn = self._db.get_connection()
        rows = conn.execute("""
            SELECT status, COUNT(*) as c
            FROM declarations
            GROUP BY status
        """).fetchall()

        result = {"draft": 0, "submitted": 0, "validated": 0, "rejected": 0}
        for r in rows:
            result[r["status"]] = r["c"]
        return result

    def total_amount_due(self):
        conn = self._db.get_connection()
        row = conn.execute("SELECT SUM(total_due) FROM declarations").fetchone()
        return row[0] or 0