# RustChain Telegram Bot

A Telegram bot for interacting with RustChain bounties.

## Features

- Browse available bounties
- Create new bounties
- Track your bounty submissions
- Get notifications about bounty updates
- Interactive menu system

## Setup

### Prerequisites

- Python 3.7+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Scottcjn/rustchain-bounties.git
   cd rustchain-bounties
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the bot:
   ```bash
   cp bot_config.env bot.env
   # Edit bot.env and add your bot token
   ```

4. Run the bot:
   ```bash
   python telegram_bot.py
   ```

## Usage

### Commands

- `/start` - Start interacting with the bot
- `/help` - Show help message
- `/bounties` - View all available bounties
- `/my_bounties` - View bounties you've created
- `/create_bounty` - Create a new bounty

### Interactions

The bot provides an interactive menu system with buttons for easy navigation.

## Development

### Adding New Features

1. Add new command handlers in `RustChainBot` class
2. Update the keyboard in relevant methods
3. Add new states in `user_states` dictionary if needed

### Testing

```bash
pytest tests/test_telegram_bot.py
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is part of RustChain Bounties. See [LICENSE](LICENSE) for details.
