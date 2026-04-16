# RustChain Telegram Bot — @RustChainBot

**Bounty:** [#2869](https://github.com/Scottcjn/rustchain-bounties/issues/2869) | **Reward: 10 RTC**

A Telegram bot that lets users check their RustChain wallet and miner status.

## Commands

| Command | Description |
|---------|-------------|
| `/balance <wallet>` | Check RTC balance |
| `/miners` | List active miners |
| `/epoch` | Current epoch info |
| `/price` | Show RTC reference rate ($0.10) |
| `/help` | Show commands |

## Features

- ✅ Rate limiting (1 request per 5 seconds per user)
- ✅ Error handling for offline nodes
- ✅ Markdown-formatted responses
- ✅ CLI mode (no Telegram token required)
- ✅ Configurable node URL via `RTC_NODE_URL` env var

## Setup

### 1. Get a Telegram Bot Token

Message [@BotFather](https://t.me/BotFather) on Telegram:
```
/newbot
```
Follow the prompts and copy your token.

### 2. Install Dependencies

```bash
pip install python-telegram-bot>=20
```

### 3. Run

**Telegram mode:**
```bash
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
python3 tools/telegram_bot.py telegram "$TELEGRAM_BOT_TOKEN"
```

**CLI mode (no bot required):**
```bash
python3 tools/telegram_bot.py cli balance chenzhizhuan
python3 tools/telegram_bot.py cli miners
python3 tools/telegram_bot.py cli epoch
python3 tools/telegram_bot.py cli price
```

### 4. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | (required in telegram mode) | Telegram bot token |
| `RTC_NODE_URL` | `http://50.28.86.131:8099` | RustChain node URL |

## Deployment

### systemd (Linux server)

```ini
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/rustchain-bounties
ExecStart=/usr/bin/python3 tools/telegram_bot.py telegram "YOUR_TOKEN"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo cp rustchain-telegram-bot.service /etc/systemd/system/
sudo systemctl enable rustchain-telegram-bot
sudo systemctl start rustchain-telegram-bot
```

### Railway

1. Connect your GitHub repo to [Railway](https://railway.app)
2. Add environment variable: `TELEGRAM_BOT_TOKEN`
3. Set start command: `python3 tools/telegram_bot.py telegram $TELEGRAM_BOT_TOKEN`

### Fly.io

```bash
fly launch
fly secrets set TELEGRAM_BOT_TOKEN="your-token"
fly deploy
```

## API Endpoints

The bot queries these RustChain node endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /wallet/balance?wallet_id=<name>` | Check wallet balance |
| `GET /api/miners` | List active miners |
| `GET /epoch` | Current epoch info |
| `GET /health` | Node health check |

Default node: `http://50.28.86.131:8099`

## Architecture

```
┌──────────────┐     ┌───────────────────┐     ┌──────────────────┐
│ Telegram     │────▶│  telegram_bot.py  │────▶│  RustChain Node   │
│ User         │◀────│  (python-telegram │◀────│  (50.28.86.131   │
│              │     │   -bot v20+)      │     │   :8099)         │
└──────────────┘     └───────────────────┘     └──────────────────┘
```

## License

MIT — part of [Scottcjn/rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties)

## Contributor

RTC Wallet: `chenzhizhuan` (for bounty payout)
