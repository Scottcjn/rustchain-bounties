#!/usr/bin/env python3
"""
RustChain Telegram Bot - Query RustChain blockchain data from Telegram
"""

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.com")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


def rpc_call(method, params):
    """Make JSON-RPC call to RustChain"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        return {"error": str(e)}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "🤖 **RustChain Bot**\n\n"
        "Commands:\n"
        "/balance <address> - Query RTC balance\n"
        "/block - Get latest block\n"
        "/tx <hash> - Get transaction details\n"
        "/stats - Network statistics"
    )


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Query RTC balance"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /balance <address>")
        return
    
    address = context.args[0]
    result = rpc_call("eth_getBalance", [address, "latest"])
    
    if result and "error" not in str(result):
        balance_rtc = int(result, 16) / 1e18 if result != "0x0" else 0
        await update.message.reply_text(
            f"💰 Balance for `{address}`:\n**{balance_rtc:.4f} RTC**"
        )
    else:
        await update.message.reply_text(f"❌ Error: {result}")


async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get latest block number"""
    result = rpc_call("eth_blockNumber", [])
    
    if result:
        block_num = int(result, 16)
        await update.message.reply_text(f"📦 Latest block: **#{block_num}**")
    else:
        await update.message.reply_text("❌ Error getting block number")


async def tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Query transaction details"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /tx <hash>")
        return
    
    tx_hash = context.args[0]
    result = rpc_call("eth_getTransactionByHash", [tx_hash])
    
    if result and "error" not in str(result):
        await update.message.reply_text(
            f"✅ Transaction found:\n"
            f"From: `{result.get('from')}`\n"
            f"To: `{result.get('to')}`\n"
            f"Value: `{result.get('value')}`"
        )
    else:
        await update.message.reply_text("❌ Transaction not found")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get network statistics"""
    block_result = rpc_call("eth_blockNumber", [])
    chain_result = rpc_call("eth_chainId", [])
    
    if block_result and chain_result:
        block_num = int(block_result, 16)
        chain_id = int(chain_result, 16)
        await update.message.reply_text(
            f"📊 **RustChain Stats**\n"
            f"Chain ID: `{chain_id}`\n"
            f"Latest Block: **#{block_num}**"
        )
    else:
        await update.message.reply_text("❌ Error getting stats")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await update.message.reply_text(
        "🤖 **RustChain Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Welcome message\n"
        "/balance <address> - Query RTC balance\n"
        "/block - Get latest block number\n"
        "/tx <hash> - Get transaction details\n"
        "/stats - Network statistics\n"
        "/help - This help message"
    )


def main():
    """Start the bot"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("block", block))
    app.add_handler(CommandHandler("tx", tx))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("help", help_command))
    
    # Start the bot
    print("Telegram bot is running...")
    app.run_polling()


if __name__ == "__main__":
    if TELEGRAM_TOKEN:
        main()
    else:
        print("Please set TELEGRAM_TOKEN environment variable")
