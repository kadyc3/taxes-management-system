from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"

    @classmethod
    def from_str(cls, role_str: str) -> "UserRole":
        try:
            return cls(role_str.lower())
        except ValueError:
            return cls.USER

@dataclass
class User:
    id: int
    username: str
    role: UserRole
    created_at: datetime
