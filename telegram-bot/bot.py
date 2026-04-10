#!/usr/bin/env python3
import os
import json
import time
import urllib.request
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuration
NODE_URL = os.environ.get('NODE_URL', 'https://50.28.86.131')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
BOT_VERSION = '1.0.0'

# Rate limiting: user_id -> last_request_timestamp
rate_limit_store = {}
RATE_LIMIT_SECONDS = 5

def rate_limit_decorator(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        current_time = time.time()
        
        if user_id in rate_limit_store:
            elapsed = current_time - rate_limit_store[user_id]
            if elapsed < RATE_LIMIT_SECONDS:
                remaining = RATE_LIMIT_SECONDS - elapsed
                update.message.reply_text(
                    f'Please wait {int(remaining)} seconds before next request.'
                )
                return
        
        rate_limit_store[user_id] = current_time
        return func(update, context)
    return wrapper

def api_request(method: str, params: dict = None) -> dict:
    try:
        payload = json.dumps({
            'method': method,
            'params': params or {}
        }).encode('utf-8')
        
        req = urllib.request.Request(
            NODE_URL,
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

@rate_limit_decorator
def cmd_balance(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text('Usage: /balance <wallet_address>')
        return
    
    wallet = context.args[0]
    result = api_request('getBalance', {'address': wallet})
    
    if 'error' in result:
        update.message.reply_text(f'Error: {result["error"]}')
        return
    
    balance = result.get('balance', 0)
    update.message.reply_text(
        f'Wallet: {wallet}\nBalance: {balance} RTC'
    )

@rate_limit_decorator
def cmd_miners(update: Update, context: CallbackContext):
    result = api_request('getMiners')
    
    if 'error' in result:
        update.message.reply_text(f'Error: {result["error"]}')
        return
    
    miners = result.get('miners', [])
    if not miners:
        update.message.reply_text('No active miners found.')
        return
    
    miner_list = '\n'.join([
        f'- {m.get("address", "unknown")}: {m.get("hashrate", 0)} H/s'
        for m in miners[:10]
    ])
    update.message.reply_text(f'Active Miners:\n{miner_list}')

@rate_limit_decorator
def cmd_epoch(update: Update, context: CallbackContext):
    result = api_request('getEpochInfo')
    
    if 'error' in result:
        update.message.reply_text(f'Error: {result["error"]}')
        return
    
    epoch = result.get('epoch', 'N/A')
    block = result.get('block', 'N/A')
    update.message.reply_text(f'Current Epoch: {epoch}\nBlock: {block}')

@rate_limit_decorator
def cmd_price(update: Update, context: CallbackContext):
    update.message.reply_text('RTC Reference Rate: .10 USD')

@rate_limit_decorator
def cmd_help(update: Update, context: CallbackContext):
    help_text = '''
RustChain Bot Commands:

/balance <wallet> - Check wallet balance
/miners - List active miners
/epoch - Current epoch info
/price - RTC reference rate
/help - Show this help

Rate limit: 1 request per 5 seconds per user.
'''
    update.message.reply_text(help_text)

def error_handler(update: Update, context: CallbackContext):
    update.message.reply_text('An error occurred. Please try again later.')

def main():
    if not TELEGRAM_TOKEN:
        print('Error: TELEGRAM_BOT_TOKEN not set')
        return
    
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler('balance', cmd_balance))
    dp.add_handler(CommandHandler('miners', cmd_miners))
    dp.add_handler(CommandHandler('epoch', cmd_epoch))
    dp.add_handler(CommandHandler('price', cmd_price))
    dp.add_handler(CommandHandler('help', cmd_help))
    dp.add_error_handler(error_handler)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()