"""
RustChain Telegram Bot (@RustChainBot)
Bounty #2869 - 10 RTC Reward

Commands:
  /balance <wallet>  - Check RTC balance
  /miners            - List active miners
  /epoch             - Current epoch info
  /price             - Show RTC reference rate
  /help              - Show commands

Requirements:
  pip install python-telegram-bot httpx

Deploy: Railway, Fly.io, or systemd
"""

import os
import logging
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import httpx

# ── Configuration ──────────────────────────────────────────────
RUSTCHAIN_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
RATE_LIMIT_SECONDS = 5  # 1 request per 5 seconds per user

if not BOT_TOKEN:
    raise ValueError("Set TELEGRAM_BOT_TOKEN environment variable")

# ── Rate Limiting ──────────────────────────────────────────────
user_last_request: dict[str, float] = defaultdict(float)

def is_rate_limited(user_id: str) -> bool:
    now = time.time()
    if now - user_last_request[user_id] < RATE_LIMIT_SECONDS:
        return True
    user_last_request[user_id] = now
    return False

# ── API Helpers ────────────────────────────────────────────────
async def api_get(path: str) -> dict:
    """Make GET request to RustChain node."""
    url = f"{RUSTCHAIN_NODE}{path}"
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

async def api_get_tronscan(address: str) -> dict:
    """Get TRON account info from TronScan API."""
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

# ── Command Handlers ───────────────────────────────────────────
async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check RTC balance of a wallet address."""
    user_id = str(update.effective_user.id)
    if is_rate_limited(user_id):
        await update.message.reply_text(
            f"⏳ Rate limited. Please wait {RATE_LIMIT_SECONDS} seconds between requests."
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /balance <wallet_address>\n"
            "Example: /balance TTvwY4Y1m5DXNSeoo1W1YuV948mtvNwgnD"
        )
        return

    wallet = context.args[0]
    
    try:
        # Try TronScan for TRC20 balance
        data = await api_get_tronscan(wallet)
        trc20_tokens = data.get("trc20token_balances", [])
        trx_balance = data.get("balance", 0) / 1_000_000
        
        msg = f"🔍 Wallet: {wallet[:10]}...{wallet[-8:]}\n"
        msg += f"💰 TRX Balance: {trx_balance:.6f} TRX\n"
        
        if trc20_tokens:
            msg += "\n📦 TRC20 Tokens:\n"
            for token in trc20_tokens:
                if token.get("balance"):
                    bal = int(token.get("balance", 0))
                    decimals = int(token.get("decimals", 6))
                    name = token.get("tokenName", token.get("tokenAbbr", "Unknown"))
                    msg += f"  • {name}: {bal / (10**decimals):.2f}\n"
        else:
            msg += "\n📦 No TRC20 tokens found"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching balance: {str(e)}")

async def cmd_miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List active miners."""
    user_id = str(update.effective_user.id)
    if is_rate_limited(user_id):
        await update.message.reply_text(
            f"⏳ Rate limited. Please wait {RATE_LIMIT_SECONDS} seconds."
        )
        return

    try:
        data = await api_get("/miners")
        miners = data.get("miners", [])
        
        if not miners:
            await update.message.reply_text("No active miners found.")
            return
        
        msg = f"⛏️ Active Miners ({len(miners)}):\n\n"
        for m in miners[:10]:  # Show first 10
            name = m.get("name", m.get("wallet", "Unknown"))
            reward = m.get("reward", "N/A")
            msg += f"• {name}: {reward} RTC\n"
        
        if len(miners) > 10:
            msg += f"\n... and {len(miners) - 10} more"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching miners: {str(e)}")

async def cmd_epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current epoch information."""
    user_id = str(update.effective_user.id)
    if is_rate_limited(user_id):
        await update.message.reply_text(
            f"⏳ Rate limited. Please wait {RATE_LIMIT_SECONDS} seconds."
        )
        return

    try:
        data = await api_get("/epoch")
        
        msg = "📊 RustChain Epoch Info:\n\n"
        msg += f"• Epoch: {data.get('epoch', 'N/A')}\n"
        msg += f"• Slot: {data.get('slot', 'N/A')}\n"
        msg += f"• Blocks per epoch: {data.get('blocks_per_epoch', 'N/A')}\n"
        msg += f"• Epoch pot: {data.get('epoch_pot', 'N/A')} RTC\n"
        msg += f"• Enrolled miners: {data.get('enrolled_miners', 'N/A')}\n"
        msg += f"• Total miners: {data.get('total_miners', 'N/A')}\n"
        
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching epoch: {str(e)}")

async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show RTC reference price."""
    await update.message.reply_text(
        "💲 RTC Reference Rate:\n\n"
        "• 1 RTC ≈ $0.10 USD\n"
        "• 10 RTC ≈ $1.00 USD\n"
        "• 100 RTC ≈ $10.00 USD\n"
        "• 200 RTC ≈ $20.00 USD\n\n"
        "⚠️ Reference rate only. Actual market price may vary.\n"
        "Source: rustchain.org"
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands."""
    await update.message.reply_text(
        "🤖 <b>RustChain Bot — Commands</b>\n\n"
        "/balance &lt;wallet&gt; — Check wallet balance\n"
        "/miners — List active miners\n"
        "/epoch — Current epoch info\n"
        "/price — RTC reference rate\n"
        "/help — Show this message\n\n"
        "⏱️ Rate limit: 1 request per 5 seconds\n"
        "💰 RustChain Node: 50.28.86.131"
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text(
        "Unknown command. Use /help to see available commands."
    )

# ── Main ───────────────────────────────────────────────────────
def main():
    """Start the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("balance", cmd_balance))
    app.add_handler(CommandHandler("miners", cmd_miners))
    app.add_handler(CommandHandler("epoch", cmd_epoch))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("help", cmd_help))
    
    # Handle unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    print("🤖 RustChain Bot started. Polling for updates...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
