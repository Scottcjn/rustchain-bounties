# RustChain Telegram Bot

Check RustChain wallet balance, miner status, epoch info from Telegram.

## Commands

| Command | Description |
|---------|-------------|
| /balance <wallet> | Check RTC balance |
| /miners | List active miners |
| /epoch | Current epoch info |
| /price | RTC reference rate |
| /help | Show all commands |

## Deploy

### Railway (recommended)
1. Fork this repo
2. Connect to Railway
3. Set env vars: , 
4. Deploy

### Fly.io


### Systemd
Collecting python-telegram-bot
  Downloading python_telegram_bot-22.7-py3-none-any.whl.metadata (17 kB)
Collecting httpx
  Downloading httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting anyio (from httpx)
  Downloading anyio-4.13.0-py3-none-any.whl.metadata (4.5 kB)
Requirement already satisfied: certifi in /usr/local/lib/python3.12/site-packages (from httpx) (2026.2.25)
Collecting httpcore==1.* (from httpx)
  Downloading httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Requirement already satisfied: idna in /usr/local/lib/python3.12/site-packages (from httpx) (3.11)
Collecting h11>=0.16 (from httpcore==1.*->httpx)
  Downloading h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting typing_extensions>=4.5 (from anyio->httpx)
  Using cached typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
Downloading python_telegram_bot-22.7-py3-none-any.whl (745 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 745.4/745.4 kB 68.4 kB/s eta 0:00:00
Downloading httpx-0.28.1-py3-none-any.whl (73 kB)
Downloading httpcore-1.0.9-py3-none-any.whl (78 kB)
Downloading anyio-4.13.0-py3-none-any.whl (114 kB)
Downloading h11-0.16.0-py3-none-any.whl (37 kB)
Using cached typing_extensions-4.15.0-py3-none-any.whl (44 kB)
Installing collected packages: typing_extensions, h11, httpcore, anyio, httpx, python-telegram-bot
Successfully installed anyio-4.13.0 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 python-telegram-bot-22.7 typing_extensions-4.15.0

## Features
- Rate limiting (1 req/5s per user)
- Error handling for offline node
- No external DB needed
- Python stdlib + 2 packages

## License
MIT
