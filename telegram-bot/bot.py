#!/usr/bin/env python3
"""
RustChain Telegram Bot — Wallet Balance & Miner Status
Bounty: #2869 (10 RTC)
"""

import os
import time
import logging
import json
from collections import defaultdict
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Config ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_SECONDS", "5"))
RTC_PRICE_USD = 0.10

# --- Logging ---
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

# --- Rate Limiting ---
_last_request: dict[int, float] = defaultdict(float)


def check_rate_limit(user_id: int) -> bool:
    """Return True if user is rate-limited."""
    now = time.time()
    if now - _last_request[user_id] < RATE_LIMIT:
        return True
    _last_request[user_id] = now
    return False


# --- API Helpers ---
def api_get(path: str, timeout: int = 10) -> dict | list | None:
    """GET from RustChain node API."""
    url = f"{NODE_URL}{path}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except (URLError, HTTPError, json.JSONDecodeError, OSError) as e:
        log.warning("API error %s: %s", url, e)
        return None


def get_balance(wallet: str) -> dict | None:
    """Fetch wallet balance."""
    data = api_get(f"/balance/{wallet}")
    if data and isinstance(data, dict):
        return {
            "wallet": wallet,
            "balance": data.get("balance", data.get("rtc", 0)),
            "pending": data.get("pending", 0),
        }
    # Try alternate endpoint
    data = api_get(f"/wallet/{wallet}")
    if data and isinstance(data, dict):
        return {
            "wallet": wallet,
            "balance": data.get("balance", data.get("rtc", 0)),
            "pending": data.get("pending", 0),
        }
    return None


def get_miners() -> list | None:
    """Fetch active miners list."""
    data = api_get("/miners")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("miners", data.get("data", []))
    return None


def get_epoch() -> dict | None:
    """Fetch current epoch info."""
    data = api_get("/epoch")
    if isinstance(data, dict):
        return data
    data = api_get("/info")
    if isinstance(data, dict):
        return {
            "epoch": data.get("epoch", data.get("current_epoch", "N/A")),
            "height": data.get("height", data.get("block_height", "N/A")),
            "hashrate": data.get("hashrate", data.get("network_hashrate", "N/A")),
        }
    return None


# --- Command Handlers ---
async def cmd_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance <wallet>"""
    if check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Please wait a few seconds between requests.")
        return

    if not ctx.args:
        await update.message.reply_text("Usage: `/balance <wallet>`", parse_mode="Markdown")
        return

    wallet = ctx.args[0].strip()
    msg = await update.message.reply_text(f"🔍 Checking balance for `{wallet}`...", parse_mode="Markdown")

    info = get_balance(wallet)
    if info is None:
        await msg.edit_text(f"❌ Could not fetch balance for `{wallet}`.\nNode may be offline.", parse_mode="Markdown")
        return

    bal = float(info.get("balance", 0))
    usd = bal * RTC_PRICE_USD
    pending = info.get("pending", 0)

    text = (
        f"💰 **Balance for `{wallet}`**\n\n"
        f"• RTC: `{bal:,.4f}`\n"
        f"• USD: `≈${usd:,.2f}` ( @{RTC_PRICE_USD}/RTC )\n"
        f"• Pending: `{pending}`\n"
    )
    await msg.edit_text(text, parse_mode="Markdown")


async def cmd_miners(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /miners"""
    if check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Please wait a few seconds between requests.")
        return

    msg = await update.message.reply_text("⛏️ Fetching active miners...")

    miners = get_miners()
    if miners is None:
        await msg.edit_text("❌ Could not fetch miners.\nNode may be offline.")
        return

    if not miners:
        await msg.edit_text("ℹ️ No active miners found.")
        return

    lines = [f"⛏️ **Active Miners ({len(miners)})**\n"]
    for m in miners[:20]:
        if isinstance(m, dict):
            name = m.get("name", m.get("wallet", m.get("id", "unknown")))
            hashrate = m.get("hashrate", m.get("hr", "N/A"))
            status = m.get("status", "🟢")
            lines.append(f"• `{name}` — {hashrate} H/s {status}")
        else:
            lines.append(f"• `{m}`")

    if len(miners) > 20:
        lines.append(f"\n... and {len(miners) - 20} more")

    await msg.edit_text("\n".join(lines), parse_mode="Markdown")


async def cmd_epoch(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /epoch"""
    if check_rate_limit(update.effective_user.id):
        await update.message.reply_text("⏳ Please wait a few seconds between requests.")
        return

    msg = await update.message.reply_text("📅 Fetching epoch info...")

    info = get_epoch()
    if info is None:
        await msg.edit_text("❌ Could not fetch epoch info.\nNode may be offline.")
        return

    lines = ["📅 **Epoch Info**\n"]
    for k, v in info.items():
        lines.append(f"• {k}: `{v}`")

    await msg.edit_text("\n".join(lines), parse_mode="Markdown")


async def cmd_price(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /price"""
    text = (
        f"💵 **RTC Price**\n\n"
        f"• Rate: `$0.10 USD`\n"
        f"• 1 RTC = $0.10\n"
        f"• 10 RTC = $1.00\n"
        f"• 100 RTC = $10.00\n\n"
        f"_Reference rate for bounty calculations._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help"""
    text = (
        "🤖 **@RustChainBot Commands**\n\n"
        "• `/balance <wallet>` — Check RTC balance\n"
        "• `/miners` — List active miners\n"
        "• `/epoch` — Current epoch info\n"
        "• `/price` — RTC reference rate\n"
        "• `/help` — This message\n\n"
        "_Rate limit: 1 request per 5 seconds._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# --- Main ---
def main() -> None:
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        print("Get one from @BotFather on Telegram")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("start", cmd_help))

    log.info("RustChain Telegram Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
