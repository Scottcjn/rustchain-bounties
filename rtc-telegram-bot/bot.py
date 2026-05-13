#!/usr/bin/env python3
"""
RustChain Telegram Bot — READ-ONLY query bot for RustChain blockchain data.
No transfer/send functionality. Query-only.

Commands:
    /balance <wallet>  — Query wallet RTC balance
    /epoch             — Query current epoch info
    /miners            — Query miner status
    /price             — Query RTC price
    /help              — Show help message
"""

import json
import logging
import os
import urllib.request
import urllib.error

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ── Configuration ──────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("RTC_BOT_TOKEN", "")
API_BASE = os.environ.get("RTC_API_BASE", "https://rustchain.org")
TIMEOUT = int(os.environ.get("RTC_API_TIMEOUT", "10"))

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ── API helper (GET only, read-only) ──────────────────────────────────────

def _api_get(path: str, params: dict | None = None) -> dict | list | None:
    """Perform a read-only GET request to the RustChain API."""
    url = f"{API_BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    logger.info("GET %s", url)
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        logger.error("HTTP %s for %s", exc.code, url)
        return None
    except Exception as exc:
        logger.error("Request error: %s", exc)
        return None


# ── Command handlers ──────────────────────────────────────────────────────

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands."""
    text = (
        "⛓ *RustChain Query Bot* ⛓\n"
        "_Read-only — no transfers, no keys needed._\n\n"
        "Commands:\n"
        "/balance <wallet> — Query wallet RTC balance\n"
        "/epoch — Current epoch information\n"
        "/miners — Miner status overview\n"
        "/price — RTC price info\n"
        "/help — This message\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query a wallet's RTC balance."""
    if not context.args:
        await update.message.reply_text(
            "Usage: /balance <wallet_id>\nExample: /balance bai-su"
        )
        return

    wallet = " ".join(context.args).strip()
    data = _api_get("/wallet/balance", {"miner_id": wallet})
    if data is None:
        await update.message.reply_text(f"❌ Could not fetch balance for `{wallet}`.")
        return

    amount = data.get("amount_rtc", "N/A")
    await update.message.reply_text(
        f"💰 Wallet: `{wallet}`\n💎 Balance: *{amount} RTC*",
        parse_mode="Markdown",
    )


async def epoch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query current epoch information."""
    data = _api_get("/epoch")
    if data is None:
        await update.message.reply_text("❌ Could not fetch epoch info.")
        return

    text = (
        f"📊 *Epoch Info*\n"
        f"• Epoch: *{data.get('epoch', 'N/A')}*\n"
        f"• Slot: {data.get('slot', 'N/A')}\n"
        f"• Blocks per Epoch: {data.get('blocks_per_epoch', 'N/A')}\n"
        f"• Enrolled Miners: {data.get('enrolled_miners', 'N/A')}\n"
        f"• Epoch Pot: {data.get('epoch_pot', 'N/A')} RTC\n"
        f"• Total Supply: {data.get('total_supply_rtc', 'N/A')} RTC"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def miners_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query miner status overview."""
    data = _api_get("/miners")
    if data is None:
        await update.message.reply_text(
            "❌ Could not fetch miner data. The endpoint may be temporarily unavailable."
        )
        return

    if isinstance(data, list):
        text = f"⛏ *Miners ({len(data)} total)*\n"
        for m in data[:20]:
            mid = m.get("miner_id", "?")
            bal = m.get("balance_rtc", m.get("amount_rtc", "?"))
            status = m.get("status", "?")
            text += f"• {mid} — {bal} RTC [{status}]\n"
        if len(data) > 20:
            text += f"_…and {len(data) - 20} more_"
    else:
        text = f"⛏ *Miners*\n{json.dumps(data, indent=2)[:4000]}"
    await update.message.reply_text(text, parse_mode="Markdown")


async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Query RTC price information."""
    data = _api_get("/price")
    if data is None:
        await update.message.reply_text(
            "❌ Could not fetch price info. The endpoint may be temporarily unavailable."
        )
        return

    text = f"💲 *RTC Price*\n{json.dumps(data, indent=2)[:4000]}"
    await update.message.reply_text(text, parse_mode="Markdown")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Error: RTC_BOT_TOKEN env var is required.")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", help_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("epoch", epoch_cmd))
    app.add_handler(CommandHandler("miners", miners_cmd))
    app.add_handler(CommandHandler("price", price_cmd))
    logger.info("RustChain Telegram Bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
