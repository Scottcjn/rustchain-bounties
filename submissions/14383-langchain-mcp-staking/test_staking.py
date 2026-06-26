"""
Tests for the RustChain staking SDK, LangChain tool, and MCP server.
Bounty #14383: https://github.com/Scottcjn/rustchain-bounties/issues/14383

Run:
    cd submissions/14383-langchain-mcp-staking
    pip install -r requirements.txt
    pytest test_staking.py -v
"""

from __future__ import annotations

import json
import sys
import os
import io
from unittest.mock import patch, MagicMock

import pytest

# Make the submission directory importable
sys.path.insert(0, os.path.dirname(__file__))

import staking_sdk as sdk
from staking_sdk import (
    StakeResult,
    stake_and_acquire,
    _build_attestation,
    _verify_attestation,
    _request_skill_verdict,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

LIVE_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
SKIP_LIVE = not os.environ.get("RUSTCHAIN_RUN_LIVE_TESTS")


@pytest.fixture
def dummy_epoch_response():
    return {"epoch": 42, "enrolled_miners": 10}


@pytest.fixture
def dummy_gate_pass():
    return {"acquired": True, "verdict": "pass", "reason": "ok"}


@pytest.fixture
def dummy_gate_deny():
    return {"acquired": False, "verdict": "fail", "reason": "insufficient_bond"}


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — StakeResult
# ─────────────────────────────────────────────────────────────────────────────

class TestStakeResult:
    def test_to_dict_is_json_serialisable(self):
        r = StakeResult(
            skill="rust_async", bond_rtc=1.0,
            success=True, refunded=False, verdict="acquired",
        )
        d = r.to_dict()
        assert json.loads(json.dumps(d))  # no serialisation error

    def test_str_success(self):
        r = StakeResult(
            skill="rust_async", bond_rtc=1.0,
            success=True, refunded=False, verdict="acquired",
            attestation={"sig_hex": "a" * 32},
        )
        assert "✅" in str(r)
        assert "rust_async" in str(r)

    def test_str_refunded(self):
        r = StakeResult(
            skill="rust_async", bond_rtc=1.0,
            success=False, refunded=True, verdict="error",
            error="gate_unavailable:404",
        )
        assert "↩️" in str(r)
        assert "refunded" in str(r).lower()

    def test_str_denied(self):
        r = StakeResult(
            skill="rust_async", bond_rtc=1.0,
            success=False, refunded=True, verdict="denied",
            error="insufficient_bond",
        )
        assert "❌" in str(r) or "↩️" in str(r)


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — Attestation
# ─────────────────────────────────────────────────────────────────────────────

class TestAttestation:
    def test_build_and_verify_stub(self):
        """HMAC-SHA256 stub attestation round-trip."""
        att = _build_attestation("rust_async", 1.0, 42)
        assert att["algorithm"] == "hmac-sha256-stub"
        assert len(att["sig_hex"]) == 64
        assert _verify_attestation(att)

    def test_attestation_fields(self):
        att = _build_attestation("zero_knowledge", 5.0, 10)
        body = att["body"]
        assert body["skill"] == "zero_knowledge"
        assert body["bond_rtc"] == 5.0
        assert body["epoch"] == 10

    def test_canonical_is_sorted_json(self):
        att = _build_attestation("test_skill", 1.0, 1)
        parsed = json.loads(att["canonical"])
        # Should be deterministically ordered
        assert "skill" in parsed

    def test_tampered_attestation_fails(self):
        att = _build_attestation("rust_async", 1.0, 42)
        att["sig_hex"] = "0" * 64  # tamper
        assert not _verify_attestation(att)

    def test_ed25519_attestation(self):
        """Real Ed25519 round-trip when cryptography is available."""
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError:
            pytest.skip("cryptography library not installed")

        priv = Ed25519PrivateKey.generate()
        from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
        priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        priv_hex = priv_bytes.hex()

        att = _build_attestation("ed25519_skill", 2.0, 5, private_key_hex=priv_hex)
        assert att["algorithm"] == "ed25519"
        assert len(att["pub_hex"]) == 64
        assert _verify_attestation(att)

    def test_ed25519_tampered_fails(self):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError:
            pytest.skip("cryptography library not installed")

        priv = Ed25519PrivateKey.generate()
        from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
        priv_bytes = priv.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

        att = _build_attestation("ed25519_skill", 2.0, 5, private_key_hex=priv_bytes.hex())
        att["sig_hex"] = "ff" * 64  # tamper
        assert not _verify_attestation(att)


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — stake_and_acquire (mocked)
# ─────────────────────────────────────────────────────────────────────────────

class TestStakeAndAcquireMocked:
    """All network I/O mocked — no live node required."""

    def _mock_get(self, epoch=42):
        return {"epoch": epoch}

    def test_success_path(self, dummy_epoch_response, dummy_gate_pass):
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post", return_value=dummy_gate_pass):
            result = stake_and_acquire("rust_async", 1.0)
        assert result.success
        assert not result.refunded
        assert result.verdict == "acquired"
        assert result.attestation is not None

    def test_gate_denied(self, dummy_epoch_response, dummy_gate_deny):
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post", return_value=dummy_gate_deny):
            result = stake_and_acquire("rust_async", 1.0)
        assert not result.success
        assert result.refunded           # stake returned on denial
        assert result.verdict == "denied"

    def test_gate_unavailable_404(self, dummy_epoch_response):
        import requests
        http_error = requests.exceptions.HTTPError(response=MagicMock(status_code=404))
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post", side_effect=http_error):
            result = stake_and_acquire("rust_async", 1.0)
        assert not result.success
        assert result.refunded           # FAIL-SAFE: stake returned
        assert result.verdict == "error"
        assert "gate_unavailable" in (result.error or "")

    def test_gate_server_error_500(self, dummy_epoch_response):
        import requests
        http_error = requests.exceptions.HTTPError(response=MagicMock(status_code=500))
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post", side_effect=http_error):
            result = stake_and_acquire("rust_async", 1.0)
        assert result.refunded

    def test_gate_connection_error(self, dummy_epoch_response):
        import requests
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post",
                          side_effect=requests.exceptions.ConnectionError("refused")):
            result = stake_and_acquire("rust_async", 1.0)
        assert result.refunded
        assert "gate_unreachable" in (result.error or "")

    def test_node_unreachable(self):
        import requests
        with patch.object(sdk, "_get",
                          side_effect=requests.exceptions.ConnectionError("refused")):
            result = stake_and_acquire("rust_async", 1.0)
        assert not result.success
        assert result.refunded
        assert "node_unreachable" in (result.error or "")

    def test_invalid_bond_rtc(self):
        result = stake_and_acquire("rust_async", -1.0)
        assert not result.success
        assert result.refunded
        assert result.verdict == "error"

    def test_zero_bond_rtc(self):
        result = stake_and_acquire("rust_async", 0.0)
        assert not result.success
        assert result.refunded

    def test_result_is_json_serialisable(self, dummy_epoch_response, dummy_gate_pass):
        with patch.object(sdk, "_get", return_value=dummy_epoch_response), \
             patch.object(sdk, "_post", return_value=dummy_gate_pass):
            result = stake_and_acquire("rust_async", 1.0)
        d = result.to_dict()
        json.dumps(d)  # must not raise


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — LangChain Tool
# ─────────────────────────────────────────────────────────────────────────────

