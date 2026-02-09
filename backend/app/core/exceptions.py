"""Custom exceptions for the application."""


class NotFoundException(Exception):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id {identifier} not found")

class InvalidTokenException(Exception):
    """Raised when an auth token is invalid."""
    def __init__(self, reason: str = "Invalid token"):
        self.reason = reason
        super().__init__(reason)

class ExpiredTokenException(Exception):
    """Raised when an auth token is expired."""
    def __init__(self, reason: str = "Token expired"):
        self.reason = reason
        super().__init__(reason)

class DevUserNotAllowedException(Exception):
    """Raised when dev-token is used outside development."""
    def __init__(self, reason: str = "Dev user not allowed"):
        self.reason = reason
        super().__init__(reason)

