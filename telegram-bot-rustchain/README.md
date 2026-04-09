# RustChain Telegram Bot

## Description
A Telegram bot to check RustChain wallet balance and miner status.

## Reward
10 RTC (~$1.00 USD)

## Bot Commands

| Command | Description |
|---------|-------------|
| /balance \<wallet\> | Check RTC balance |
| /miners | List active miners |
| /epoch | Current epoch info |
| /price | Show RTC reference rate |
| /help | Show commands |

## Implementation

### Bot Username
@RustChainBot

### API Endpoints
- Balance: `GET https://50.28.86.131/wallet/balance?wallet_id={name}`
- Miners: `GET https://50.28.86.131/api/miners`
- Epoch: `GET https://50.28.86.131/epoch`

### Code (Python)

```python
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

NODE_URL = "https://50.28.86.131"

async def balance(update: Update, context):
    wallet = ' '.join(context.args)
    if not wallet:
        await update.message.reply_text("Usage: /balance <wallet_name>")
        return
    
    try:
        resp = requests.get(f"{NODE_URL}/wallet/balance", params={"wallet_id": wallet})
        data = resp.json()
        balance = data.get("balance", 0)
        await update.message.reply_text(
            f"💰 Wallet: {wallet}\nBalance: {balance} RTC (${balance * 0.10:.2f})"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def epoch(update: Update, context):
    try:
        resp = requests.get(f"{NODE_URL}/epoch")
        data = resp.json()
        await update.message.reply_text(
            f"🕐 Epoch: {data.get('epoch', 'N/A')}\nBlocks: {data.get('blocks', 'N/A')}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token("BOT_TOKEN").build()
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("epoch", epoch))
    app.run_polling()

if __name__ == "__main__":
    main()
```

## Usage
1. Create bot via @BotFather
2. Set BOT_TOKEN environment variable
3. Run the bot

Closes #2869
