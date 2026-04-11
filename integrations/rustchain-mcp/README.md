# RustChain MCP Server

This MCP server lets **Claude Code** (and any MCP-compatible client) query the RustChain network from the terminal.

## Features

Core tools:
- `rustchain_health` — check node health (with automatic failover)
- `rustchain_miners` — list active miners and architectures
- `rustchain_epoch` — fetch current epoch info
- `rustchain_balance` — fetch RTC balance for a wallet/miner_id
- `rustchain_transfer` — **stub** (requires private key / signing; see below)

Agent tools (bounty #2859):
- `rustchain_register_wallet` — register a new agent wallet on the RustChain network
- `rustchain_submit_attestation` — submit hardware fingerprint / proof-of-physical-AI attestation
- `rustchain_bounties` — list open bounties from the GitHub issue tracker (filterable by label)

## Install (Claude Code)

From the repo root:

```bash
cd integrations/rustchain-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add to Claude Code
claude mcp add rustchain "$(pwd)/run.sh"
```

## Usage examples

- Health:
  - `rustchain_health`
- Miners:
  - `rustchain_miners`
- Epoch:
  - `rustchain_epoch`
- Balance:
  - `rustchain_balance miner_id=WALLET_NAME`
- Register wallet:
  - `rustchain_register_wallet wallet_name=my-agent-wallet`
- Submit attestation:
  - `rustchain_submit_attestation wallet_name=my-agent-wallet`
- List bounties:
  - `rustchain_bounties`
  - `rustchain_bounties label=easy max_results=5`

## Transfer tool (important)

RustChain transfer requires a **wallet private key** and a signing/broadcast endpoint.
The bounty prompt mentions `rustchain_transfer` but only provides read-only endpoints in the API reference.

This implementation ships the tool as a **safe stub** that returns a clear error message until the signing API is confirmed.

## Node failover

Primary node: `https://50.28.86.131`

You can override nodes via environment variables:

- `RUSTCHAIN_PRIMARY_URL`
- `RUSTCHAIN_FALLBACK_URLS` (comma-separated)

## GitHub integration (bounties)

`rustchain_bounties` calls the GitHub REST API to list open bounty issues.
Set `GITHUB_TOKEN` environment variable to avoid rate limiting.

## Security

- Never commit private keys.
- If transfer signing is later added, prefer reading keys from environment variables and support a dry-run mode.
