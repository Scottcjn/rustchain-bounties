#!/usr/bin/env python3
"""RustChain Telegram Bot - Check wallet balance and miner status"""

import os
import asyncio
import aiohttp
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes

# Rate limiting storage
rate_limit = {}

async def check_rate_limit(user_id: int) -> bool:
    """Check if user is rate limited (1 request per 5 seconds)"""
    import time
    now = time.time()
    if user_id in rate_limit:
        if now - rate_limit[user_id] < 5:
            return False
    rate_limit[user_id] = now
    return True

async def get_balance(wallet: str) -> str:
    """Get RTC balance for wallet"""
    try:
        async with aiohttp.ClientSession() as session:
            # Try the RustChain explorer API
            url = f"https://50.28.86.131/explorer/api/wallet/{wallet}"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return f"💰 Wallet: `{wallet}`\n\nBalance: `{data.get('balance', 0)} RTC`\nValue: `${data.get('balance', 0) * 0.1:.2f} USD`"
                return f"❌ Wallet `{wallet}` not found or node offline"
    except Exception as e:
        return f"⚠️ Error fetching balance: {str(e)}"

async def get_miners() -> str:
    """Get list of active miners"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://50.28.86.131/explorer/api/miners"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    miners = data.get('miners', [])[:10]  # Top 10
                    result = "⛏️ Active Miners:\n\n"
                    for i, m in enumerate(miners, 1):
                        name = m.get('name', 'Unknown')[:20]
                        hashrate = m.get('hashrate', 0)
                        result += f"{i}. `{name}` - {hashrate} H/s\n"
                    return result + f"\n_Total: {data.get('count', 0)} miners_"
                return "⚠️ Explorer node offline"
    except Exception as e:
        return f"⚠️ Error fetching miners: {str(e)}"

async def get_epoch() -> str:
    """Get current epoch info"""
    try:
        async with aiohttp.ClientSession() as session:
            url = "https://50.28.86.131/explorer/api/status"
            async with session.get(url, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    epoch = data.get('current_epoch', 0)
                    blocks = data.get('blocks_today', 0)
                    return f"📊 Epoch Info:\n\nEpoch: `{epoch}`\nBlocks Today: `{blocks}`\nStatus: `✅ Online`"
                return "⚠️ Node offline"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to RustChain Bot!\n\n"
        "Use /help to see available commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **RustChainBot Commands:**\n\n"
        "/balance `<wallet>` - Check RTC balance\n"
        "/miners - List active miners\n"
        "/epoch - Current epoch info\n"
        "/price - Show RTC reference rate\n"
        "/help - Show this message\n\n"
        "_Rate limit: 1 request per 5 seconds_",
        parse_mode='Markdown'
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_rate_limit(user_id):
        await update.message.reply_text("⚠️ Rate limited. Please wait 5 seconds.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/balance <wallet>`")
        return
    
    wallet = context.args[0]
    result = await get_balance(wallet)
    await update.message.reply_text(result, parse_mode='Markdown')

async def miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_rate_limit(user_id):
        await update.message.reply_text("⚠️ Rate limited. Please wait 5 seconds.")
        return
    
    result = await get_miners()
    await update.message.reply_text(result, parse_mode='Markdown')

async def epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_rate_limit(user_id):
        await update.message.reply_text("⚠️ Rate limited. Please wait 5 seconds.")
        return
    
    result = await get_epoch()
    await update.message.reply_text(result, parse_mode='Markdown')

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💵 **RTC Reference Rate:**\n\n"
        "1 RTC = $0.10 USD\n\n"
        "_Updated from RustChain reference rate_",
        parse_mode='Markdown'
    )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Set TELEGRAM_BOT_TOKEN environment variable")
        return
    
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("miners", miners))
    application.add_handler(CommandHandler("epoch", epoch))
    application.add_handler(CommandHandler("price", price))
    
    print("🤖 RustChainBot started...")
    application.run_polling()

if __name__ == "__main__":
    main()