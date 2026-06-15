from dataclasses import dataclass
from kernell.models.role import Role

@dataclass
class User:
    id: int
    username: str
    full_name: str
    role: Role
    is_active: bool

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_agent(self):
        return self.role == Role.AGENT

    def is_viewer(self):
        return self.role == Role.VIEWER