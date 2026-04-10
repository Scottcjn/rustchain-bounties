# Claude Code Slash Command: /rtc-balance

Check RustChain wallet balance without leaving the terminal.

## Usage

```
/rtc-balance <wallet_id>
```

### Example

```
/rtc-balance developer-wallet
```

### Output

```
Wallet: developer-wallet
Balance: 42.50 RTC ($4.25 USD)
Epoch: 1847 | Miners online: 14
```

## Installation

### Option 1: Use as Claude Code Skill

1. Copy `.claude/skills/rtc-balance.md` to your project's `.claude/skills/` directory
2. Claude Code will automatically load the skill

### Option 2: Standalone Python Script

```bash
python check_balance.py <wallet_id>
```

## Files

- `.claude/skills/rtc-balance.md` - Claude Code skill definition
- `check_balance.py` - Python helper script for direct API calls

## API Endpoints

- Balance: `GET https://50.28.86.131/wallet/balance?wallet_id={id}`
- Epoch: `GET https://50.28.86.131/epoch`
- Miners: `GET https://50.28.86.131/miners`

## Error Handling

| Error | Message |
|-------|---------|
| Wallet not found | `Wallet not found: <id>` |
| Node offline | `Error: RustChain node is offline` |

## License

MIT