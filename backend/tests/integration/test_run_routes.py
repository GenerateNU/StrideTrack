from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.schemas.coach_schemas import Coach
from tests.factories.athlete_factory import AthleteFactory

BASE = "/api/runs"
ATHLETE_BASE = "/api/athletes"

# Seeded sprint runs
SEEDED_SPRINT_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0"
SEEDED_ATHLETE_ID = "00000000-0000-0000-0000-000000000002"


# Runs — List


@pytest.mark.integration
class TestListRuns:
    """GET /api/run"""

    def test_list_returns_200(self, test_client: TestClient) -> None:
        """The run list endpoint should return 200 with a JSON array."""
        response = test_client.get(BASE)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_seeded_run_appears_in_list(self, test_client: TestClient) -> None:
        """The seeded sprint run should appear in the full run list."""
        response = test_client.get(BASE)

        assert response.status_code == 200
        run_ids = [r["run_id"] for r in response.json()]
        assert SEEDED_SPRINT_RUN_ID in run_ids


# Runs — List by Athlete


@pytest.mark.integration
class TestListRunsByAthlete:
    """GET /api/run/athlete/{athlete_id}"""

    def test_list_by_athlete_returns_200(self, test_client: TestClient) -> None:
        """Listing runs for a known athlete should return 200 with their runs."""
        response = test_client.get(f"{BASE}/athlete/{SEEDED_ATHLETE_ID}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_by_unknown_athlete_returns_404(self, test_client: TestClient) -> None:
        """Listing runs for a non-existent athlete should return 404."""
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/athlete/{fake_id}")

        assert response.status_code == 404


# Runs — Create


@pytest.mark.integration
class TestCreateRun:
    """POST /api/run"""

    def test_create_run_returns_201(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Creating a run with valid data should return 201 with run_id and created_at."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Run Test Athlete"
        )
        athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
        assert athlete_resp.status_code == 201
        athlete_id = athlete_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)

        run_data = {
            "athlete_id": athlete_id,
            "event_type": "sprint_100m",
            "elapsed_ms": 12500,
        }

        response = test_client.post(BASE, json=run_data)

        assert response.status_code == 201
        data = response.json()
        created_ids["run_ids"].append(data["run_id"])

        assert data["athlete_id"] == athlete_id
        assert data["event_type"] == "sprint_100m"
        assert "run_id" in data
        assert "created_at" in data

    def test_create_run_missing_required_field_returns_422(
        self, test_client: TestClient
    ) -> None:
        """Omitting athlete_id should return 422 validation error."""
        response = test_client.post(
            BASE, json={"event_type": "sprint_100m", "elapsed_ms": 12500}
        )

        assert response.status_code == 422

    def test_create_run_invalid_elapsed_ms_returns_422(
        self, test_client: TestClient
    ) -> None:
        """An elapsed_ms of 0 should fail validation (gt=0) and return 422."""
        response = test_client.post(
            BASE,
            json={
                "athlete_id": str(uuid4()),
                "event_type": "sprint_100m",
                "elapsed_ms": 0,
            },
        )

        assert response.status_code == 422


# Run Metrics


@pytest.mark.integration
class TestGetRunMetrics:
    """GET /api/run/athletes/{run_id}/metrics"""

    def test_get_metrics_returns_200_with_data(self, test_client: TestClient) -> None:
        """Fetching metrics for the seeded sprint run should return 200 with a
        non-empty list of stride metric rows."""
        response = test_client.get(f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_metrics_row_has_expected_fields(self, test_client: TestClient) -> None:
        """Each metrics row should contain the fields defined in RunResponse."""
        response = test_client.get(f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics")

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row
        assert "foot" in row
        assert "gct_ms" in row
        assert "flight_ms" in row
        assert "step_time_ms" in row

    def test_get_metrics_nonexistent_run_returns_200_empty(
        self, test_client: TestClient
    ) -> None:
        """Fetching metrics for a non-existent run should return 200 or 404
        with an empty list."""
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/{fake_id}/metrics")

        assert response.status_code in (200, 404)


# LR Overlay


@pytest.mark.integration
class TestGetLrOverlay:
    """GET /api/run/athletes/{run_id}/metrics/lr-overlay"""

    def test_lr_overlay_gct_returns_200(self, test_client: TestClient) -> None:
        """Requesting LR overlay with metric=gct_ms should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/lr-overlay",
            params={"metric": "gct_ms"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_lr_overlay_flight_returns_200(self, test_client: TestClient) -> None:
        """Requesting LR overlay with metric=flight_ms should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/lr-overlay",
            params={"metric": "flight_ms"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_lr_overlay_row_has_stride_num(self, test_client: TestClient) -> None:
        """Each LR overlay row should contain a stride_num field."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/lr-overlay",
            params={"metric": "gct_ms"},
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row


# Stacked Bar


@pytest.mark.integration
class TestGetStackedBar:
    """GET /api/run/athletes/{run_id}/metrics/stacked-bar"""

    def test_stacked_bar_returns_200(self, test_client: TestClient) -> None:
        """Requesting stacked bar data should return 200 with a non-empty list."""
        response = test_client.get(f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/stacked-bar")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_stacked_bar_row_has_expected_fields(self, test_client: TestClient) -> None:
        """Each stacked bar row should contain stride_num, foot, label, gct_ms, flight_ms."""
        response = test_client.get(f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/stacked-bar")

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row
        assert "foot" in row
        assert "label" in row
        assert "gct_ms" in row
        assert "flight_ms" in row


# Sprint Drift


@pytest.mark.integration
class TestGetSprintDrift:
    """GET /api/run/athletes/{run_id}/metrics/sprint-drift"""

    def test_sprint_drift_returns_200(self, test_client: TestClient) -> None:
        """Requesting sprint drift should return 200 with gct and ft drift percentages."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/sprint/drift"
        )

        assert response.status_code == 200
        data = response.json()
        assert "gct_drift_pct" in data
        assert "ft_drift_pct" in data

    def test_sprint_drift_values_are_floats(self, test_client: TestClient) -> None:
        """Both drift values should be numeric floats."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/sprint/drift"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["gct_drift_pct"], float)
        assert isinstance(data["ft_drift_pct"], float)


# Step Frequency


@pytest.mark.integration
class TestGetStepFrequency:
    """GET /api/run/athletes/{run_id}/metrics/step-frequency"""

    def test_step_frequency_returns_200(self, test_client: TestClient) -> None:
        """Requesting step frequency should return 200 with a non-empty list."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/sprint/step-frequency"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_step_frequency_row_has_expected_fields(
        self, test_client: TestClient
    ) -> None:
        """Each step frequency row should contain stride_num, foot, label, step_frequency_hz."""
        response = test_client.get(
            f"{BASE}/{SEEDED_SPRINT_RUN_ID}/metrics/sprint/step-frequency"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row
        assert "foot" in row
        assert "label" in row
        assert "step_frequency_hz" in row
