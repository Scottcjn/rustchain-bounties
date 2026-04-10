# RustChain Telegram Bot — Bounty #2869

A Telegram bot for checking RustChain wallet balance and network status.

## Commands

| Command | Description |
|---------|-------------|
| `/balance <wallet>` | Check RTC balance and USD value |
| `/miners` | List active miners with antiquity multipliers |
| `/epoch` | Current epoch, slot, and pot |
| `/price` | RTC reference price + network stats |
| `/help` | Show all commands |

## Quick Start

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your-bot-token-here"
python bot.py
```

## Get a Bot Token

1. Open Telegram → search **@BotFather**
2. Send `/newbot` and follow prompts
3. Copy the token

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | *(required)* | Token from @BotFather |
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | Node URL |
| `RATE_LIMIT_S` | `5` | Seconds between requests per user |

## Deploy with systemd

```ini
# /etc/systemd/system/rustchain-bot.service
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/rustchain-bot/bot.py
Environment=TELEGRAM_BOT_TOKEN=your-token-here
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now rustchain-bot
```

## Deploy with Railway / Fly.io

```bash
# Railway (one command)
railway up

# Fly.io
fly launch --name rustchain-bot
fly secrets set TELEGRAM_BOT_TOKEN=your-token-here
fly deploy
```

## Wallet

`暖暖`