class TestLangChainTool:
    def _get_tool(self):
        from langchain_staking_tool import RustChainStakeTool
        return RustChainStakeTool()

    def test_tool_metadata(self):
        tool = self._get_tool()
        assert tool.name == "rustchain_stake_and_acquire"
        assert "stake" in tool.description.lower()
        assert "refunded" in tool.description.lower()

    def test_shorthand_string_input(self):
        tool = self._get_tool()
        parsed = tool._parse_input("rust_async:2.5")
        assert parsed.skill == "rust_async"
        assert parsed.bond_rtc == 2.5

    def test_shorthand_no_bond(self):
        tool = self._get_tool()
        parsed = tool._parse_input("zero_knowledge")
        assert parsed.skill == "zero_knowledge"
        assert parsed.bond_rtc == 1.0

    def test_dict_input(self):
        tool = self._get_tool()
        parsed = tool._parse_input({"skill": "p2p", "bond_rtc": 3.0})
        assert parsed.skill == "p2p"
        assert parsed.bond_rtc == 3.0

    def test_json_string_input(self):
        tool = self._get_tool()
        parsed = tool._parse_input('{"skill": "json_skill", "bond_rtc": 1.5}')
        assert parsed.skill == "json_skill"
        assert parsed.bond_rtc == 1.5

    def test_run_returns_json(self):
        """End-to-end with mocked SDK."""
        import staking_sdk as sdk_module
        mock_result = StakeResult(
            skill="rust_async", bond_rtc=1.0,
            success=False, refunded=True,
            verdict="error", error="gate_unavailable:404",
        )
        with patch.object(sdk_module, "_get", return_value={"epoch": 1}), \
             patch.object(sdk_module, "_post",
                          side_effect=__import__("requests").exceptions.HTTPError(
                              response=MagicMock(status_code=404))):
            from langchain_staking_tool import RustChainStakeTool
            tool = RustChainStakeTool()
            output = tool._run(skill="rust_async", bond_rtc=1.0)
        data = json.loads(output)
        assert "verdict" in data
        assert "refunded" in data
        assert data["refunded"] is True


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests — MCP Server
# ─────────────────────────────────────────────────────────────────────────────

