#!/usr/bin/env python3
"""
RustChain Telegram Bot — Bounty #2869
Commands: /balance /miners /epoch /price /help
"""

import json
import logging
import os
import ssl
import time
import urllib.error
import urllib.request
from collections import defaultdict
from functools import wraps

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

NODE = os.getenv("RUSTCHAIN_NODE", "https://50.28.86.131")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
RATE_LIMIT_S = int(os.getenv("RATE_LIMIT_S", "5"))

# Per-user rate limiting
_last_request: dict[int, float] = defaultdict(float)

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def fetch(path: str) -> dict:
    url = f"{NODE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "rustchain-tgbot/1.0"})
    resp = urllib.request.urlopen(req, context=_ctx, timeout=8)
    return json.loads(resp.read().decode())


def rate_limited(func):
    """Enforce RATE_LIMIT_S seconds between requests per user."""
    @wraps(func)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        now = time.time()
        wait = RATE_LIMIT_S - (now - _last_request[uid])
        if wait > 0:
            await update.message.reply_text(f"⏳ Please wait {wait:.1f}s before the next request.")
            return
        _last_request[uid] = now
        await func(update, ctx)
    return wrapper


@rate_limited
async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Check RTC balance: /balance <wallet_id>"""
    args = ctx.args
    if not args:
        await update.message.reply_text("Usage: /balance <wallet_id>\nExample: /balance my-wallet")
        return

    wallet_id = args[0].strip()
    try:
        data = fetch(f"/wallet/balance?wallet_id={urllib.request.quote(wallet_id)}")
        balance = float(data.get("balance", 0))
        usd = balance * 0.10
        await update.message.reply_text(
            f"💰 *RustChain Wallet*\n"
            f"Wallet: `{wallet_id}`\n"
            f"Balance: `{balance:.4f} RTC`\n"
            f"USD Value: `${usd:.4f}`\n"
            f"Rate: $0.10 / RTC",
            parse_mode="Markdown",
        )
    except urllib.error.HTTPError as e:
        if e.code == 404 or e.code == 400:
            await update.message.reply_text(f"❌ Wallet `{wallet_id}` not found.", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"⚠️ Node error: HTTP {e.code}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Node offline: {e}")


@rate_limited
async def cmd_miners(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """List top active miners: /miners"""
    try:
        data = fetch("/api/miners")
        miners = data.get("miners", [])[:10]
        if not miners:
            await update.message.reply_text("No active miners found.")
            return
        lines = ["⛏️ *Active Miners (top 10)*\n"]
        for i, m in enumerate(miners, 1):
            arch = m.get("device_arch", "?")
            family = m.get("device_family", "?")
            mult = m.get("antiquity_multiplier", 1.0)
            mid = m.get("miner_id", "?")[:12]
            lines.append(f"{i}. `{mid}` | {arch} | {family} | ×{mult:.2f}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ {e}")


@rate_limited
async def cmd_epoch(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Current epoch info: /epoch"""
    try:
        data = fetch("/epoch")
        epoch = data.get("epoch", "?")
        slot = data.get("slot", "?")
        pot = data.get("epoch_pot", 0)
        enrolled = data.get("enrolled_miners", "?")
        blocks = data.get("blocks_per_epoch", "?")
        await update.message.reply_text(
            f"🕐 *RustChain Epoch*\n"
            f"Epoch: `{epoch}`\n"
            f"Slot: `{slot}` / `{blocks}`\n"
            f"Pot: `{pot:.2f} RTC`\n"
            f"Miners: `{enrolled}`",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ {e}")


@rate_limited
async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """RTC reference price: /price"""
    try:
        data = fetch("/api/stats")
        total_bal = data.get("total_balance", 0)
        total_miners = data.get("total_miners", 0)
        version = data.get("version", "?")
        await update.message.reply_text(
            f"📊 *RustChain Network*\n"
            f"RTC Price: `$0.10 USD` (reference)\n"
            f"Total Supply in Wallets: `{total_bal:,.2f} RTC`\n"
            f"Total Miners: `{total_miners}`\n"
            f"Node Version: `{version}`",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ {e}")


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help: /help"""
    await update.message.reply_text(
        "🤖 *RustChain Bot*\n\n"
        "/balance `<wallet>` — Check RTC balance\n"
        "/miners — List active miners\n"
        "/epoch — Current epoch info\n"
        "/price — RTC network stats\n"
        "/help — Show this message\n\n"
        "RTC = $0.10 USD | Node: `50.28.86.131`",
        parse_mode="Markdown",
    )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))

    log.info("RustChain Telegram Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
