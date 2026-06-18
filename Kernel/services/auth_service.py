from Kernel.models.user import User
from Kernel.models.role import Role


class AuthService:
    """
    Handles authentication and stores the current session user.
    """

    def __init__(self, user_repository):
        self.user_repository = user_repository
        self.current_user = None

    def login(self, username, password):
        """
        Authenticate user and set current_user if successful.
        """

        user_data = self.user_repository.find_by_credentials(
            username,
            password
        )

        # If credentials are wrong
        if user_data is None:
            self.current_user = None
            return None

        # Build User object from DB result
        user = User(
            user_id=user_data[0],
            username=user_data[1],
            role=Role(user_data[2].upper())
        )

        # Store session user (IMPORTANT FIX)
        self.current_user = user

        return user

    def logout(self):
        """
        Clear current session.
        """
        self.current_user = None

    def is_authenticated(self):
        """
        Check if a user is logged in.
        """
        return self.current_user is not None