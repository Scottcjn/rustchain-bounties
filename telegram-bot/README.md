# RustChain Telegram Bot

**Bounty #2869 — 10 RTC**

A Telegram bot that checks RustChain wallet balances and miner status directly from Telegram.

## Features

- 💰 **Wallet Balance** — `/balance <wallet_id>` → RTC balance + pending
- ⛏️ **Miner Status** — `/miner <miner_id>` → 🟢 Active / 🔴 Not attesting
- ⏱️ **Epoch Info** — `/epoch` → current epoch, slot, enrolled miners, next settlement
- 🩺 **Node Health** — `/health` → node online/offline status
- 🎛️ **Inline Buttons** — quick-access keyboard in `/start`

## Quick Start

```bash
# 1. Clone / copy this folder
cd telegram-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env: add your TELEGRAM_BOT_TOKEN

# 4. Run
python bot.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | *(required)* | Token from [@BotFather](https://t.me/BotFather) |
| `RUSTCHAIN_NODE_URL` | `https://50.28.86.131` | RustChain node URL |

## API Endpoints Used

| Endpoint | Purpose |
|---|---|
| `GET /health` | Node health |
| `GET /wallet/balance?wallet_id=<id>` | Wallet balance |
| `GET /api/miners` | Active miners list |
| `GET /epoch` | Epoch info |

## Bot Commands

```
/start   — Welcome message + quick buttons
/balance <wallet_id> — Check RTC balance
/miner   <miner_id>  — Miner attestation status
/epoch               — Current epoch info
/health              — Node health check
/help                — Command list
```

## RTC Wallet

`mtstachowiak`

## License

MIT
