#!/usr/bin/env python3
"""
RustChain Telegram Bot
Checks wallet balance, miner status, epoch info, and price.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from functools import wraps

import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = os.getenv("RUSTCHAIN_API_URL", "https://50.28.86.131:8099")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_OWNER_WALLET = "RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5"
BOT_OWNER_WALLET_DISPLAY = "RTCd5f...6e5"

# Rate limiting storage: {user_id: datetime_of_last_request}
rate_limit_store: dict[int, datetime] = {}
RATE_LIMIT_SECONDS = 5

# States for conversation
(WALLET_INPUT,) = range(1)


def rate_limit(func):
    """Decorator to rate limit commands per user."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        now = datetime.now()

        if user_id in rate_limit_store:
            last_request = rate_limit_store[user_id]
            if now - last_request < timedelta(seconds=RATE_LIMIT_SECONDS):
                remaining = (last_request + timedelta(seconds=RATE_LIMIT_SECONDS)) - now
                await update.message.reply_text(
                    f"⏳ Rate limit exceeded. Please wait {remaining.seconds + 1} seconds."
                )
                return

        rate_limit_store[user_id] = now
        return await func(update, context, *args, **kwargs)
    return wrapper


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred while processing your request. Please try again later."
        )


def fetch_api(endpoint: str, method: str = "GET", data: dict = None) -> dict | None:
    """Fetch data from RustChain API with SSL verification disabled."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, verify=False, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, verify=False, timeout=10)
        else:
            return None

        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError:
        logger.error("SSL Certificate error - node may have self-signed cert")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error - node may be offline: {url}")
        return None
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


@rate_limit
async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /balance <wallet> command."""
    if not context.args:
        await update.message.reply_text(
            "📝 Usage: /balance <wallet_address>\n"
            "Example: /balance RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5"
        )
        return

    wallet = context.args[0].strip()

    # Basic validation - RTC addresses typically start with RTC
    if not wallet.startswith("RTC"):
        await update.message.reply_text(
            "❌ Invalid wallet address. RTC addresses start with 'RTC'."
        )
        return

    await update.message.reply_text(f"🔍 Checking balance for `{wallet}`...", parse_mode=ParseMode.MARKDOWN_V2)

    data = fetch_api(f"/wallet/balance/{wallet}")

    if data is None:
        await update.message.reply_text(
            "❌ Could not connect to the RustChain node. It may be offline or unreachable.\n"
            "Please try again later."
        )
        return

    # Parse response - adjust based on actual API response format
    try:
        if "balance" in data:
            balance = data["balance"]
            await update.message.reply_text(
                f"💰 *Wallet Balance*\n"
                f"`{wallet}`\n"
                f"Balance: *{balance} RTC*",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        elif "error" in data:
            await update.message.reply_text(f"❌ Error: {data['error']}")
        else:
            # Try to display raw response
            await update.message.reply_text(f"📊 Response: `{data}`", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Error parsing balance response: {e}")
        await update.message.reply_text("❌ Error parsing response from node.")


@rate_limit
async def cmd_miners(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /miners command - show active miners."""
    await update.message.reply_text("⛏️ Fetching miner information...")

    data = fetch_api("/miners")

    if data is None:
        await update.message.reply_text(
            "❌ Could not connect to the RustChain node. It may be offline or unreachable.\n"
            "Please try again later."
        )
        return

    try:
        if isinstance(data, dict):
            if "miners" in data:
                miners = data["miners"]
                if not miners:
                    await update.message.reply_text("📭 No active miners found.")
                    return

                msg = "⛏️ *Active Miners*\n\n"
                for miner in miners[:20]:  # Limit to 20 miners
                    if isinstance(miner, dict):
                        address = miner.get("address", "Unknown")
                        hash_rate = miner.get("hash_rate", miner.get("hashrate", "N/A"))
                        shares = miner.get("shares", miner.get("valid_shares", "N/A"))
                        msg += f"• `{address[:16]}...` | HR: {hash_rate} | Shares: {shares}\n"
                    else:
                        msg += f"• `{str(miner)[:20]}...`\n"

                if len(miners) > 20:
                    msg += f"\n_...and {len(miners) - 20} more miners_"

                await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

            elif "error" in data:
                await update.message.reply_text(f"❌ Error: {data['error']}")
            else:
                await update.message.reply_text(f"📊 {data}")
        elif isinstance(data, list):
            if not data:
                await update.message.reply_text("📭 No active miners found.")
                return

            msg = "⛏️ *Active Miners*\n\n"
            for miner in data[:20]:
                if isinstance(miner, dict):
                    address = miner.get("address", "Unknown")
                    hash_rate = miner.get("hash_rate", miner.get("hashrate", "N/A"))
                    msg += f"• `{address[:16]}...` | HR: {hash_rate}\n"
                else:
                    msg += f"• `{str(miner)[:20]}...`\n"

            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(f"📊 Response: `{data}`", parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Error parsing miners response: {e}")
        await update.message.reply_text("❌ Error parsing response from node.")


@rate_limit
async def cmd_epoch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /epoch command - show current epoch info."""
    await update.message.reply_text("📡 Fetching epoch information...")

    data = fetch_api("/epoch")

    if data is None:
        await update.message.reply_text(
            "❌ Could not connect to the RustChain node. It may be offline or unreachable.\n"
            "Please try again later."
        )
        return

    try:
        if isinstance(data, dict):
            epoch = data.get("epoch", "N/A")
            block = data.get("current_block", data.get("block", "N/A"))
            difficulty = data.get("difficulty", data.get("diff", "N/A"))
            validators = data.get("validators", data.get("active_validators", "N/A"))
            rewards = data.get("epoch_rewards", data.get("rewards", "N/A"))

            msg = (
                f"📅 *Epoch Information*\n\n"
                f"Epoch: *{epoch}*\n"
                f"Block: *{block}*\n"
                f"Difficulty: *{difficulty}*\n"
                f"Active Validators: *{validators}*\n"
                f"Epoch Rewards: *{rewards} RTC*"
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)

        elif "error" in str(data):
            await update.message.reply_text(f"❌ Error: {data}")
        else:
            await update.message.reply_text(f"📊 {data}")
    except Exception as e:
        logger.error(f"Error parsing epoch response: {e}")
        await update.message.reply_text("❌ Error parsing response from node.")


@rate_limit
async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /price command - show RTC price (mock/fetched from exchange)."""
    # In a real implementation, you might fetch from an exchange API
    # For now, we indicate price is unavailable or use a placeholder
    await update.message.reply_text(
        "💲 *RTC Price*\n\n"
        "Price data is currently unavailable.\n"
        "Please check back later or visit the official RustChain website for current pricing.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@rate_limit
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "🤖 *RustChain Bot Commands*\n\n"
        "Available commands:\n\n"
        "📝 `/balance <wallet>` - Check wallet balance\n"
        "   Example: `/balance RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`\n\n"
        "⛏️ `/miners` - View active miners\n\n"
        "📅 `/epoch` - Current epoch information\n\n"
        "💲 `/price` - RTC price information\n\n"
        "❓ `/help` - Show this help message\n\n"
        "_\n"
        f"Bot payouts: `{BOT_OWNER_WALLET_DISPLAY}`\n"
        "Rate limit: 1 request per 5 seconds"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN_V2)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Welcome to the RustChain Bot!\n\n"
        "Use /help to see available commands.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def main() -> None:
    """Run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        print("Error: TELEGRAM_BOT_TOKEN environment variable is not set.")
        print("Get a token from @BotFather on Telegram.")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("balance", cmd_balance))
    application.add_handler(CommandHandler("miners", cmd_miners))
    application.add_handler(CommandHandler("epoch", cmd_epoch))
    application.add_handler(CommandHandler("price", cmd_price))

    # Error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print(f"🤖 RustChain Bot starting...")
    print(f"📡 API: {API_BASE_URL}")
    print(f"💰 Payout wallet: {BOT_OWNER_WALLET_DISPLAY}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
