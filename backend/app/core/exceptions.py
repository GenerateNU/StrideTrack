"""Custom exceptions for the application."""

from app.utils.split_score_constants import SUPPORTED_EVENTS


class NotFoundException(Exception):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str) -> None:
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id {identifier} not found")


class InvalidTokenException(Exception):
    """Raised when an auth token is invalid."""

    def __init__(self, reason: str = "Invalid token") -> None:
        self.reason = reason
        super().__init__(reason)


class ExpiredTokenException(Exception):
    """Raised when an auth token is expired."""

    def __init__(self, reason: str = "Token expired") -> None:
        self.reason = reason
        super().__init__(reason)


class DevUserNotAllowedException(Exception):
    """Raised when dev-token is used outside development."""

    def __init__(self, reason: str = "Dev user not allowed") -> None:
        self.reason = reason
        super().__init__(reason)


class NotACoachException(Exception):
    """Raised when a non-coach user tries to access coach-only resources."""

    def __init__(self, reason: str = "User is not a coach") -> None:
        self.reason = reason
        super().__init__(reason)


class UnsupportedEventError(Exception):
    """Raised when the run's event_type has no split score implementation."""

    def __init__(self, event_type: str) -> None:
        self.event_type = event_type
        supported = ", ".join(sorted(SUPPORTED_EVENTS))
        super().__init__(
            f"Split score analysis is not supported for event type '{event_type}'. "
            f"Supported events: {supported}."
        )
