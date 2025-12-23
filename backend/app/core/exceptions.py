"""Custom exceptions for the application."""


class NotFoundException(Exception):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id {identifier} not found")
