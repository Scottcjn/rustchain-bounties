# RustChain Telegram Bot

A Telegram bot for checking RustChain wallet balances and miner status.

## Commands

| Command | Description |
|---------|-------------|
| /balance <wallet> | Check RTC balance for a wallet |
| /miners | List active miners |
| /epoch | Current epoch info |
| /price | RTC reference rate (.10) |
| /help | Show help |

## Features

- Rate limiting (1 request per 5 seconds per user)
- Error handling for offline nodes
- Clean, simple interface

## Setup

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)

### Installation

`ash
pip install -r requirements.txt
`

### Configuration

Set environment variables:

`ash
export TELEGRAM_BOT_TOKEN=your_bot_token_here
export NODE_URL=https://50.28.86.131
`

### Run

`ash
python bot.py
`

## Deploy

### systemd (Linux)

`ini
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/rustchain-bot
ExecStart=/usr/bin/python3 bot.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
`

### Railway

1. Connect GitHub repo
2. Set TELEGRAM_BOT_TOKEN environment variable
3. Deploy

## License

MIT