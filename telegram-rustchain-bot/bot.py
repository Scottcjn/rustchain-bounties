#!/usr/bin/env python3
"""
RustChain Telegram Bot
Check wallet balance and miner status via Telegram
"""

import os
import logging
from typing import Optional
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configuration
NODE_URL = os.environ.get("NODE_URL", "https://50.28.86.131")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USERS = os.environ.get("ALLOWED_USER_IDS", "").split(",") if os.environ.get("ALLOWED_USER_IDS") else []

# Rate limiting
user_last_request = {}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_rate_limit(user_id: int) -> bool:
    """Rate limit: 1 request per 5 seconds."""
    import time
    current = time.time()
    if user_id in user_last_request:
        if current - user_last_request[user_id] < 5:
            return False
    user_last_request[user_id] = current
    return True


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🤖 *RustChain Bot*\n\n"
        "Commands:\n"
        "/balance <wallet> - Check RTC balance\n"
        "/miners - List active miners\n"
        "/epoch - Current epoch info\n"
        "/price - Show RTC price\n"
        "/help - Show this help",
        parse_mode="Markdown"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await cmd_start(update, ctx)


async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /balance <wallet> command."""
    if not await check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Rate limited. Try again in 5 seconds.")
        return

    if not ctx.args:
        await update.message.reply_text("Usage: /balance <wallet_name>")
        return

    wallet = ctx.args[0]
    
    try:
        resp = requests.get(f"{NODE_URL}/wallet/balance", params={"wallet_id": wallet}, timeout=10)
        data = resp.json()
        
        balance = data.get("balance", "Unknown")
        last_claim = data.get("lastClaim", "Never")
        
        await update.message.reply_text(
            f"💰 *Wallet: {wallet}*\n\n"
            f"Balance: *{balance} RTC*\n"
            f"Last Claim: {last_claim}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Balance check failed: {e}")
        await update.message.reply_text(f"❌ Error: Could not fetch balance. Node may be offline.")


async def cmd_miners(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /miners command."""
    if not await check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Rate limited. Try again in 5 seconds.")
        return

    try:
        resp = requests.get(f"{NODE_URL}/api/miners", timeout=10)
        data = resp.json()
        miners = data.get("miners", [])[:10]  # Top 10
        
        if not miners:
            await update.message.reply_text("No active miners found.")
            return
        
        text = "⛏️ *Top Miners*\n\n"
        for i, m in enumerate(miners, 1):
            wallet = m.get("wallet", "Unknown")
            status = "🟢" if m.get("status") == "active" else "🔴"
            text += f"{i}. {status} {wallet}\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Miners fetch failed: {e}")
        await update.message.reply_text("❌ Error: Could not fetch miners. Node may be offline.")


async def cmd_epoch(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /epoch command."""
    if not await check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Rate limited. Try again in 5 seconds.")
        return

    try:
        resp = requests.get(f"{NODE_URL}/epoch", timeout=10)
        data = resp.json()
        
        epoch = data.get("epoch", "?")
        blocks = data.get("blocksRemaining", "?")
        start = data.get("startTime", "?")
        
        await update.message.reply_text(
            f"📅 *Epoch #{epoch}*\n\n"
            f"Blocks Remaining: *{blocks}*\n"
            f"Started: {start}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Epoch fetch failed: {e}")
        await update.message.reply_text("❌ Error: Could not fetch epoch. Node may be offline.")


async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Handle /price command."""
    if not await check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Rate limited. Try again in 5 seconds.")
        return

    await update.message.reply_text(
        "💵 *RTC Price*\n\n"
        "Reference Rate: *$0.10 USD*\n\n"
        "Note: Price may vary on exchanges.",
        parse_mode="Markdown"
    )


def main():
    """Run the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        print("Error: Set TELEGRAM_BOT_TOKEN environment variable")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("price", cmd_price))

    # Handle unknown messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_help))

    logger.info("Starting RustChain Telegram Bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
