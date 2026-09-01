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

NODE_URL = os.getenv("RUSTCHAIN_NODE_URL", "https://50.28.86.131")

# Path to a CA bundle for TLS verification; override via env var if needed.
# Default None lets httpx use its own trust store. Setting RUSTCHAIN_CA_BUNDLE=""
# previously crashed httpx because empty string is not a valid "verify" value.
_ca_bundle_raw = os.getenv("RUSTCHAIN_CA_BUNDLE")
TLS_CA_BUNDLE = _ca_bundle_raw if _ca_bundle_raw else None

# Per-user rate limiter (1 request / 5 seconds). The original bounty #2869
# spec called for this; without it, a single user can DoS the upstream node
# and trigger Telegram rate-limits that block all other users.
_RATE_LIMIT_SECONDS = 5.0
_last_call_by_user = {}


async def _enforce_rate_limit(user_id):
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
    # _ * ` [
    return re.sub(r"([_*`\[])", r"\\\1", str(text))


# ── API helpers ──────────────────────────────────────────────────────────────

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
        return {"error": str(e)}


async def get_miners() -> list:
    """List active miners from the RustChain node."""
    try:
        async with httpx.AsyncClient(verify=TLS_CA_BUNDLE, timeout=10) as client:
            r = await client.get(f"{NODE_URL}/api/miners")
            r.raise_for_status()
            return r.json()
    except (httpx.HTTPError, ValueError):
        # ValueError covers json.JSONDecodeError; surface empty list on any
        # failure so callers can distinguish from a hard crash.
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
        return "⚠️ Could not reach node"
    active_ids = [m.get("miner_id") or m.get("wallet_id") or "" for m in miners]
    return "🟢 Active" if miner_id in active_ids else "🔴 Not attesting"


# ── Command Handlers ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance_prompt")],
        [InlineKeyboardButton("⛏️ Miner", callback_data="miner_prompt")],
        [InlineKeyboardButton("⏱️ Epoch", callback_data="epoch")],
        [InlineKeyboardButton("🩺 Health", callback_data="health")],
    ]
    await update.message.reply_text(
        "👋 *RustChain Bot*\n\n"
        "Check your wallet balance and miner status on the RustChain network.\n\n"
        "Commands:\n"
        "• `/balance <wallet\\_id>`\n"
        "• `/miner <miner\\_id>`\n"
        "• `/epoch`\n"
        "• `/health`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# Identifier shape used by the RustChain node: base58 / hex wallet id.
# 64 chars upper-bounded by the longest wallet in production (RTC + 40 hex).
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,64}$")


def _validate_id(value):
    return bool(_ID_RE.match(value))


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # In groups, the wallet id and balance are visible to every member.
    # Restrict to private chats to avoid leaking sensitive holdings.
    if update.effective_chat and update.effective_chat.type != "private":
        await update.message.reply_text(
            "Please use /balance in a private chat with me to keep your wallet info safe.",
            parse_mode="Markdown",
        )
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: `/balance <wallet_id>`", parse_mode="Markdown"
        )
        return
    wallet_id = context.args[0].strip()
    if not _validate_id(wallet_id):
        await update.message.reply_text(
            "Invalid wallet id. Use letters, digits, '.', '_', ':', '-' (max 64 chars).",
            parse_mode="Markdown",
        )
        return
    user_id = update.effective_user.id if update.effective_user else 0
    if not await _enforce_rate_limit(user_id):
        await update.message.reply_text(
            "Rate limit: wait 5 seconds between requests.",
            parse_mode="Markdown",
        )
        return
    safe_wallet_id = _escape_md(wallet_id)
    msg = await update.message.reply_text(
        f"🔍 Querying `{safe_wallet_id}`\u2026", parse_mode="Markdown"
    )
    data = await get_balance(wallet_id)
    if "error" in data:
        await msg.edit_text(f"❌ Error: {_escape_md(data['error'])}", parse_mode="Markdown")
        return
    balance = data.get("balance", data.get("rtc_balance", "N/A"))
    pending = data.get("pending_balance", "")
    text = f"💰 *Wallet:* `{safe_wallet_id}`\n*Balance:* `{_escape_md(balance)} RTC`"
    if pending is not None and pending != "":
        text += f"\n*Pending:* `{_escape_md(str(pending))} RTC`"
    await msg.edit_text(text, parse_mode="Markdown")


