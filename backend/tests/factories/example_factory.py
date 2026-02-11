from dataclasses import dataclass, field
from typing import Any

from faker import Faker

fake = Faker()


@dataclass
class ExampleFactory:
    """Factory for generating training run test data."""

    athlete_name: str = field(default_factory=fake.name)
    distance_meters: int = field(
        default_factory=lambda: fake.random_int(min=100, max=10000)
    )
    duration_seconds: float = field(
        default_factory=lambda: fake.pyfloat(min_value=10.0, max_value=3600.0)
    )
    avg_ground_contact_time_ms: float | None = field(
        default_factory=lambda: fake.pyfloat(min_value=100.0, max_value=300.0)
    )

    def build(self) -> dict[str, Any]:
        """Return dict with all fields for API requests."""
        return {
            "athlete_name": self.athlete_name,
            "distance_meters": self.distance_meters,
            "duration_seconds": self.duration_seconds,
            "avg_ground_contact_time_ms": self.avg_ground_contact_time_ms,
        }

    def build_without_optional(self) -> dict[str, Any]:
        """Return dict with only required fields."""
        return {
            "athlete_name": self.athlete_name,
            "distance_meters": self.distance_meters,
            "duration_seconds": self.duration_seconds,
        }

    @classmethod
    def create(cls, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with optional field overrides."""
        instance = cls(**{k: v for k, v in overrides.items() if v is not None})
        return instance.build()

    @classmethod
    def create_minimal(cls, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with only required fields + overrides."""
        instance = cls(**{k: v for k, v in overrides.items() if v is not None})
        return instance.build_without_optional()
