"""Tests for the AgentFolio <-> Beacon reference implementation (no network)."""

import requests

from agentfolio_beacon.agentfolio_beacon_tool import (
    MCP_TOOL,
    AgentFolioBeaconClient,
    TTLCache,
    handle_mcp_tool_call,
)

BEACON_ID = "bcn_my-agent_a1b2c3d4"


class FakeResponse:
    def __init__(self, payload=None, status_code=200, json_error=False):
        self._payload = payload
        self.status_code = status_code
        self._json_error = json_error

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP {0}".format(self.status_code))

    def json(self):
        if self._json_error:
            raise ValueError("invalid json")
        return self._payload


class FakeSession:
    """Returns queued responses/exceptions in call order and records calls."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def make_client(responses, cache=None):
    session = FakeSession(responses)
    return AgentFolioBeaconClient(session=session, cache=cache), session


def test_lookup_happy_path_merges_both_layers():
    client, session = make_client(
        [
            FakeResponse({"beacon": {"agent_name": "my-agent", "status": "active"}}),
            FakeResponse({"agent": {"trust_score": 87.5, "agent_name": "my-agent"}}),
        ]
    )
    result = client.lookup(BEACON_ID)

    assert result["ok"] is True
    assert result["error"] is None
    assert result["degraded"] is False
    assert result["agent_name"] == "my-agent"
    assert result["trust"]["score"] == 87.5
    assert result["trust"]["confidence"] == "high"
    assert result["provenance"]["beacon_status"] == "ok"
    assert result["provenance"]["agentfolio_status"] == "ok"
    assert result["cache"] == {"hit": False, "ttl_seconds": 300.0}
    assert len(session.calls) == 2


def test_invalid_beacon_id_fails_fast_without_network():
    client, session = make_client([])
    result = client.lookup("not-a-beacon")

    assert result["ok"] is False
    assert result["error"] == "invalid_beacon_id"
    assert result["trust"]["confidence"] == "none"
    assert session.calls == []


def test_beacon_offline_degrades_to_satp_score_only():
    client, _ = make_client(
        [
            requests.ConnectionError("beacon down"),
            FakeResponse({"agent": {"trust_score": 42}}),
        ]
    )
    result = client.lookup(BEACON_ID)

    assert result["ok"] is True
    assert result["degraded"] is True
    assert result["trust"]["score"] == 42.0
    assert result["trust"]["confidence"] == "medium"
    assert result["provenance"]["beacon_status"] == "unavailable"
    assert any(w.startswith("beacon_unavailable") for w in result["warnings"])


def test_expired_beacon_is_flagged_but_still_returned():
    client, _ = make_client(
        [
            FakeResponse({"beacon": {"agent_name": "old-agent", "status": "expired"}}),
            FakeResponse({"agent": {"score": 10}}),
        ]
    )
    result = client.lookup(BEACON_ID)

    assert result["ok"] is True
    assert result["degraded"] is True
    assert result["provenance"]["beacon_status"] == "expired"
    assert any(w.startswith("beacon_expired") for w in result["warnings"])
    assert result["trust"]["confidence"] == "medium"


def test_all_sources_unavailable_reports_no_confidence():
    client, _ = make_client(
        [requests.Timeout("beacon timeout"), FakeResponse(status_code=500)]
    )
    result = client.lookup(BEACON_ID)

    assert result["ok"] is False
    assert result["error"] == "all_sources_unavailable"
    assert result["trust"]["score"] is None
    assert result["trust"]["confidence"] == "none"
    assert result["provenance"]["agentfolio_status"] == "unavailable"


def test_malformed_json_is_handled():
    client, _ = make_client([FakeResponse(json_error=True), FakeResponse(json_error=True)])
    result = client.lookup(BEACON_ID)

    assert result["ok"] is False
    assert any(w.startswith("beacon_unavailable: invalid_json") for w in result["warnings"])
    assert any(
        w.startswith("agentfolio_unavailable: invalid_json") for w in result["warnings"]
    )


def test_cache_prevents_duplicate_requests():
    client, session = make_client(
        [
            FakeResponse({"beacon": {"agent_name": "my-agent"}}),
            FakeResponse({"agent": {"trust_score": 55}}),
        ]
    )
    first = client.lookup(BEACON_ID)
    second = client.lookup(BEACON_ID)

    assert first["cache"]["hit"] is False
    assert second["cache"]["hit"] is True
    assert second["trust"]["score"] == 55.0
    assert len(session.calls) == 2


def test_ttl_cache_expiry():
    now = [0.0]
    cache = TTLCache(ttl=300.0, clock=lambda: now[0])
    cache.set("k", {"v": 1})

    assert cache.get("k") == {"v": 1}
    now[0] = 301.0
    assert cache.get("k") is None


def test_mcp_tool_schema_and_dispatch():
    assert MCP_TOOL["name"] == "agentfolio_lookup_beacon"
    assert MCP_TOOL["inputSchema"]["required"] == ["beacon_id"]

    unknown = handle_mcp_tool_call("nope", {})
    assert unknown["ok"] is False
    assert unknown["error"] == "unknown_tool"

    bad_args = handle_mcp_tool_call("agentfolio_lookup_beacon", {"beacon_id": 42})
    assert bad_args["ok"] is False
    assert bad_args["error"] == "invalid_arguments"

    rejected = handle_mcp_tool_call("agentfolio_lookup_beacon", {"beacon_id": "bad"})
    assert rejected["error"] == "invalid_beacon_id"
