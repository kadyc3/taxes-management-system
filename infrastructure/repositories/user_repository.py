from typing import Optional
from Kernel.models.user import User
from Kernel.models.role import Role
from Infrastructure.database import get_connection

class UserRepository:

    def find_by_username(self, username: str) -> Optional[User]:
        """Finds a user by username. Returns User or None."""
        conn = get_connection()
        try:
            row = conn.execute("""
                SELECT u.id, u.username, u.full_name, u.is_active, r.name as role_name
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.username = ?
            """, (username,)).fetchone()

            if row is None:
                return None

            return User(
                id=row["id"],
                username=row["username"],
                full_name=row["full_name"],
                role=Role(row["role_name"]),
                is_active=bool(row["is_active"]),
            )
        finally:
            conn.close()

    def get_password_hash(self, username: str) -> Optional[str]:
        """Returns the stored password hash for a username."""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()
            return row["password_hash"] if row else None
        finally:
            conn.close()