# Claude Code Slash Command: /rtc-balance

Check your RustChain wallet balance without leaving the terminal.

## Installation

### Option 1: Copy to your project

```bash
# Copy the command to your Claude Code project
cp -r .claude/commands/rtc-balance.md /path/to/your/project/.claude/commands/
```

### Option 2: Global installation

```bash
# Add to your Claude Code skills directory
mkdir -p ~/.claude/commands
cp .claude/commands/rtc-balance.md ~/.claude/commands/
```

## Usage

```
/rtc-balance my-wallet-name
```

## Output

```
Wallet: my-wallet-name
Balance: 42.50 RTC ($4.25 USD)
Last Claim: 2024-01-15
Epoch: 1847 | Miners online: 14
```

## Files

```
.
├── .claude/
│   └── commands/
│       └── rtc-balance.md    # Slash command definition
├── rtc_balance.py            # Python script
└── README.md
```

## Requirements

- Python 3.6+
- `requests` library

```bash
pip install requests
```
