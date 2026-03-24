"""
Integration tests for GET /run/athletes/{run_id}/metrics/split-score.

Covers:
  - 404 for a missing run_id
  - 422 for an unsupported event type
  - 200 with a real run_id that has metrics (requires pre-seeded data; see note)

Note on the "real run" test
────────────────────────────
The 200 test requires a run record in the `run` table with event_type="400mH"
AND corresponding rows in `run_metrics`. Because seeding a complete hurdle
stride dataset via the API is out of scope for CI, this test is marked with
`pytest.mark.requires_seed` and is skipped unless you set:

    export SPLIT_SCORE_TEST_RUN_ID=<a valid UUID from your DB>

Run it locally after seeding:

    pytest -m requires_seed backend/tests/integration/test_split_score.py
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

BASE = "/api/run/athletes"
SPLIT_SCORE_PATH = "metrics/split-score"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _url(run_id: str) -> str:
    return f"{BASE}/{run_id}/{SPLIT_SCORE_PATH}"


# ── Missing run ───────────────────────────────────────────────────────────────


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
        data = response.json()

        assert "detail" in data


# ── Unsupported event type ────────────────────────────────────────────────────


@pytest.mark.integration
class TestSplitScoreUnsupportedEvent:
    """GET for a run whose event_type is not supported by split score analysis."""

    def test_unsupported_event_returns_422(
        self,
        test_client: TestClient,
        supabase_client,
        created_ids: dict,
    ) -> None:
        # Create a run with an unsupported event type directly via Supabase
        # (the API POST /run accepts any event_type string, so this is valid)
        create_resp = test_client.post(
            "/api/run",
            json={
                "athlete_id": str(uuid4()),  # FK not enforced in test env
                "event_type": "110mH",  # not in SUPPORTED_EVENTS
                "elapsed_ms": 13500,
            },
        )
        # If the run table has an athlete FK constraint this will 422/500 —
        # fall back to a skip so CI doesn't fail due to missing athlete seed.
        if create_resp.status_code not in (200, 201):
            pytest.skip("Could not create run — athlete FK constraint requires seed.")

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
            "/api/run",
            json={
                "athlete_id": str(uuid4()),
                "event_type": "110mH",
                "elapsed_ms": 13500,
            },
        )
        if create_resp.status_code not in (200, 201):
            pytest.skip("Could not create run — athlete FK constraint requires seed.")

        run_id = create_resp.json()["run_id"]
        created_ids["run_ids"].append(run_id)

        response = test_client.get(_url(run_id))
        data = response.json()

        assert "detail" in data
        assert "110mH" in data["detail"]


# ── Real run with metrics (requires pre-seeded data) ─────────────────────────


@pytest.mark.integration
@pytest.mark.requires_seed
class TestSplitScoreRealRun:
    """
    GET with a real run_id that has 400mH stride metrics in the DB.

    Set SPLIT_SCORE_TEST_RUN_ID to a valid UUID before running:

        export SPLIT_SCORE_TEST_RUN_ID=<uuid>
        pytest -m requires_seed backend/tests/integration/test_split_score.py
    """

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
        response = test_client.get(_url(seeded_run_id))
        data = response.json()

        assert "run_id" in data
        assert "event_type" in data
        assert "total_ms" in data
        assert isinstance(data["segments"], list)
        assert isinstance(data["coaching_notes"], list)

    def test_400mh_returns_11_segments(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        response = test_client.get(_url(seeded_run_id))
        data = response.json()

        assert len(data["segments"]) == 11

    def test_segments_have_required_fields(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        response = test_client.get(_url(seeded_run_id))
        segments = response.json()["segments"]

        for seg in segments:
            assert "label" in seg
            assert "raw_ms" in seg
            assert "pct_of_total" in seg
            assert "percentile" in seg

    def test_percentiles_bounded(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        response = test_client.get(_url(seeded_run_id))
        segments = response.json()["segments"]

        for seg in segments:
            assert 0.0 <= seg["percentile"] <= 100.0

    def test_segment_pcts_sum_to_approximately_100(
        self, test_client: TestClient, seeded_run_id: str
    ) -> None:
        response = test_client.get(_url(seeded_run_id))
        segments = response.json()["segments"]
        total_pct = sum(s["pct_of_total"] for s in segments)

        assert abs(total_pct - 100.0) < 2.0, (
            f"Segment pct_of_total values should sum to ~100%, got {total_pct:.1f}%"
        )
