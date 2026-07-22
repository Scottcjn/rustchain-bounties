#!/usr/bin/env python3
"""
RustChain Telegram Community Bot — background alert loop.

Polls the RustChain node for bonus events:
  * new miner joins (miner count increases)
  * epoch settles (epoch number changes)
  * wRTC price moves > 5% since last check

Alerts are sent to the chat ids configured in RUSTCHAIN_ALERT_CHAT_IDS.
The loop is a no-op when no alert chats are configured.
"""
from __future__ import annotations

import asyncio
import logging

from telegram.ext import Application

import api_client
import config

logger = logging.getLogger(__name__)

POLL_INTERVAL_S = float(config.REQUEST_TIMEOUT) * 3
PRICE_MOVE_THRESHOLD = 0.05


def _fmt_price(value) -> str:
    return f"${value}" if value is not None else "N/A"


async def run_alerts(app: Application, chat_ids: list[str]) -> None:
    last_epoch = None
    last_miner_count = None
    last_price = None

    while True:
        try:
            epoch = await api_client.get_epoch()
            miner_count = await api_client.get_active_miner_count()
            price_data = await api_client.get_price()
            price = price_data.get("price")

            epoch_no = epoch.get("epoch")
            if last_epoch is not None and epoch_no != last_epoch:
                for cid in chat_ids:
                    await app.bot.send_message(
                        cid,
                        f"⏱️ *Epoch {epoch_no} started!* Previous: {last_epoch}",
                        parse_mode="MarkdownV2",
                    )
            last_epoch = epoch_no

            if last_miner_count is not None and miner_count > last_miner_count:
                for cid in chat_ids:
                    await app.bot.send_message(
                        cid,
                        f"⛏️ *New miner joined!* Active miners: {miner_count} "
                        f"(+{miner_count - last_miner_count})",
                        parse_mode="MarkdownV2",
                    )
            last_miner_count = miner_count

            if last_price is not None and price is not None and last_price:
                move = abs(price - last_price) / last_price
                if move >= PRICE_MOVE_THRESHOLD:
                    direction = "📈 up" if price > last_price else "📉 down"
                    for cid in chat_ids:
                        await app.bot.send_message(
                            cid,
                            f"💰 wRTC {direction} >5%: {_fmt_price(last_price)} → "
                            f"{_fmt_price(price)} ({move:.1%})",
                            parse_mode="MarkdownV2",
                        )
            last_price = price

        except Exception as exc:  # noqa: BLE001 - keep polling despite errors
            logger.warning("alert loop error: %s", exc)

        await asyncio.sleep(POLL_INTERVAL_S)


def start_alert_loop(app: Application) -> None:
    if not config.ALERT_CHAT_IDS:
        logger.info("Alert loop disabled (no RUSTCHAIN_ALERT_CHAT_IDS set)")
        return
    app.create_task(run_alerts(app, config.ALERT_CHAT_IDS))
