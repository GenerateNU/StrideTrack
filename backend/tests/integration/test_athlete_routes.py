from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.schemas.coach_schemas import Coach
from tests.factories.athlete_factory import AthleteFactory

BASE = "/api/athletes"


@pytest.mark.integration
class TestListAthletes:
    """GET /api/athletes"""

    def test_list_returns_200(self, test_client: TestClient) -> None:
        """The list endpoint should return 200 with a JSON array."""
        response = test_client.get(BASE)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_created_athlete_appears_in_list(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """An athlete created via POST should appear in the subsequent GET list."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="List Test Athlete"
        )
        create_resp = test_client.post(BASE, json=athlete_data)
        assert create_resp.status_code == 201
        athlete_id = create_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)

        response = test_client.get(BASE)

        assert response.status_code == 200
        ids = [a["athlete_id"] for a in response.json()]
        assert athlete_id in ids


@pytest.mark.integration
class TestGetAthlete:
    """GET /api/athletes/{athlete_id}"""

    def test_get_existing_athlete_returns_200(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Fetching a created athlete by ID should return 200 with correct data."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Get Test Athlete"
        )
        create_resp = test_client.post(BASE, json=athlete_data)
        assert create_resp.status_code == 201
        athlete_id = create_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)

        response = test_client.get(f"{BASE}/{athlete_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["athlete_id"] == athlete_id
        assert data["name"] == "Get Test Athlete"

    def test_get_nonexistent_athlete_returns_404(self, test_client: TestClient) -> None:
        """Fetching a non-existent athlete ID should return 404."""
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/{fake_id}")

        assert response.status_code == 404


@pytest.mark.integration
class TestCreateAthlete:
    """POST /api/athletes"""

    def test_create_full_athlete_returns_201(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Creating an athlete with all fields should return 201 with the full response."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id),
            name="Full Athlete",
            height_in=72.0,
            weight_lbs=180.0,
        )

        response = test_client.post(BASE, json=athlete_data)

        assert response.status_code == 201
        data = response.json()
        created_ids["athlete_ids"].append(data["athlete_id"])

        assert data["name"] == "Full Athlete"
        assert data["height_in"] == 72.0
        assert data["weight_lbs"] == 180.0
        assert "athlete_id" in data
        assert "created_at" in data

    def test_create_minimal_athlete_returns_201(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Creating an athlete with only required fields should return 201
        with nullable fields set to None."""
        athlete_data = AthleteFactory.create_minimal(
            coach_id=str(test_coach.coach_id), name="Minimal Athlete"
        )

        response = test_client.post(BASE, json=athlete_data)

        assert response.status_code == 201
        data = response.json()
        created_ids["athlete_ids"].append(data["athlete_id"])

        assert data["name"] == "Minimal Athlete"
        assert data["height_in"] is None
        assert data["weight_lbs"] is None

    def test_create_missing_required_field_returns_422(
        self, test_client: TestClient
    ) -> None:
        """Omitting the required 'name' field should return 422 validation error."""
        response = test_client.post(BASE, json={"coach_id": str(uuid4())})

        assert response.status_code == 422

    def test_create_invalid_height_returns_422(self, test_client: TestClient) -> None:
        """A height_in of 0 or below should fail validation (gt=0) and return 422."""
        response = test_client.post(
            BASE,
            json={
                "coach_id": str(uuid4()),
                "name": "Bad Height",
                "height_in": 0,
            },
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestUpdateAthlete:
    """PATCH /api/athletes/{athlete_id}"""

    def test_update_returns_200_with_new_values(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Patching an athlete's name and height should return 200 with the updated values."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="Before Update"
        )
        create_resp = test_client.post(BASE, json=athlete_data)
        assert create_resp.status_code == 201
        athlete_id = create_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)

        response = test_client.patch(
            f"{BASE}/{athlete_id}",
            json={"name": "After Update", "height_in": 75.0},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "After Update"
        assert data["height_in"] == 75.0

    def test_update_nonexistent_athlete_returns_404(
        self, test_client: TestClient
    ) -> None:
        """Patching a non-existent athlete ID should return 404."""
        fake_id = str(uuid4())

        response = test_client.patch(f"{BASE}/{fake_id}", json={"name": "Ghost"})

        assert response.status_code == 404


@pytest.mark.integration
class TestDeleteAthlete:
    """DELETE /api/athletes/{athlete_id}"""

    def test_delete_returns_204(
        self,
        test_client: TestClient,
        test_coach: Coach,
        created_ids: dict,
    ) -> None:
        """Deleting an existing athlete should return 204, and a subsequent GET should 404."""
        athlete_data = AthleteFactory.create(
            coach_id=str(test_coach.coach_id), name="To Be Deleted"
        )
        create_resp = test_client.post(BASE, json=athlete_data)
        assert create_resp.status_code == 201
        athlete_id = create_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)

        response = test_client.delete(f"{BASE}/{athlete_id}")

        assert response.status_code == 204

        get_resp = test_client.get(f"{BASE}/{athlete_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_athlete_returns_404(
        self, test_client: TestClient
    ) -> None:
        """Deleting a non-existent athlete ID should return 404."""
        fake_id = str(uuid4())

        response = test_client.delete(f"{BASE}/{fake_id}")

        assert response.status_code == 404
