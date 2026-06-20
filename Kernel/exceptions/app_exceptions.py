class AppError(Exception):
    """
    Base application exception.
    Used for business-rule and validation errors.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass


class AuthorizationError(AppError):
    pass