from io import StringIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from supabase import Client

from app.schemas.coach_schemas import Coach
from app.utils.transform_run import transform_feet_to_stride_cycles
from tests.factories.athlete_factory import AthleteFactory
from tests.factories.csv_factory import CSVFactory

BASE = "/api/runs"
CSV_UPLOAD = "/api/athletes/{athlete_id}/csv/upload-run"
ATHLETE_BASE = "/api/athletes"

# Shared fixtures


@pytest.fixture
def hurdle_run_id(
    test_client: TestClient,
    test_coach: Coach,
    created_ids: dict,
) -> str:
    """Create a coach → athlete → 110m hurdle CSV upload and return the run_id."""
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Hurdle Test Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    csv_content = CSVFactory.create_hurdle_110m_csv_content()
    filename, file_obj, content_type = CSVFactory.create_csv_file(
        content=csv_content, filename="hurdle_test.csv"
    )
    upload_resp = test_client.post(
        CSV_UPLOAD.format(athlete_id=athlete_id),
        data={
            "event_type": "hurdles_110m",
            "name": "Test 110mH",
        },
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_resp.status_code == 201
    run_id = upload_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)
    return run_id


@pytest.fixture
def partial_hurdle_run_id(
    test_client: TestClient,
    test_coach: Coach,
    supabase_client: Client,
    created_ids: dict,
) -> str:
    """Create a partial hurdle run with metrics and return the run_id.

    Uses POST /api/runs to create the run record (with target_event and
    hurdles_completed to satisfy the DB constraint), then inserts stride
    metrics directly via supabase_client since the CSV upload endpoint
    cannot create hurdles_partial runs.
    """
    # Create athlete
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Partial Hurdle Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    # Create partial hurdle run via POST /api/runs
    run_resp = test_client.post(
        BASE,
        json={
            "athlete_id": athlete_id,
            "event_type": "hurdles_partial",
            "target_event": "hurdles_110m",
            "hurdles_completed": 5,
            "elapsed_ms": 7690,
        },
    )
    assert run_resp.status_code == 201
    run_id = run_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)

    # Transform the hurdle CSV into stride metrics
    csv_content = CSVFactory.create_hurdle_110m_csv_content()
    raw_df = pd.read_csv(StringIO(csv_content))
    metrics_df = transform_feet_to_stride_cycles(raw_df)
    metrics_df["run_id"] = run_id

    # Insert metrics directly via supabase_client
    rows = metrics_df.to_dict(orient="records")
    supabase_client.table("run_metrics").insert(rows).execute()

    return run_id


@pytest.fixture
def sprint_run_id(
    test_client: TestClient,
    test_coach: Coach,
    created_ids: dict,
) -> str:
    """Create a sprint run (non-hurdle) for negative-path tests."""
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Sprint Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    csv_content = CSVFactory.create_sprint_csv_content()
    filename, file_obj, content_type = CSVFactory.create_csv_file(
        content=csv_content, filename="sprint_test.csv"
    )
    upload_resp = test_client.post(
        CSV_UPLOAD.format(athlete_id=athlete_id),
        data={
            "event_type": "sprint_100m",
            "name": "Test Sprint",
        },
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_resp.status_code == 201
    run_id = upload_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)
    return run_id


# Hurdle Metrics


@pytest.mark.integration
class TestGetHurdleMetrics:
    """GET /api/runs/{run_id}/metrics/hurdles"""

    def test_hurdle_metrics_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting hurdle metrics should return 200 with a non-empty list."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_hurdle_metrics_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each hurdle metrics row should contain the core HurdleMetricRow fields."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles")

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "clearance_start_ms" in row
        assert "clearance_end_ms" in row
        assert "takeoff_ft_ms" in row
        assert "takeoff_foot" in row
        assert "landing_foot" in row


# Hurdle Splits


@pytest.mark.integration
class TestGetHurdleSplits:
    """GET /api/runs/{run_id}/metrics/hurdles/splits"""

    def test_hurdle_splits_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting hurdle splits should return 200 with data."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles/splits")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_hurdle_splits_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num and hurdle_split_ms."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles/splits")

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "hurdle_split_ms" in row


# Steps Between Hurdles


@pytest.mark.integration
class TestGetStepsBetweenHurdles:
    """GET /api/runs/{run_id}/metrics/hurdles/steps-between"""

    def test_steps_between_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting steps between hurdles should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/steps-between"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_steps_between_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num and steps_between_hurdles."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/steps-between"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "steps_between_hurdles" in row


# Takeoff GCT


