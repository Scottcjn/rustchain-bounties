# rtc-balance — Claude Code Slash Command

**Bounty**: #2860 | **Reward**: 15 RTC  
**Wallet**: `0x6FCBd5d14FB296933A4f5a515933B153bA24370E`

## What This Is

A standalone Python CLI tool + Claude Code skill that checks RustChain wallet balances.

## Usage

```bash
python rtc_balance.py <wallet-name>
```

```
$ python rtc_balance.py agent-001
Wallet: agent-001
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Claude Code Integration

Add to your `CLAUDE.md` or `.claude/commands/`:

```markdown
## /rtc-balance <wallet-name>
Check RustChain wallet balance. Calls the BCOS node API at 50.28.86.131.
```

## Installation

No external dependencies — uses Python stdlib only.

## Testing

```bash
python rtc_balance.py test-wallet
```
