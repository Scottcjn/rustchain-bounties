#!/usr/bin/env python3
"""
RustChain Telegram Bot
Check wallet balance, miner status, epoch info, and RTC price.

Usage:
    BOT_TOKEN=your_token python rustchain_bot.py

Requirements:
    pip install python-telegram-bot httpx
"""

import os
import time
import httpx
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

NODE_URL = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
RATE_LIMIT_SECONDS = 5

# Rate limiting: {user_id: last_request_time}
_rate_limits: dict[int, float] = defaultdict(float)


def is_rate_limited(user_id: int) -> bool:
    now = time.time()
    if now - _rate_limits[user_id] < RATE_LIMIT_SECONDS:
        return True
    _rate_limits[user_id] = now
    return False


async def api_get(path: str) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{NODE_URL}{path}")
            return r.json() if r.status_code == 200 else None
    except Exception:
        return None


async def balance_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_rate_limited(update.effective_user.id):
        await update.message.reply_text("Rate limited. Wait 5s between requests.")
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return
    wallet = ctx.args[0]
    data = await api_get(f"/api/balance/{wallet}")
    if data and "balance" in data:
        bal = data["balance"]
        await update.message.reply_text("Wallet: " + wallet + "\nBalance: " + str(bal) + " RTC")
    else:
        await update.message.reply_text("Could not fetch balance. Node may be offline.")


async def miners_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_rate_limited(update.effective_user.id):
        await update.message.reply_text("Rate limited. Wait 5s between requests.")
        return
    data = await api_get("/api/miners")
    if data and isinstance(data, list):
        lines = ["Miners (" + str(len(data)) + " active):"]
        for m in data[:10]:
            addr = str(m.get("address", "???"))[:12]
            status = "🟢" if m.get("active") else "🔴"
            lines.append(status + " " + addr + "...")
        await update.message.reply_text("
".join(lines))
    else:
        await update.message.reply_text("Could not fetch miners. Node may be offline.")


async def epoch_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_rate_limited(update.effective_user.id):
        await update.message.reply_text("Rate limited. Wait 5s between requests.")
        return
    data = await api_get("/api/epoch")
    if data:
        current = data.get("current_epoch", "?")
        next_e = data.get("next_epoch", "?")
        await update.message.reply_text("Current Epoch: " + str(current) + "\nNext Epoch: " + str(next_e))
    else:
        await update.message.reply_text("Could not fetch epoch info. Node may be offline.")


async def price_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("RTC Reference Rate: bash.10 USD per RTC")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "RustChain Bot Commands:

"
        "/balance <wallet> - Check RTC balance
"
        "/miners - List active miners
"
        "/epoch - Current epoch info
"
        "/price - RTC reference rate
"
        "/help - Show this message

"
        f"Node: {NODE_URL}"
    )
    await update.message.reply_text(text)


def main():
    if not BOT_TOKEN:
        print("Error: Set BOT_TOKEN environment variable")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("miners", miners_cmd))
    app.add_handler(CommandHandler("epoch", epoch_cmd))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("start", help_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    print("RustChain Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
