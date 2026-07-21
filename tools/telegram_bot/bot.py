#!/usr/bin/env python3
"""
RustChain Telegram Community Bot — command handlers / main entrypoint.

Commands:
  /start    welcome + help
  /price    current wRTC price (Raydium)
  /miners   active miner count
  /epoch    current epoch info
  /balance <wallet>   RTC balance for a wallet
  /health   node health status
Plus bonus features: mining/epoch/price alerts and inline queries.
"""
from __future__ import annotations

import logging
import re

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    InlineQueryHandler,
)

import api_client
import config
from alerts import start_alert_loop
from inline import build_inline_handler

logger = logging.getLogger(__name__)

MD_ESCAPE = r"([_*`\[\])"


def esc(text: str) -> str:
    """Escape Telegram Markdown v2 special characters in user-supplied text."""
    return re.sub(MD_ESCAPE, r"\\\1", str(text))


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "*RustChain Community Bot* ⚡\n\n"
        "Commands:\n"
        "/price — current wRTC price\n"
        "/miners — active miner count\n"
        "/epoch — current epoch info\n"
        "/balance <wallet> — RTC balance\n"
        "/health — node health status",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_client.get_price()
    except Exception as exc:  # noqa: BLE001 - report any failure to user
        logger.warning("price failed: %s", exc)
        await update.message.reply_text(f"❌ Could not fetch wRTC price: {esc(exc)}")
        return
    price = data.get("price")
    price_str = f"${price}" if price is not None else "N/A"
    await update.message.reply_text(
        f"💰 *wRTC Price*\n\n"
        f"Price: `{price_str}`\n"
        f"Pair: `{esc(data.get('pair', 'N/A'))}`\n"
        f"24h Volume: `{esc(data.get('volume_24h', 'N/A'))}`\n"
        f"Source: `{esc(data.get('source', 'raydium'))}`",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def cmd_miners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        count = await api_client.get_active_miner_count()
    except Exception as exc:  # noqa: BLE001
        logger.warning("miners failed: %s", exc)
        await update.message.reply_text(f"❌ Could not fetch miners: {esc(exc)}")
        return
    await update.message.reply_text(
        f"⛏️ *Active Miners*\n\n`{count}` miners currently active",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def cmd_epoch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_client.get_epoch()
    except Exception as exc:  # noqa: BLE001
        logger.warning("epoch failed: %s", exc)
        await update.message.reply_text(f"❌ Could not fetch epoch: {esc(exc)}")
        return
    await update.message.reply_text(
        f"⏱️ *Epoch Info*\n\n"
        f"Epoch: `{esc(data.get('epoch', 'N/A'))}`\n"
        f"Slot: `{esc(data.get('slot', 'N/A'))}`\n"
        f"Enrolled Miners: `{esc(data.get('enrolled_miners', 'N/A'))}`\n"
        f"Blocks/Epoch: `{esc(data.get('blocks_per_epoch', 'N/A'))}`\n"
        f"Epoch Pot: `{esc(data.get('epoch_pot', 'N/A'))}` RTC",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: `/balance <wallet>`")
        return
    wallet = context.args[0].strip()
    try:
        data = await api_client.get_balance(wallet)
    except Exception as exc:  # noqa: BLE001
        logger.warning("balance failed: %s", exc)
        await update.message.reply_text(
            f"❌ Could not fetch balance: {esc(exc)}",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return
    balance = data.get("balance") or data.get("balance_rtc") or data.get("rtc_balance")
    locked = data.get("locked") or data.get("locked_rtc")
    text = f"💰 *Balance*\n\nWallet: `{esc(wallet)}`\nBalance: `{esc(balance)}` RTC"
    if locked is not None:
        text += f"\nLocked: `{esc(locked)}` RTC"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        data = await api_client.get_health()
    except Exception as exc:  # noqa: BLE001
        logger.warning("health failed: %s", exc)
        await update.message.reply_text(f"❌ Node unreachable: {esc(exc)}")
        return
    ok = data.get("ok") in (True, "true", 1) or data.get("status") in ("ok", "healthy")
    status = "🟢 Online" if ok else "🔴 Degraded"
    await update.message.reply_text(
        f"🩺 *Node Health*\n\n"
        f"Status: {status}\n"
        f"Version: `{esc(data.get('version', 'N/A'))}`\n"
        f"Uptime: `{esc(data.get('uptime_s', 'N/A'))}s`\n"
        f"DB RW: `{esc(data.get('db_rw', 'N/A'))}`",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def main() -> None:
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN environment variable")
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(build_inline_handler())

    start_alert_loop(app)

    logger.info("RustChain Telegram Bot running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
