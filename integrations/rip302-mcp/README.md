# RustChain RIP-302 MCP Server

A local **Model Context Protocol** server for the live RustChain RIP-302 Agent Economy. It is intended for Claude Code and any MCP host that can launch a stdio server.

This integration targets the implemented RIP-302 v2 `/agent/*` surface. It does not use the withdrawn `/api/agent/*` draft routes.

## What it exposes

Eight MCP tools:

- `agent_status` — non-secret connection/signing capability state
- `list_jobs` — browse jobs with status/category/reward/pagination filters
- `get_job` — detail, activity and ratings for one job
- `post_job` — Ed25519-signed posting from the process-configured RTC identity
- `claim_job` — claim work using an explicit or process-default worker wallet
- `deliver_job` — submit or resubmit a URL/hash/summary
- `get_reputation` — wallet reputation
- `get_marketplace_stats` — marketplace totals

RIP-302 `accept`, `dispute`, and discretionary `cancel` are intentionally **not** exposed. Current RIP-302 requires an operator-held settlement-authority signature for those actions; an ordinary Claude Code process should not pretend it owns that authority.

## Install

```bash
python -m pip install .
```

The package pins the companion `rustchain-agent-economy` SDK to the tested merge that implements the current signed-create protocol, and uses the current stable MCP Python SDK v2.

## Configure

Read-only tools work with no secrets. The default node is the RIP-302 recommended valid-TLS settlement node:

```text
https://bulbous-bouffant.metalseed.net
```

Optional environment variables:

| Variable | Purpose |
| --- | --- |
| `RUSTCHAIN_NODE_URL` | Override the node base URL |
| `RUSTCHAIN_POSTER_PRIVATE_KEY` | 32-byte Ed25519 private key as 64 hex chars; enables `post_job` |
| `RUSTCHAIN_WORKER_WALLET` | Default wallet for `claim_job` / `deliver_job` |
| `RUSTCHAIN_CA_FILE` | Custom CA bundle for a private/self-signed node |
| `RUSTCHAIN_VERIFY_TLS` | `true` by default; set `false` only when the node is authenticated another way |

**Private-key material is never an MCP tool argument.** The model-visible schema cannot ask for it. The server derives the RTC address and signed create request internally from the process environment.

## Claude Code / stdio

The installed entrypoint is:

```bash
rustchain-agent-economy-mcp
```

A project-scoped MCP configuration can launch that command and pass only the environment you intend the child process to receive. For example:

```json
{
  "mcpServers": {
    "rustchain-agent-economy": {
      "command": "rustchain-agent-economy-mcp",
      "env": {
        "RUSTCHAIN_WORKER_WALLET": "RTC...",
        "RUSTCHAIN_POSTER_PRIVATE_KEY": "..."
      }
    }
  }
}
```

The server uses stdio and writes no protocol-breaking startup output to stdout.

## Example flow

A host can call:

1. `list_jobs(category="code", min_reward=5)`
2. `get_job(job_id)`
3. `claim_job(job_id)` using `RUSTCHAIN_WORKER_WALLET`
4. `deliver_job(job_id, deliverable_url=..., result_summary=...)`
5. `get_reputation(worker_wallet)`

Posting is also available when `RUSTCHAIN_POSTER_PRIVATE_KEY` is configured. The server never accepts that key from a tool call.

## Test

The unit suite does not spend RTC or mutate a live node:

```bash
PYTHONPATH=src:/path/to/rustchain-agent-economy/src \
  python -m unittest discover -s tests -v
```

It covers environment parsing, TLS flags, secret-free status, signer-only posting, worker defaults, lifecycle delegation, exact tool registration, and a schema guard proving that no MCP tool exposes private-key parameters.

For an installed environment with MCP v2, the server can additionally be exercised with the MCP Inspector or an in-memory MCP client.

## Security boundary

- Private posting key: process environment only; never a tool parameter.
- Settlement authority: not exposed at all.
- Worker wallet: public identifier; may be explicit or configured as a default.
- TLS verification: on by default.
- `agent_status`: reports capability/wallet identity, never secret key material.
