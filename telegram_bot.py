#!/usr/bin/env python3
"""
Telegram Bot for RustChain Bounties
This bot allows users to interact with RustChain bounties through Telegram.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RustChainBot:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.updater = Updater(token=bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('help', self.help_command))
        self.dispatcher.add_handler(CommandHandler('bounties', self.show_bounties))
        self.dispatcher.add_handler(CommandHandler('my_bounties', self.show_my_bounties))
        self.dispatcher.add_handler(CommandHandler('create_bounty', self.create_bounty))
        self.dispatcher.add_handler(CallbackQueryHandler(self.button))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_text))
        
        # State tracking
        self.user_states = {}
        
    def start(self, update: Update, context: CallbackContext):
        """Send a message when the command /start is issued."""
        user = update.effective_user
        welcome_text = f"Welcome to RustChain Bounties, {user.first_name}!\n\n"
        welcome_text += "I'm here to help you explore and manage bounties on the RustChain network.\n\n"
        welcome_text += "Use /help to see available commands."
        
        keyboard = [
            [InlineKeyboardButton("View Bounties", callback_data='view_bounties')],
            [InlineKeyboardButton("My Bounties", callback_data='my_bounties')],
            [InlineKeyboardButton("Create Bounty", callback_data='create_bounty')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    def help_command(self, update: Update, context: CallbackContext):
        """Send a message when the command /help is issued."""
        help_text = "*RustChain Bounties Bot Help*\n\n"
        help_text += "*Commands:*\n"
        help_text += "/start - Start interacting with the bot\n"
        help_text += "/help - Show this help message\n"
        help_text += "/bounties - View all available bounties\n"
        help_text += "/my_bounties - View bounties you've created\n"
        help_text += "/create_bounty - Create a new bounty\n\n"
        help_text += "*Features:*\n"
        help_text += "• Browse available bounties\n"
        help_text += "• Create new bounties\n"
        help_text += "• Track your bounty submissions\n"
        help_text += "• Get notifications about bounty updates\n"
        
        update.message.reply_text(help_text, parse_mode='Markdown')
    
    def show_bounties(self, update: Update, context: CallbackContext):
        """Show all available bounties."""
        # This would normally fetch from the RustChain API
        bounties_text = "*Available Bounties*\n\n"
        bounties_text += "1. [BOUNTY: 10 RTC] Create a Telegram bot for RustChain\n"
        bounties_text += "   Status: Open | Reward: 10 RTC\n\n"
        bounties_text += "2. [BOUNTY: 5 RTC] Implement wallet integration\n"
        bounties_text += "   Status: Open | Reward: 5 RTC\n\n"
        bounties_text += "3. [BOUNTY: 15 RTC] Build mobile app\n"
        bounties_text += "   Status: Open | Reward: 15 RTC\n\n"
        
        keyboard = [
            [InlineKeyboardButton("Refresh", callback_data='refresh_bounties')],
            [InlineKeyboardButton("Back to Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(bounties_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def show_my_bounties(self, update: Update, context: CallbackContext):
        """Show bounties created by the user."""
        user_id = update.effective_user.id
        
        # This would normally fetch from the RustChain API
        my_bounties_text = "*Your Bounties*\n\n"
        my_bounties_text += "No bounties found. Use /create_bounty to create your first bounty.\n"
        
        keyboard = [
            [InlineKeyboardButton("Create Bounty", callback_data='create_bounty')],
            [InlineKeyboardButton("Back to Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(my_bounties_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def create_bounty(self, update: Update, context: CallbackContext):
        """Start the bounty creation process."""
        user_id = update.effective_user.id
        self.user_states[user_id] = 'creating_bounty'
        
        keyboard = [
            [InlineKeyboardButton("Cancel", callback_data='cancel_creation')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            "Let's create a new bounty! Please provide the following information:\n\n"
            "1. Bounty title\n"
            "2. Bounty description\n"
            "3. Reward amount (RTC)\n\n"
            "Send each item one by one, starting with the title.",
            reply_markup=reply_markup
        )
    
    def handle_text(self, update: Update, context: CallbackContext):
        """Handle text messages based on user state."""
        user_id = update.effective_user.id
        
        if user_id in self.user_states and self.user_states[user_id] == 'creating_bounty':
            self.handle_bounty_creation(update, context)
    
    def handle_bounty_creation(self, update: Update, context: CallbackContext):
        """Handle bounty creation steps."""
        user_id = update.effective_user.id
        text = update.message.text
        
        # This is a simplified version - in a real implementation,
        # you'd track which step of the creation process you're in
        
        # For now, just acknowledge the input
        update.message.reply_text(
            "Thank you! Your bounty creation request has been received.\n\n"
            "In a full implementation, this would be processed and added to the RustChain bounty system."
        )
        
        # Reset state
        del self.user_states[user_id]
    
    def button(self, update: Update, context: CallbackContext):
        """Handle button presses."""
        query = update.callback_query
        query.answer()
        
        if query.data == 'view_bounties':
            self.show_bounties(update, context)
        elif query.data == 'my_bounties':
            self.show_my_bounties(update, context)
        elif query.data == 'create_bounty':
            self.create_bounty(update, context)
        elif query.data == 'main_menu':
            self.start(update, context)
        elif query.data == 'refresh_bounties':
            self.show_bounties(update, context)
        elif query.data == 'cancel_creation':
            user_id = update.effective_user.id
            if user_id in self.user_states:
                del self.user_states[user_id]
            query.edit_message_text(text="Bounty creation cancelled.")
    
    def run(self):
        """Start the bot."""
        logger.info("Starting RustChain Telegram Bot...")
        self.updater.start_polling()
        self.updater.idle()

def main():
    """Main function to run the bot."""
    # Get bot token from environment variable
    bot_token = os.getenv('RUSTCHAIN_BOT_TOKEN')
    
    if not bot_token:
        logger.error("Bot token not found. Please set RUSTCHAIN_BOT_TOKEN environment variable.")
        return
    
    bot = RustChainBot(bot_token)
    bot.run()

if __name__ == '__main__':
    main()
