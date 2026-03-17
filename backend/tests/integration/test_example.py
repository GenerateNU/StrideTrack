"""
Integration tests for the example stack: routes → service → repository.

Covers all CRUD operations on the training_runs table via:
  GET    /api/example/training-runs
  GET    /api/example/training-runs/{id}
  POST   /api/example/training-runs
  PATCH  /api/example/training-runs/{id}
  DELETE /api/example/training-runs/{id}

Pattern reference:
  - Mark each class @pytest.mark.integration
  - Register every created ID in created_ids immediately after creation
  - Cleanup is automatic via the cleanup_created autouse fixture in conftest.py
  - Use factories — never hardcode data
  - Arrange → Act → Assert
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from tests.factories.example_factory import ExampleFactory

BASE = "/api/example/training-runs"


@pytest.mark.integration
class TestListTrainingRuns:
    """GET /api/example/training-runs"""

    def test_list_returns_200(self, test_client: TestClient) -> None:
        response = test_client.get(BASE)

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_created_run_appears_in_list(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create(athlete_name="List Test Athlete")
        create_resp = test_client.post(BASE, json=run_data)
        assert create_resp.status_code == 201
        run_id = create_resp.json()["id"]
        created_ids["training_run_ids"].append(run_id)

        response = test_client.get(BASE)

        assert response.status_code == 200
        ids = [r["id"] for r in response.json()]
        assert run_id in ids


@pytest.mark.integration
class TestGetTrainingRun:
    """GET /api/example/training-runs/{id}"""

    def test_get_existing_run_returns_200(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create(athlete_name="Get Test Athlete")
        create_resp = test_client.post(BASE, json=run_data)
        assert create_resp.status_code == 201
        run_id = create_resp.json()["id"]
        created_ids["training_run_ids"].append(run_id)

        response = test_client.get(f"{BASE}/{run_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == run_id
        assert data["athlete_name"] == "Get Test Athlete"

    def test_get_nonexistent_run_returns_404(
        self, test_client: TestClient
    ) -> None:
        fake_id = str(uuid4())

        response = test_client.get(f"{BASE}/{fake_id}")

        assert response.status_code == 404


@pytest.mark.integration
class TestCreateTrainingRun:
    """POST /api/example/training-runs"""

    def test_create_full_run_returns_201(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create(
            athlete_name="Create Full Athlete",
            distance_meters=800,
            duration_seconds=120.5,
            avg_ground_contact_time_ms=230.0,
        )

        response = test_client.post(BASE, json=run_data)

        assert response.status_code == 201
        data = response.json()
        created_ids["training_run_ids"].append(data["id"])

        assert data["athlete_name"] == "Create Full Athlete"
        assert data["distance_meters"] == 800
        assert data["duration_seconds"] == 120.5
        assert data["avg_ground_contact_time_ms"] == 230.0
        assert "id" in data
        assert "created_at" in data

    def test_create_minimal_run_returns_201(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create_minimal(
            athlete_name="Minimal Athlete",
            distance_meters=100,
            duration_seconds=15.0,
        )

        response = test_client.post(BASE, json=run_data)

        assert response.status_code == 201
        data = response.json()
        created_ids["training_run_ids"].append(data["id"])

        assert data["athlete_name"] == "Minimal Athlete"
        assert data["avg_ground_contact_time_ms"] is None

    def test_create_missing_required_field_returns_422(
        self, test_client: TestClient
    ) -> None:
        response = test_client.post(
            BASE, json={"distance_meters": 400, "duration_seconds": 60.0}
        )

        assert response.status_code == 422

    def test_create_invalid_distance_returns_422(
        self, test_client: TestClient
    ) -> None:
        run_data = ExampleFactory.create()
        run_data["distance_meters"] = 0  # must be > 0

        response = test_client.post(BASE, json=run_data)

        assert response.status_code == 422


@pytest.mark.integration
class TestUpdateTrainingRun:
    """PATCH /api/example/training-runs/{id}"""

    def test_update_returns_200_with_new_values(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create(athlete_name="Before Update")
        create_resp = test_client.post(BASE, json=run_data)
        assert create_resp.status_code == 201
        run_id = create_resp.json()["id"]
        created_ids["training_run_ids"].append(run_id)

        response = test_client.patch(
            f"{BASE}/{run_id}", json={"athlete_name": "After Update", "distance_meters": 1600}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["athlete_name"] == "After Update"
        assert data["distance_meters"] == 1600

    def test_update_nonexistent_run_returns_404(
        self, test_client: TestClient
    ) -> None:
        fake_id = str(uuid4())

        response = test_client.patch(
            f"{BASE}/{fake_id}", json={"athlete_name": "Ghost"}
        )

        assert response.status_code == 404


@pytest.mark.integration
class TestDeleteTrainingRun:
    """DELETE /api/example/training-runs/{id}"""

    def test_delete_returns_204(
        self,
        test_client: TestClient,
        created_ids: dict,
    ) -> None:
        run_data = ExampleFactory.create(athlete_name="To Be Deleted")
        create_resp = test_client.post(BASE, json=run_data)
        assert create_resp.status_code == 201
        run_id = create_resp.json()["id"]
        # Don't add to created_ids — this test deletes it itself

        response = test_client.delete(f"{BASE}/{run_id}")

        assert response.status_code == 204

        # Confirm it's gone
        get_resp = test_client.get(f"{BASE}/{run_id}")
        assert get_resp.status_code == 404

    def test_delete_nonexistent_run_returns_404(
        self, test_client: TestClient
    ) -> None:
        fake_id = str(uuid4())

        response = test_client.delete(f"{BASE}/{fake_id}")

        assert response.status_code == 404
