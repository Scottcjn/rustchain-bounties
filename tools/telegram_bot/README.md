# RustChain Telegram Community Bot

A Telegram bot for the RustChain community built with `python-telegram-bot`.
It exposes live network data from the public RustChain node and supports bonus
alerts and inline queries.

## Commands

| Command | Description |
|---|---|
| `/price` | Current wRTC price (via Raydium) |
| `/miners` | Active miner count |
| `/epoch` | Current epoch info |
| `/balance <wallet>` | RTC balance for a wallet / public key |
| `/health` | Node health status |
| `/start` | Welcome message + command list |

### Bonus features

- **Mining alerts** — a chat is notified when a new miner joins or an epoch settles.
- **Price alerts** — a chat is notified when wRTC moves >5% between checks.
- **Inline queries** — type `@YourBot price` or `@YourBot epoch` in any chat.

## Setup

```bash
# 1. Move into the bot folder
cd tools/telegram_bot

# 2. (Recommended) create a virtualenv
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env and set TELEGRAM_BOT_TOKEN from @BotFather

# 5. Run
python bot.py
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | *(required)* | Token from [@BotFather](https://t.me/BotFather) |
| `RUSTCHAIN_API_BASE` | `https://50.28.86.131` | RustChain node base URL |
| `RUSTCHAIN_VERIFY_TLS` | `0` | Set `1` to verify TLS (node uses a self-signed cert) |
| `RUSTCHAIN_REQUEST_TIMEOUT` | `10` | Per-request timeout (seconds) |
| `RUSTCHAIN_ALERT_CHAT_IDS` | *(empty)* | Comma-separated chat ids for bonus alerts |

## API endpoints used

| Endpoint | Purpose |
|---|---|
| `GET /health` | Node health |
| `GET /epoch` | Epoch info |
| `GET /api/miners` | Active miners |
| `GET /balance/{wallet}` | Wallet RTC balance |
| Raydium pairs API | wRTC price |

## Notes

The public RustChain node serves a self-signed certificate, so TLS verification
is disabled by default (mirroring `curl -k` in the docs). Set
`RUSTCHAIN_VERIFY_TLS=1` for a node with a trusted certificate.

## License

MIT
