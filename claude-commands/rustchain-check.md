---
name: rustchain-check
description: Check RustChain wallet balance, miner status, and recent bounties
---

# RustChain Check Command

Check your RustChain wallet balance, miner attestation status, and latest bounties.

## Usage

```
/rustchain-check <wallet-address>
```

Or set `RUSTCHAIN_WALLET` environment variable to skip the address parameter.

## What it does

1. **Wallet Balance** — Fetches and displays your RTC balance
2. **Miner Status** — Shows if your miner is actively attesting
3. **Recent Bounties** — Lists the 5 most recent open bounties
4. **Network Health** — Quick node health check

## Example

```
> /rustchain-check 0x1234567890abcdef1234567890abcdef12345678

🦀 RustChain Status
━━━━━━━━━━━━━━━━━━
💰 Balance: 42.5 RTC
⛏️  Miner: 🟢 Attesting (last epoch)
📋 Open Bounties: 23
❤️  Node: Online (v2.2.1)
```

## Implementation

This slash command uses the RustChain API at `https://api.rustchain.io/v1` to fetch:
- `GET /balance/{address}` — Wallet balance
- `GET /miner/{address}/status` — Miner status
- `GET /bounties?limit=5` — Recent bounties
- `GET /health` — Node health

## Setup

Add to your Claude Code settings:

```json
{
  "commands": {
    "rustchain-check": {
      "script": "claude-commands/rustchain-check.sh",
      "description": "Check RustChain wallet and miner status"
    }
  }
}
```
