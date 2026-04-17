from dataclasses import dataclass, field
from typing import Any

from faker import Faker

fake = Faker()


@dataclass
class AthleteFactory:
    """Factory for generating athlete test data.

    NOTE: coach_id must reference an existing row in the coaches table.
    Always create a coach first and pass its ID here.

    athletes table: athlete_id (auto), coach_id (FK → coaches), name,
    height_in (nullable), weight_lbs (nullable), created_at (auto).
    """

    coach_id: str  # required — must reference an existing coaches row
    name: str = field(default_factory=fake.name)
    gender: str = field(default="male")
    height_in: float | None = field(
        default_factory=lambda: round(fake.pyfloat(min_value=60.0, max_value=84.0), 1)
    )
    weight_lbs: float | None = field(
        default_factory=lambda: round(fake.pyfloat(min_value=100.0, max_value=300.0), 1)
    )

    def build(self) -> dict[str, Any]:
        """Return dict with all fields for API requests."""
        return {
            "coach_id": self.coach_id,
            "name": self.name,
            "gender": self.gender,
            "height_in": self.height_in,
            "weight_lbs": self.weight_lbs,
        }

    def build_without_optional(self) -> dict[str, Any]:
        """Return dict with only required fields."""
        return {
            "coach_id": self.coach_id,
            "name": self.name,
            "gender": self.gender,
        }

    @classmethod
    def create(cls, coach_id: str, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with optional field overrides."""
        instance = cls(
            coach_id=coach_id,
            **{k: v for k, v in overrides.items() if v is not None},
        )
        return instance.build()

    @classmethod
    def create_minimal(cls, coach_id: str, **overrides: Any) -> dict[str, Any]:  # noqa: ANN401
        """Create a dict with only required fields + overrides."""
        instance = cls(
            coach_id=coach_id,
            **{k: v for k, v in overrides.items() if v is not None},
        )
        return instance.build_without_optional()
