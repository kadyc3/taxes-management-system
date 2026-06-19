"""AuditLog domain model."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AuditAction(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE_TAXPAYER = "create_taxpayer"
    UPDATE_TAXPAYER = "update_taxpayer"
    DELETE_TAXPAYER = "delete_taxpayer"
    CREATE_DECLARATION = "create_declaration"
    UPDATE_DECLARATION = "update_declaration"
    DELETE_DECLARATION = "delete_declaration"


@dataclass
class AuditLog:
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: Optional[AuditAction] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action.value if self.action else None,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            action=AuditAction(data["action"]) if data.get("action") else None,
            entity_type=data.get("entity_type"),
            entity_id=data.get("entity_id"),
            details=data.get("details"),
            ip_address=data.get("ip_address"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )