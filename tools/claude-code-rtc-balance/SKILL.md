# RustChain RTC Balance — Claude Code Skill

**Bounty:** [#2860](https://github.com/Scottcjn/rustchain-bounties/issues/2860) | **Reward:** 15 RTC

## Overview

This skill adds a `/rtc-balance` slash command to Claude Code that queries your RustChain wallet balance without leaving the terminal.

## Usage

```
/rtc-balance my-wallet-name
```

**Output:**
```
Wallet: my-wallet-name
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Setup

### Option 1: Project-level CLAUDE.md (recommended)

Add to the top of any project's `CLAUDE.md`:

```markdown
## RustChain Wallet Check

You can check any RustChain wallet balance using:

/rtc-balance <wallet-name>

This calls the RustChain public node at https://50.28.86.131
```

### Option 2: Global skill (user-level)

Copy `rtc_balance.sh` to a directory in your PATH, or add this function to your shell rc:

```bash
rtc-balance() {
  wallet="${1:?Usage: rtc-balance <wallet-name>}"
  curl -s "https://50.28.86.131/wallet/balance?miner_id=$wallet" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    bal = d.get("balance", d.get("result", {}).get("balance", "N/A"))
    print(f"Wallet: '"'"'$wallet'"'"'")
    print(f"Balance: {bal} RTC (~\${float(bal)*0.10:.2f} USD)")
except Exception as e:
    print(f"Error parsing response: {e}")
    print("Raw:", sys.stdin.read()[:200])
'
}
```

## API Reference

| Endpoint | Description |
|----------|-------------|
| `GET https://50.28.86.131/wallet/balance?miner_id={name}` | Get RTC balance for wallet |
| `GET https://50.28.86.131/epoch` | Current epoch number + miner count |
| `GET https://50.28.86.131/health` | Node health status |

## Error Handling

The skill handles:
- **Wallet not found** → `Wallet not found: <name>`
- **Node offline** → `Error: Node unreachable at https://50.28.86.131`
- **Rate limited** → `Rate limited. Wait 5s and retry.`

## Implementation

See `rtc_balance.sh` for the full implementation.
