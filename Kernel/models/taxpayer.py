"""Taxpayer domain model."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaxpayerStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEREGISTERED = "deregistered"


class TaxpayerType(Enum):
    PHYSICAL = "physical"
    LEGAL = "legal"


@dataclass
class Taxpayer:
    id: Optional[int] = None
    tax_id: str = ""
    name: str = ""
    taxpayer_type: TaxpayerType = TaxpayerType.PHYSICAL
    status: TaxpayerStatus = TaxpayerStatus.ACTIVE
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_active(self) -> bool:
        return self.status == TaxpayerStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tax_id": self.tax_id,
            "name": self.name,
            "taxpayer_type": self.taxpayer_type.value,
            "status": self.status.value,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Taxpayer":
        return cls(
            id=data.get("id"),
            tax_id=data.get("tax_id", ""),
            name=data.get("name", ""),
            taxpayer_type=TaxpayerType(data.get("taxpayer_type", "individual")),
            status=TaxpayerStatus(data.get("status", "active")),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )