from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    VIEWER = "viewer"