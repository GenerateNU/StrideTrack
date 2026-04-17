from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.schemas.coach_schemas import Coach
from tests.factories.athlete_factory import AthleteFactory
from tests.factories.csv_factory import CSVFactory

ATHLETE_BASE = "/api/athletes"
CSV_UPLOAD = "/api/csv/upload-run"


def _url(run_id: str) -> str:
    return f"/api/runs/{run_id}/metrics/split-score"


# ── Shared fixtures ──


@pytest.fixture
def hurdle_400m_run_id(
    test_client: TestClient,
    test_coach: Coach,
    created_ids: dict,
) -> str:
    """Create a 400m hurdle run with stride metrics via CSV upload."""
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Split Score Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    csv_content = CSVFactory.create_hurdle_400m_csv_content()
    filename, file_obj, content_type = CSVFactory.create_csv_file(
        content=csv_content, filename="hurdle_400m_test.csv"
    )
    upload_resp = test_client.post(
        CSV_UPLOAD,
        data={
            "athlete_id": athlete_id,
            "event_type": "hurdles_400m",
            "name": "Test 400mH",
        },
        files={"file": (filename, file_obj, content_type)},
    )
    assert upload_resp.status_code == 201
    run_id = upload_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)
    return run_id


@pytest.fixture
def unsupported_event_run_id(
    test_client: TestClient,
    test_coach: Coach,
    created_ids: dict,
) -> str:
    """Create a run with an unsupported event type for split score."""
    athlete_data = AthleteFactory.create(
        coach_id=str(test_coach.coach_id), name="Unsupported Event Athlete"
    )
    athlete_resp = test_client.post(ATHLETE_BASE, json=athlete_data)
    assert athlete_resp.status_code == 201
    athlete_id = athlete_resp.json()["athlete_id"]
    created_ids["athlete_ids"].append(athlete_id)

    run_resp = test_client.post(
        "/api/runs",
        json={
            "athlete_id": athlete_id,
            "event_type": "long_jump",
            "elapsed_ms": 13500,
        },
    )
    assert run_resp.status_code in (200, 201)
    run_id = run_resp.json()["run_id"]
    created_ids["run_ids"].append(run_id)
    return run_id


# ── Missing Run ──


@pytest.mark.integration
class TestSplitScoreMissingRun:
    """GET with a run_id that does not exist in the DB."""

    def test_nonexistent_run_returns_404(self, test_client: TestClient) -> None:
        fake_id = str(uuid4())
        response = test_client.get(_url(fake_id))
        assert response.status_code == 404

    def test_404_response_has_detail(self, test_client: TestClient) -> None:
        fake_id = str(uuid4())
        response = test_client.get(_url(fake_id))
        assert "detail" in response.json()


# ── Unsupported Event ──


@pytest.mark.integration
class TestSplitScoreUnsupportedEvent:
    """GET for a run whose event_type is not supported by split score analysis."""

    def test_unsupported_event_returns_422(
        self, test_client: TestClient, unsupported_event_run_id: str
    ) -> None:
        response = test_client.get(_url(unsupported_event_run_id))
        assert response.status_code == 422

    def test_422_response_mentions_event_type(
        self, test_client: TestClient, unsupported_event_run_id: str
    ) -> None:
        response = test_client.get(_url(unsupported_event_run_id))
        data = response.json()
        assert "detail" in data
        assert "long_jump" in data["detail"]


# ── Real Run with Metrics ──


@pytest.mark.integration
class TestSplitScoreRealRun:
    """GET with a real run_id that has hurdles_400m stride metrics in the DB."""

    def test_returns_200(
        self, test_client: TestClient, hurdle_400m_run_id: str
    ) -> None:
        response = test_client.get(_url(hurdle_400m_run_id))
        assert response.status_code == 200

    def test_response_has_correct_shape(
        self, test_client: TestClient, hurdle_400m_run_id: str
    ) -> None:
        data = test_client.get(_url(hurdle_400m_run_id)).json()
        assert "run_id" in data
        assert "event_type" in data
        assert "total_ms" in data
        assert isinstance(data["segments"], list)
        assert isinstance(data["coaching_notes"], list)

    def test_segments_have_required_fields(
        self, test_client: TestClient, hurdle_400m_run_id: str
    ) -> None:
        segments = test_client.get(_url(hurdle_400m_run_id)).json()["segments"]
        for seg in segments:
            assert "label" in seg
            assert "raw_ms" in seg
            assert "pct_of_total" in seg
            assert "diff_s" in seg
            assert "diff_pct" in seg

    def test_segment_pcts_sum_to_approximately_100(
        self, test_client: TestClient, hurdle_400m_run_id: str
    ) -> None:
        segments = test_client.get(_url(hurdle_400m_run_id)).json()["segments"]
        total_pct = sum(s["pct_of_total"] for s in segments)
        assert abs(total_pct - 100.0) < 2.0
