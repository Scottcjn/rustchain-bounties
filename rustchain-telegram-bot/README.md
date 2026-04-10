# RustChain Telegram Bot

A Telegram bot for checking RustChain wallet balances, miners, and epochs.

## Commands
- `/balance <wallet>` - Check RTC wallet balance
- `/miners` - Show active miners count
- `/epoch` - Current epoch information
- `/price` - Show RTC reference price
- `/help` - Show available commands

## Deployment

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Set token:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   ```
3. Run bot:
   ```bash
   python bot.py
   ```
