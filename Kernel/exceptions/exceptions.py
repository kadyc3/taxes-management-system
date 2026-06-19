"""Domain exceptions for the Taxes Management System."""


class TaxSystemError(Exception):
    """Base exception."""


class ValidationError(TaxSystemError):
    """Raised when input data fails validation."""


class NotFoundError(TaxSystemError):
    """Raised when a requested entity does not exist."""


class DuplicateError(TaxSystemError):
    """Raised when a unique constraint is violated."""


class AuthenticationError(TaxSystemError):
    """Raised on authentication failure."""


class PermissionError(TaxSystemError):
    """Raised when the user lacks permission."""