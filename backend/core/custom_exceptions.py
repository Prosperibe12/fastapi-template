from typing import Any

class ServiceError(Exception):
    """Custom exception for service errors with additional context."""
    def __init__(self, message: str, **context: Any):
        super().__init__(message)
        self.context = context

class UserAlreadyExists(Exception):
    """Exception raised when a user already exists in the system."""
    pass

class InvalidUserCredentials(Exception):
    """Exception raised when invalid user credentials are provided."""
    pass

class URLTokenError(Exception):
    """Exception raised when a refresh token is required for an operation."""
    pass

class InvalidTokenError(Exception):
    """Exception raised when a user does not have sufficient permissions."""
    pass

class BlacklistedTokenError(Exception):
    """Exception raised when a token is blacklisted."""
    pass