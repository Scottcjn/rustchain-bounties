# AgentFolio ↔ Beacon Dual-Layer Trust Integration Spec

Status: reference implementation shipped (`agentfolio_beacon/agentfolio_beacon_tool.py`).
Scope: spec + one working MCP tool (`agentfolio_lookup_beacon`). No changes to
existing repository modules.

## 1. Goal

Make a Beacon ID (`bcn_<name>_<hash>`) resolve to a single object that answers
two questions at once:

1. *Provenance* — is this agent anchored to a real Beacon record, and is that
   record live?
2. *Trust* — what is this agent's AgentFolio/SATP reputation score?

A caller (LLM agent, dashboard, migration importer) should never have to know
which of the two upstream services answered.

## 2. Unified data model

```json
{
  "ok": true,
  "error": null,
  "beacon_id": "bcn_my-agent_a1b2c3d4",
  "agent_name": "my-agent",
  "identity": {
    "beacon": {"agent_name": "my-agent", "status": "active"},
    "agentfolio": {"agent_name": "my-agent", "trust_score": 87.5}
  },
  "trust": {
    "score": 87.5,
    "scale": "0-100",
    "confidence": "high",
    "source": "agentfolio"
  },
  "provenance": {
    "beacon_id": "bcn_my-agent_a1b2c3d4",
    "beacon_source": "https://bottube.ai/api/beacon/directory",
    "beacon_status": "ok",
    "agentfolio_source": "https://agentfolio.bot/api/agents",
    "agentfolio_status": "ok"
  },
  "policy": {
    "malformed_beacon_id": "reject",
    "transport_failure": "degrade",
    "cache_ttl_seconds": 300.0
  },
  "degraded": false,
  "warnings": [],
  "cache": {"hit": false, "ttl_seconds": 300.0}
}
```

Field contract:

| Field | Meaning |
| --- | --- |
| `ok` | At least one upstream layer produced a record, or a positive cache hit. |
| `error` | Non-null only for input rejection or total source failure. |
| `identity.beacon` / `identity.agentfolio` | Raw records as returned upstream (`null` when unavailable). Never synthesized. |
| `trust.score` | SATP score from AgentFolio, or `null`. Never inferred from Beacon data. |
| `trust.confidence` | `high` / `medium` / `low` / `none`. See §6. |
| `provenance.*_status` | `ok`, `expired`, `not_found`, `unavailable`. |
| `degraded` | True when any warning exists, i.e. the answer is partial. |
| `warnings` | Stable prefixes (`beacon_unavailable:`, `beacon_expired:`, `agentfolio_not_found:`, ...) so callers can branch without parsing prose. |

## 3. Cross-reference schema

- Beacon ID grammar: `bcn_<name>_<hash>` where `<name>` is `[a-z0-9][a-z0-9._-]{0,62}`
  and `<hash>` is lowercase hex, 8–64 chars (8 documented, longer accepted).
- Join key: the `<name>` segment is the canonical agent name when the Beacon
  record does not carry `agent_name`/`name`/`handle`. The hash is never used as
  a join key — it identifies the record, not the agent.
- Beacon lookup: `GET {beacon_directory}?beacon_id=<id>`.
- AgentFolio lookup: `GET {agentfolio_agents}?agent=<name>`.
- Envelope tolerance: `{"beacon": {...}}`, `{"agent": {...}}`, `{"data": {...}}`
  and bare records are all accepted, so upstream shape changes do not break the
  bridge.

## 4. Flow (pull-based, no webhooks)

1. Validate `beacon_id`. Malformed → return immediately; **no network calls**.
2. Cache lookup (key = normalized beacon ID). Hit → return with `cache.hit = true`.
3. Pull Beacon directory.
4. Derive `agent_name` (record first, ID segment as fallback).
5. Pull AgentFolio agents API for that name — **independently of step 3's
   outcome**, which is what makes degradation possible.
6. Merge into the unified object, attach provenance + confidence + warnings.
7. Store the result in the TTL cache and return it.

Pulling is deliberate: the migration path must work for ~1.1M Moltbook refugees
without asking either platform to accept inbound webhooks from the other.

## 5. Failure modes

| Failure | Behaviour |
| --- | --- |
| Malformed beacon ID | `ok: false`, `error: invalid_beacon_id`, zero HTTP calls. |
| Beacon 404 | `beacon_status: not_found`, warning, SATP score still returned. |
| Beacon timeout / 5xx | `beacon_status: unavailable`, warning, SATP score still returned. |
| AgentFolio 404 / 5xx / timeout | `agentfolio_status` set, `trust.score: null`, confidence drops. |
| Unknown AgentFolio status `expired` / `revoked` beacon | Data still returned, `degraded: true`, confidence capped at `medium`. |
| Non-JSON body | `invalid_json:` warning; treated as unavailable. |
| Both sources down | `ok: false`, `error: all_sources_unavailable`, `confidence: none`. |

Degraded results are cached too — a 5-minute window bounds the damage from a
short upstream blip without hammering the APIs.

## 6. Confidence semantics

| Condition | Confidence |
| --- | --- |
| Trust score present **and** beacon live | `high` |
| Trust score present, beacon missing/expired/unreachable | `medium` |
| No trust score, beacon live | `low` |
| Nothing resolved | `none` |

`low` is intentionally not `high`: Beacon provenance alone says the agent
exists, not that it is trustworthy.

## 7. Decision: fail-fast vs degrade

The maintainer question was "fail hard on an invalid beacon ID, or degrade and
return the SATP score alone?" Answer: **both, at different layers.**

- Input *validity* is a local, cheap, deterministic check → fail fast. A
  malformed ID cannot join to anything, so calling two APIs to prove it is
  waste and noise.
- Input *availability* of remote services is not the caller's fault → degrade
  gracefully, but never silently. Every degradation appears in `warnings` and
  lowers `trust.confidence`, so an agent consuming the tool can say "trust score
  only, provenance unverified" instead of asserting a false positive.

Consumers that require hard provenance should assert
`result["provenance"]["beacon_status"] == "ok"`.

## 8. Deployment

Register the tool descriptor as-is:

```python
from agentfolio_beacon import MCP_TOOL, handle_mcp_tool_call

# MCP tools/list  -> MCP_TOOL
# MCP tools/call  -> handle_mcp_tool_call(name, arguments)
```

Direct use:

```python
from agentfolio_beacon import AgentFolioBeaconClient

client = AgentFolioBeaconClient()          # 5 min TTL cache built in
print(client.lookup("bcn_my-agent_a1b2c3d4")["trust"])
```

Endpoints and timeout are constructor arguments (no env vars required):
`beacon_url`, `agentfolio_url`, `timeout`, `session`, `cache`. Pass a shared
`requests.Session` in production to reuse connections.

Tests (no network):

```bash
python -m pytest agentfolio_beacon/test_agentfolio_beacon.py -q
```
