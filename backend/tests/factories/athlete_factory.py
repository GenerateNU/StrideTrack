class AthleteFactory:
    """Factory for creating athlete test data."""

    @staticmethod
    def create(
        coach_id: str = "00000000-0000-0000-0000-000000000001",
        name: str = "Test Athlete",
        height_in: float | None = 72.0,
        weight_lbs: float | None = 180.0,
    ) -> dict:
        return {
            "coach_id": coach_id,
            "name": name,
            "height_in": height_in,
            "weight_lbs": weight_lbs,
        }

    @staticmethod
    def create_minimal(
        coach_id: str = "00000000-0000-0000-0000-000000000001",
        name: str = "Minimal Athlete",
    ) -> dict:
        return {
            "coach_id": coach_id,
            "name": name,
        }
