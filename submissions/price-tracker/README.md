# RTC Price Tracker

Track RustChain (RTC) price changes, record history, and set price alerts.

## Features

- 📈 Record and track price changes
- 📊 Price statistics (high, low, average, change %)
- 🚨 Price alerts (above/below target, percent change)
- 📤 Export to CSV
- 💾 Persistent JSON storage

## Installation

```bash
pip install -r requirements.txt
```

No external dependencies required — uses only Python standard library.

## Usage

### Record a price

```bash
python track.py record 0.0045 --source coinmarketcap
```

### View history

```bash
python track.py history -n 50
```

### Price statistics

```bash
python track.py stats
```

### Add price alerts

```bash
# Alert when price goes above $0.01
python track.py add-alert above --target 0.01

# Alert when price drops below $0.003
python track.py add-alert below --target 0.003 --note "Buy signal"

# Alert on 10% change
python track.py add-alert change_percent --percent 10
```

### Export to CSV

```bash
python track.py export -o rtc_prices.csv
```

## Data Storage

- `price_history.json` — Historical price records
- `price_alerts.json` — Active price alerts

## Author

zp6 — RustChain Bounty Submission
