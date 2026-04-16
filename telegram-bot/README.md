# RustChain Telegram Bot

A Telegram bot for checking wallet balances, miner status, epoch information, and price for the RustChain blockchain.

## Features

- **/balance <wallet>** - Check RTC wallet balance
- **/miners** - View active miners on the network
- **/epoch** - Current epoch information (block, difficulty, validators)
- **/price** - RTC price information
- **/help** - Show help message
- **/start** - Start the bot

## Rate Limiting

- 1 request per 5 seconds per user
- Protects against spam and API overload

## Prerequisites

- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Local Development

1. Clone the repository:
```bash
git clone <repo-url>
cd telegram-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export RUSTCHAIN_API_URL="https://50.28.86.131:8099"
```

4. Run the bot:
```bash
python telegram_bot.py
```

## Deployment Options

### Railway (Recommended)

1. Create a new Railway project
2. Connect your GitHub repository
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `RUSTCHAIN_API_URL` = `https://50.28.86.131:8099`
4. Deploy

### Fly.io

1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Login: `flyctl auth login`
3. Create app: `flyctl apps create rustchain-bot`
4. Deploy:
```bash
flyctl deploy
```
5. Set secrets:
```bash
flyctl secrets set TELEGRAM_BOT_TOKEN="your_token_here"
flyctl secrets set RUSTCHAIN_API_URL="https://50.28.86.131:8099"
```

### systemd (VPS/Server)

1. Copy files to server:
```bash
scp -r telegram-bot user@your-server:/opt/rustchain-bot
```

2. Create systemd service at `/etc/systemd/system/rustchain-bot.service`:
```ini
[Unit]
Description=RustChain Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/rustchain-bot
Environment=TELEGRAM_BOT_TOKEN=your_token_here
Environment=RUSTCHAIN_API_URL=https://50.28.86.131:8099
ExecStart=/usr/bin/python3 /opt/rustchain-bot/telegram_bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rustchain-bot
sudo systemctl start rustchain-bot
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY telegram_bot.py .
CMD ["python", "telegram_bot.py"]
```

Build and run:
```bash
docker build -t rustchain-bot .
docker run -d \
  --name rustchain-bot \
  -e TELEGRAM_BOT_TOKEN=your_token_here \
  -e RUSTCHAIN_API_URL=https://50.28.86.131:8099 \
  rustchain-bot
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | - | Telegram bot token from @BotFather |
| `RUSTCHAIN_API_URL` | No | `https://50.28.86.131:8099` | RustChain node API URL |

## Error Handling

- **Node Offline**: Bot returns "Could not connect to the RustChain node" message
- **SSL Errors**: Automatically handled with verify=False for self-signed certs
- **Invalid Input**: Returns usage instructions
- **Rate Limited**: Tells user to wait before retrying

## Bot Payout Wallet

All bounties and tips for bot development can be sent to:

```
RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5
```

## License

MIT License
