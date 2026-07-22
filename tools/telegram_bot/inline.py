#!/usr/bin/env python3
"""
RustChain Telegram Community Bot — inline query support (bonus feature).

Lets users type @YourBot price or @YourBot epoch in any chat to get a quick
wRTC price or current epoch snapshot without invoking a command.
"""
from __future__ import annotations

import logging

from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, InlineQueryHandler

import api_client

logger = logging.getLogger(__name__)


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.strip().lower()
    results = []

    try:
        if query.startswith("price") or query == "":
            price = await api_client.get_price()
            results.append(
                InlineQueryResultArticle(
                    id="price",
                    title="wRTC Price",
                    description=str(price.get("price", "N/A")),
                    input_message_content=InputTextMessageContent(
                        f"💰 wRTC: {price.get('price')}",
                        parse_mode=ParseMode.MARKDOWN_V2,
                    ),
                )
            )

        if query.startswith("epoch") or query == "":
            epoch = await api_client.get_epoch()
            results.append(
                InlineQueryResultArticle(
                    id="epoch",
                    title="Current Epoch",
                    description=str(epoch.get("epoch", "N/A")),
                    input_message_content=InputTextMessageContent(
                        f"⏱️ Epoch: {epoch.get('epoch')} (slot {epoch.get('slot')})",
                        parse_mode=ParseMode.MARKDOWN_V2,
                    ),
                )
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("inline query failed: %s", exc)

    await update.inline_query.answer(results, cache_time=5)


def build_inline_handler() -> InlineQueryHandler:
    return InlineQueryHandler(inline_query)
