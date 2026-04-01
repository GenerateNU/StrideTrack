from collections.abc import Generator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from supabase import Client, create_client

from app.core.auth import get_current_coach
from app.core.config import settings
from app.main import app
from app.schemas.coach_schemas import Coach
from app.schemas.profile_schemas import Profile
from tests.factories.coach_factory import CoachFactory

# ── Seeded coach constants (must match supabase/seed.sql) ──
SEEDED_COACH_ID = UUID("00000000-0000-0000-0000-000000000001")
SEEDED_PROFILE_ID = UUID("00000000-0000-0000-0000-000000000010")
SEEDED_AUTH_USER_ID = UUID("00000000-0000-0000-0000-000000000099")


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


# ── Auth override fixtures ──


@pytest.fixture(autouse=True)
def _override_auth() -> Generator[None, None, None]:
    """Default auth override using the seeded coach.

    Tests that need a fresh coach should use the ``test_coach`` fixture,
    which overwrites this override with the newly created coach.
    """
    seeded_coach = Coach(
        coach_id=SEEDED_COACH_ID,
        profile=Profile(
            profile_id=SEEDED_PROFILE_ID,
            auth_user_id=SEEDED_AUTH_USER_ID,
            email="dev@stridetrack.dev",
            name="Coach Sam Baldwin",
            role="coach",
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
        ),
        created_at=datetime(2024, 1, 1, tzinfo=UTC),
    )
    app.dependency_overrides[get_current_coach] = lambda: seeded_coach
    yield
    app.dependency_overrides.pop(get_current_coach, None)


@pytest.fixture
def test_coach(
    supabase_client: Client, created_ids: dict
) -> Generator[Coach, None, None]:
    """Create a fresh coach and override auth to use it.

    Use this fixture in tests that create their own data and need a
    coach that owns that data.  The coach is cleaned up automatically.

    Only the coach row is inserted into the DB (needed as FK target for
    athletes/runs).  The Profile embedded in the returned Coach object
    is synthetic — no real profile row is created, since the dependency
    override means the auth layer never queries profiles.
    """
    coach_resp = (
        supabase_client.table("coaches").insert(CoachFactory.create()).execute()
    )
    coach_data = coach_resp.data[0]
    created_ids["coach_ids"].append(coach_data["coach_id"])

    fake_profile = Profile(
        profile_id=uuid4(),
        auth_user_id=uuid4(),
        email="test@stridetrack.dev",
        name="Test Coach",
        role="coach",
        created_at=coach_data["created_at"],
    )

    coach = Coach(
        coach_id=coach_data["coach_id"],
        profile=fake_profile,
        created_at=coach_data["created_at"],
    )

    # Overwrite the default (seeded) auth override
    app.dependency_overrides[get_current_coach] = lambda: coach
    yield coach


# ── Test-data tracking & cleanup ──


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
        training_run_ids: list of training_run id strings
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

    Deletes in FK-safe order:
    run_metrics → run → athletes → coaches → training_runs.
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
