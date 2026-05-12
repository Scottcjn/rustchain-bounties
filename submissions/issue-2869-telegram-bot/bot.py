#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""RustChainBot — Telegram bot for RTC balance/miner/epoch checks."""
import os, time, logging, aiohttp
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RustChainBot")

API_BASE = os.getenv("RUSTCHAIN_API", "https://rustchain.org")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
RTC_PRICE = 0.10
RATE_LIMIT_SEC = 5
user_last_request = {}

def rate_limit(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        now = time.time()
        if uid in user_last_request and now - user_last_request[uid] < RATE_LIMIT_SEC:
            await update.message.reply_text("⏳ Rate limited. Wait 5 seconds.")
            return
        user_last_request[uid] = now
        return await func(update, context)
    return wrapper

async def fetch_json(path, default=None):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{API_BASE}{path}", timeout=10) as r:
                if r.status == 200:
                    return await r.json()
    except Exception as e:
        logger.error(f"API error: {e}")
    return default

@rate_limit
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ RustChainBot\n\n"
        "/balance <wallet> — Check RTC balance\n"
        "/miners — Active miners\n"
        "/epoch — Current epoch info\n"
        "/price — RTC price ($0.10)\n"
        "/help — Commands"
    )

@rate_limit
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wallet = " ".join(context.args) if context.args else None
    if not wallet:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return
    try:
        data = await fetch_json(f"/wallet/balance?address={wallet}")
        if data and "amount_rtc" in data:
            rtc = float(data["amount_rtc"])
            usd = rtc * RTC_PRICE
            await update.message.reply_text(
                f"💰 Wallet: `{wallet[:10]}...`\n"
                f"Balance: {rtc:.4f} RTC (~${usd:.2f} USD)",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ Wallet not found or API unreachable")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

@rate_limit
async def miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await fetch_json("/api/miners")
        if data:
            miners_list = data.get("miners", [])
            total = data.get("pagination", {}).get("total", len(miners_list))
            await update.message.reply_text(f"⛏️ Active miners: {total}")
        else:
            await update.message.reply_text("⚠️ Miner data unavailable")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

@rate_limit
async def epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = await fetch_json("/epoch")
        if data:
            supply = data.get('total_supply_rtc', '?')
            await update.message.reply_text(
                f"🌐 Epoch: {data.get('epoch','?')}\n"
                f"📊 Slot: {data.get('slot','?')}\n"
                f"⛏️ Miners: {data.get('enrolled_miners','?')}\n"
                f"💰 Epoch Pot: {data.get('epoch_pot','?')} RTC\n"
                f"🔒 Supply: {supply} RTC"
            )
        else:
            await update.message.reply_text("⚠️ Epoch data unavailable")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

@rate_limit
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💎 RTC Reference Price: ${RTC_PRICE}/token")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    if not BOT_TOKEN:
        print("Set TELEGRAM_BOT_TOKEN env var")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    for cmd, handler in [
        ("start", start), ("balance", balance), ("miners", miners),
        ("epoch", epoch), ("price", price), ("help", help_cmd)
    ]:
        app.add_handler(CommandHandler(cmd, handler))
    logger.info("RustChainBot started")
    app.run_polling()

if __name__ == "__main__":
    main()
