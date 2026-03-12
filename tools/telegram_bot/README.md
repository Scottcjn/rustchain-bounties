# RustChain Telegram Bot

A Telegram bot for RustChain community that provides quick access to network information.

## Features

- `/balance <wallet>` - Check RTC balance for any wallet
- `/miners` - List all active miners on the network
- `/price` - Current wRTC price information
- `/health` - Node health status
- `/epoch` - Current epoch information

## Setup

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Save the API token provided

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Bot Token

Edit `bot.py` and replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 4. Run the Bot

```bash
python bot.py
```

## Usage

Start a chat with your bot on Telegram and use the commands:

- `/start` - Show welcome message and available commands
- `/balance scott` - Check balance for wallet "scott"
- `/miners` - See all active miners
- `/health` - Check node health status
- `/epoch` - Get current epoch info

## API Reference

This bot uses the RustChain API at `https://rustchain.org`:

- `GET /health` - Node health status
- `GET /epoch` - Current epoch info
- `GET /api/miners` - List of miners
- `GET /wallet/balance?miner_id={name}` - Wallet balance

**Note:** The API uses a self-signed TLS certificate. The bot handles this automatically.

## Deployment Options

### Systemd Service (Linux)

Create `/etc/systemd/system/rustchain-bot.service`:

```ini
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/telegram_bot
ExecStart=/usr/bin/python3 /path/to/telegram_bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable rustchain-bot
sudo systemctl start rustchain-bot
sudo systemctl status rustchain-bot
```

### Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py .
CMD ["python", "bot.py"]
```

Build and run:

```bash
docker build -t rustchain-bot .
docker run -d --name rustchain-bot rustchain-bot
```

## Development

### Adding New Commands

1. Add a new async command handler function:

```python
async def mycommand_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = await get_api("/my-endpoint")
    await update.message.reply_text(f"Result: {data}")
```

2. Register the handler in `main()`:

```python
application.add_handler(CommandHandler("mycommand", mycommand_command))
```

## Troubleshooting

### Bot doesn't respond

- Check if the bot token is correct
- Verify the bot is running (`python bot.py`)
- Check logs for errors

### API errors

- The RustChain node might be temporarily unavailable
- Check `https://rustchain.org/health` directly
- Verify your internet connection

### Certificate warnings

The bot automatically handles the self-signed certificate. No action needed.

## License

MIT License - Feel free to modify and distribute.

## Support

For issues or feature requests, please open an issue on the rustchain-bounties repository.
