"""AgentFolio <-> Beacon dual-layer trust lookup (reference implementation).

The tool answers one question: "given a Beacon ID, what is the unified
identity + trust picture for that agent?" It pulls from two independent
sources and never lets one source's outage hide the other's data.

Spec: ``agentfolio_beacon/INTEGRATION_SPEC.md``.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests

DEFAULT_BEACON_DIRECTORY_URL = "https://bottube.ai/api/beacon/directory"
DEFAULT_AGENTFOLIO_AGENTS_URL = "https://agentfolio.bot/api/agents"
DEFAULT_TIMEOUT = 8.0
DEFAULT_CACHE_TTL = 300.0
USER_AGENT = "agentfolio-beacon-tool/0.1"

# Beacon ID schema: bcn_<name>_<hash>. The hash is hex; 8 chars is the
# documented length, longer digests are tolerated for forward compatibility.
BEACON_ID_PATTERN = re.compile(r"^bcn_[a-z0-9][a-z0-9._-]{0,62}_[0-9a-f]{8,64}$")

AGENT_NAME_KEYS = ("agent_name", "name", "handle", "agent_id", "miner_id")
TRUST_SCORE_KEYS = ("trust_score", "satp_score", "score", "trust")
RECORD_KEYS = ("beacon", "agent", "record", "data", "result")
EXPIRED_STATUSES = {"expired", "revoked"}


@dataclass
class _CacheEntry:
    value: Dict[str, Any]
    expires_at: float


class TTLCache:
    """Minimal TTL cache keyed by beacon ID (default 5 minute window)."""

    def __init__(self, ttl: float = DEFAULT_CACHE_TTL, clock=time.monotonic) -> None:
        self.ttl = ttl
        self.clock = clock
        self._entries: Dict[str, _CacheEntry] = {}

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at <= self.clock():
            del self._entries[key]
            return None
        return entry.value

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self._entries[key] = _CacheEntry(
            value=value, expires_at=self.clock() + self.ttl
        )

    def clear(self) -> None:
        self._entries.clear()


def _as_record(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Unwrap ``{"beacon": {...}}`` / ``{"agent": {...}}`` style envelopes."""
    if not isinstance(payload, dict):
        return {}
    for key in RECORD_KEYS:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def _first_string(record: Dict[str, Any], keys) -> Optional[str]:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_trust_score(record: Dict[str, Any]) -> Optional[float]:
    for key in TRUST_SCORE_KEYS:
        value = record.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
        if isinstance(value, dict):
            for inner_key in ("score", "value"):
                inner = value.get(inner_key)
                if isinstance(inner, bool):
                    continue
                if isinstance(inner, (int, float)):
                    return float(inner)
                if isinstance(inner, str):
                    try:
                        return float(inner)
                    except ValueError:
                        continue
    return None


