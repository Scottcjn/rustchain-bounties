#!/usr/bin/env python3
"""
RustChain Telegram Bot
Commands: /balance, /miners, /epoch, /price, /help
"""

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
RTC_PRICE = 0.10  # Reference rate

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data='balance')],
        [InlineKeyboardButton("⛏️ Active Miners", callback_data='miners')],
        [InlineKeyboardButton("📊 Current Epoch", callback_data='epoch')],
    ]
    await update.message.reply_text(
        "👋 Welcome to RustChain Bot!\n\n"
        "I help you check your wallet and mining status.\n\n"
        "Commands:\n"
        "/balance <wallet> - Check RTC balance\n"
        "/miners - List active miners\n"
        "/epoch - Current epoch info\n"
        "/price - RTC reference rate\n"
        "/help - Show all commands",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check wallet balance"""
    if not context.args:
        await update.message.reply_text(
            "Usage: /balance <wallet_address>\n"
            "Example: /balance 0x1234..."
        )
        return

    wallet = context.args[0]

    # API call would go here
    # For now, return placeholder
    balance_rtc = 1250.50
    balance_usd = balance_rtc * RTC_PRICE

    await update.message.reply_text(
        f"💼 Wallet Balance\n\n"
        f"📍 Address: {wallet[:8]}...{wallet[-6:]}\n"
        f"💰 Balance: {balance_rtc:,.2f} RTC\n"
        f"💵 USD Value: ${balance_usd:,.2f}\n"
        f"📊 Rate: $0.10/RTC"
    )

async def miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List active miners"""
    # API call would go here
    miners_list = [
        {"name": "miner-alpha", "hashrate": "1.2 GH/s", "uptime": "99.5%"},
        {"name": "miner-beta", "hashrate": "850 MH/s", "uptime": "98.2%"},
        {"name": "miner-gamma", "hashrate": "2.1 GH/s", "uptime": "99.9%"},
    ]

    message = "⛏️ Active Miners\n\n"
    for i, miner in enumerate(miners_list, 1):
        message += f"{i}. {miner['name']}\n"
        message += f"   📊 Hashrate: {miner['hashrate']}\n"
        message += f"   ⏱️ Uptime: {miner['uptime']}\n\n"

    message += f"Total Active: {len(miners_list)}"

    await update.message.reply_text(message)

async def epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Current epoch information"""
    # API call would go here
    epoch_data = {
        "number": 15420,
        "start_time": "2026-04-11 00:00:00 UTC",
        "blocks_mined": 1440,
        "difficulty": "1.2T",
        "reward_per_block": 50
    }

    await update.message.reply_text(
        f"📊 Current Epoch\n\n"
        f"🔢 Epoch: #{epoch_data['number']}\n"
        f"⏰ Started: {epoch_data['start_time']}\n"
        f"📦 Blocks: {epoch_data['blocks_mined']}\n"
        f"🎯 Difficulty: {epoch_data['difficulty']}\n"
        f"💰 Reward: {epoch_data['reward_per_block']} RTC/block"
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """RTC reference rate"""
    await update.message.reply_text(
        f"💰 RTC Price Information\n\n"
        f"📊 Reference Rate: $0.10 USD\n"
        f"💎 Market Price: N/A (Not listed)\n"
        f"📝 Note: This is the official reference rate\n"
        f"        used for bounty calculations.\n\n"
        f"#rustchain #rtc"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    await update.message.reply_text(
        "📚 RustChain Bot Help\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/balance <wallet> - Check RTC balance\n"
        "/miners - List active miners\n"
        "/epoch - Current epoch info\n"
        "/price - RTC reference rate\n"
        "/help - This message\n\n"
        "🔗 Links:\n"
        "• Website: https://rustchain.org\n"
        "• GitHub: https://github.com/Scottcjn/Rustchain\n"
        "• Docs: https://docs.rustchain.org"
    )

def main():
    """Run the bot"""
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("miners", miners))
    app.add_handler(CommandHandler("epoch", epoch))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 RustChain Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
