from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from supabase import Client

from app.core.auth import get_current_coach
from app.main import app
from app.schemas.coach_schemas import Coach
from app.schemas.profile_schemas import Profile
from tests.factories.coach_factory import CoachFactory


@pytest.fixture(scope="session")
def default_coach(supabase_client: Client) -> Generator[Coach, None, None]:
    """Session-scoped real coach row used by the default auth override.

    Created once for the entire integration test session via CoachFactory
    so no seed data is required. Cleaned up at session teardown.
    """
    coach_resp = (
        supabase_client.table("coaches").insert(CoachFactory.create()).execute()
    )
    coach_data = coach_resp.data[0]
    coach_id = UUID(coach_data["coach_id"])

    fake_profile = Profile(
        profile_id=uuid4(),
        auth_user_id=uuid4(),
        email="default@stridetrack.dev",
        name="Default Test Coach",
        role="coach",
        created_at=coach_data["created_at"],
    )
    coach = Coach(
        coach_id=coach_id,
        profile=fake_profile,
        created_at=coach_data["created_at"],
    )
    yield coach
    supabase_client.table("coaches").delete().eq("coach_id", str(coach_id)).execute()


@pytest.fixture(autouse=True)
def _override_auth(default_coach: Coach) -> Generator[None, None, None]:
    """Default auth override using a session-generated coach (no seed data required).

    Tests that need a fresh coach should use the ``test_coach`` fixture,
    which overwrites this override with the newly created coach.
    """
    app.dependency_overrides[get_current_coach] = lambda: default_coach
    yield
    app.dependency_overrides.pop(get_current_coach, None)
