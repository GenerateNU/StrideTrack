import pytest
from fastapi.testclient import TestClient

BASE = "/api/run"

# Seeded hurdle run
SEEDED_HURDLE_RUN_ID = "11111111-1111-1111-1111-111111111111"


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

    def test_hurdle_metrics_row_has_expected_fields(self, test_client: TestClient) -> None:
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

    def test_hurdle_splits_row_has_expected_fields(self, test_client: TestClient) -> None:
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

    def test_steps_between_row_has_expected_fields(self, test_client: TestClient) -> None:
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

    def test_gct_increase_row_has_expected_fields(self, test_client: TestClient) -> None:
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