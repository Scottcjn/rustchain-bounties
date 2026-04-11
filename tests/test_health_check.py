import sys
import os
import json
from unittest.mock import patch, Mock

# Add the root directory to path to import health-check
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
health_check = __import__('health-check')

def test_query_node_success():
    """Test successful node query with valid JSON response, simulating a healthy node"""
    with patch("requests.get") as mock_get:
        # Construct mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "version": "1.0.4",
            "uptime": "5d 12h",
            "db_rw": True,
            "tip_age": 14
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = health_check.query_node("test.node:8099")

        assert result["status"] == "✅ Online"
        assert result["version"] == "1.0.4"
        assert result["db_rw"] == "✅ RW"
        assert result["tip_age"] == "14s"
        assert mock_get.called


def test_query_node_offline():
    """Test offline node handling (e.g., connection error or 500 status)"""
    with patch("requests.get") as mock_get:
        # Simulate connection error
        mock_get.side_effect = Exception("Connection Refused")

        result = health_check.query_node("offline.node:8099")

        assert result["status"] == "❌ Offline"
        assert result["version"] == "N/A"
        assert result["db_rw"] == "N/A"
        assert "Connection Refused" in result["error"]
