import pytest
from fastapi.testclient import TestClient

BASE = "/api/run"

# Seeded hurdle run
SEEDED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111"

# Seeded partial hurdle run
SEEDED_PARTIAL_RUN_ID = "22222222-2222-2222-2222-222222222222"

# A non-partial run
SEEDED_SPRINT_RUN_ID = "d0271452-4bec-4759-84ef-c62beaafdbf0"


# Hurdle Metrics


@pytest.mark.integration
class TestGetHurdleMetrics:
    """GET /api/run/athletes/{run_id}/metrics/hurdles"""

    def test_hurdle_metrics_returns_200(self, test_client: TestClient) -> None:
        """Requesting hurdle metrics for the seeded hurdle run should return 200
        with a non-empty list of hurdle rows."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_hurdle_metrics_row_has_expected_fields(
        self, test_client: TestClient
    ) -> None:
        """Each hurdle metrics row should contain the core HurdleMetricRow fields."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles"
        )

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
    """GET /api/run/athletes/{run_id}/metrics/hurdles/splits"""

    def test_hurdle_splits_returns_200(self, test_client: TestClient) -> None:
        """Requesting hurdle splits should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/splits"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_hurdle_splits_row_has_expected_fields(
        self, test_client: TestClient
    ) -> None:
        """Each row should contain hurdle_num and hurdle_split_ms."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/splits"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "hurdle_split_ms" in row


# Steps Between Hurdles


@pytest.mark.integration
class TestGetStepsBetweenHurdles:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/steps-between"""

    def test_steps_between_returns_200(self, test_client: TestClient) -> None:
        """Requesting steps between hurdles should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/steps-between"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_steps_between_row_has_expected_fields(
        self, test_client: TestClient
    ) -> None:
        """Each row should contain hurdle_num and steps_between_hurdles."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/steps-between"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "steps_between_hurdles" in row


# Takeoff GCT


@pytest.mark.integration
class TestGetTakeoffGct:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/takeoff-gct"""

    def test_takeoff_gct_returns_200(self, test_client: TestClient) -> None:
        """Requesting takeoff GCT should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/takeoff-gct"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_takeoff_gct_row_has_expected_fields(self, test_client: TestClient) -> None:
        """Each row should contain hurdle_num, takeoff_foot, and takeoff_gct_ms."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/takeoff-gct"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_foot" in row
        assert "takeoff_gct_ms" in row


# Landing GCT


@pytest.mark.integration
class TestGetLandingGct:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/landing-gct"""

    def test_landing_gct_returns_200(self, test_client: TestClient) -> None:
        """Requesting landing GCT should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/landing-gct"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_landing_gct_row_has_expected_fields(self, test_client: TestClient) -> None:
        """Each row should contain hurdle_num, landing_foot, and landing_gct_ms."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/landing-gct"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "landing_foot" in row
        assert "landing_gct_ms" in row


# Takeoff FT


@pytest.mark.integration
class TestGetTakeoffFt:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/takeoff-ft"""

    def test_takeoff_ft_returns_200(self, test_client: TestClient) -> None:
        """Requesting takeoff flight time should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/takeoff-ft"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_takeoff_ft_row_has_expected_fields(self, test_client: TestClient) -> None:
        """Each row should contain hurdle_num and takeoff_ft_ms."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/takeoff-ft"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_ft_ms" in row


# GCT Increase


@pytest.mark.integration
class TestGetGctIncrease:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/gct-increase"""

    def test_gct_increase_returns_200(self, test_client: TestClient) -> None:
        """Requesting GCT increase data should return 200 with data."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/gct-increase"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_gct_increase_row_has_expected_fields(
        self, test_client: TestClient
    ) -> None:
        """Each row should contain hurdle_num, takeoff_gct_ms, and
        gct_increase_hurdle_to_hurdle_pct."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_HURDLE_RUN_ID}/metrics/hurdles/gct-increase"
        )

        assert response.status_code == 200
        row = response.json()[0]
        assert "hurdle_num" in row
        assert "takeoff_gct_ms" in row
        assert "gct_increase_hurdle_to_hurdle_pct" in row


# Hurdle Projection


@pytest.mark.integration
class TestGetHurdleProjection:
    """GET /api/run/athletes/{run_id}/metrics/hurdles/projection"""

    def test_projection_returns_200(self, test_client: TestClient) -> None:
        """Requesting projection for the seeded partial run should return 200."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200

    def test_projection_has_expected_fields(self, test_client: TestClient) -> None:
        """The projection response should contain all HurdleProjectionResponse fields."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
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
        self, test_client: TestClient
    ) -> None:
        """completed_splits should be a non-empty list."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["completed_splits"], list)
        assert len(data["completed_splits"]) > 0

    def test_projection_projected_splits_are_list(
        self, test_client: TestClient
    ) -> None:
        """projected_splits should be a non-empty list."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["projected_splits"], list)
        assert len(data["projected_splits"]) > 0

    def test_projection_split_row_has_hurdle_num_and_split_ms(
        self, test_client: TestClient
    ) -> None:
        """Each split (completed or projected) should have hurdle_num and split_ms."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()

        for split in data["completed_splits"]:
            assert "hurdle_num" in split
            assert "split_ms" in split

        for split in data["projected_splits"]:
            assert "hurdle_num" in split
            assert "split_ms" in split

    def test_projection_target_event_matches(self, test_client: TestClient) -> None:
        """The target_event in the response should match the seeded run's target."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["target_event"] == "hurdles_110m"

    def test_projection_total_hurdles_is_ten(self, test_client: TestClient) -> None:
        """For a 110mH target, total_hurdles should be 10."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_hurdles"] == 10

    def test_projection_confidence_is_between_zero_and_one(
        self, test_client: TestClient
    ) -> None:
        """Confidence should be in [0, 1]."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_projection_total_ms_is_positive(self, test_client: TestClient) -> None:
        """The projected total time should be a positive number."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["projected_total_ms"] is not None
        assert data["projected_total_ms"] > 0

    def test_projection_final_segment_matches_110m_config(
        self, test_client: TestClient
    ) -> None:
        """The final segment should be 1400ms for a 110mH target."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_PARTIAL_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["projected_final_segment_ms"] == 1400

    def test_projection_non_partial_run_returns_error(
        self, test_client: TestClient
    ) -> None:
        """Requesting projection for a non-partial run should return an error."""
        response = test_client.get(
            f"{BASE}/athletes/{SEEDED_SPRINT_RUN_ID}/metrics/hurdles/projection"
        )

        assert response.status_code in (400, 422, 500)
