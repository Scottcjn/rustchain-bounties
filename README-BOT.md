# RustChain Telegram Bot

🤖 A Telegram bot that checks RustChain wallet balances and miner status.

## Commands

| Command | Description |
|---------|-------------|
| `/balance <wallet>` | Check RTC balance |
| `/miners` | List active miners |
| `/epoch` | Current epoch info |
| `/price` | Show RTC reference rate ($0.10) |
| `/help` | Show commands |

## Setup (5 Steps)

### 1. Get Telegram Bot Token
- Talk to [@BotFather](https://t.me/BotFather)
- Send `/newbot` and follow instructions
- Copy the token

### 2. Deploy to Railway (Easiest)
```bash
# Fork this repo
git clone https://github.com/yourname/rustchain-bot
cd rustchain-bot

# Create railway.json
echo '{"services": [{"name": "bot", "startCommand": "python rustchain_bot.py"}]}' > railway.json
```

- Go to [Railway.app](https://railway.app)
- Create new project from GitHub repo
- Add environment variable: `TELEGRAM_BOT_TOKEN` = your bot token
- Deploy!

### 3. Deploy to Fly.io (Alternative)
```bash
flyctl launch
flyctl secrets set TELEGRAM_BOT_TOKEN=your_token
flyctl deploy
```

### 4. Test the Bot
- Find your bot: `@RustChainBot` (or your bot name)
- Send `/help`

### 5. Verify All Commands
```
/balance rust-miner-123
/miners
/epoch
/price
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |

## Features

- **Rate Limiting**: 1 request per 5 seconds per user
- **Error Handling**: Graceful offline node handling
- **Markdown Formatting**: Clean output display

## Wallet Address

RTC wallet: `miner-20260508-rustchain` (update when paid)

## License

MIT