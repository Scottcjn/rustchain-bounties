"""Tests for RustChain MCP Server."""

import pytest
import json

def test_tools_list():
    """Test that all tools are defined."""
    from rustchain_mcp.server import TOOLS
    assert len(TOOLS) >= 6
    tool_names = [t["name"] for t in TOOLS]
    assert "rustchain_health" in tool_names
    assert "rustchain_balance" in tool_names

def test_balance_args():
    """Test balance tool requires wallet_id."""
    from rustchain_mcp.server import TOOLS
    balance_tool = next(t for t in TOOLS if t["name"] == "rustchain_balance")
    assert "wallet_id" in balance_tool["inputSchema"]["required"]
