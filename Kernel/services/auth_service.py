import hashlib
from datetime import datetime
from typing import Optional
from ..models.user import User, UserRole
from ..exceptions.app_exceptions import AuthenticationError

class AuthService:
    def __init__(self, user_repo, audit_repo):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
        self.current_user: Optional[User] = None

    def login(self, username: str, password: str) -> User:
        user_dict = self.user_repo.get_by_username(username)
        if not user_dict:
            self.audit_repo.log(
                username, 
                "failed_login", 
                "user", 
                None, 
                f"Login failed: user '{username}' not found"
            )
            raise AuthenticationError("Invalid username or password.")

        salt_bytes = bytes.fromhex(user_dict["salt"])
        stored_hash = user_dict["password"]
        
        input_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt_bytes,
            100000
        ).hex()

        if input_hash != stored_hash:
            self.audit_repo.log(
                username, 
                "failed_login", 
                "user", 
                user_dict["id"], 
                f"Login failed: incorrect password for user '{username}'"
            )
            raise AuthenticationError("Invalid username or password.")

        role = UserRole.from_str(user_dict["role"])
        # Handle potential fractional seconds or simplified ISO format
        created_at_str = user_dict["created_at"]
        try:
            created_at_dt = datetime.fromisoformat(created_at_str)
        except ValueError:
            created_at_dt = datetime.now()

        self.current_user = User(
            id=user_dict["id"],
            username=user_dict["username"],
            role=role,
            created_at=created_at_dt
        )
        
        self.audit_repo.log(
            self.current_user.username, 
            "login", 
            "user", 
            self.current_user.id, 
            f"User logged in successfully (Role: {role.value})"
        )
        return self.current_user

    def logout(self):
        if self.current_user:
            username = self.current_user.username
            uid = self.current_user.id
            self.current_user = None
            self.audit_repo.log(
                username, 
                "logout", 
                "user", 
                uid, 
                "User logged out successfully"
            )

    def is_authenticated(self) -> bool:
        return self.current_user is not None

    def get_current_user(self) -> Optional[User]:
        return self.current_user
