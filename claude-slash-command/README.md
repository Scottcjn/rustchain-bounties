# /rtc-balance — Claude Code Slash Command

Check your RustChain miner balance without leaving the terminal.

## Install

Copy the skill file to your project:

```bash
mkdir -p .claude/skills
cp rtc-balance.md .claude/skills/rtc-balance.md
```

Or add the content to your project's `CLAUDE.md`.

## Use in Claude Code

```
/rtc-balance my-miner
```

Output:
```
Miner:   my-miner
Balance: 42.50 RTC ($4.25 USD)
Epoch:   1847 | Miners online: 14
```

## Use standalone

```bash
python3 check_balance.py my-miner
```

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)
- Network access to `50.28.86.131`

## Error handling

| Situation | Output |
|-----------|--------|
| Miner not found | `Error: miner_id or address required` |
| Node offline | `Node offline or unreachable: ...` |
| HTTP error | `Node error: HTTP 500` |

## Files

| File | Purpose |
|------|---------|
| `.claude/skills/rtc-balance.md` | Claude Code skill definition |
| `claude-slash-command/check_balance.py` | Standalone Python script |
| `claude-slash-command/README.md` | This file |
