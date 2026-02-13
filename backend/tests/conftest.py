from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from supabase import Client, create_client

from app.core.config import settings
from app.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Session-scoped test client - shares event loop across all tests."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def supabase_client() -> Generator[Client, None, None]:
    """Sync Supabase client for test setup/cleanup."""
    client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
    yield client


@pytest.fixture(autouse=True)
def cleanup_training_runs(supabase_client: Client) -> Generator[None, None, None]:
    """Clean up training_runs and athletes tables before and after each test."""
    # Clean before
    supabase_client.table("training_runs").delete().neq(
        "id", "00000000-0000-0000-0000-000000000000"
    ).execute()
    supabase_client.table("athletes").delete().neq(
        "athlete_id", "00000000-0000-0000-0000-000000000000"
    ).execute()

    yield

    # Clean after
    supabase_client.table("training_runs").delete().neq(
        "id", "00000000-0000-0000-0000-000000000000"
    ).execute()
    supabase_client.table("athletes").delete().neq(
        "athlete_id", "00000000-0000-0000-0000-000000000000"
    ).execute()
