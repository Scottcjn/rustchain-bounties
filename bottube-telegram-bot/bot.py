#!/usr/bin/env python3
"""
BoTTube Telegram Bot — Bounty #2299
Browse and watch BoTTube AI-native video platform directly in Telegram.

Commands:
  /latest          - 5 most recent videos
  /trending        - top videos by views
  /watch <id>      - watch a specific video
  /search <query>  - search videos
  /agent <name>    - agent profile
  /tip <id> <amt>  - tip a video (requires linked wallet)
  /link <wallet>   - link your RTC wallet

Inline mode: @bottube_bot <query> — search in any chat
"""

import os
import logging
from typing import Optional

import httpx
from telegram import (
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    InlineQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Config ──────────────────────────────────────────────────────
BOTTUBE_URL = os.environ.get("BOTTUBE_URL", "https://bottube.ai")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
RUSTCHAIN_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")

# In-memory wallet store (use Redis/DB in production)
_user_wallets: dict[int, str] = {}


# ── BoTTube API client ──────────────────────────────────────────

def _client() -> httpx.Client:
    return httpx.Client(timeout=15, verify=False)


def fetch_latest(limit: int = 5) -> list[dict]:
    with _client() as c:
        r = c.get(f"{BOTTUBE_URL}/api/v1/videos", params={"limit": limit, "sort": "newest"})
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("videos", data.get("items", []))


def fetch_trending(limit: int = 5) -> list[dict]:
    with _client() as c:
        r = c.get(f"{BOTTUBE_URL}/api/v1/videos/trending", params={"limit": limit})
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("videos", data.get("items", []))


def fetch_search(query: str, limit: int = 5) -> list[dict]:
    with _client() as c:
        r = c.get(f"{BOTTUBE_URL}/api/v1/videos/search", params={"q": query, "limit": limit})
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("videos", data.get("results", []))


def fetch_video(video_id: str) -> Optional[dict]:
    with _client() as c:
        r = c.get(f"{BOTTUBE_URL}/api/v1/videos/{video_id}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()


def fetch_agent(agent_name: str) -> Optional[dict]:
    with _client() as c:
        r = c.get(f"{BOTTUBE_URL}/api/v1/agents/{agent_name}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()


def send_tip(video_id: str, from_wallet: str, amount: float) -> dict:
    """Send an RTC tip to a video's creator via RustChain."""
    with _client() as c:
        # First get video creator's wallet
        video = fetch_video(video_id)
        if not video:
            return {"error": "Video not found"}

        creator_wallet = video.get("creator_wallet") or video.get("wallet")
        if not creator_wallet:
            return {"error": "Creator wallet not found"}

        r = c.post(
            f"{RUSTCHAIN_NODE}/wallet/transfer",
            json={"from": from_wallet, "to": creator_wallet, "amount": amount},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()


# ── Formatting helpers ──────────────────────────────────────────

def format_video(v: dict, index: Optional[int] = None) -> str:
    vid_id = v.get("id", v.get("video_id", "?"))
    title = v.get("title", "Untitled")[:60]
    creator = v.get("agent_name") or v.get("creator") or v.get("uploader", "unknown")
    views = v.get("views", v.get("view_count", 0))
    url = v.get("url") or f"{BOTTUBE_URL}/watch/{vid_id}"

    prefix = f"{index}. " if index is not None else ""
    return (
        f"{prefix}*{title}*\n"
        f"  👤 {creator} · 👁 {views:,} views\n"
        f"  🆔 `{vid_id}` · [Watch]({url})"
    )


def format_video_list(videos: list[dict]) -> str:
    if not videos:
        return "No videos found."
    return "\n\n".join(format_video(v, i + 1) for i, v in enumerate(videos))


# ── Command handlers ────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🎬 *BoTTube Bot* — AI-native video platform\n\n"
        "Commands:\n"
        "• /latest — 5 newest videos\n"
        "• /trending — most popular\n"
        "• /watch `<id>` — watch a video\n"
        "• /search `<query>` — search\n"
        "• /agent `<name>` — agent profile\n"
        "• /tip `<id>` `<amount>` — tip in RTC\n"
        "• /link `<wallet>` — link RTC wallet\n\n"
        "💡 Inline mode: type `@bottube_bot <query>` in any chat"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⏳ Fetching latest videos…")
    try:
        videos = fetch_latest(5)
        text = "🆕 *Latest Videos*\n\n" + format_video_list(videos)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except Exception as e:
        logger.error("latest error: %s", e)
        await update.message.reply_text("❌ Could not fetch videos. Try again later.")


async def cmd_trending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⏳ Fetching trending videos…")
    try:
        videos = fetch_trending(5)
        text = "🔥 *Trending Videos*\n\n" + format_video_list(videos)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except Exception as e:
        logger.error("trending error: %s", e)
        await update.message.reply_text("❌ Could not fetch trending. Try again later.")


async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /watch `<video_id>`", parse_mode=ParseMode.MARKDOWN)
        return

    video_id = context.args[0].strip()
    try:
        video = fetch_video(video_id)
        if not video:
            await update.message.reply_text(f"❌ Video `{video_id}` not found.", parse_mode=ParseMode.MARKDOWN)
            return

        title = video.get("title", "Untitled")
        creator = video.get("agent_name") or video.get("creator", "unknown")
        views = video.get("views", 0)
        description = video.get("description", "")[:200]
        url = video.get("url") or f"{BOTTUBE_URL}/watch/{video_id}"
        thumbnail = video.get("thumbnail_url") or video.get("thumbnail")

        text = (
            f"🎬 *{title}*\n\n"
            f"👤 Creator: {creator}\n"
            f"👁 Views: {views:,}\n"
        )
        if description:
            text += f"\n📝 {description}\n"
        text += f"\n▶️ [Watch on BoTTube]({url})"

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("▶️ Watch", url=url),
        ]])

        if thumbnail:
            try:
                await update.message.reply_photo(thumbnail, caption=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
                return
            except Exception:
                pass

        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    except Exception as e:
        logger.error("watch error: %s", e)
        await update.message.reply_text("❌ Could not fetch video. Try again later.")


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /search `<query>`", parse_mode=ParseMode.MARKDOWN)
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for *{query}*…", parse_mode=ParseMode.MARKDOWN)
    try:
        videos = fetch_search(query, 5)
        if not videos:
            await update.message.reply_text(f"No results for *{query}*.", parse_mode=ParseMode.MARKDOWN)
            return
        text = f"🔍 *Results for \"{query}\"*\n\n" + format_video_list(videos)
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    except Exception as e:
        logger.error("search error: %s", e)
        await update.message.reply_text("❌ Search failed. Try again later.")


async def cmd_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /agent `<agent_name>`", parse_mode=ParseMode.MARKDOWN)
        return

    agent_name = context.args[0].strip()
    try:
        agent = fetch_agent(agent_name)
        if not agent:
            await update.message.reply_text(f"❌ Agent `{agent_name}` not found.", parse_mode=ParseMode.MARKDOWN)
            return

        name = agent.get("name") or agent.get("agent_name", agent_name)
        bio = agent.get("bio", agent.get("description", ""))[:200]
        video_count = agent.get("video_count", agent.get("videos", 0))
        total_views = agent.get("total_views", agent.get("views", 0))
        profile_url = agent.get("url") or f"{BOTTUBE_URL}/agent/{agent_name}"

        text = (
            f"🤖 *{name}*\n\n"
            f"🎬 Videos: {video_count}\n"
            f"👁 Total views: {total_views:,}\n"
        )
        if bio:
            text += f"\n📝 {bio}\n"

        recent = agent.get("recent_videos") or agent.get("videos_list", [])
        if recent:
            text += f"\n*Recent uploads:*\n" + format_video_list(recent[:3])

        text += f"\n\n[View profile]({profile_url})"
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    except Exception as e:
        logger.error("agent error: %s", e)
        await update.message.reply_text("❌ Could not fetch agent profile. Try again later.")


async def cmd_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        wallet = _user_wallets.get(update.effective_user.id)
        if wallet:
            await update.message.reply_text(
                f"✅ Your linked wallet: `{wallet}`\n\nTo change: /link `<new_wallet>`",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await update.message.reply_text("Usage: /link `<rtc_wallet_id>`", parse_mode=ParseMode.MARKDOWN)
        return

    wallet = context.args[0].strip()
    _user_wallets[update.effective_user.id] = wallet
    await update.message.reply_text(
        f"✅ Wallet linked: `{wallet}`\n\nYou can now use /tip to support creators.",
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_tip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /tip `<video_id>` `<amount_rtc>`\n\nFirst link your wallet with /link",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user_id = update.effective_user.id
    wallet = _user_wallets.get(user_id)
    if not wallet:
        await update.message.reply_text(
            "❌ No wallet linked. Use /link `<wallet_id>` first.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    video_id = context.args[0].strip()
    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Use a number, e.g. /tip abc123 5.0")
        return

    if amount <= 0:
        await update.message.reply_text("❌ Amount must be positive.")
        return

    await update.message.reply_text(f"⏳ Sending {amount} RTC tip…")
    try:
        result = send_tip(video_id, wallet, amount)
        if "error" in result:
            await update.message.reply_text(f"❌ Tip failed: {result['error']}")
        else:
            tx_id = result.get("tx_id") or result.get("transaction_id", "")
            await update.message.reply_text(
                f"✅ Sent *{amount} RTC* tip!\n"
                + (f"TX: `{tx_id}`" if tx_id else ""),
                parse_mode=ParseMode.MARKDOWN,
            )
    except Exception as e:
        logger.error("tip error: %s", e)
        await update.message.reply_text("❌ Tip failed. Check your wallet balance and try again.")


# ── Inline query handler ────────────────────────────────────────

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query.strip()
    if not query:
        return

    try:
        videos = fetch_search(query, 5)
    except Exception:
        videos = []

    results = []
    for v in videos:
        vid_id = v.get("id", v.get("video_id", ""))
        title = v.get("title", "Untitled")[:60]
        creator = v.get("agent_name") or v.get("creator", "")
        views = v.get("views", 0)
        url = v.get("url") or f"{BOTTUBE_URL}/watch/{vid_id}"

        results.append(
            InlineQueryResultArticle(
                id=str(vid_id),
                title=title,
                description=f"👤 {creator} · 👁 {views:,} views",
                input_message_content=InputTextMessageContent(
                    f"🎬 *{title}*\n👤 {creator} · 👁 {views:,}\n▶️ [Watch]({url})",
                    parse_mode=ParseMode.MARKDOWN,
                ),
            )
        )

    await update.inline_query.answer(results, cache_time=30)


# ── Main ────────────────────────────────────────────────────────

def main() -> None:
    token = TELEGRAM_TOKEN
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("latest", cmd_latest))
    app.add_handler(CommandHandler("trending", cmd_trending))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("agent", cmd_agent))
    app.add_handler(CommandHandler("link", cmd_link))
    app.add_handler(CommandHandler("tip", cmd_tip))
    app.add_handler(InlineQueryHandler(inline_query))

    logger.info("BoTTube Telegram Bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
