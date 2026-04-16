#!/usr/bin/env python3
"""
RustChain Telegram Bot — @RustChainBot

A Telegram bot that lets users check their RustChain wallet and miner status.

Commands:
    /balance <wallet>   Check RTC balance
    /miners             List active miners
    /epoch              Current epoch info
    /price              Show RTC reference rate ($0.10)
    /help               Show commands

Reward: 10 RTC (~$1.00 USD)
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2869

Usage:
    export TELEGRAM_BOT_TOKEN="your-bot-token"
    export RTC_NODE_URL="http://50.28.86.131:8099"  # optional
    python3 tools/telegram_bot.py

Deploy: Railway, Fly.io, systemd, or any Python host.
"""

import argparse
import json
import logging
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# Rate limiting: user_id -> last_request_timestamp
_rate_limit: Dict[int, float] = {}
RATE_LIMIT_SECONDS = 5

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("rustchain_telegram_bot")


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

DEFAULT_NODE_URL = os.environ.get("RTC_NODE_URL", "http://50.28.86.131:8099")


def create_ssl_context(insecure: bool = False) -> Optional[ssl.SSLContext]:
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def api_get(endpoint: str, params: Optional[Dict[str, str]] = None) -> Tuple[bool, Any, str]:
    """Make GET request to RustChain node. Returns (ok, data, error)."""
    node = os.environ.get("RTC_NODE_URL", DEFAULT_NODE_URL)
    url = f"{node}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rustchain-telegram-bot/1.0"})
        ctx = create_ssl_context(insecure=True)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return True, json.loads(body), ""
            except json.JSONDecodeError:
                return False, None, "invalid_json"
    except urllib.error.HTTPError as e:
        return False, None, f"http_{e.code}"
    except urllib.error.URLError:
        return False, None, "node_unreachable"
    except Exception as e:
        return False, None, str(type(e).__name__)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_balance(wallet: str) -> str:
    """Check RTC balance for a wallet."""
    if not wallet or len(wallet) < 3:
        return "⚠️ Usage: /balance <wallet_name>\nExample: /balance chenzhizhuan"

    ok, data, err = api_get("wallet/balance", {"wallet_id": wallet})
    if not ok:
        return f"❌ Failed to fetch balance: {err}\nNode may be offline."

    balance = data.get("balance", data.get("amount", data.get("result", "unknown")))
    unit = data.get("unit", "RTC")

    # Try to format nicely
    try:
        bal = float(balance)
        formatted = f"{bal:,.4f}"
    except (TypeError, ValueError):
        formatted = str(balance)

    return (
        f"💰 *Wallet: {wallet}*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"Balance: *{formatted} {unit}*\n"
        f"USD Value: ~${bal * 0.10:.2f} (at $0.10/RTC)"
    )


def cmd_miners() -> str:
    """List active miners."""
    ok, data, err = api_get("api/miners")
    if not ok:
        return f"❌ Failed to fetch miners: {err}\nNode may be offline."

    miners = data if isinstance(data, list) else data.get("miners", data.get("result", []))
    if not miners:
        return "🔍 No active miners found."

    # Limit to top 10
    display = miners[:10]
    lines = ["⛏️ *Active Miners (Top 10)*\n━━━━━━━━━━━━━━━━━"]
    for m in display:
        name = m.get("name", m.get("miner_id", "unknown"))
        status = m.get("status", "unknown")
        hardware = m.get("hardware", m.get("machine_type", "unknown"))
        status_emoji = "🟢" if status == "active" else "🟡" if status == "idle" else "🔴"
        lines.append(f"{status_emoji} `{name}` — {hardware}")

    total = len(miners) if isinstance(miners, list) else "?"
    lines.append(f"\n_...and {total - 10 if isinstance(total, int) and total > 10 else '0'} more_")
    return "\n".join(lines)


def cmd_epoch() -> str:
    """Get current epoch info."""
    ok, data, err = api_get("epoch")
    if not ok:
        return f"❌ Failed to fetch epoch: {err}\nNode may be offline."

    epoch = data.get("epoch", data.get("current_epoch", "?"))
    block = data.get("block", data.get("tip_height", "?"))
    reward = data.get("epoch_reward", data.get("reward", "?"))
    next_epoch = data.get("next_epoch_in", data.get("blocks_to_next", "?"))

    return (
        f"📊 *Epoch Info*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"Epoch: *{epoch}*\n"
        f"Block Height: *{block}*\n"
        f"Epoch Reward: *{reward} RTC*\n"
        f"Next Epoch In: *{next_epoch} blocks*"
    )


