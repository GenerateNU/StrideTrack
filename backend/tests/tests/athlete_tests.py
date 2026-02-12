from fastapi.testclient import TestClient

from tests.factories.athlete_factory import AthleteFactory


class TestListAthletes:
    """Tests for GET /api/athletes"""

    def test_list_empty(self, test_client: TestClient) -> None:
        """Returns empty list when no athletes exist."""
        response = test_client.get("/api/athletes")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_created_athletes(self, test_client: TestClient) -> None:
        """Returns all created athletes."""
        athlete1 = AthleteFactory.create(name="Athlete One")
        athlete2 = AthleteFactory.create(name="Athlete Two")

        test_client.post("/api/athletes", json=athlete1)
        test_client.post("/api/athletes", json=athlete2)

        response = test_client.get("/api/athletes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [a["name"] for a in data]
        assert "Athlete One" in names
        assert "Athlete Two" in names


class TestGetAthlete:
    """Tests for GET /api/athletes/{athlete_id}"""

    def test_get_existing_athlete(self, test_client: TestClient) -> None:
        """Returns athlete by ID."""
        athlete_data = AthleteFactory.create()
        create_response = test_client.post("/api/athletes", json=athlete_data)
        athlete_id = create_response.json()["athlete_id"]

        response = test_client.get(f"/api/athletes/{athlete_id}")

        assert response.status_code == 200
        assert response.json()["athlete_id"] == athlete_id
        assert response.json()["name"] == athlete_data["name"]

    def test_get_nonexistent_athlete(self, test_client: TestClient) -> None:
        """Returns 404 for nonexistent athlete."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.get(f"/api/athletes/{fake_id}")

        assert response.status_code == 404

    def test_get_invalid_uuid(self, test_client: TestClient) -> None:
        """Returns 422 for invalid UUID format."""
        response = test_client.get("/api/athletes/not-a-uuid")

        assert response.status_code == 422


class TestCreateAthlete:
    """Tests for POST /api/athletes"""

    def test_create_with_all_fields(self, test_client: TestClient) -> None:
        """Creates athlete with all fields."""
        athlete_data = AthleteFactory.create()

        response = test_client.post("/api/athletes", json=athlete_data)

        assert response.status_code == 201
        data = response.json()
        assert "athlete_id" in data
        assert data["name"] == athlete_data["name"]
        assert data["height_in"] == athlete_data["height_in"]
        assert data["weight_lbs"] == athlete_data["weight_lbs"]
        assert data["coach_id"] == athlete_data["coach_id"]

    def test_create_minimal(self, test_client: TestClient) -> None:
        """Creates athlete with only required fields."""
        athlete_data = AthleteFactory.create_minimal()

        response = test_client.post("/api/athletes", json=athlete_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == athlete_data["name"]
        assert data["height_in"] is None
        assert data["weight_lbs"] is None

    def test_create_missing_required_field(self, test_client: TestClient) -> None:
        """Returns 422 when required field is missing."""
        incomplete_data = {"coach_id": "00000000-0000-0000-0000-000000000001"}

        response = test_client.post("/api/athletes", json=incomplete_data)

        assert response.status_code == 422

    def test_create_invalid_height(self, test_client: TestClient) -> None:
        """Returns 422 when height_in is not positive."""
        athlete_data = AthleteFactory.create(height_in=-10)

        response = test_client.post("/api/athletes", json=athlete_data)

        assert response.status_code == 422


class TestUpdateAthlete:
    """Tests for PATCH /api/athletes/{athlete_id}"""

    def test_update_single_field(self, test_client: TestClient) -> None:
        """Updates a single field."""
        athlete_data = AthleteFactory.create()
        create_response = test_client.post("/api/athletes", json=athlete_data)
        athlete_id = create_response.json()["athlete_id"]

        response = test_client.patch(
            f"/api/athletes/{athlete_id}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        assert response.json()["height_in"] == athlete_data["height_in"]

    def test_update_multiple_fields(self, test_client: TestClient) -> None:
        """Updates multiple fields at once."""
        athlete_data = AthleteFactory.create()
        create_response = test_client.post("/api/athletes", json=athlete_data)
        athlete_id = create_response.json()["athlete_id"]

        update_data = {
            "name": "New Name",
            "weight_lbs": 200.0,
        }

        response = test_client.patch(
            f"/api/athletes/{athlete_id}",
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["weight_lbs"] == 200.0

    def test_update_nonexistent_athlete(self, test_client: TestClient) -> None:
        """Returns 404 when updating nonexistent athlete."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.patch(
            f"/api/athletes/{fake_id}",
            json={"name": "Test"},
        )

        assert response.status_code == 404


class TestDeleteAthlete:
    """Tests for DELETE /api/athletes/{athlete_id}"""

    def test_delete_existing_athlete(self, test_client: TestClient) -> None:
        """Deletes existing athlete."""
        athlete_data = AthleteFactory.create()
        create_response = test_client.post("/api/athletes", json=athlete_data)
        athlete_id = create_response.json()["athlete_id"]

        response = test_client.delete(f"/api/athletes/{athlete_id}")

        assert response.status_code == 204

        get_response = test_client.get(f"/api/athletes/{athlete_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_athlete(self, test_client: TestClient) -> None:
        """Returns 404 when deleting nonexistent athlete."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.delete(f"/api/athletes/{fake_id}")

        assert response.status_code == 404
