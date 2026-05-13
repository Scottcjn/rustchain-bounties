# RustChain Telegram Bot

A **read-only** Telegram bot that queries the RustChain blockchain API.
No transfer, no wallet private keys, no sending functionality — purely informational.

## Commands

| Command | Description |
|---|---|
| `/balance <wallet>` | Query a wallet's RTC balance |
| `/epoch` | Current epoch information |
| `/miners` | Miner status overview |
| `/price` | RTC price info |
| `/help` | Show help message |

## Prerequisites

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/legendhy/rustchain-bounties.git
cd rustchain-bounties/rtc-telegram-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your bot token
export RTC_BOT_TOKEN="your-telegram-bot-token"

# 4. Run the bot
python bot.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `RTC_BOT_TOKEN` | *(required)* | Telegram Bot API token |
| `RTC_API_BASE` | `https://rustchain.org` | RustChain API base URL |
| `RTC_API_TIMEOUT` | `10` | API request timeout in seconds |

## Deployment (systemd)

Create `/etc/systemd/system/rtc-telegram-bot.service`:

```ini
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=rtcbot
WorkingDirectory=/opt/rtc-telegram-bot
ExecStart=/usr/bin/python3 bot.py
Environment=RTC_BOT_TOKEN=your-token-here
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now rtc-telegram-bot
```

## Deployment (Docker)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

```bash
docker build -t rtc-telegram-bot .
docker run -d --name rtc-bot -e RTC_BOT_TOKEN=your-token rtc-telegram-bot
```

## Security

This bot is **strictly read-only**. It only performs GET requests to the RustChain API.
- ❌ No wallet private keys
- ❌ No transfer/send functionality
- ❌ No write operations of any kind

## License

MIT
