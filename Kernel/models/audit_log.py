from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AuditLog:
    id: Optional[int]
    username: str
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[str]
    created_at: datetime
