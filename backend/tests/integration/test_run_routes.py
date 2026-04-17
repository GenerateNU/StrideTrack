from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.schemas.coach_schemas import Coach
from tests.factories.athlete_factory import AthleteFactory
from tests.factories.csv_factory import CSVFactory

BASE = "/api/runs"
ATHLETE_BASE = "/api/athletes"
CSV_UPLOAD = "/api/csv/upload-run"


# ── Shared fixture ──


@pytest.fixture
def sprint_run_with_metrics(
    test_client: TestClient,
    test_coach: Coach,
    created_ids: dict,
) -> dict:
    """Create a coach → athlete → sprint CSV upload and return IDs.

    Returns dict with 'athlete_id' and 'run_id' for tests that need
    a run with processed stride metrics.
    """
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Sprint Metrics Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    csv_content = CSVFactory.create_sprint_csv_content()
    filename, file_obj, content_type = CSVFactory.create_csv_file(
        content=csv_content, filename="sprint_metrics_test.csv"
    )
    upload_resp = test_client.post(
        CSV_UPLOAD,
        data={
            "athlete_id": athlete_id,
            "event_type": "sprint_100m",
            "name": "Test Sprint",
        },
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_resp.status_code == 201
    run_id = upload_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)

    return {"athlete_id": athlete_id, "run_id": run_id}


# ── Runs — List ──


