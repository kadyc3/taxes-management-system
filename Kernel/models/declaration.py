from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class DeclarationStatus(Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    VALIDATED = "Validated"
    REJECTED = "Rejected"

    @classmethod
    def from_str(cls, value: str) -> "DeclarationStatus":
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.DRAFT

@dataclass
class Declaration:
    id: Optional[int]
    taxpayer_id: int
    reference_number: str
    declaration_type: str
    fiscal_year: int
    period: str
    gross_amount: float
    deductions: float
    penalties: float
    total_due: float
    status: DeclarationStatus
    filed_date: datetime
    rejection_reason: Optional[str] = None
    taxpayer_name: Optional[str] = None  # Helper for display in UI tables
