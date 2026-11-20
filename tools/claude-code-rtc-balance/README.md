# Claude Code Slash Command — `/rtc-balance`

**Bounty:** [#2860](https://github.com/Scottcjn/rustchain-bounties/issues/2860) | **Reward:** 15 RTC

A Claude Code skill that checks RustChain wallet balances from the terminal.

## What it does

```
/rtc-balance my-wallet-name
```

```
Wallet: my-wallet-name
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill documentation |
| `CLAUDE.md` | Snippet to paste into any project's CLAUDE.md |
| `rtc_balance.sh` | Bash implementation (macOS/Linux) |
| `rtc_balance.py` | Python implementation (cross-platform) |
| `test_rtc_balance.py` | Unit tests |

## Quick Install

```bash
# Clone
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/tools/claude-code-rtc-balance

# Bash version
chmod +x rtc_balance.sh
sudo cp rtc_balance.sh /usr/local/bin/rtc-balance

# Python version
pip install requests  # optional, uses stdlib by default
chmod +x rtc_balance.py
sudo cp rtc_balance.py /usr/local/bin/rtc-balance
```

## Usage in Claude Code

### Option A: Project-level (recommended)

Add to your `CLAUDE.md`:

```
## RustChain Wallet Check
/rtc-balance <wallet-name>
```

### Option B: Copy script to PATH

```bash
cp tools/claude-code-rtc-balance/rtc_balance.sh ~/bin/rtc-balance
```

Then use it anywhere in Claude Code:

```
/rtc-balance agent-001
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET https://50.28.86.131/wallet/balance?miner_id={name}` | Get wallet RTC balance |
| `GET https://50.28.86.131/epoch` | Current epoch + miner count |
| `GET https://50.28.86.131/health` | Node health |

## Error Handling

- **Wallet not found** → Graceful error with raw response preview
- **Node offline** → `Error: Node unreachable` with retry hint
- **Rate limited** → Wait 5 seconds message

## Acceptance Criteria

- [x] Works as a Claude Code skill (`/rtc-balance <wallet>`)
- [x] Handles errors gracefully (wallet not found, node offline)
- [x] README with install instructions
- [x] Bash + Python implementations
