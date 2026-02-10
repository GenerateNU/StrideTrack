from typing import Any, Protocol


class Factory(Protocol):
    """Protocol defining the interface for test data factories."""

    def build(self) -> dict[str, Any]:  # noqa: ANN401
        """Return dict with all fields for API requests."""
        ...

    def build_without_optional(self) -> dict[str, Any]:  # noqa: ANN401
        """Return dict with only required fields."""
        ...

    @classmethod
    def create(cls, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with optional field overrides."""
        ...

    @classmethod
    def create_minimal(cls, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with only required fields + overrides."""
        ...
