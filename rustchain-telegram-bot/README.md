# RustChain Telegram Bot (@RustChainBot)

> Bounty #2869 — Reward: 10 RTC (~$1.00 USD)

A Telegram bot that lets users check their RustChain wallet balance, miner status, epoch info, and RTC price.

## Features

- `/balance <wallet>` — Check TRX and TRC20 token balances
- `/miners` — List active RustChain miners
- `/epoch` — Current epoch information (pot, miners, slots)
- `/price` — RTC reference rate ($0.10 USD)
- `/help` — Show available commands
- Rate limiting (1 request per 5 seconds per user)
- Error handling for offline nodes

## Requirements

- Python 3.10+
- `python-telegram-bot` v20+
- `httpx`

## Installation

```bash
pip install python-telegram-bot httpx
```

## Usage

### 1. Get a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy the bot token

### 2. Configure

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export RUSTCHAIN_NODE="https://50.28.86.131"  # Optional, default shown
```

### 3. Run

```bash
python bot.py
```

## Deploy Options

### Railway

1. Push this repo to GitHub
2. Connect to Railway
3. Set `TELEGRAM_BOT_TOKEN` as an environment variable
4. Deploy

### Fly.io

```bash
flyctl launch --name rustchain-bot
flyctl secrets set TELEGRAM_BOT_TOKEN=your_token
flyctl deploy
```

### Systemd (VPS)

```bash
sudo tee /etc/systemd/system/rustchain-bot.service << EOF
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/rustchain-bot
Environment=TELEGRAM_BOT_TOKEN=your_token
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now rustchain-bot
```

## Wallet

My RTC wallet for bounty payment: `TTvwY4Y1m5DXNSeoo1W1YuV948mtvNwgnD` (TRC20)

## License

MIT
