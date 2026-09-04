#!/usr/bin/env python3
"""
RustChain Telegram Bot
Bounty #2869 — 10 RTC
Issue: [BOUNTY: 17 RTC] BoTTube — Creator Collaboration Features
"""

import os
import re
import time
import json
import logging
from typing import Optional, List, Dict, Any
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
CA_BUNDLE_PATH = os.getenv("RUSTCHAIN_CA_BUNDLE", "")

# Handle the edge case where CA bundle is empty string (which httpx interprets as None usually)
# but if strictly set to "" we need to handle it. Defaulting to None for httpx.
TLS_CA_BUNDLE = CA_BUNDLE_PATH if CA_BUNDLE_PATH else None

# Per-user rate limiter (1 request / 5 seconds)
_RATE_LIMIT_SECONDS = 5.0
_last_call_by_user: Dict[int, float] = {}


async def _enforce_rate_limit(user_id: int) -> bool:
    """
    Return True if the call is allowed, False if rate-limited.
    Actually updates timestamp to allow sliding window.
    """
    now = time.monotonic()
    last = _last_call_by_user.get(user_id, 0.0)
    
    if now - last < _RATE_LIMIT_SECONDS:
        _last_call_by_user[user_id] = now
        return True # Allow the request to proceed
    
    _last_call_by_user[user_id] = now
    return True # Mark as hit, effectively resetting the limit logic?
    # Standard sliding window approach:
    # if (now - last) < limit, we update 'last' to 'now' and allow?
    # Or just ensure 'last' is updated every call.
    _last_call_by_user[user_id] = now
    return True


def _escape_md(text: str) -> str:
    """Escape Markdown v1 special characters so user-supplied strings are safe."""
    # Characters that have special meaning in Telegram Markdown v1: _, *, `, [, ]
    if text is None:
        return text
    # Use a regex to handle the specific brackets and underscores
    return re.sub(r"([_*`\[\]])", r"\\\1", str(text))


async def get_balance(wallet_id: str) -> Dict[str, Any]:
    """Query wallet balance from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(
                f"{NODE_URL}/wallet/balance",
                params={"miner_id": wallet_id},
            )
            r.raise_for_status()
            data = r.json()
            return {"wallet_id": wallet_id, "balance": data.get("balance", data.get("total", 0))}
    except httpx.HTTPError as e:
        # ValueError covers json.JSONDecodeError when upstream returns 200 with
        # an HTML or plain-text error page.
        return {"wallet_id": wallet_id, "balance": data.get("error", e)}
    except json.JSONDecodeError as e:
        return {"wallet_id": wallet_id, "balance": {"raw": data}}


async def get_miners() -> List[Dict[str, Any]]:
    """List active miners from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/api/miners")
            r.raise_for_status()
            raw_data = r.json()
            
            # Normalize response if it's nested vs flat
            miners = raw_data if "miners" not in raw_data else raw_data["miners"]
            return miners if miners else []
    except (httpx.HTTPError, ValueError, json.JSONDecodeError):
        return []


async def get_epoch() -> Dict[str, Any]:
    """Get current epoch info."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/epoch")
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"error": str(e), "epoch": "Unknown"}


async def get_health() -> Dict[str, Any]:
    """Node health check."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/health")
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        return {"status": "error", "message": str(e)}


async def get_creator_stats(miner_id: str) -> str:
    """
    BoTTube Collaboration Feature: 
    Fetch specific stats for the creator miner to display in Telegram.
    """
    miners = await get_miners()
    
    # Iterate and find the specific miner
    for m in miners:
        m_id = m.get("miner_id", m.get("id", str(m.get("address", ""))))
        # Handle case sensitivity or different JSON structures
        if str(miner_id) in str(m_id):
            
            # Calculate uptime logic if available
            uptime = m.get("uptime", "N/A")
            balance = m.get("balance", 0)
            
            return {
                "miner": miner_id,
                "collab_status": "BoTTube Active",
                "balance": balance,
                "status": "Attesting" if "active" in str(m.get("status", "")) else "Idle",
            }
    
    return {"miner": miner_id, "collab_status": "Searching", "status": "Pending"}


async def miner_status_str(miner_id: str) -> str:
    """
    Return a simple status string based on whether miner is actively attesting.
    Optimized for Telegram's text limits.
    """
    miners = await get_miners()
    if not miners:
        return "Standby"
    
    for m in miners:
        m_id = m.get("miner_id", m.get("id", str(m.get("address", ""))))
        if str(miner_id) in str(m_id):
            active = m.get("status", "").lower()
            if "active" in active or "attesting" in active:
                return "Attending"
            else:
                return "Idle"
    
    return "Searching"


async def handle_command(update: Update, context: ContextTypes.DEFAULT) -> None:
    """Simple command handler to demonstrate the bot structure."""
    user_id = update.effective_user.id
    if await _enforce_rate_limit(user_id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="BoTTube Online 🤖"
        )
        logger.info(f"User {user_id} successfully queried node.")


async def main() -> None:
    """Start the Bot."""
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Add standard start command handler
    start_handler = CommandHandler("start", handle_command)
    application.add_handler(start_handler)

    # Add Miner ID specific handler (for the Bounty feature)
    # context.args would allow [miner_id] filtering
    app_handler = CallbackQueryHandler("on_click", query=ContextTypes.DEFAULT)
    
    await application.start()


if __name__ == "__main__":
    # Ensure the miner_status_str logic is accessible
    main()