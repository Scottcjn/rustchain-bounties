import os
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

NODE_URL = os.getenv("NODE_URL", "https://50.28.86.131")

user_last_call = {}
RATE_LIMIT_SECONDS = 5

async def check_rate_limit(update: Update) -> bool:
    user_id = update.effective_user.id
    now = time.time()
    if user_id in user_last_call:
        if now - user_last_call[user_id] < RATE_LIMIT_SECONDS:
            await update.message.reply_text("Rate limit exceeded. Please wait 5 seconds.")
            return False
    user_last_call[user_id] = now
    return True

async def fetch_json(url):
    try:
        import urllib3
        urllib3.disable_warnings()
        r = requests.get(url, verify=False, timeout=5)
        return r.json()
    except Exception as e:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to RustChain Bot! Use /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Available Commands:\n"
        "/balance <wallet> - Check RTC balance\n"
        "/miners - Check miner stats\n"
        "/epoch - Check network epoch\n"
        "/price - Check RTC price info\n"
        "/help - Show this message"
    )
    await update.message.reply_text(help_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_rate_limit(update): return
    if not context.args:
        await update.message.reply_text("Usage: /balance <wallet_address>")
        return
    wallet = context.args[0]
    data = await fetch_json(f"{NODE_URL}/wallet/balance?address={wallet}")
    if not data:
        await update.message.reply_text("Error: Could not reach RustChain node or invalid wallet.")
        return
    bal = data.get("amount_rtc", 0)
    await update.message.reply_text(f"💰 Wallet: {wallet}\nBalance: {bal} RTC\n(~${bal * 0.10:.2f} USD)")

async def miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_rate_limit(update): return
    data = await fetch_json(f"{NODE_URL}/epoch")
    if not data:
        await update.message.reply_text("Error: Could not reach RustChain node.")
        return
    miners_count = data.get("enrolled_miners", 0)
    await update.message.reply_text(f"⛏ Enrolled Miners: {miners_count}")

async def epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_rate_limit(update): return
    data = await fetch_json(f"{NODE_URL}/epoch")
    if not data:
        await update.message.reply_text("Error: Could not reach RustChain node.")
        return
    epoch_num = data.get("epoch", "Unknown")
    slot = data.get("slot", "Unknown")
    await update.message.reply_text(f"📅 Current Epoch: {epoch_num}\nSlot: {slot}")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_rate_limit(update): return
    await update.message.reply_text("💵 RTC is currently pegged/valued at approximately $0.10 USD.")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN not set!")
        return
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("miners", miners))
    application.add_handler(CommandHandler("epoch", epoch))
    application.add_handler(CommandHandler("price", price))
    application.run_polling()

if __name__ == '__main__':
    main()
