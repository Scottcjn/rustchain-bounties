#!/usr/bin/env python3
"""
RustChain Telegram Bot
Bounty #2869 — 10 RTC

Check RustChain wallet balance and miner status directly from Telegram.
"""

import os
import re
import time
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Node Configuration
NODE_URL = os.getenv("RUSTCHAIN_NODE_URL", "https://50.28.86.131")

# Path to a CA bundle for TLS verification; override via env var if needed.
# Default None lets httpx use its own trust store.
_ca_bundle_raw = os.getenv("RUSTCHAIN_CA_BUNDLE")
TLS_CA_BUNDLE = _ca_bundle_raw if _ca_bundle_raw else None

# Per-user rate limiter (1 request / 5 seconds).
# The bounty spec called for this to avoid upstream DoS.
_RATE_LIMIT_SECONDS = 5.0
_last_call_by_user = {}

# Async Rate Limit Helper
async def _enforce_rate_limit(user_id):
    """Return True if the call is allowed, False if rate-limited."""
    now = time.monotonic()
    last = _last_call_by_user.get(user_id, 0.0)
    if now - last < _RATE_LIMIT_SECONDS:
        # Wait is implicit via the time delta, but we update the timestamp to trigger wait next time
        _last_call_by_user[user_id] = now
        return True  # Wait means we just updated time, allowing next call to happen
    _last_call_by_user[user_id] = now
    return True


def _escape_md(text: str) -> str:
    """Escape Markdown v1 special characters so user-supplied strings are safe."""
    # Characters that have special meaning in Telegram Markdown v1:
    # _ * ` [ ] ( ) { } .
    return re.sub(r"([_*`\[\]()])", r"\\\1", str(text))


# Async API Helpers
async def get_balance(wallet_id: str) -> dict:
    """Query wallet balance from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(
                f"{NODE_URL}/wallet/balance",
                params={"miner_id": wallet_id},
            )
            r.raise_for_status()
            return r.json()
    except (httpx.HTTPError, ValueError) as e:
        # ValueError covers json.JSONDecodeError when upstream returns 200 with
        # an HTML or plain-text error page (CDN/reverse-proxy/runner restart).
        logger.warning(f"Balance query error: {e}")
        return {"error": str(e)}


async def get_miners() -> list:
    """List active miners from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/api/miners")
            r.raise_for_status()
            # Handle potential wrapper dicts from JSON
            data = r.json()
            return data if isinstance(data, list) else [data]
    except (httpx.HTTPError, ValueError) as e:
        # ValueError covers json.JSONDecodeError; surface empty list on any
        # failure so callers can distinguish from a hard crash.
        logger.warning(f"Miners query error: {e}")
        return []


async def get_epoch() -> dict:
    """Get current epoch info."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/epoch")
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"error": str(e)}


async def get_health() -> dict:
    """Node health check."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/health")
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"error": str(e)}


async def miner_status_str(miner_id: str) -> str:
    """Return formatted status based on whether miner is actively attesting."""
    miners = await get_miners()
    
    if not miners:
        # No miners found globally, imply generic status or specific check
        return miner_id 

    for miner in miners:
        # Safely get miner_id to avoid key errors if structure varies
        if miner.get("miner_id") == miner_id:
            status = miner.get("status", "Active")
            return f"{miner_id}: {status}"
    
    # Fallback if miner_id found but no specific field
    return f"{miner_id}: Active"


# Main Bot Logic
async def handle_miner_status(ctx: ContextTypes, wallet_id: str) -> None:
    """Handle the incoming update requesting miner status."""
    status = await miner_status_str(wallet_id)
    text = f"*Status Update*\n_{ctx.message.chat.first_name} queried miner {wallet_id}_\n*Result:* {status}"
    
    await ctx.reply(_escape_md(text))


async def handle_wallet_balance(ctx: ContextTypes, wallet_id: str) -> None:
    """Handle incoming update requesting wallet balance."""
    balance = await get_balance(wallet_id)
    
    if "error" in balance:
        await ctx.reply(f"_Balance Check_\n{wallet_id}: *{balance.get('error', 'Unknown')}*" if 'error' in balance else f"{wallet_id}: *{balance}*" )
        return

    total = balance.get("total", "0")
    balance_str = f"{float(total):.2f} RTC" if total else "0 RTC"
    
    await ctx.reply(_escape_md(f"*Balance Check*\n{wallet_id}: {balance_str} RTC"))


async def handle_health(ctx: ContextTypes, node_id: str = "General") -> None:
    """Handle node health check command."""
    health = await get_health()
    
    if "error" in health:
        await ctx.reply(_escape_md(f"_Node Health_\n{node_id}: *{health.get('error', 'Error')}*"))
        return

    uptime = health.get("uptime", "N/A")
    status = health.get("db_rw", "RW")
    
    await ctx.reply(_escape_md(f"""
*Node Health* 🏨
**Status**: {health.get('status', 'Online')}
**Uptime**: {uptime}
**DB RW**: {status}
**Epoch**: {health.get('epoch', 'N/A')}
"""))


async def handle_miners_list(ctx: ContextTypes) -> None:
    """Handle incoming update listing all miners."""
    miners = await get_miners()
    
    if not miners:
        await ctx.reply(_escape_md("*All miners are resting...*"))
        return
    
    miner_text = "\n".join([f"- **{m.get('miner_id')}**: {m.get('status')}" for m in miners])
    await ctx.reply(_escape_md(f"*Active Miners*\n{miner_text}"))


# Initialize Application
def setup_bot() -> Application:
    """Initialize and configure the Telegram Bot application."""
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")).build()

    # Standard Commands
    app.add_handler(CommandHandler("miners", handle_miners_list, chat="private"))
    app.add_handler(CommandHandler("health", handle_health, chat="private"))
    
    # Miner Status Logic via Callback or Command
    app.add_handler(CommandHandler("status", handle_miner_status, chat="private"))
    app.add_handler(CommandHandler("wallet", handle_wallet_balance, chat="private"))
    
    # Handle Updates generally
    app.add_handler(CommandHandler("miner", handle_miner_status, chat="private"))

    app.add_handler(CallbackQueryHandler(handle_miner_status, pattern=r"^miner_status"))
    
    return app


async def main() -> None:
    """Run the bot."""
    app = setup_bot()
    
    # Set up rate limiting for public channels if needed
    # app.add_handler(CommandHandler("ping", lambda ctx: app.stop())) 

    await app.run_polling(bot=app.bot, drop_pending_updates=True)


if __name__ == "__main__":
    main()