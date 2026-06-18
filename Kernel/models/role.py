from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"
    VIEWER = "VIEWER"