from Kernel.models.declaration import Declaration, DeclarationType, DeclarationStatus
from Kernel.models.audit_log import AuditAction


class DeclarationService:

    TYPE_MAP = {
        "TVA": DeclarationType.VAT,
        "IS": DeclarationType.CORPORATE_TAX,
        "IRPP": DeclarationType.INCOME_TAX,
        "RS": DeclarationType.WITHHOLDING_TAX,
        "vat": DeclarationType.VAT,
        "income_tax": DeclarationType.INCOME_TAX,
        "corporate_tax": DeclarationType.CORPORATE_TAX,
        "withholding_tax": DeclarationType.WITHHOLDING_TAX,
    }

    STATUS_MAP = {
        "draft": DeclarationStatus.DRAFT,
        "submitted": DeclarationStatus.SUBMITTED,
        "validated": DeclarationStatus.VALIDATED,
        "rejected": DeclarationStatus.REJECTED,
    }

    def __init__(self, repo, taxpayer_repo, audit_service):
        self._repo = repo
        self._tp_repo = taxpayer_repo
        self._audit = audit_service

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, data: dict, user_id=None):

        decl = Declaration(
            taxpayer_id=data["taxpayer_id"],
            declaration_type=self.TYPE_MAP.get(
                data.get("declaration_type"),
                DeclarationType.INCOME_TAX
            ),
            fiscal_year=data["fiscal_year"],
            period=data.get("period"),
            gross_amount=data.get("gross_amount", 0),
            tax_rate=data.get("tax_rate", 0),
            penalties=data.get("penalties", 0),
            status=self.STATUS_MAP.get(
                data.get("status", "draft"),
                DeclarationStatus.DRAFT
            ),
            notes=data.get("notes"),
        )

        decl.calculate_tax()
        saved = self._repo.create(decl)

        self._audit.log(
            AuditAction.CREATE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=saved.id,
            details=f"Created declaration {saved.id}"
        )

        return saved

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(self, decl_id: int, data: dict, user_id=None):

        decl = self._repo.find_by_id(decl_id)

        decl.taxpayer_id = data["taxpayer_id"]
        decl.declaration_type = self.TYPE_MAP.get(
            data.get("declaration_type"),
            decl.declaration_type
        )
        decl.fiscal_year = data["fiscal_year"]
        decl.period = data.get("period")
        decl.gross_amount = data.get("gross_amount", 0)
        decl.tax_rate = data.get("tax_rate", decl.tax_rate)
        decl.penalties = data.get("penalties", 0)
        decl.status = self.STATUS_MAP.get(
            data.get("status"),
            decl.status
        )
        decl.notes = data.get("notes")

        decl.calculate_tax()
        updated = self._repo.update(decl)

        self._audit.log(
            AuditAction.UPDATE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=updated.id,
            details=f"Updated declaration {updated.id}"
        )

        return updated

    # -----------------------------
    # DELETE
    # -----------------------------
    def delete(self, decl_id, user_id=None):
        self._repo.delete(decl_id)

        self._audit.log(
            AuditAction.DELETE_DECLARATION,
            user_id=user_id,
            entity_type="declaration",
            entity_id=decl_id,
            details=f"Deleted declaration {decl_id}"
        )

    # -----------------------------
    # READ
    # -----------------------------
    def get_all(self):
        return self._repo.find_all()

    def get_by_id(self, decl_id):
        return self._repo.find_by_id(decl_id)

    def search(self, q):
        return self._repo.search(q)

    # -----------------------------
    # WORKFLOW
    # -----------------------------
    def submit(self, decl_id, user_id=None):
        d = self._repo.find_by_id(decl_id)
        d.status = DeclarationStatus.SUBMITTED
        return self._repo.update(d)

    def validate_declaration(self, decl_id, user_id=None):
        d = self._repo.find_by_id(decl_id)
        d.status = DeclarationStatus.VALIDATED
        return self._repo.update(d)

    def reject_declaration(self, decl_id, reason, user_id=None):
        d = self._repo.find_by_id(decl_id)
        d.status = DeclarationStatus.REJECTED
        d.notes = reason
        return self._repo.update(d)

    # -----------------------------
    # STATS
    # -----------------------------
    def get_stats(self):
        return {
            "total": self._repo.count_total(),
            **self._repo.count_by_status(),
            "total_amount_due": self._repo.total_amount_due()
        }

    def get_recent(self, n=5):
        return self._repo.find_all()[:n]