class CoachFactory:
    """Factory for creating coach test data.

    coaches table: coach_id (auto), profile_id (nullable FK → profiles), created_at (auto)
    Insert with {} — all columns are auto-generated or nullable.
    """

    @staticmethod
    def create() -> dict:
        return {}
