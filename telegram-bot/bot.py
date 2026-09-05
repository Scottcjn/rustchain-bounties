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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Node Configuration
NODE_URL = os.getenv("RUSTCHAIN_NODE_URL", "https://50.28.86.131")

# Path to a CA bundle for TLS verification; override via env var if needed.
# Default None lets httpx use its own trust store. Setting RUSTCHAIN_CA_BUNDLE=""
# previously crashed httpx because empty string is not a valid "verify" value.
_ca_bundle_raw = os.getenv("RUSTCHAIN_CA_BUNDLE")
TLS_CA_BUNDLE = _ca_bundle_raw if _ca_bundle_raw else None

# Per-user rate limiter (1 request / 5 seconds).
_RATE_LIMIT_SECONDS = 5.0
_last_call_by_user = {}


async def _enforce_rate_limit(user_id: str) -> bool:
    """Return True if the call is allowed, False if rate-limited."""
    now = time.monotonic()
    last = _last_call_by_user.get(user_id, 0.0)
    if now - last < _RATE_LIMIT_SECONDS:
        return False
    _last_call_by_user[user_id] = now
    return True


def _escape_md(text: str) -> str:
    """Escape Markdown v1 special characters so user-supplied strings are safe."""
    # Characters that have special meaning in Telegram Markdown v1:
    # _ * ` [ ] ( )
    # Note: Re-using the regex pattern from context
    return re.sub(r"([_*`\[\]()])", r"\\\1", str(text))


# --- API Helpers ---
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
        return {"error": str(e)}


async def get_miners() -> list:
    """List active miners from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/api/miners")
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else [data]
    except (httpx.HTTPError, ValueError):
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
    """Return green/red status based on whether miner is actively attesting."""
    miners = await get_miners()
    if not miners:
        return "Miners Offline"
    
    # Assuming miners is a list of dicts or strings. 
    # Handle both common API response structures.
    found = None
    if isinstance(miners, list):
        for m in miners:
            if isinstance(m, dict) and m.get("id") == miner_id:
                found = m
            elif m == miner_id:  # Handle flat list
                found = m
    
    if found:
        return f"✓ {found.get('status', 'Active')} - {found.get('miner_id', 'Unknown')}"
    return f"○ {miner_id} (Scanning...)"


async def get_video_page_context() -> str:
    """
    Helper for BoTTube Video Page Customization.
    Simulates fetching custom metadata or specific video stats.
    """
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/video/context")
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"error": "Video context load failed"}


async def handle_status_command(ctx: ContextTypes, user_id: str):
    """
    Handler for /status command to check wallet/miner.
    Uses the rate limiter decorator pattern.
    """
    # Apply rate limit to this specific call
    if await _enforce_rate_limit(user_id):
        wallet = await get_balance(user_id)
        miners = await get_miners()
        
        text = f"**RustChain Status**\n"
        text += f"Miners: {len(miners)}\n"
        
        if "wallet" in wallet:
            text += f"**Wallet:** ${wallet['wallet'] or wallet['balance']} RTC\n"
        
        text += f"**Epoch:** {await get_epoch()}\n"
        
        # Inline keyboard for quick interaction
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("👆 Check Video", callback_data=f"video_{user_id}")]])
        await ctx.message.reply(text, reply_markup=kb)


async def handle_video_callback(ctx: ContextTypes):
    """Handle the custom video page click."""
    data = ctx.callback_query.data
    if "video" in data:
        data_parts = data.split("_")
        user_id = data_parts[1] if len(data_parts) > 1 else "0"
        
        context_data = await get_video_page_context()
        # Re-apply rate limit since we just did one
        if await _enforce_rate_limit(user_id):
            await ctx.answer(f"Loading Video Page...")
        
        # Simulate a rich text response for the video page
        await ctx.edit_message_text(f"**BoTTube Video Page**\n*Context:* {context_data}")


async def handle_health_check(ctx: ContextTypes):
    """Trigger a specific node health check from the chat."""
    health = await get_health()
    if "status" in health:
        await ctx.message.reply(f"**Node Health**: {health.get('status', 'Active')}\n**Uptime**: {health.get('uptime', 'N/A')}")


def main():
    """Main entry point to run the Telegram Bot."""
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN", "7381234_502886131:BotToken")).build()

    # Register Command Handlers
    app.add_handler(CommandHandler("status", handle_status_command))
    app.add_handler(CommandHandler("health", handle_health_check))
    
    # Register Callback Query Handlers (for the Video Page interaction)
    app.add_handler(CallbackQueryHandler(handle_video_callback, pattern=r"^video_" + re.escape(str(_last_call_by_user.get)) if _last_call_by_user else r"^video.*"))
    
    # Simple run loop
    app.run_polling(timeout=10)


if __name__ == "__main__":
    # Handle the case where _last_call_by_user is a number (from time.monotonic)
    # This ensures the regex matches the specific user format
    last_key = str(_last_call_by_user.get(0, 0))
    app.add_handler(CallbackQueryHandler(handle_video_callback, pattern=r"^video_" + last_key if last_key.isdigit() else last_key))
    
    # Actually, to keep it simple and robust, let's just run the main app logic.
    # We'll use the _enforce_rate_limit inside the handler.
    
    # Refined Main to be less brittle
    def run_bot():
        app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN", "7381234_502886131:BotToken")).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("status", lambda ctx: handle_status_command(ctx, ctx.effective_user.id)))
        app.add_handler(CommandHandler("health", handle_health_check))
        app.add_handler(CallbackQueryHandler(handle_video_callback, pattern=".*"))
        
        app.run_polling(timeout=10)
    
    run_bot()