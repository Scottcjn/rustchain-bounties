#!/usr/bin/env python3
"""Unit tests for health_check.py"""

from health_check import parse_args, format_node_health, NODE_STATUS, DEFAULT_NODES


class TestParseArgs:
    """Test argument parsing."""

    def test_default_nodes(self):
        args = parse_args([])
        assert args.nodes == DEFAULT_NODES

    def test_custom_node(self):
        args = parse_args(["--node", "http://example.com:8099"])
        assert args.nodes == ["http://example.com:8099"]

    def test_timeout_default(self):
        args = parse_args([])
        assert args.timeout == 10

    def test_custom_timeout(self):
        args = parse_args(["--timeout", "30"])
        assert args.timeout == 30


class TestFormatNodeHealth:
    """Test formatting of node health data."""

    def test_healthy_node(self):
        data = {
            "version": "1.2.3",
            "uptime": 3600,
            "db_rw": True,
            "tip_age": 5
        }
        result = format_node_health("node1", data)
        assert "node1" in result
        assert "1.2.3" in result
        assert "healthy" in result.lower() or "ok" in result.lower()

    def test_unhealthy_node(self):
        data = None
        result = format_node_health("dead_node", data)
        assert "dead_node" in result
        assert "down" in result.lower() or "error" in result.lower() or "unreachable" in result.lower()

    def test_old_tip(self):
        data = {
            "version": "1.0.0",
            "uptime": 999999,
            "db_rw": True,
            "tip_age": 9999
        }
        result = format_node_health("old_node", data)
        assert "old_node" in result

    def test_db_readonly(self):
        data = {
            "version": "1.0.0",
            "uptime": 100,
            "db_rw": False,
            "tip_age": 10
        }
        result = format_node_health("ro_node", data)
        assert "ro_node" in result
