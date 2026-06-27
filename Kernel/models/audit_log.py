from dataclasses import dataclass
from enum import Enum


class AuditSeverity(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


@dataclass
class AuditLog:
    id: str
    date: str
    user: str
    action: str
    entity: str
    description: str
    severity: AuditSeverity