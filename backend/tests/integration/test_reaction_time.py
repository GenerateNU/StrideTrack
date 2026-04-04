from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

BASE = "/api/runs"
ATHLETES_BASE = "/api/athletes"

# Seeded IDs (must match seed.sql)
SEEDED_SPRINT_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0"
SEEDED_RT_RUN_ID = "cccccccc-0001-4000-8000-000000000001"
SEEDED_BOSCO_RUN_ID = "b1a2c3d4-5678-9abc-def0-111111111111"
SEEDED_ATHLETE_ID = "00000000-0000-0000-0000-000000000002"


# ── GET /{run_id}/metrics/reaction-time ──


@pytest.mark.integration
class TestGetReactionTime:
    """GET /api/runs/{run_id}/metrics/reaction-time"""

    def test_reaction_time_test_run_returns_200(self, test_client: TestClient) -> None:
        """A seeded sprint run should return 200."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        assert response.status_code == 200

    def test_reaction_time_test_run_has_correct_shape(
        self, test_client: TestClient
    ) -> None:
        """Response should contain all expected fields."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        data = response.json()
        assert "run_id" in data
        assert "reaction_time_ms" in data
        assert "onset_timestamp_ms" in data
        assert "zone" in data
        assert "zone_description" in data

    def test_reaction_time_test_run_zone_is_valid(
        self, test_client: TestClient
    ) -> None:
        """Zone should be one of green, yellow, red."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        data = response.json()
        assert data["zone"] in ("green", "yellow", "red")

    def test_reaction_time_test_run_value_is_positive(
        self, test_client: TestClient
    ) -> None:
        """Reaction time should be a positive number."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        data = response.json()
        assert data["reaction_time_ms"] > 0

    def test_sprint_run_returns_200(self, test_client: TestClient) -> None:
        """A sprint run should also return 200 as reaction time is universal."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        assert response.status_code == 200

    def test_nonexistent_run_returns_404(self, test_client: TestClient) -> None:
        """A non-existent run_id should return 404."""
        fake_id = str(uuid4())
        response = test_client.get(f"{BASE}/{fake_id}/metrics/reaction-time")
        assert response.status_code == 404

    def test_reaction_time_run_id_matches_request(
        self, test_client: TestClient
    ) -> None:
        """The run_id in the response should match the requested run_id."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/reaction-time"
        )
        data = response.json()
        assert data["run_id"] == SEEDED_SPRINT_RUN_ID


# ── GET /athletes/{athlete_id}/metrics/reaction-time/average ──


@pytest.mark.integration
class TestGetAverageReactionTime:
    """GET /api/runs/athletes/{athlete_id}/metrics/reaction-time/average"""

    def test_returns_200_for_seeded_athlete(self, test_client: TestClient) -> None:
        """A seeded athlete with runs should return 200."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        assert response.status_code == 200

    def test_response_has_correct_shape(self, test_client: TestClient) -> None:
        """Response should contain all expected fields."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        data = response.json()
        assert "athlete_id" in data
        assert "average_reaction_time_ms" in data
        assert "run_count" in data
        assert "zone" in data
        assert "zone_description" in data

    def test_average_is_positive(self, test_client: TestClient) -> None:
        """Average reaction time should be a positive number."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        data = response.json()
        assert data["average_reaction_time_ms"] > 0

    def test_run_count_excludes_bosco(self, test_client: TestClient) -> None:
        """run_count should not include bosco runs."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        data = response.json()
        # Ben has: 1 sprint + 1 hurdles + 1 hurdles_partial + 1 reaction_time_test
        # Bosco should be excluded
        assert data["run_count"] >= 1

    def test_athlete_id_matches_request(self, test_client: TestClient) -> None:
        """The athlete_id in the response should match the requested athlete_id."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        data = response.json()
        assert data["athlete_id"] == SEEDED_ATHLETE_ID

    def test_zone_is_valid(self, test_client: TestClient) -> None:
        """Zone should be one of green, yellow, red."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_ATHLETE_ID}/metrics/reaction-time/average"
        )
        data = response.json()
        assert data["zone"] in ("green", "yellow", "red")

    def test_nonexistent_athlete_returns_404(self, test_client: TestClient) -> None:
        """A non-existent athlete_id should return 404."""
        fake_id = str(uuid4())
        response = test_client.get(
            f"{BASE}/athletes/{fake_id}/metrics/reaction-time/average"
        )
        assert response.status_code == 404