class AgentFolioBeaconClient:
    """Pull-based bridge between the Beacon directory and AgentFolio (SATP)."""

    def __init__(
        self,
        beacon_url: str = DEFAULT_BEACON_DIRECTORY_URL,
        agentfolio_url: str = DEFAULT_AGENTFOLIO_AGENTS_URL,
        timeout: float = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
        cache: Optional[TTLCache] = None,
    ) -> None:
        self.beacon_url = beacon_url.rstrip("/")
        self.agentfolio_url = agentfolio_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": USER_AGENT}
        )
        self.cache = cache or TTLCache()

    # ------------------------------------------------------------------ public
    def lookup(self, beacon_id: str) -> Dict[str, Any]:
        """Resolve a Beacon ID into a unified identity + trust object."""
        candidate = beacon_id.strip() if isinstance(beacon_id, str) else ""
        if not BEACON_ID_PATTERN.match(candidate):
            # Fail fast: a malformed ID can never join to a SATP profile.
            return {
                "ok": False,
                "error": "invalid_beacon_id",
                "message": (
                    "Beacon IDs must match bcn_<name>_<hex-hash>, "
                    "e.g. bcn_my-agent_a1b2c3d4"
                ),
                "beacon_id": beacon_id,
                "degraded": True,
                "warnings": ["invalid_beacon_id: rejected before any network call"],
                "trust": {"score": None, "confidence": "none", "source": None},
                "provenance": {},
                "cache": {"hit": False, "ttl_seconds": self.cache.ttl},
            }

        cached = self.cache.get(candidate)
        if cached is not None:
            result = dict(cached)
            result["cache"] = {"hit": True, "ttl_seconds": self.cache.ttl}
            return result

        result = self._compose(candidate)
        self.cache.set(candidate, result)
        fresh = dict(result)
        fresh["cache"] = {"hit": False, "ttl_seconds": self.cache.ttl}
        return fresh

    # ----------------------------------------------------------------- private
    def _compose(self, beacon_id: str) -> Dict[str, Any]:
        beacon_payload, beacon_error = self._fetch_json(
            self.beacon_url, {"beacon_id": beacon_id}
        )
        beacon_record = _as_record(beacon_payload)
        agent_name = (
            _first_string(beacon_record, AGENT_NAME_KEYS)
            or self._name_from_beacon_id(beacon_id)
        )

        agent_payload, agent_error = self._fetch_json(
            self.agentfolio_url, {"agent": agent_name}
        )
        agent_record = _as_record(agent_payload)

        warnings = []
        if beacon_error == "not_found":
            beacon_status = "not_found"
            warnings.append(
                "beacon_not_found: no directory record for this beacon id"
            )
        elif beacon_error:
            beacon_status = "unavailable"
            warnings.append("beacon_unavailable: {0}".format(beacon_error))
        elif (
            beacon_record.get("expired") is True
            or str(beacon_record.get("status", "")).lower() in EXPIRED_STATUSES
        ):
            beacon_status = "expired"
            warnings.append(
                "beacon_expired: stale beacon metadata returned with reduced "
                "confidence"
            )
        else:
            beacon_status = "ok"

        if agent_error == "not_found":
            agentfolio_status = "not_found"
            warnings.append(
                "agentfolio_not_found: no SATP profile for agent '{0}'".format(
                    agent_name
                )
            )
        elif agent_error:
            agentfolio_status = "unavailable"
            warnings.append("agentfolio_unavailable: {0}".format(agent_error))
        else:
            agentfolio_status = "ok"

        trust_score = _extract_trust_score(agent_record)
        if trust_score is not None and beacon_status == "ok":
            confidence = "high"
        elif trust_score is not None:
            confidence = "medium"
        elif beacon_status == "ok":
            confidence = "low"
        else:
            confidence = "none"

        resolved = bool(beacon_record or agent_record)
        return {
            "ok": resolved,
            "error": None if resolved else "all_sources_unavailable",
            "beacon_id": beacon_id,
            "agent_name": agent_name,
            "identity": {
                "beacon": beacon_record or None,
                "agentfolio": agent_record or None,
            },
            "trust": {
                "score": trust_score,
                "scale": "0-100",
                "confidence": confidence,
                "source": "agentfolio" if trust_score is not None else None,
            },
            "provenance": {
                "beacon_id": beacon_id,
                "beacon_source": self.beacon_url,
                "beacon_status": beacon_status,
                "agentfolio_source": self.agentfolio_url,
                "agentfolio_status": agentfolio_status,
            },
            "policy": {
                "malformed_beacon_id": "reject",
                "transport_failure": "degrade",
                "cache_ttl_seconds": self.cache.ttl,
            },
            "degraded": bool(warnings),
            "warnings": warnings,
        }

    def _fetch_json(
        self, url: str, params: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            return None, "request_failed: {0}".format(exc)

        if getattr(response, "status_code", 200) == 404:
            return None, "not_found"
        try:
            response.raise_for_status()
        except requests.RequestException as exc:
            return None, "http_error: {0}".format(exc)
        try:
            payload = response.json()
        except ValueError as exc:
            return None, "invalid_json: {0}".format(exc)
        if not isinstance(payload, dict):
            return None, "unexpected_payload"
        return payload, None

    @staticmethod
    def _name_from_beacon_id(beacon_id: str) -> str:
        body = beacon_id[len("bcn_"):]
        name, _, _digest = body.rpartition("_")
        return name or body


MCP_TOOL: Dict[str, Any] = {
    "name": "agentfolio_lookup_beacon",
    "description": (
        "Resolve a Beacon ID (bcn_<name>_<hash>) into a unified identity "
        "object combining Beacon provenance and the AgentFolio/SATP trust "
        "score. Degrades gracefully when one source is unreachable and "
        "reports confidence plus per-source provenance."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "beacon_id": {
                "type": "string",
                "description": "Beacon identifier, e.g. bcn_my-agent_a1b2c3d4",
            }
        },
        "required": ["beacon_id"],
        "additionalProperties": False,
    },
}

_DEFAULT_CLIENT: Optional[AgentFolioBeaconClient] = None


def get_default_client() -> AgentFolioBeaconClient:
    """Return (and lazily create) the process-wide client, cache included."""
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = AgentFolioBeaconClient()
    return _DEFAULT_CLIENT


def agentfolio_lookup_beacon(beacon_id: str) -> Dict[str, Any]:
    """MCP tool entry point: look up a Beacon ID across both trust layers."""
    return get_default_client().lookup(beacon_id)


def handle_mcp_tool_call(
    name: str, arguments: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Dispatch an MCP ``tools/call`` payload to this module's tools."""
    arguments = arguments or {}
    if name != MCP_TOOL["name"]:
        return {
            "ok": False,
            "error": "unknown_tool",
            "message": "Unknown tool: {0}".format(name),
        }
    beacon_id = arguments.get("beacon_id")
    if not isinstance(beacon_id, str):
        return {
            "ok": False,
            "error": "invalid_arguments",
            "message": "'beacon_id' must be a string",
        }
    return agentfolio_lookup_beacon(beacon_id)
