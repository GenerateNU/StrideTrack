import pytest
from fastapi.testclient import TestClient
 
 
@pytest.mark.integration
class TestHealthCheck:
    """GET /api/health"""
 
    def test_health_returns_200(self, test_client: TestClient) -> None:
        """The health endpoint should return 200 with status and database fields."""
        response = test_client.get("/api/health")
 
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
 