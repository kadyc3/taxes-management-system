from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class TaxpayerType(Enum):
    INDIVIDUAL = "Individual"
    COMPANY = "Company"

    @classmethod
    def from_str(cls, value: str) -> "TaxpayerType":
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.INDIVIDUAL

class TaxpayerStatus(Enum):
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    DEREGISTERED = "Deregistered"

    @classmethod
    def from_str(cls, value: str) -> "TaxpayerStatus":
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return cls.ACTIVE

@dataclass
class Taxpayer:
    id: Optional[int]
    nin: str
    full_name: str
    taxpayer_type: TaxpayerType
    status: TaxpayerStatus
    email: str
    phone: str
    address: str
    registration_date: datetime
