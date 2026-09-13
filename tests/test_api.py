"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from app.main import app


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "DV Sentinel"
    
    def test_health_endpoint(self):
        """Test health endpoint."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "app" in data
        assert "caspian" in data
        assert "database" in data
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_messages" in data