def cmd_price() -> str:
    """Show RTC reference rate."""
    return (
        f"💎 *RTC Reference Rate*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"Price: *$0.10 USD per RTC*\n\n"
        f"_Reference rate set by RustChain foundation._\n"
        f"_Total Paid Out: 23,299.92 RTC_"
    )


def cmd_help() -> str:
    return (
        "🤖 *RustChain Bot Commands*\n"
        "━━━━━━━━━━━━━━━━━\n"
        "/balance `<wallet>` — Check RTC balance\n"
        "/miners — List active miners\n"
        "/epoch — Current epoch info\n"
        "/price — RTC reference rate\n"
        "/help — Show this message\n\n"
        "_Powered by RustChain — Proof-of-Antiquity blockchain_"
    )


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

def check_rate_limit(user_id: int) -> bool:
    """Return True if user is within rate limit, False if they should wait."""
    import time
    now = time.time()
    last = _rate_limit.get(user_id, 0)
    if now - last < RATE_LIMIT_SECONDS:
        return False
    _rate_limit[user_id] = now
    return True


# ---------------------------------------------------------------------------
# Telegram Handler (python-telegram-bot v20+)
# ---------------------------------------------------------------------------

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
        ConversationHandler,
    )

    async def start_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "👋 Welcome to RustChain Bot!\n\n"
            "Check your RTC wallet, miners, and more.\n"
            "Type /help for commands.",
            parse_mode="Markdown",
        )

    async def balance_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not check_rate_limit(update.effective_user.id):
            await update.message.reply_text("⏳ Please wait a few seconds between requests.")
            return

        wallet = " ".join(ctx.args).strip() if ctx.args else ""
        text = cmd_balance(wallet)
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    async def miners_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not check_rate_limit(update.effective_user.id):
            await update.message.reply_text("⏳ Please wait a few seconds between requests.")
            return

        text = cmd_miners()
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    async def epoch_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not check_rate_limit(update.effective_user.id):
            await update.message.reply_text("⏳ Please wait a few seconds between requests.")
            return

        text = cmd_epoch()
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    async def price_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        if not check_rate_limit(update.effective_user.id):
            await update.message.reply_text("⏳ Please wait a few seconds between requests.")
            return

        text = cmd_price()
        await update.message.reply_text(text, parse_mode="Markdown")

    async def help_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        text = cmd_help()
        await update.message.reply_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    async def unknown_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "🤖 Unknown command. Type /help for available commands.",
            parse_mode="Markdown",
        )

    def run_telegram_bot(token: str) -> None:
        """Start the Telegram bot."""
        log.info("Starting RustChain Telegram Bot...")
        app = Application.builder().token(token).build()

        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("balance", balance_command))
        app.add_handler(CommandHandler("miners", miners_command))
        app.add_handler(CommandHandler("epoch", epoch_command))
        app.add_handler(CommandHandler("price", price_command))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

        log.info("Bot is running. Press Ctrl+C to stop.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

except ImportError:
    # python-telegram-bot not installed — provide CLI mode
    def run_telegram_bot(token: str) -> None:
        print("python-telegram-bot not installed. Use CLI mode instead:")
        print("  python3 tools/telegram_bot.py balance <wallet>")
        print("  python3 tools/telegram_bot.py miners")
        print("  python3 tools/telegram_bot.py epoch")
        print("  python3 tools/telegram_bot.py price")


# ---------------------------------------------------------------------------
# CLI Mode (no Telegram token required)
# ---------------------------------------------------------------------------

def run_cli(args_namespace) -> None:
    """Run bot commands from command line."""
    cmd = getattr(args_namespace, "cli_command", None)
    wallet = getattr(args_namespace, "wallet", "")

    if cmd == "balance":
        print(cmd_balance(wallet))
    elif cmd == "miners":
        print(cmd_miners())
    elif cmd == "epoch":
        print(cmd_epoch())
    elif cmd == "price":
        print(cmd_price())
    elif cmd == "help":
        print(cmd_help())
    else:
        print("Unknown command. Use: balance, miners, epoch, price, help")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="RustChain Telegram Bot")
    sub = parser.add_subparsers(dest="mode", help="run mode")

    # Telegram mode
    telega_parser = sub.add_parser("telegram", help="Run as Telegram bot")
    telega_parser.add_argument("token", help="Telegram bot token from @BotFather")

    # CLI mode
    cli_parser = sub.add_parser("cli", help="Run from command line (no bot)")
    cli_parser.add_argument("cli_command", choices=["balance", "miners", "epoch", "price", "help"],
                            help="Command to run")
    cli_parser.add_argument("wallet", nargs="?", default="", help="Wallet name (for balance)")

    args = parser.parse_args()

    if args.mode == "telegram":
        run_telegram_bot(args.token)
    elif args.mode == "cli":
        run_cli(args)
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()
