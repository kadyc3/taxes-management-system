import hashlib
from typing import Optional
from Kernel.models.user import User

class AuthService:
    def __init__(self, user_repository):
        # We inject the repository — Kernel never imports Infrastructure
        self.user_repository = user_repository

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Returns the User object if credentials are valid.
        Returns None if login fails.
        """
        user = self.user_repository.find_by_username(username)

        if user is None:
            return None  # Username not found

        if not user.is_active:
            return None  # Account disabled

        if not self._verify_password(password, username):
            return None  # Wrong password

        return user

    def _verify_password(self, password: str, username: str) -> bool:
        stored = self.user_repository.get_password_hash(username)
        return password == stored
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()