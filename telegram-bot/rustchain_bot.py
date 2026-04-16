import os
import time
from collections import defaultdict

try:
    import httpx
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
    print("Install deps: pip install python-telegram-bot httpx")
    exit(1)

NODE_URL = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
RATE_LIMIT = 5
_limits = defaultdict(float)


def rate_limited(uid):
    now = time.time()
    if now - _limits[uid] < RATE_LIMIT:
        return True
    _limits[uid] = now
    return False


async def api_get(path):
    try:
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(NODE_URL + path)
            return r.json() if r.status_code == 200 else None
    except Exception:
        return None


async def balance_cmd(update, ctx):
    if rate_limited(update.effective_user.id):
        await update.message.reply_text("Wait 5s between requests.")
        return
    if not ctx.args:
        await update.message.reply_text("Usage: /balance <wallet>")
        return
    wallet = ctx.args[0]
    data = await api_get("/api/balance/" + wallet)
    if data and "balance" in data:
        await update.message.reply_text("Wallet: " + wallet + "\nBalance: " + str(data["balance"]) + " RTC")
    else:
        await update.message.reply_text("Could not fetch balance.")


async def miners_cmd(update, ctx):
    if rate_limited(update.effective_user.id):
        await update.message.reply_text("Wait 5s.")
        return
    data = await api_get("/api/miners")
    if data and isinstance(data, list):
        lines = ["Miners (" + str(len(data)) + " active):"]
        for m in data[:10]:
            addr = str(m.get("address", "?"))[:12]
            s = "ON" if m.get("active") else "OFF"
            lines.append(s + " " + addr + "...")
        await update.message.reply_text("\n".join(lines))
    else:
        await update.message.reply_text("Could not fetch miners.")


async def epoch_cmd(update, ctx):
    if rate_limited(update.effective_user.id):
        await update.message.reply_text("Wait 5s.")
        return
    data = await api_get("/api/epoch")
    if data:
        cur = data.get("current_epoch", "?")
        nxt = data.get("next_epoch", "?")
        await update.message.reply_text("Epoch: " + str(cur) + "\nNext: " + str(nxt))
    else:
        await update.message.reply_text("Could not fetch epoch.")


async def price_cmd(update, ctx):
    await update.message.reply_text("RTC Reference Rate: $0.10 USD")


async def help_cmd(update, ctx):
    msg = "RustChain Bot\n/balance <wallet> - Check balance\n/miners - List miners\n/epoch - Epoch info\n/price - RTC rate\n/help - This message"
    await update.message.reply_text(msg)


def main():
    if not BOT_TOKEN:
        print("Set BOT_TOKEN env var")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("miners", miners_cmd))
    app.add_handler(CommandHandler("epoch", epoch_cmd))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("start", help_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    print("RustChain Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
