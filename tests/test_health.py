import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch
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


class TestHealthEndpointExceptions:
    """Test exception handling in the health check endpoint"""

    @patch("main.psutil.virtual_memory")
    def test_health_check_memory_exception(self, mock_memory):
        """Test health check when psutil memory check fails"""
        # Mock psutil.virtual_memory to raise an exception
        mock_memory.side_effect = Exception("Memory check failed")

        response = client.get("/health")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    @patch("main.psutil.cpu_percent")
    def test_health_check_cpu_exception(self, mock_cpu):
        """Test health check when psutil CPU check fails"""
        # Mock psutil.cpu_percent to raise an exception
        mock_cpu.side_effect = Exception("CPU check failed")

        response = client.get("/health")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    @patch("main.psutil.disk_usage")
    def test_health_check_disk_exception(self, mock_disk):
        """Test health check when psutil disk check fails"""
        # Mock psutil.disk_usage to raise an exception
        mock_disk.side_effect = Exception("Disk check failed")

        response = client.get("/health")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"

    @patch("main.datetime")
    def test_health_check_datetime_exception(self, mock_datetime):
        """Test health check when datetime fails"""
        # Mock datetime.utcnow to raise an exception
        mock_datetime.utcnow.side_effect = Exception("Datetime failed")

        response = client.get("/health")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"


class TestFormatUptimeFunction:
    """Test the format_uptime utility function"""

    def test_format_uptime_seconds(self):
        """Test uptime formatting for seconds"""
        from main import format_uptime

        assert format_uptime(30) == "30s"
        assert format_uptime(59.9) == "59s"

    def test_format_uptime_minutes(self):
        """Test uptime formatting for minutes and seconds"""
        from main import format_uptime

        assert format_uptime(60) == "1m 0s"
        assert format_uptime(90) == "1m 30s"
        assert format_uptime(3599) == "59m 59s"

    def test_format_uptime_hours(self):
        """Test uptime formatting for hours and minutes"""
        from main import format_uptime

        assert format_uptime(3600) == "1h 0m"
        assert format_uptime(3660) == "1h 1m"
        assert format_uptime(7320) == "2h 2m"
