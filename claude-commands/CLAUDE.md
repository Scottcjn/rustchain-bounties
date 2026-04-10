# RustChain Claude Code Skills

A set of Claude Code custom commands for interacting with RustChain.

## Install

Copy the `claude-commands/` directory to your project or home directory:

```bash
# For a specific project
cp -r claude-commands/ /path/to/your/project/.claude/

# Or globally (Claude Code will pick up from current directory)
```

## Available Commands

### `/rtc-balance <wallet>`

Check RTC wallet balance:

```
/rtc-balance nox-ventures
→ Wallet: nox-ventures
  Balance: 42.50 RTC ($4.25 USD)
  Miners online: 14
  Epoch: 1847 | Next in: 3h 21m
```

### `/rtc-status`

Check network status:

```
/rtc-status
→ RustChain Network Status
  Status: Online
  Version: 2.2.1-rip200
  Uptime: 2468h
  Active Miners: 14
  Epoch: 1847
```

### `/rtc-bounties [limit]`

List open bounties:

```
/rtc-bounties
rtc-bounties 5
→ 💰 Open Bounties (top 5)
   #2861 | 50 RTC | Autonomous AI Agent
   #2868 | 30 RTC | VSCode Extension
   #2867 | 100RTC | Security Audit
```

## Files

```
claude-commands/
├── CLAUDE.md          — This file
├── rtc-balance.md     — /rtc-balance command
├── rtc-status.md      — /rtc-status command
└── rtc-bounties.md   — /rtc-bounties command
```

## Implementation

These commands call `rtc.py` (a Python CLI tool):

```bash
python rtc.py balance <wallet>
python rtc.py status
python rtc.py bounties [limit]
```

## Python CLI Tool

See `rtc.py` in this repo for the full implementation.
