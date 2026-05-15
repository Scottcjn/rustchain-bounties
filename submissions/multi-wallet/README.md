# Multi-Wallet Manager

Manage multiple RustChain (RTC) wallets with balance summaries and transfer templates.

## Features

- 💼 Add/remove multiple wallets with aliases
- 📊 Balance summary across all wallets
- 🏷️ Group wallets by category (e.g., trading, savings, staking)
- 📋 Transfer templates for recurring transactions
- 📤 Export wallet data (addresses only)
- 💾 Persistent JSON storage

## Installation

No external dependencies — uses only Python standard library.

```bash
# Just run it
python manage.py --help
```

## Usage

### Add wallets

```bash
python manage.py add savings rtc1abc123... --group savings
python manage.py add trading rtc1def456... --group trading -n "Main trading wallet"
```

### List wallets

```bash
python manage.py list
python manage.py list --group savings
```

### Update balances

```bash
python manage.py update-balance savings 1500.5
```

### Balance summary

```bash
python manage.py summary
```

### Transfer templates

```bash
# Create a template
python manage.py add-template weekly-savings --from trading --to rtc1abc123... --amount 100

# Preview a template
python manage.py apply-template weekly-savings

# List templates
python manage.py list-templates
```

### Export

```bash
python manage.py export -o my_wallets.json
```

## Data Storage

- `wallets.json` — Wallet data (addresses, balances, groups)
- `transfer_templates.json` — Transfer templates

## Author

zp6 — RustChain Bounty Submission
