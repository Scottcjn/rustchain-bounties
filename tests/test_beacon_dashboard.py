#!/usr/bin/env python3
"""Tests for beacon_dashboard"""

import json
import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from beacon_dashboard.dashboard import (
    DashboardState,
    TransportStats,
    AgentStats,
    get_dashboard_state,
    filter_transports,
    export_to_json,
    export_to_csv,
)


class TestTransportStats:
    """Test TransportStats dataclass"""

    def test_create_transport_stats(self):
        transport = TransportStats(
            name="discord",
            status="healthy",
            messages_sent=100,
            messages_received=90,
            errors=1,
            last_activity="2026-02-19T00:00:00",
            top_agents=[{"agent_id": "agent-001", "messages": 50}]
        )
        
        assert transport.name == "discord"
        assert transport.status == "healthy"
        assert transport.messages_sent == 100
        assert len(transport.top_agents) == 1


class TestAgentStats:
    """Test AgentStats dataclass"""

    def test_create_agent_stats(self):
        agent = AgentStats(
            agent_id="agent-001",
            role="coordinator",
            status="active",
            last_heartbeat="2026-02-19T00:00:00",
            messages_sent=500,
            tips_earned=25.5
        )
        
        assert agent.agent_id == "agent-001"
        assert agent.role == "coordinator"
        assert agent.tips_earned == 25.5


class TestDashboardState:
    """Test DashboardState dataclass"""

    def test_create_empty_state(self):
        state = DashboardState()
        
        assert len(state.transports) == 0
        assert len(state.agents) == 0
        assert len(state.filters) == 0

    def test_state_with_data(self):
        state = DashboardState()
        state.transports["discord"] = TransportStats(
            name="discord", status="healthy"
        )
        state.agents["agent-001"] = AgentStats(
            agent_id="agent-001", role="worker", status="active"
        )
        
        assert len(state.transports) == 1
        assert len(state.agents) == 1


class TestGetDashboardState:
    """Test get_dashboard_state function"""

    def test_returns_dashboard_state(self):
        state = get_dashboard_state()
        
        assert isinstance(state, DashboardState)
        assert state.last_update is not None
        assert len(state.transports) > 0

    def test_transports_have_required_fields(self):
        state = get_dashboard_state()
        
        for name, transport in state.transports.items():
            assert transport.name == name
            assert transport.status in ["healthy", "degraded", "down"]
            assert transport.messages_sent >= 0
            assert transport.messages_received >= 0


class TestFilterTransports:
    """Test filter_transports function"""

    def test_no_filters_returns_all(self):
        state = get_dashboard_state()
        filtered = filter_transports(state)
        
        assert len(filtered) == len(state.transports)

    def test_status_filter(self):
        state = get_dashboard_state()
        state.filters = ["healthy"]
        
        filtered = filter_transports(state)
        
        for transport in filtered.values():
            assert transport.status == "healthy"

    def test_search_query(self):
        state = get_dashboard_state()
        state.search_query = "discord"
        
        filtered = filter_transports(state)
        
        assert "discord" in filtered

    def test_search_no_match(self):
        state = get_dashboard_state()
        state.search_query = "nonexistent"
        
        filtered = filter_transports(state)
        
        assert len(filtered) == 0


class TestExportToJson:
    """Test export_to_json function"""

    def test_export_creates_file(self):
        state = get_dashboard_state()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            success = export_to_json(state, filepath)
            
            assert success is True
            assert Path(filepath).exists()
            
            # Verify content
            with open(filepath) as f:
                data = json.load(f)
            
            assert "transports" in data
            assert "agents" in data
            assert "timestamp" in data
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_export_contains_transport_data(self):
        state = get_dashboard_state()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            export_to_json(state, filepath)
            
            with open(filepath) as f:
                data = json.load(f)
            
            # Check first transport
            transport_name = list(state.transports.keys())[0]
            assert transport_name in data["transports"]
            
            transport_data = data["transports"][transport_name]
            assert "status" in transport_data
            assert "messages_sent" in transport_data
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestExportToCsv:
    """Test export_to_csv function"""

    def test_export_creates_file(self):
        state = get_dashboard_state()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name
        
        try:
            success = export_to_csv(state, filepath)
            
            assert success is True
            assert Path(filepath).exists()
            
            # Verify content has data
            content = Path(filepath).read_text()
            assert "Transport Stats" in content
            assert "discord" in content
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_export_contains_headers(self):
        state = get_dashboard_state()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name
        
        try:
            export_to_csv(state, filepath)
            
            content = Path(filepath).read_text()
            assert "Name" in content
            assert "Status" in content
            assert "Sent" in content
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestIntegration:
    """Integration tests for full workflow"""

    def test_full_workflow(self):
        # Get state
        state = get_dashboard_state()
        
        # Apply filter
        state.filters = ["healthy"]
        filtered = filter_transports(state)
        
        # Export to both formats
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "export.json"
            csv_path = Path(tmpdir) / "export.csv"
            
            export_to_json(state, str(json_path))
            export_to_csv(state, str(csv_path))
            
            assert json_path.exists()
            assert csv_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
