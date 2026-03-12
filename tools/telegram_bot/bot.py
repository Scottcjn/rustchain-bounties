#!/usr/bin/env python3
"""
RustChain Telegram Bot
Provides commands: /balance, /miners, /price, /health, /epoch
API: https://rustchain.org
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

# Configuration
API_BASE = "https://rustchain.org"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with actual bot token from @BotFather

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def get_api(endpoint: str) -> dict:
    """Fetch data from RustChain API (ignores self-signed cert)"""
    url = f"{API_BASE}{endpoint}"
    async with aiohttp.TCPConnector(ssl=False) as connector:
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.get(url) as response:
                    return await response.json()
            except Exception as e:
                logger.error(f"API error: {e}")
                return {"error": str(e)}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🦀 **Welcome to RustChain Bot!**\n\n"
        "Available commands:\n"
        "/balance <wallet> - Check RTC balance\n"
        "/miners - List active miners\n"
        "/price - Current wRTC price\n"
        "/health - Node health status\n"
        "/epoch - Current epoch info\n\n"
        "API: https://rustchain.org"
    )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /balance command"""
    if not context.args:
        await update.message.reply_text(
            "Usage: /balance <wallet_name>\n"
            "Example: /balance scott"
        )
        return
    
    wallet = context.args[0]
    data = await get_api(f"/wallet/balance?miner_id={wallet}")
    
    if "error" in data:
        await update.message.reply_text(f"❌ Error: {data['error']}")
    elif data.get("ok"):
        await update.message.reply_text(
            f"💰 **Balance for {wallet}**\n"
            f"Amount: `{data['amount_rtc']}` RTC\n"
            f"Raw: `{data['amount_i64']}`"
        )
    else:
        await update.message.reply_text(f"❌ {data}")


async def miners_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /miners command"""
    data = await get_api("/api/miners")
    
    if "error" in data:
        await update.message.reply_text(f"❌ Error: {data['error']}")
        return
    
    if not data:
        await update.message.reply_text("No miners found.")
        return
    
    msg = f"⛏️ **Active Miners ({len(data)})**\n\n"
    for miner in data[:10]:  # Show first 10
        msg += (
            f"• `{miner.get('miner', 'N/A')[:20]}...`\n"
            f"  Device: {miner.get('hardware_type', 'Unknown')}\n"
            f"  Multiplier: {miner.get('antiquity_multiplier', 1)}x\n\n"
        )
    
    if len(data) > 10:
        msg += f"... and {len(data) - 10} more miners"
    
    await update.message.reply_text(msg)


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command"""
    # Note: Price endpoint not in API reference, using placeholder
    await update.message.reply_text(
        "📊 **wRTC Price**\n"
        "Price data from Raydium coming soon.\n"
        "Check https://rustchain.org for updates."
    )


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command"""
    data = await get_api("/health")
    
    if "error" in data:
        await update.message.reply_text(f"❌ Error: {data['error']}")
    elif data.get("ok"):
        msg = (
            "✅ **Node Health**\n\n"
            f"Version: `{data.get('version', 'N/A')}`\n"
            f"Uptime: `{data.get('uptime_s', 0) / 3600:.1f}` hours\n"
            f"DB Read/Write: `{data.get('db_rw', False)}`\n"
            f"Tip Age: `{data.get('tip_age_slots', 0)}` slots\n"
            f"Backup Age: `{data.get('backup_age_hours', 0)}` hours"
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text(f"❌ {data}")


async def epoch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /epoch command"""
    data = await get_api("/epoch")
    
    if "error" in data:
        await update.message.reply_text(f"❌ Error: {data['error']}")
    elif data:
        msg = (
            f"📅 **Epoch {data.get('epoch', 'N/A')}**\n\n"
            f"Slot: `{data.get('slot', 0)}`\n"
            f"Blocks/Epoch: `{data.get('blocks_per_epoch', 144)}`\n"
            f"Epoch POT: `{data.get('epoch_pot', 0)}` RTC\n"
            f"Enrolled Miners: `{data.get('enrolled_miners', 0)}`"
        )
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No epoch data available")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Please try again.")


def main():
    """Start the bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Error: Please set BOT_TOKEN in bot.py")
        print("Get token from @BotFather on Telegram")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("miners", miners_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("epoch", epoch_command))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🦀 RustChain Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
