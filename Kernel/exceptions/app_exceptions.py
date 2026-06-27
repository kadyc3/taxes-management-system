class AppException(Exception):
    """Base exception class for the Taxes Management System."""
    pass

class ValidationError(AppException):
    """Raised when data validation fails."""
    pass

class AuthenticationError(AppException):
    """Raised when user login or authentication fails."""
    pass

class PermissionDeniedError(AppException):
    """Raised when a user attempts an action not allowed by their role."""
    pass

class NotFoundError(AppException):
    """Raised when a requested resource is not found."""
    pass
