"""Declaration domain model."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class DeclarationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    REJECTED = "rejected"


class DeclarationType(str, Enum):
    INCOME_TAX = "income_tax"
    VAT = "vat"
    CORPORATE_TAX = "corporate_tax"
    WITHHOLDING_TAX = "withholding_tax"


# Tax rates per declaration type
TAX_RATES = {
    DeclarationType.INCOME_TAX: 0.25,
    DeclarationType.VAT: 0.19,
    DeclarationType.CORPORATE_TAX: 0.15,
    DeclarationType.WITHHOLDING_TAX: 0.10,
}


@dataclass
class Declaration:
    id: Optional[int] = None
    taxpayer_id: Optional[int] = None
    declaration_type: DeclarationType = DeclarationType.INCOME_TAX
    fiscal_year: int = datetime.now().year
    period: Optional[str] = None          # e.g. "Q1", "Q2", "annual"
    gross_amount: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    penalties: float = 0.0
    total_due: float = 0.0
    status: DeclarationStatus = DeclarationStatus.DRAFT
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Joined field (not stored in declarations table)
    taxpayer_name: Optional[str] = None

    def calculate_tax(self) -> None:
        """Recalculate tax_amount and total_due from gross_amount and tax_rate."""
        if self.tax_rate == 0.0:
            self.tax_rate = TAX_RATES.get(self.declaration_type, 0.0)
        self.tax_amount = round(self.gross_amount * self.tax_rate, 3)
        self.total_due = round(self.tax_amount + self.penalties, 3)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "taxpayer_id": self.taxpayer_id,
            "declaration_type": self.declaration_type.value,
            "fiscal_year": self.fiscal_year,
            "period": self.period,
            "gross_amount": self.gross_amount,
            "tax_rate": self.tax_rate,
            "tax_amount": self.tax_amount,
            "penalties": self.penalties,
            "total_due": self.total_due,
            "status": self.status.value,
            "notes": self.notes,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Declaration":
        def _dt(val):
            return datetime.fromisoformat(val) if val else None

        return cls(
            id=data.get("id"),
            taxpayer_id=data.get("taxpayer_id"),
            declaration_type=DeclarationType(data.get("declaration_type", "income_tax")),
            fiscal_year=data.get("fiscal_year", datetime.now().year),
            period=data.get("period"),
            gross_amount=float(data.get("gross_amount", 0)),
            tax_rate=float(data.get("tax_rate", 0)),
            tax_amount=float(data.get("tax_amount", 0)),
            penalties=float(data.get("penalties", 0)),
            total_due=float(data.get("total_due", 0)),
            status=DeclarationStatus(data.get("status", "draft")),
            notes=data.get("notes"),
            submitted_at=_dt(data.get("submitted_at")),
            validated_at=_dt(data.get("validated_at")),
            created_at=_dt(data.get("created_at")),
            updated_at=_dt(data.get("updated_at")),
            taxpayer_name=data.get("taxpayer_name"),
        )