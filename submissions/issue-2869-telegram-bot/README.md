# RustChainBot — Telegram Bot

Checks RTC balance and miner status. **Bounty: Scottcjn/rustchain-bounties#2869 (10 RTC)**

## Commands
| Command | Description |
|---------|-------------|
| /start | Welcome message |
| /balance <wallet> | Check RTC balance |
| /miners | Active miners |
| /epoch | Current epoch info |
| /price | RTC reference price ($0.10) |
| /help | Show commands |

## Setup
```bash
pip install python-telegram-bot aiohttp
export TELEGRAM_BOT_TOKEN="your_bot_token"
export RUSTCHAIN_API="https://rustchain.org"
python bot.py
```

## Deploy
```bash
sudo cp rustchain-bot.service /etc/systemd/system/
sudo systemctl enable --now rustchain-bot
```