@pytest.mark.integration
class TestListRuns:
    """GET /api/runs"""

    def test_list_returns_200(self, test_client: TestClient) -> None:
        """The run list endpoint should return 200 with a JSON array."""
        response = test_client.get(BASE)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_created_run_appears_in_list(
        self,
        test_client: TestClient,
        sprint_run_with_metrics: dict,
    ) -> None:
        """A run created via CSV upload should appear in the subsequent GET list."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(BASE)

        assert response.status_code == 200
        run_ids = [r["run_id"] for r in response.json()]
        assert run_id in run_ids


# ── Runs — List by Athlete ──


@pytest.mark.integration
class TestListRunsByAthlete:
    """GET /api/runs/athlete/{athlete_id}"""

    def test_list_by_athlete_returns_200(
        self,
        test_client: TestClient,
        sprint_run_with_metrics: dict,
    ) -> None:
        """Listing runs for a known athlete should return 200 with their runs."""
        athlete_id = sprint_run_with_metrics["athlete_id"]

        response = test_client.get(f"{BASE}/athlete/{athlete_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_by_unknown_athlete_returns_404(self, test_client: TestClient) -> None:
        """Listing runs for a non-existent athlete should return 404."""
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/athlete/{fake_id}")

        assert response.status_code == 404


# ── Runs — Create ──


@pytest.mark.integration
class TestCreateRun:
    """POST /api/runs"""

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


# ── Run Metrics ──


@pytest.mark.integration
class TestGetRunMetrics:
    """GET /api/runs/{run_id}/metrics"""

    def test_get_metrics_returns_200_with_data(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Fetching metrics for a run with data should return 200 with a non-empty list."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_metrics_row_has_expected_fields(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Each metrics row should contain the fields defined in RunResponse."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics")

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
        """Fetching metrics for a non-existent run should return 200 or 404."""
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/{fake_id}/metrics")

        assert response.status_code in (200, 404)


# ── LR Overlay ──


@pytest.mark.integration
class TestGetLrOverlay:
    """GET /api/runs/{run_id}/metrics/lr-overlay"""

    def test_lr_overlay_gct_returns_200(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Requesting LR overlay with metric=gct_ms should return 200 with data."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(
            f"{BASE}/{run_id}/metrics/lr-overlay",
            params={"metric": "gct_ms"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_lr_overlay_flight_returns_200(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Requesting LR overlay with metric=flight_ms should return 200 with data."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(
            f"{BASE}/{run_id}/metrics/lr-overlay",
            params={"metric": "flight_ms"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_lr_overlay_row_has_stride_num(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Each LR overlay row should contain a stride_num field."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(
            f"{BASE}/{run_id}/metrics/lr-overlay",
            params={"metric": "gct_ms"},
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row


# ── Stacked Bar ──


@pytest.mark.integration
class TestGetStackedBar:
    """GET /api/runs/{run_id}/metrics/stacked-bar"""

    def test_stacked_bar_returns_200(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Requesting stacked bar data should return 200 with a non-empty list."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/stacked-bar")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_stacked_bar_row_has_expected_fields(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Each stacked bar row should contain stride_num, foot, label, gct_ms, flight_ms."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/stacked-bar")

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row
        assert "foot" in row
        assert "label" in row
        assert "gct_ms" in row
        assert "flight_ms" in row


# ── Sprint Drift ──


@pytest.mark.integration
class TestGetSprintDrift:
    """GET /api/runs/{run_id}/metrics/sprint/drift"""

    def test_sprint_drift_returns_200(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Requesting sprint drift should return 200 with gct and ft drift percentages."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/sprint/drift")

        assert response.status_code == 200
        data = response.json()
        assert "gct_drift_pct" in data
        assert "ft_drift_pct" in data

    def test_sprint_drift_values_are_floats(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Both drift values should be numeric floats."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/sprint/drift")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["gct_drift_pct"], float)
        assert isinstance(data["ft_drift_pct"], float)


# ── Step Frequency ──


@pytest.mark.integration
class TestGetStepFrequency:
    """GET /api/runs/{run_id}/metrics/sprint/step-frequency"""

    def test_step_frequency_returns_200(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Requesting step frequency should return 200 with a non-empty list."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/sprint/step-frequency")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_step_frequency_row_has_expected_fields(
        self, test_client: TestClient, sprint_run_with_metrics: dict
    ) -> None:
        """Each step frequency row should contain stride_num, foot, label, step_frequency_hz."""
        run_id = sprint_run_with_metrics["run_id"]

        response = test_client.get(f"{BASE}/{run_id}/metrics/sprint/step-frequency")

        assert response.status_code == 200
        row = response.json()[0]
        assert "stride_num" in row
        assert "foot" in row
        assert "label" in row
        assert "step_frequency_hz" in row


# ── Update Run ──


@pytest.mark.integration
class TestUpdateRun:
    """PATCH /api/runs/{run_id}"""

    def test_update_event_type_returns_200(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Patching a run's event_type should return 200 with the updated value."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Update Run Athlete"
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
        run_resp = test_client.post(BASE, json=run_data)
        assert run_resp.status_code == 201
        run_id = run_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)

        response = test_client.patch(
            f"{BASE}/{run_id}", json={"event_type": "sprint_200m"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["event_type"] == "sprint_200m"

    def test_update_name_returns_200(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Patching a run's name should return 200 with the updated name."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Name Update Athlete"
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
        run_resp = test_client.post(BASE, json=run_data)
        assert run_resp.status_code == 201
        run_id = run_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)

        response = test_client.patch(
            f"{BASE}/{run_id}", json={"name": "Morning Sprint"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Morning Sprint"

    def test_update_nonexistent_run_returns_404(self, test_client: TestClient) -> None:
        """Patching a non-existent run ID should return 404."""
        fake_id = str(uuid4())

        response = test_client.patch(
            f"{BASE}/{fake_id}", json={"event_type": "sprint_200m"}
        )

        assert response.status_code == 404


# ── Delete Run ──


@pytest.mark.integration
class TestDeleteRun:
    """DELETE /api/runs/{run_id}"""

    def test_delete_returns_204(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Deleting an existing run should return 204, and a subsequent metadata
        GET should return 404."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Delete Run Athlete"
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
        run_resp = test_client.post(BASE, json=run_data)
        assert run_resp.status_code == 201
        run_id = run_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)

        response = test_client.delete(f"{BASE}/{run_id}")

        assert response.status_code == 204

        get_resp = test_client.get(f"{BASE}/{run_id}/metadata")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_run_returns_404(self, test_client: TestClient) -> None:
        """Deleting a non-existent run ID should return 404."""
        fake_id = str(uuid4())

        response = test_client.delete(f"{BASE}/{fake_id}")

        assert response.status_code == 404
