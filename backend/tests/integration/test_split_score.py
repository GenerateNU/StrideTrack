from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


def _url(run_id: str) -> str:
    return f"/api/runs/{run_id}/metrics/split-score"


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


SEEDED_ATHLETE_ID = "00000000-0000-0000-0000-000000000002"


@pytest.mark.integration
class TestSplitScoreUnsupportedEvent:
    """GET for a run whose event_type is not supported by split score analysis."""

    def test_unsupported_event_returns_422(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        create_resp = test_client.post(
            "/api/runs",
            json={
                "athlete_id": SEEDED_ATHLETE_ID,
                "event_type": "long_jump",
                "elapsed_ms": 13500,
            },
        )
        assert create_resp.status_code in (200, 201)
        run_id = create_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)
        response = test_client.get(_url(run_id))
        assert response.status_code == 422

    def test_422_response_mentions_event_type(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        create_resp = test_client.post(
            "/api/runs",
            json={
                "athlete_id": SEEDED_ATHLETE_ID,
                "event_type": "long_jump",
                "elapsed_ms": 13500,
            },
        )
        assert create_resp.status_code in (200, 201)
        run_id = create_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)
        response = test_client.get(_url(run_id))
        data = response.json()
        assert "detail" in data
        assert "long_jump" in data["detail"]


@pytest.mark.integration
@pytest.mark.requires_seed
class TestSplitScoreRealRun:
    """GET with a real run_id that has hurdles_400m stride metrics in the DB."""

    @pytest.fixture
    def seeded_run_id(self) -> str:
        run_id = os.environ.get("SPLIT_SCORE_TEST_RUN_ID")
        if not run_id:
            pytest.skip("SPLIT_SCORE_TEST_RUN_ID not set.")
        return run_id

    def test_returns_200(self, test_client: TestClient, seeded_run_id: str) -> None:
        response = test_client.get(_url(seeded_run_id))
        assert response.status_code == 200

    def test_response_has_correct_shape(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        data = test_client.get(_url(seeded_run_id)).json()
        assert "run_id" in data
        assert "event_type" in data
        assert "total_ms" in data
        assert isinstance(data["segments"], list)
        assert isinstance(data["coaching_notes"], list)

    def test_hurdles_400m_returns_11_segments(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        data = test_client.get(_url(seeded_run_id)).json()
        assert len(data["segments"]) == 11

    def test_segments_have_required_fields(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        segments = test_client.get(_url(seeded_run_id)).json()["segments"]
        for seg in segments:
            assert "label" in seg
            assert "raw_ms" in seg
            assert "pct_of_total" in seg
            assert "diff_s" in seg
            assert "diff_pct" in seg

    def test_segment_pcts_sum_to_approximately_100(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        segments = test_client.get(_url(seeded_run_id)).json()["segments"]
        total_pct = sum(s["pct_of_total"] for s in segments)
        assert abs(total_pct - 100.0) < 2.0
