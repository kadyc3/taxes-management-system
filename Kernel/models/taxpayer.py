from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TaxpayerStatus(str, Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DEREGISTERED = "Deregistered"


class TaxpayerType(str, Enum):
    INDIVIDUAL = "Individual"
    COMPANY = "Company"
    SELF_EMPLOYED = "Self-employed"


@dataclass
class Taxpayer:
    id: str
    name: str
    email: str
    phone: str
    status: TaxpayerStatus
    taxpayer_type: TaxpayerType
    registration_date: str
    address: str = ""
    notes: str = ""

    @staticmethod
    def empty() -> "Taxpayer":
        return Taxpayer(
            id="",
            name="",
            email="",
            phone="",
            status=TaxpayerStatus.ACTIVE,
            taxpayer_type=TaxpayerType.INDIVIDUAL,
            registration_date=date.today().isoformat(),
        )