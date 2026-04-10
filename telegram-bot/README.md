# Telegram Bot for RustChain

A Telegram bot that lets users check their RustChain wallet balance and miner status.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your-bot-token"
export RUSTCHAIN_NODE_URL="https://50.28.86.131"

# Run
python bot.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/balance <wallet>` | Check RTC wallet balance |
| `/miners` | List active miners |
| `/epoch` | Current epoch info |
| `/price` | Show RTC reference rate |
| `/help` | Show available commands |

## Deploy

### Systemd (Linux)

```bash
sudo cp rustchain-telegram-bot.service /etc/systemd/system/
sudo systemctl enable --now rustchain-telegram-bot
```

### Docker

```bash
docker build -t rustchain-telegram-bot .
docker run -d \
  -e TELEGRAM_BOT_TOKEN=your-token \
  -e RUSTCHAIN_NODE_URL=https://50.28.86.131 \
  --name rtc-bot \
  rustchain-telegram-bot
```

### Railway / Fly.io

Set `TELEGRAM_BOT_TOKEN` and `RUSTCHAIN_NODE_URL` as environment variables, then deploy.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | (required) | Telegram bot token from @BotFather |
| `RUSTCHAIN_NODE_URL` | `https://50.28.86.131` | RustChain node API URL |
| `RATE_LIMIT_SECONDS` | `5` | Min seconds between requests per user |

## License

MIT
