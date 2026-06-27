from dataclasses import dataclass
from enum import Enum
from datetime import date


class DeclarationStatus(str, Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    VALIDATED = "Validated"
    REJECTED = "Rejected"


class DeclarationType(str, Enum):
    VAT = "VAT"
    INCOME_TAX = "Income Tax"
    CORPORATE = "Corporate"
    WITHHOLDING = "Withholding"


@dataclass
class Declaration:
    number: str
    taxpayer: str
    amount: float
    status: DeclarationStatus
    date: str
    declaration_type: DeclarationType
    notes: str = ""

    @staticmethod
    def empty() -> "Declaration":
        return Declaration(
            number="",
            taxpayer="",
            amount=0.0,
            status=DeclarationStatus.DRAFT,
            date=date.today().isoformat(),
            declaration_type=DeclarationType.VAT,
        )