# RustChain MCP Server

This MCP server lets **Claude Code** (and any MCP-compatible client) query the RustChain network from the terminal.

## Features

Required tools (bounty minimum):
- `rustchain_health` — check node health (with automatic failover)
- `rustchain_miners` — list active miners and architectures
- `rustchain_epoch` — fetch current epoch info
- `rustchain_balance` — fetch RTC balance for a wallet/miner_id
- `rustchain_transfer` — **stub** (requires private key / signing; see below)

Bonus tools (optional):
- `rustchain_ledger` — stub
- `rustchain_register_wallet` — stub
- `rustchain_bounties` — list bounties from this repo (local file parsing)

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

## Transfer tool (important)

RustChain transfer requires a **wallet private key** and a signing/broadcast endpoint.
The bounty prompt mentions `rustchain_transfer` but only provides read-only endpoints in the API reference.

This implementation ships the tool as a **safe stub** that returns a clear error message until the signing API is confirmed.

## Node failover

Primary node: `https://50.28.86.131`

You can override nodes via environment variables:

- `RUSTCHAIN_PRIMARY_URL`
- `RUSTCHAIN_FALLBACK_URLS` (comma-separated)

## Security

- Never commit private keys.
- If transfer signing is later added, prefer reading keys from environment variables and support a dry-run mode.