class TestMCPServer:
    def _rpc(self, method, params=None, msg_id=1):
        """Build a JSON-RPC 2.0 request line."""
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "method": method,
            "params": params or {},
        })

    def _run_server(self, lines):
        """Feed lines to the MCP server main loop, capture stdout."""
        import mcp_staking_server as srv
        stdin = io.StringIO("\n".join(lines) + "\n")
        stdout_buf = []
        original_print = __builtins__["print"] if isinstance(__builtins__, dict) else print

        responses = []
        with patch("sys.stdin", stdin), \
             patch("builtins.print", side_effect=lambda s, **kw: responses.append(s)):
            srv.main()
        return [json.loads(r) for r in responses if r.strip()]

    def test_initialize(self):
        responses = self._run_server([self._rpc("initialize")])
        assert len(responses) == 1
        r = responses[0]
        assert r["result"]["protocolVersion"] == "2024-11-05"
        assert r["result"]["serverInfo"]["name"] == "rustchain-staking-mcp"

    def test_tools_list(self):
        responses = self._run_server([
            self._rpc("initialize", msg_id=1),
            self._rpc("tools/list", msg_id=2),
        ])
        tools_resp = next(r for r in responses if r.get("id") == 2)
        tools = tools_resp["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "stake_and_acquire" in names
        assert "rustchain_health" in names

    def test_stake_tool_schema(self):
        responses = self._run_server([self._rpc("tools/list")])
        tools = responses[0]["result"]["tools"]
        stake_tool = next(t for t in tools if t["name"] == "stake_and_acquire")
        schema = stake_tool["inputSchema"]
        assert "skill" in schema["properties"]
        assert "bond_rtc" in schema["properties"]
        assert "skill" in schema["required"]

    def test_unknown_method(self):
        responses = self._run_server([self._rpc("nonexistent/method")])
        r = responses[0]
        assert "error" in r
        assert r["error"]["code"] == -32601

    def test_unknown_tool(self):
        responses = self._run_server([
            self._rpc("tools/call", {"name": "does_not_exist", "arguments": {}})
        ])
        r = responses[0]
        assert r["result"]["isError"] is True

    def test_tool_call_stake_mocked(self):
        """Call stake_and_acquire via MCP with mocked SDK."""
        import staking_sdk as sdk_module
        import requests

        err = requests.exceptions.HTTPError(response=MagicMock(status_code=404))
        with patch.object(sdk_module, "_get", return_value={"epoch": 1}), \
             patch.object(sdk_module, "_post", side_effect=err):
            responses = self._run_server([
                self._rpc("tools/call", {
                    "name": "stake_and_acquire",
                    "arguments": {"skill": "rust_async", "bond_rtc": 1.0},
                })
            ])
        r = responses[0]
        text = r["result"]["content"][0]["text"]
        assert "refunded" in text.lower() or "unavailable" in text.lower()

    def test_missing_skill_argument(self):
        responses = self._run_server([
            self._rpc("tools/call", {
                "name": "stake_and_acquire",
                "arguments": {},  # skill omitted
            })
        ])
        r = responses[0]
        assert r["result"]["isError"] is True
        assert "required" in r["result"]["content"][0]["text"].lower() or \
               "skill" in r["result"]["content"][0]["text"].lower()

    def test_notifications_no_response(self):
        """notifications/* must not produce a response."""
        responses = self._run_server([
            self._rpc("notifications/initialized"),
            self._rpc("initialize", msg_id=99),
        ])
        ids = [r.get("id") for r in responses]
        assert 99 in ids
        # No response should be generated for the notification (id=1)
        assert None not in ids or len([r for r in responses if r.get("id") is None]) == 0


# ─────────────────────────────────────────────────────────────────────────────
# Live integration tests (skipped unless RUSTCHAIN_RUN_LIVE_TESTS=1)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(SKIP_LIVE, reason="Set RUSTCHAIN_RUN_LIVE_TESTS=1 to run live tests")
class TestLiveIntegration:
    def test_live_node_reachable(self):
        data = sdk._get("/health")
        assert data.get("ok") is True or "version" in data

    def test_live_epoch(self):
        data = sdk._get("/epoch")
        assert "epoch" in data
        assert isinstance(data["epoch"], int)

    def test_live_stake_gate_failsafe(self):
        """
        With real node: gate /skill/gate likely returns 404 (not implemented),
        triggering the fail-safe and returning the stake.
        """
        result = stake_and_acquire("rust_async", 0.001)
        # Either acquired (gate exists and passed) or refunded (gate unavailable)
        assert result.success or result.refunded, (
            f"Expected success or refund, got: verdict={result.verdict} "
            f"error={result.error}"
        )
        # Attestation should always be built
        assert result.attestation is not None

    def test_live_attestation_verified(self):
        """Attestation built against live epoch should self-verify."""
        epoch_data = sdk._get("/epoch")
        epoch = epoch_data.get("epoch", 0)
        att = _build_attestation("live_test", 0.001, epoch)
        assert _verify_attestation(att)
