# QR Wallet Address Generator

Generate QR codes for RustChain (RTC) wallet addresses with customizable colors and sizes.

## Features

- 🎨 Customizable foreground and background colors
- 📐 Adjustable QR code size and border
- 💰 Optional amount and label in QR URI
- 📦 Batch generation from JSON config
- ✅ Address validation

## Installation

```bash
pip install qrcode[pil]
```

## Usage

### Generate a single QR code

```bash
python wallet_qr.py generate rtc1abc123def456789 -o my_wallet.png
```

### Custom colors and size

```bash
python wallet_qr.py generate rtc1abc123... -f FF0000 -b 000000 -s 15
```

### With amount and label

```bash
python wallet_qr.py generate rtc1abc123... --amount 100.5 --label "My Wallet"
```

### Batch generation

Create a `config.json`:
```json
[
  {
    "address": "rtc1abc123...",
    "output": "wallet1.png",
    "fill_color": "0066CC",
    "bg_color": "FFFFFF",
    "size": 12
  },
  {
    "address": "rtc1def456...",
    "output": "wallet2.png",
    "fill_color": "CC0000"
  }
]
```

```bash
python wallet_qr.py batch config.json
```

### Validate an address

```bash
python wallet_qr.py validate rtc1abc123def456789
```

## RTC Address Format

- Prefix: `rtc1`
- Length: 40-64 characters
- Characters: alphanumeric after prefix

## QR URI Format

QR codes encode a `rustchain:` URI:
```
rustchain:rtc1abc123...?amount=100.5&label=My%20Wallet
```

## Author

zp6 — RustChain Bounty Submission
