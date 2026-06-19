from Kernel.models.declaration import Declaration


class DeclarationService:
    def __init__(self, repo, taxpayer_repo, audit_service):
        self._repo = repo
        self._tp_repo = taxpayer_repo
        self._audit = audit_service

    def create(self, data: dict, user_id=None):
        decl = Declaration(
            id=None,
            taxpayer_id=data["taxpayer_id"],
            taxpayer_name=None,
            tax_type=data["tax_type"],
            fiscal_year=data["fiscal_year"],
            fiscal_period=data["fiscal_period"],
            gross_amount=data["gross_amount"],
            deductions=data.get("deductions", 0),
            penalties=data.get("penalties", 0),
            total_due=0,
            status=data.get("status", "draft"),
            notes=data.get("notes"),
            created_at=None,
            updated_at=None,
        )

        saved = self._repo.create(decl)

        self._audit.log(
            "CREATE_DECLARATION",
            user_id=user_id,
            entity_type="declaration",
            entity_id=saved.id,
            details=f"Created declaration {saved.id}"
        )

        return saved

    def update(self, decl_id, data: dict):
        decl = self._repo.find_by_id(decl_id)
        if not decl:
            raise Exception("Declaration not found")

        for k, v in data.items():
            setattr(decl, k, v)

        return self._repo.update(decl)

    def delete(self, decl_id):
        self._repo.delete(decl_id)

    def get_all(self):
        return self._repo.find_all()

    def get_by_id(self, decl_id):
        return self._repo.find_by_id(decl_id)

    def search(self, q):
        return self._repo.search(q)

    def submit(self, decl_id):
        d = self._repo.find_by_id(decl_id)
        d.status = "submitted"
        return self._repo.update(d)

    def validate_declaration(self, decl_id):
        d = self._repo.find_by_id(decl_id)
        d.status = "validated"
        return self._repo.update(d)

    def reject_declaration(self, decl_id, reason):
        d = self._repo.find_by_id(decl_id)
        d.status = "rejected"
        d.notes = reason
        return self._repo.update(d)

    def get_stats(self):
        return {
            "total": self._repo.count_total(),
            **self._repo.count_by_status(),
            "total_amount_due": self._repo.total_amount_due()
        }

    def get_recent(self, n=5):
        return self._repo.find_all()[:n]