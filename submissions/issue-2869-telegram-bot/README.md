# RustChainBot — Telegram Bot

Checks RTC balance and miner status via Telegram.

**Bounty:** Scottcjn/rustchain-bounties#2869

## Setup
```bash
pip install python-telegram-bot aiohttp
export TELEGRAM_BOT_TOKEN="your_bot_token"
export RUSTCHAIN_API="https://rustchain.org/api"
python bot.py
```

## Commands
| Command | Description |
|---------|-------------|
| /start | Welcome message |
| /balance <wallet> | Check RTC balance |
| /miners | Active miners |
| /epoch | Current epoch |
| /price | RTC price |
| /status | Node status |
| /help | Show commands |

## Deploy (systemd)
```bash
sudo cp rustchain-bot.service /etc/systemd/system/
sudo systemctl enable rustchain-bot
sudo systemctl start rustchain-bot
```
