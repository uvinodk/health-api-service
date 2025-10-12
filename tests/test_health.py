import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app

# Create test client
client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for the health check endpoint"""

    def test_health_check_success(self):
        """Test successful health check response"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "Healthy"

        # Validate timestamp format (ISO 8601)
        try:
            datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pytest.fail("Timestamp is not in the correct ISO 8601 format")

    def test_health_check_response_structure(self):
        """Test that the response has the required structure with additional metrics"""
        response = client.get("/health")
        data = response.json()

        # Check that response has the core required keys
        required_keys = {"status", "timestamp"}
        actual_keys = set(data.keys())
        assert required_keys.issubset(actual_keys), (
            f"Missing required keys. Expected at least {required_keys}, "
            f"got {actual_keys}"
        )

        # Check data types for core fields
        assert isinstance(data["status"], str)
        assert isinstance(data["timestamp"], str)

        # Check additional metrics structure if present
        if "uptime" in data:
            assert isinstance(data["uptime"], dict)
            assert "seconds" in data["uptime"]
            assert "human_readable" in data["uptime"]

        if "system" in data:
            assert isinstance(data["system"], dict)

    def test_health_check_timestamp_recent(self):
        """Test that the timestamp is recent (within last minute)"""
        response = client.get("/health")
        data = response.json()

        response_time = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.utcnow()

        # Should be within 1 minute of current time
        time_diff = abs((current_time - response_time).total_seconds())
        assert time_diff < 60, f"Timestamp too old: {time_diff} seconds"

    def test_health_check_enhanced_metrics(self):
        """Test the enhanced health metrics"""
        response = client.get("/health")
        data = response.json()

        # Test uptime metrics
        assert "uptime" in data
        uptime = data["uptime"]
        assert isinstance(uptime["seconds"], (int, float))
        assert uptime["seconds"] >= 0
        assert isinstance(uptime["human_readable"], str)

        # Test system metrics
        assert "system" in data
        system = data["system"]
        assert isinstance(system["cpu_usage_percent"], (int, float))
        assert 0 <= system["cpu_usage_percent"] <= 100

        # Test memory metrics
        memory = system["memory"]
        assert isinstance(memory["used_percent"], (int, float))
        assert 0 <= memory["used_percent"] <= 100
        assert isinstance(memory["available_gb"], (int, float))
        assert memory["available_gb"] >= 0

        # Test disk metrics
        disk = system["disk"]
        assert isinstance(disk["used_percent"], (int, float))
        assert 0 <= disk["used_percent"] <= 100
        assert isinstance(disk["free_gb"], (int, float))
        assert disk["free_gb"] >= 0


class TestAPIBehavior:
    """Test general API behavior"""

    def test_invalid_endpoint(self):
        """Test that invalid endpoints return 404"""
        response = client.get("/invalid")
        assert response.status_code == 404

    def test_wrong_method_on_health(self):
        """Test that wrong HTTP methods return 405"""
        response = client.post("/health")
        assert response.status_code == 405

        response = client.put("/health")
        assert response.status_code == 405

        response = client.delete("/health")
        assert response.status_code == 405
