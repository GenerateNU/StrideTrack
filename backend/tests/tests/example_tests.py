import pytest
from fastapi.testclient import TestClient

from tests.factories.example_factory import ExampleFactory


class TestListTrainingRuns:
    """Tests for GET /api/example/training-runs"""

    def test_list_empty(self, test_client: TestClient) -> None:
        """Returns empty list when no training runs exist."""
        response = test_client.get("/api/example/training-runs")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_created_runs(self, test_client: TestClient) -> None:
        """Returns all created training runs."""
        run1 = ExampleFactory.create(athlete_name="Athlete One")
        run2 = ExampleFactory.create(athlete_name="Athlete Two")

        test_client.post("/api/example/training-runs", json=run1)
        test_client.post("/api/example/training-runs", json=run2)

        response = test_client.get("/api/example/training-runs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [r["athlete_name"] for r in data]
        assert "Athlete One" in names
        assert "Athlete Two" in names


class TestGetTrainingRun:
    """Tests for GET /api/example/training-runs/{run_id}"""

    def test_get_existing_run(self, test_client: TestClient) -> None:
        """Returns training run by ID."""
        run_data = ExampleFactory.create()
        create_response = test_client.post("/api/example/training-runs", json=run_data)
        run_id = create_response.json()["id"]

        response = test_client.get(f"/api/example/training-runs/{run_id}")

        assert response.status_code == 200
        assert response.json()["id"] == run_id
        assert response.json()["athlete_name"] == run_data["athlete_name"]

    def test_get_nonexistent_run(self, test_client: TestClient) -> None:
        """Returns 404 for nonexistent training run."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.get(f"/api/example/training-runs/{fake_id}")

        assert response.status_code == 404

    def test_get_invalid_uuid(self, test_client: TestClient) -> None:
        """Returns 422 for invalid UUID format."""
        response = test_client.get("/api/example/training-runs/not-a-uuid")

        assert response.status_code == 422


class TestCreateTrainingRun:
    """Tests for POST /api/example/training-runs"""

    def test_create_with_all_fields(self, test_client: TestClient) -> None:
        """Creates training run with all fields."""
        run_data = ExampleFactory.create()

        response = test_client.post("/api/example/training-runs", json=run_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["athlete_name"] == run_data["athlete_name"]
        assert data["distance_meters"] == run_data["distance_meters"]
        assert data["duration_seconds"] == pytest.approx(
            run_data["duration_seconds"], rel=1e-2
        )
        assert (
            data["avg_ground_contact_time_ms"] == run_data["avg_ground_contact_time_ms"]
        )

    def test_create_minimal(self, test_client: TestClient) -> None:
        """Creates training run with only required fields."""
        run_data = ExampleFactory.create_minimal()

        response = test_client.post("/api/example/training-runs", json=run_data)

        assert response.status_code == 201
        data = response.json()
        assert data["athlete_name"] == run_data["athlete_name"]
        assert data["avg_ground_contact_time_ms"] is None

    def test_create_missing_required_field(self, test_client: TestClient) -> None:
        """Returns 422 when required field is missing."""
        incomplete_data = {"athlete_name": "Test Athlete"}

        response = test_client.post("/api/example/training-runs", json=incomplete_data)

        assert response.status_code == 422

    def test_create_invalid_distance(self, test_client: TestClient) -> None:
        """Returns 422 when distance_meters is not positive."""
        run_data = ExampleFactory.create(distance_meters=-100)

        response = test_client.post("/api/example/training-runs", json=run_data)

        assert response.status_code == 422


class TestUpdateTrainingRun:
    """Tests for PATCH /api/example/training-runs/{run_id}"""

    def test_update_single_field(self, test_client: TestClient) -> None:
        """Updates a single field."""
        run_data = ExampleFactory.create()
        create_response = test_client.post("/api/example/training-runs", json=run_data)
        run_id = create_response.json()["id"]

        response = test_client.patch(
            f"/api/example/training-runs/{run_id}",
            json={"athlete_name": "Updated Name"},
        )

        assert response.status_code == 200
        assert response.json()["athlete_name"] == "Updated Name"
        assert response.json()["distance_meters"] == run_data["distance_meters"]

    def test_update_multiple_fields(self, test_client: TestClient) -> None:
        """Updates multiple fields at once."""
        run_data = ExampleFactory.create()
        create_response = test_client.post("/api/example/training-runs", json=run_data)
        run_id = create_response.json()["id"]

        update_data = {
            "athlete_name": "New Name",
            "distance_meters": 5000,
        }

        response = test_client.patch(
            f"/api/example/training-runs/{run_id}",
            json=update_data,
        )

        assert response.status_code == 200
        assert response.json()["athlete_name"] == "New Name"
        assert response.json()["distance_meters"] == 5000

    def test_update_nonexistent_run(self, test_client: TestClient) -> None:
        """Returns 404 when updating nonexistent run."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.patch(
            f"/api/example/training-runs/{fake_id}",
            json={"athlete_name": "Test"},
        )

        assert response.status_code == 404


class TestDeleteTrainingRun:
    """Tests for DELETE /api/example/training-runs/{run_id}"""

    def test_delete_existing_run(self, test_client: TestClient) -> None:
        """Deletes existing training run."""
        run_data = ExampleFactory.create()
        create_response = test_client.post("/api/example/training-runs", json=run_data)
        run_id = create_response.json()["id"]

        response = test_client.delete(f"/api/example/training-runs/{run_id}")

        assert response.status_code == 204

        get_response = test_client.get(f"/api/example/training-runs/{run_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_run(self, test_client: TestClient) -> None:
        """Returns 404 when deleting nonexistent run."""
        fake_id = "00000000-0000-0000-0000-000000000001"

        response = test_client.delete(f"/api/example/training-runs/{fake_id}")

        assert response.status_code == 404
