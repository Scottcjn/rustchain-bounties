# RustChain Telegram Bot 🤖

> Check wallet balance and miner status via Telegram

## Commands

| Command | Description |
|---------|-------------|
| `/balance <wallet>` | Check RTC balance |
| `/miners` | List active miners |
| `/epoch` | Current epoch info |
| `/price` | Show RTC price |
| `/help` | Show commands |

## Setup

### 1. Get a Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow prompts to create your bot
4. Copy the token

### 2. Install Dependencies

```bash
pip install python-telegram-bot requests
```

### 3. Run

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export NODE_URL="https://50.28.86.131"
python3 bot.py
```

### 4. Deploy (Optional)

#### Railway
```bash
railway init
railway add
railway env set TELEGRAM_BOT_TOKEN=xxx
railway up
```

#### systemd
```bash
sudo cp rustchain-telegram-bot.service /etc/systemd/system/
sudo systemctl enable --now rustchain-telegram-bot
```

## Docker

```bash
docker build -t rustchain-telegram-bot .
docker run -d \
  --name rustchain-bot \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  rustchain-telegram-bot
```

## Rate Limiting

- 1 request per 5 seconds per user
- Prevents API abuse

## License

MIT