@pytest.mark.integration
class TestGetTakeoffGct:
    """GET /api/runs/{run_id}/metrics/hurdles/takeoff-gct"""

    def test_takeoff_gct_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting takeoff GCT should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/takeoff-gct"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_takeoff_gct_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num, takeoff_foot, and takeoff_gct_ms."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/takeoff-gct"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_foot" in row
        assert "takeoff_gct_ms" in row


# Landing GCT


@pytest.mark.integration
class TestGetLandingGct:
    """GET /api/runs/{run_id}/metrics/hurdles/landing-gct"""

    def test_landing_gct_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting landing GCT should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/landing-gct"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_landing_gct_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num, landing_foot, and landing_gct_ms."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/landing-gct"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "landing_foot" in row
        assert "landing_gct_ms" in row


# Takeoff FT


@pytest.mark.integration
class TestGetTakeoffFt:
    """GET /api/runs/{run_id}/metrics/hurdles/takeoff-ft"""

    def test_takeoff_ft_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting takeoff flight time should return 200 with data."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles/takeoff-ft")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_takeoff_ft_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num and takeoff_ft_ms."""
        response = test_client.get(f"{BASE}/{hurdle_run_id}/metrics/hurdles/takeoff-ft")

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_ft_ms" in row


# GCT Increase


@pytest.mark.integration
class TestGetGctIncrease:
    """GET /api/runs/{run_id}/metrics/hurdles/gct-increase"""

    def test_gct_increase_returns_200(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Requesting GCT increase data should return 200 with data."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/gct-increase"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_gct_increase_row_has_expected_fields(
        self, test_client: TestClient, hurdle_run_id: str
    ) -> None:
        """Each row should contain hurdle_num, takeoff_gct_ms, and
        gct_increase_hurdle_to_hurdle_pct."""
        response = test_client.get(
            f"{BASE}/{hurdle_run_id}/metrics/hurdles/gct-increase"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_gct_ms" in row
        assert "gct_increase_hurdle_to_hurdle_pct" in row


# Hurdle Projection


@pytest.mark.integration
class TestGetHurdleProjection:
    """GET /api/runs/{run_id}/metrics/hurdles/projection

    The projection endpoint requires a hurdles_partial run with
    target_event stored on the run record.
    """

    def test_projection_returns_200(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """Requesting projection for a partial hurdle run should return 200."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200

    def test_projection_has_expected_fields(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """The projection response should contain all HurdleProjectionResponse fields."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert "completed_splits" in data
        assert "projected_splits" in data
        assert "projected_final_segment_ms" in data
        assert "projected_total_ms" in data
        assert "confidence" in data
        assert "target_event" in data
        assert "total_hurdles" in data

    def test_projection_completed_splits_are_list(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """completed_splits should be a non-empty list."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["completed_splits"], list)
        assert len(data["completed_splits"]) > 0

    def test_projection_projected_splits_are_list(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """projected_splits should be a non-empty list."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["projected_splits"], list)
        assert len(data["projected_splits"]) > 0

    def test_projection_split_row_has_hurdle_num_and_split_ms(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """Each split (completed or projected) should have hurdle_num and split_ms."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()

        for split in data["completed_splits"]:
            assert "hurdle_num" in split
            assert "split_ms" in split

        for split in data["projected_splits"]:
            assert "hurdle_num" in split
            assert "split_ms" in split

    def test_projection_target_event_matches(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """The target_event in the response should match what was set on the run."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["target_event"] == "hurdles_110m"

    def test_projection_total_hurdles_is_ten(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """For a 110mH target, total_hurdles should be 10."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_hurdles"] == 10

    def test_projection_confidence_is_between_zero_and_one(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """Confidence should be in [0, 1]."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_projection_total_ms_is_positive(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """The projected total time should be a positive number."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["projected_total_ms"] is not None
        assert data["projected_total_ms"] > 0

    def test_projection_final_segment_is_positive(
        self, test_client: TestClient, partial_hurdle_run_id: str
    ) -> None:
        """The final segment should be a positive pace-based estimate."""
        response = test_client.get(
            f"{BASE}/{partial_hurdle_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["projected_final_segment_ms"] is not None
        assert data["projected_final_segment_ms"] > 0

    def test_projection_non_partial_run_returns_error(
        self, test_client: TestClient, sprint_run_id: str
    ) -> None:
        """Requesting projection for a sprint run should return an error."""
        response = test_client.get(
            f"{BASE}/{sprint_run_id}/metrics/hurdles/projection",
        )

        assert response.status_code in (400, 422, 500)