async def cmd_miner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_chat.type != "private":
        await update.message.reply_text(
            "Please use /miner in a private chat with me to keep your wallet info safe.",
            parse_mode="Markdown",
        )
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: `/miner <miner_id>`", parse_mode="Markdown"
        )
        return
    miner_id = context.args[0].strip()
    if not _validate_id(miner_id):
        await update.message.reply_text(
            "Invalid miner id. Use letters, digits, '.', '_', ':', '-' (max 64 chars).",
            parse_mode="Markdown",
        )
        return
    user_id = update.effective_user.id if update.effective_user else 0
    if not await _enforce_rate_limit(user_id):
        await update.message.reply_text(
            "Rate limit: wait 5 seconds between requests.",
            parse_mode="Markdown",
        )
        return
    safe_miner_id = _escape_md(miner_id)
    msg = await update.message.reply_text(
        f"🔍 Checking `{safe_miner_id}`\u2026", parse_mode="Markdown"
    )
    status = await miner_status_str(miner_id)
    data = await get_balance(miner_id)
    balance = data.get("balance", data.get("rtc_balance", "N/A"))
    text = (
        f"⛏️ *Miner:* `{safe_miner_id}`\n"
        f"*Status:* {status}\n"
        f"*Balance:* `{_escape_md(balance)} RTC`"
    )
    await msg.edit_text(text, parse_mode="Markdown")


async def cmd_epoch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await get_epoch()
    # Support being called from both command and button (callback query) contexts.
    reply_target = (
        update.callback_query.message
        if update.callback_query
        else update.message
    )
    if "error" in data:
        await reply_target.reply_text(f"❌ {_escape_md(data['error'])}", parse_mode="Markdown")
        return
    epoch_num = data.get("epoch", data.get("current_epoch", "N/A"))
    slot = data.get("slot", data.get("current_slot", "N/A"))
    miners_count = data.get("enrolled_miners", data.get("miner_count", "N/A"))
    next_s = data.get("next_settlement", data.get("seconds_until_next", "N/A"))
    await reply_target.reply_text(
        f"⏱️ *Epoch Info*\n"
        f"*Epoch:* `{_escape_md(epoch_num)}`\n"
        f"*Slot:* `{_escape_md(slot)}`\n"
        f"*Enrolled Miners:* `{_escape_md(miners_count)}`\n"
        f"*Next Settlement:* `{_escape_md(next_s)}s`",
        parse_mode="Markdown",
    )


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = await get_health()
    # Support being called from both command and button (callback query) contexts.
    reply_target = (
        update.callback_query.message
        if update.callback_query
        else update.message
    )
    if "error" in data:
        await reply_target.reply_text(
            f"❌ Node unreachable: {_escape_md(data['error'])}", parse_mode="Markdown"
        )
        return
    ok = data.get("status") in ("ok", "healthy", True)
    status_str = "🟢 Online" if ok else "🔴 Degraded"
    version = data.get("version", "N/A")
    await reply_target.reply_text(
        f"🩺 *Node Health*\n"
        f"*Status:* {status_str}\n"
        f"*Version:* `{_escape_md(version)}`\n"
        f"*Node:* `{_escape_md(NODE_URL)}`",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*RustChain Bot Commands*\n\n"
        "/balance <wallet\\_id> — Check RTC balance\n"
        "/miner <miner\\_id> — Miner attestation status\n"
        "/epoch — Current epoch info\n"
        "/health — Node health check\n"
        "/start — Welcome & quick buttons",
        parse_mode="Markdown",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "balance_prompt":
        await query.message.reply_text("Send: `/balance <wallet_id>`", parse_mode="Markdown")
    elif query.data == "miner_prompt":
        await query.message.reply_text("Send: `/miner <miner_id>`", parse_mode="Markdown")
    elif query.data == "epoch":
        await cmd_epoch(update, context)
    elif query.data == "health":
        await cmd_health(update, context)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("miner", cmd_miner))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("RustChain Telegram Bot running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
