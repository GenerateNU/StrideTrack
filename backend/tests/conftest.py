from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from supabase import Client, create_client

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Session-scoped test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def supabase_client() -> Generator[Client, None, None]:
    """Session-scoped sync Supabase client for test setup/cleanup."""
    client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    yield client


@pytest.fixture
def created_ids() -> dict:
    """
    Per-test registry of created record IDs.

    Tests must append IDs to this dict after creating records so the
    cleanup_created fixture can delete only what this test created.
    This ensures parallel CI runs don't interfere with each other.

    Keys:
        coach_ids: list of coach_id strings
        athlete_ids: list of athlete_id strings
        run_ids: list of run_id strings (from the `run` table)
    """
    return {
        "coach_ids": [],
        "athlete_ids": [],
        "run_ids": [],
        "training_run_ids": [],
    }


@pytest.fixture(autouse=True)
def cleanup_created(
    supabase_client: Client, created_ids: dict
) -> Generator[None, None, None]:
    """
    After each test, delete only the specific records that test created.

    Deletes in FK-safe order: run_metrics → run → athletes → coaches → training_runs.
    This is parallel-safe — no global deletes.
    """
    yield
    for run_id in created_ids["run_ids"]:
        supabase_client.table("run_metrics").delete().eq("run_id", run_id).execute()
        supabase_client.table("run").delete().eq("run_id", run_id).execute()
    for athlete_id in created_ids["athlete_ids"]:
        supabase_client.table("athletes").delete().eq(
            "athlete_id", athlete_id
        ).execute()
    for coach_id in created_ids["coach_ids"]:
        supabase_client.table("coaches").delete().eq("coach_id", coach_id).execute()
    for training_run_id in created_ids["training_run_ids"]:
        supabase_client.table("training_runs").delete().eq(
            "id", training_run_id
        ).execute()
