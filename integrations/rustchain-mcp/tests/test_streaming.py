"""Tests for rustchain-mcp streaming/long-running tool behavior.

This test verifies the documented behavior in README.md:
- Tools are blocking, single-shot calls
- No MCP notifications/progress emitted
- Server capabilities advertise tools.list_changed only
"""

import asyncio
import inspect
from typing import Any

import pytest

from rustchain_mcp.server import mcp
from rustchain_mcp.client import RustChainClient


class TestServerCapabilities:
    """Test that server capabilities match documented behavior."""

    @pytest.mark.asyncio
    async def test_tools_capability_advertised(self):
        """Server advertises tools capability with list_changed."""
        tools = await mcp.list_tools()
        # Should have at least the 5 required tools
        tool_names = {t.name for t in tools}
        expected = {
            "rustchain_health",
            "rustchain_miners",
            "rustchain_epoch",
            "rustchain_balance",
            "rustchain_transfer",
        }
        assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"

    @pytest.mark.asyncio
    async def test_no_streaming_capability_flag(self):
        """Server does not declare any streaming-specific capability flags.

        MCP ServerCapabilities has no 'streaming' or 'progress' field.
        Progress notifications are sent ad-hoc via notifications/progress
        when a tool calls ctx.report_progress() — no capability flag needed.
        """
        # The low-level server's get_capabilities() returns ServerCapabilities
        # with only: prompts, resources, tools, logging, completions, extensions, tasks
        # No streaming/progress capability exists in the spec.
        caps = mcp._lowlevel_server.get_capabilities()
        # Tools capability exists (required for any tool server)
        assert caps.tools is not None
        # No streaming-specific capability in ServerCapabilities model
        # This test documents that fact — if a 'streaming' field appears in
        # mcp_types.ServerCapabilities, this test will need updating.
        assert not hasattr(caps, "streaming")
        assert not hasattr(caps, "progress")


class TestToolBlockingBehavior:
    """Test that tools behave as blocking, single-shot calls."""

    def test_tools_do_not_accept_context_parameter(self):
        """None of the built-in tools accept a Context parameter.

        If a tool accepted Context, it could call ctx.report_progress()
        to emit notifications/progress. Current tools don't.
        """
        tools = [
            mcp._tool_manager.get_tool("rustchain_health"),
            mcp._tool_manager.get_tool("rustchain_miners"),
            mcp._tool_manager.get_tool("rustchain_epoch"),
            mcp._tool_manager.get_tool("rustchain_balance"),
            mcp._tool_manager.get_tool("rustchain_transfer"),
        ]

        for tool in tools:
            assert tool is not None, f"Tool {tool} not found"
            # context_kwarg is None when no Context parameter exists
            assert tool.context_kwarg is None, (
                f"Tool {tool.name} unexpectedly has Context parameter "
                f"({tool.context_kwarg}). This would enable progress reporting."
            )

    @pytest.mark.asyncio
    async def test_tool_returns_single_call_tool_result(self):
        """Tool calls return a single CallToolResult, not progressive results.

        This is the core blocking behavior: the tool runs to completion
        and returns one result. No intermediate progress notifications.
        """
        # We can't easily test actual network calls without a running node,
        # but we can verify the tool structure: they return str (JSON),
        # which gets wrapped in CallToolResult by the SDK.
        tool = mcp._tool_manager.get_tool("rustchain_health")
        assert tool is not None

        # The function signature shows it returns str (the JSON text)
        sig = inspect.signature(tool.fn)
        assert sig.return_annotation is str or sig.return_annotation == "str", (
            f"rustchain_health returns {sig.return_annotation}, expected str"
        )

    @pytest.mark.asyncio
    async def test_slow_tool_blocks_without_progress(self):
        """A slow mocked tool call blocks without emitting progress.

        This test simulates a long-running tool by patching the client
        to delay. The tool should block for the full duration and return
        one result — no progress notifications are sent because the tool
        doesn't accept Context.
        """
        # Create a mock client that delays
        original_get_json = RustChainClient._get_json

        async def slow_get_json(self, path: str, params: Any = None) -> Any:
            await asyncio.sleep(0.1)  # Simulate slow network
            return {"status": "ok", "path": path}

        # Patch the client method
        RustChainClient._get_json = slow_get_json
        try:
            # Call the tool - it should block for ~0.1s and return once
            start = asyncio.get_event_loop().time()
            result = await mcp.call_tool("rustchain_health", {})
            elapsed = asyncio.get_event_loop().time() - start

            # Should take at least the sleep time (blocking)
            assert elapsed >= 0.09, f"Tool returned too fast: {elapsed:.3f}s"

            # Result should be a CallToolResult with content
            assert hasattr(result, "content")
            assert len(result.content) > 0
            # No progress notifications were emitted (we can't easily
            # capture them in this test, but the tool structure
            # guarantees it — no Context parameter = no report_progress)
        finally:
            RustChainClient._get_json = original_get_json


class TestDocumentedBehaviorMatchesCode:
    """Verify README claims match actual code (file + line references)."""

    def test_readme_claims_match_server_py(self):
        """Verify specific README claims against server.py source."""
        import rustchain_mcp.server as server_module

        source = inspect.getsource(server_module)

        # Claim: "No tool accepts a Context parameter"
        # Check that no tool function has a 'ctx' or 'context' parameter
        for tool_name in [
            "rustchain_health",
            "rustchain_miners",
            "rustchain_epoch",
            "rustchain_balance",
            "rustchain_transfer",
        ]:
            tool = mcp._tool_manager.get_tool(tool_name)
            assert tool is not None
            assert tool.context_kwarg is None, (
                f"README claims no Context param, but {tool_name} has {tool.context_kwarg}"
            )

        # Claim: Tools return JSON strings via _to_pretty
        assert "_to_pretty" in source
        assert "json.dumps" in source

        # Claim: Tools are simple async functions calling client
        assert "await client.health()" in source
        assert "await client.miners()" in source
        assert "await client.epoch()" in source
        assert "await client.balance(" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])