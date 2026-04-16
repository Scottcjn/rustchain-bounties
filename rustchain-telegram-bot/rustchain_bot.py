#!/usr/bin/env python3
"""
RustChain Telegram Bot (@RustChainBot)
Commands: /balance <wallet>, /miners, /epoch, /price, /help
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/2869
"""
import asyncio, json, os, time, logging
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
NODE_URL = os.environ.get('RUSTCHAIN_NODE_URL', 'https://50.28.86.131')
RATE_LIMIT_SECONDS = 5
user_last_request = {}

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def node_get(endpoint, params=None):
    url = f'{NODE_URL}{endpoint}'
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {'error': str(e)}

def check_rate_limit(user_id):
    now = time.time()
    last = user_last_request.get(user_id, 0)
    if now - last < RATE_LIMIT_SECONDS:
        return False
    user_last_request[user_id] = now
    return True

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🦀 Welcome to RustChain Bot! Use /help for commands.')

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = ('🦀 **RustChain Bot Commands**\n\n'
        '/balance <wallet> - Check RTC balance\n'
        '/miners - List active miners\n'
        '/epoch - Current epoch info\n'
        '/price - Show RTC reference rate\n'
        '/help - Show this message\n\n'
        '*Rate limit: 1 request per 5 seconds*')
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def cmd_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_rate_limit(update.effective_user.id):
        await update.message.reply_text('⏳ Please wait 5 seconds between requests.')
        return
    if not context.args:
        await update.message.reply_text('Usage: /balance <wallet_address>')
        return
    wallet = context.args[0]
    await update.message.reply_text(f'🔍 Checking balance for \`{wallet}\`...', parse_mode='MarkdownV2')
    result = await node_get(f'/balance/{wallet}')
    if 'error' in result:
        await update.message.reply_text(f'❌ Error: {result["error"]}')
        return
    amount = result.get('amount_i64', 0)
    amount_rtc = amount / 1_000_000 if amount else 0
    await update.message.reply_text(f'💰 **Balance for** \`{wallet}\`\n\n**{amount_rtc:.6f} RTC**', parse_mode='MarkdownV2')

async def cmd_miners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_rate_limit(update.effective_user.id):
        await update.message.reply_text('⏳ Please wait 5 seconds between requests.')
        return
    await update.message.reply_text('🔍 Fetching miner list...')
    result = await node_get('/api/miners', params={'limit': 10})
    if 'error' in result:
        await update.message.reply_text(f'❌ Error: {result["error"]}')
        return
    miners = result.get('miners', [])
    if not miners:
        await update.message.reply_text('📭 No active miners found.')
        return
    text = f'⛏️ **Active Miners** ({len(miners)})\n\n'
    for i, m in enumerate(miners[:10], 1):
        mid = m.get('miner_id', 'unknown')[:20]
        text += f'{i}\. \`{mid}...\`\n'
    if len(miners) > 10:
        text += f'\n... and {len(miners) - 10} more'
    await update.message.reply_text(text, parse_mode='MarkdownV2')

async def cmd_epoch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_rate_limit(update.effective_user.id):
        await update.message.reply_text('⏳ Please wait 5 seconds between requests.')
        return
    result = await node_get('/epoch')
    if 'error' in result:
        await update.message.reply_text(f'❌ Error: {result["error"]}')
        return
    text = f'📅 **Current Epoch**\n\n**Epoch:** {result.get("epoch", "?")}\n**Slot:** {result.get("slot", "?")}'
    await update.message.reply_text(text, parse_mode='MarkdownV2')

async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_rate_limit(update.effective_user.id):
        await update.message.reply_text('⏳ Please wait 5 seconds between requests.')
        return
    await update.message.reply_text('💲 **RTC Reference Rate**\n\n**1 RTC = \/bin/zsh.10 USD**\n\n_\(Reference price, not market rate\)_', parse_mode='MarkdownV2')

def main():
    if not BOT_TOKEN:
        print('ERROR: TELEGRAM_BOT_TOKEN environment variable is required.')
        exit(1)
    print(f'🦀 Starting RustChain Telegram Bot... Node: {NODE_URL}')
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('help', cmd_help))
    app.add_handler(CommandHandler('balance', cmd_balance))
    app.add_handler(CommandHandler('miners', cmd_miners))
    app.add_handler(CommandHandler('epoch', cmd_epoch))
    app.add_handler(CommandHandler('price', cmd_price))
    print('✅ Bot is running.')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
