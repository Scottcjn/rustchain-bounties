# [BOUNTY #2860] Claude Code Slash Command — /rtc-balance

**Reward: 15 RTC** | Submitter: yw13931835525-cyber

## Overview

This submission provides a Claude Code custom slash command that lets any developer check their RustChain wallet balance without leaving the terminal.

## Files

- `SKILL.md` — The skill definition for Claude Code
- `rtc_balance.py` — Python backend script for the API call
- `README.md` — Installation and usage instructions

---

## SKILL.md

```markdown
# rtc-balance — Check RustChain Wallet Balance

Check the RTC token balance of any RustChain wallet.

## Usage

```
/rtc-balance <wallet_name>
```

## Examples

```
/rtc-balance miner-farmer-42
/rtc-balance alice-wallet
/rtc-balance bob-main
```

## Output Format

When successful:
```
 Wallet: miner-farmer-42
 Balance: 142.50 RTC ($14.25 USD)
 Epoch: 1847 | Miners online: 14
```

When wallet not found:
```
 Error: Wallet "invalid-wallet" not found
 Check your wallet name and try again.
```

When node offline:
```
 Error: Cannot reach RustChain node (50.28.86.131)
 Node may be temporarily unavailable. Try again in a few minutes.
```

## Technical Details

- Calls: GET https://50.28.86.131/wallet/balance?wallet_id={name}
- Calls: GET https://50.28.86.131/epoch (for epoch info)
- Timeout: 10 seconds
- Error handling: Graceful degradation if epoch API fails

## Installation

1. Copy this file to your Claude Code skills directory:
   - macOS/Linux: ~/.claude/skills/rtc-balance/SKILL.md
   - or place in project .claude/skills/rtc-balance/SKILL.md

2. Install the Python helper (optional but recommended):
   ```bash
   pip install requests
   ```

3. The skill also calls the raw API via curl if Python is unavailable.

## Notes

- Wallet names are case-sensitive
- Balance shown in RTC and approximate USD (at $0.10/RTC)
- RTC price is a reference rate, not a market price
```

---

## rtc_balance.py

```python
#!/usr/bin/env python3
"""
RustChain Wallet Balance Checker
Usage: python rtc_balance.py <wallet_name>
"""

import sys
import requests
import json

NODE_URL = "https://50.28.86.131"
RTC_USD_RATE = 0.10  # Reference rate


def get_balance(wallet_name: str) -> dict:
    """Fetch wallet balance from RustChain node."""
    try:
        resp = requests.get(
            f"{NODE_URL}/wallet/balance",
            params={"wallet_id": wallet_name},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"error": "Node request timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot reach RustChain node"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f'Wallet "{wallet_name}" not found'}
        return {"error": f"HTTP {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_epoch() -> dict:
    """Fetch current epoch info."""
    try:
        resp = requests.get(f"{NODE_URL}/epoch", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return {}


def format_output(wallet_name: str) -> str:
    """Format the balance output for display."""
    balance_data = get_balance(wallet_name)
    
    if "error" in balance_data:
        return f" Error: {balance_data['error']}"
    
    balance = balance_data.get("balance", 0)
    usd_value = balance * RTC_USD_RATE
    
    epoch_data = get_epoch()
    epoch = epoch_data.get("epoch", "N/A")
    miners = epoch_data.get("miners_online", "N/A")
    
    return (
        f" Wallet: {wallet_name}\n"
        f" Balance: {balance:.2f} RTC (${usd_value:.2f} USD)\n"
        f" Epoch: {epoch} | Miners online: {miners}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(" Usage: python rtc_balance.py <wallet_name>")
        sys.exit(1)
    
    wallet = sys.argv[1]
    print(format_output(wallet))
```

---

## README.md

# /rtc-balance — Claude Code Skill for RustChain

Check your RustChain wallet balance from anywhere in Claude Code.

## Install

### Option A: Claude Code Skill (Recommended)

Copy `SKILL.md` to:
```bash
mkdir -p ~/.claude/skills/rtc-balance
cp SKILL.md ~/.claude/skills/rtc-balance/SKILL.md
```

### Option B: Python Script (Direct)

```bash
pip install requests
chmod +x rtc_balance.py
./rtc_balance.py your-wallet-name
```

## Usage

```
/rtc-balance my-wallet
```

Sample output:
```
 Wallet: my-wallet
 Balance: 42.50 RTC ($4.25 USD)
 Epoch: 1847 | Miners online: 14
```

## API Endpoint

- Node: `https://50.28.86.131`
- Balance endpoint: `GET /wallet/balance?wallet_id={name}`
- Epoch endpoint: `GET /epoch`

## Author

GitHub: yw13931835525-cyber  
Wallet: EVM 0x6FCBd5d14FB296933A4f5a515933B153bA24370E

## References

- Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2860
- RustChain: https://rustchain.org
