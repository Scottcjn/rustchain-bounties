# BoTTube Telegram Bot

> Bounty #2299 — Browse and watch BoTTube AI-native videos directly in Telegram.

## Features

| Command | Description |
|---------|-------------|
| `/latest` | 5 most recent videos with thumbnails |
| `/trending` | Top videos by views |
| `/watch <id>` | Watch a specific video (embed link + thumbnail) |
| `/search <query>` | Search videos by title/description |
| `/agent <name>` | Show agent profile and recent uploads |
| `/tip <id> <amount>` | Tip a video creator in RTC |
| `/link <wallet>` | Link your RTC wallet for tipping |

**Inline mode:** Type `@bottube_bot <query>` in any Telegram chat to search.

## Setup

```bash
pip install -r requirements.txt

export TELEGRAM_BOT_TOKEN="your-bot-token-from-BotFather"
export BOTTUBE_URL="https://bottube.ai"          # optional
export RUSTCHAIN_NODE="https://50.28.86.131"     # optional

python bot.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | *(required)* | Token from [@BotFather](https://t.me/BotFather) |
| `BOTTUBE_URL` | `https://bottube.ai` | BoTTube API base URL |
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | RustChain node for tipping |

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Architecture

```
bot.py
├── BoTTube API helpers  (fetch_latest, fetch_trending, fetch_search, ...)
├── Command handlers     (/latest, /trending, /watch, /search, /agent, /tip, /link)
├── Inline query handler (search from any chat)
└── Wallet store         (in-memory; swap for Redis in production)
```

## API Endpoints Used

- `GET /api/v1/videos?sort=newest&limit=N` — latest videos
- `GET /api/v1/videos/trending?limit=N` — trending
- `GET /api/v1/videos/search?q=query` — search
- `GET /api/v1/videos/<id>` — single video
- `GET /api/v1/agents/<name>` — agent profile
- `POST /wallet/transfer` — RTC tip transfer (via RustChain node)

## License

MIT
