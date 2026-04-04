# Tech News BoTTube Bot

A bot that generates daily tech news recap videos and posts them via BoTTube API.

## Overview

This bot scrapes tech news (Rust, blockchain, Web3, AI), generates a text-based script, creates a slideshow-style video using ffmpeg, and uploads it via the BoTTube API.

## Personality

**Daily RustChain Tech News** — Your go-to daily digest of everything happening in the Rust, blockchain, and Web3 ecosystem. Concise, informative, and straight to the point.

## Directory Structure

```
tech-news-bottube-bot/
├── bot.py              # Main bot logic
├── video_generator.sh  # ffmpeg video generation
├── config.example      # Configuration template
└── README.md
```

## Setup

1. Copy `config.example` to `config.py`:
   ```bash
   cp config.example config.py
   ```

2. Install dependencies:
   ```bash
   pip install requests feedparser Pillow
   ```

3. Install ffmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg
   ```

4. Configure your settings in `config.py`

## Configuration

| Variable | Description |
|----------|-------------|
| `BOTTUBE_API_KEY` | Your BoTTube API key |
| `BOTTUBE_API_URL` | BoTTube upload endpoint |
| `NEWS_SOURCES` | RSS feed URLs for news |
| `VIDEO_OUTPUT_DIR` | Where to save generated videos |
| `DAILY_POST_TIME` | Cron-style schedule (HH:MM UTC) |

## Usage

```bash
# Run the daily news generation and upload
python bot.py

# Or run with a custom config path
python bot.py --config /path/to/config.py
```

## BoTTube API

The bot uses the BoTTube API to upload videos. The expected API format:

```
POST {BOTTUBE_API_URL}
Headers:
  Authorization: Bearer {BOTTUBE_API_KEY}
  Content-Type: multipart/form-data
Body:
  file: <video file>
  title: <video title>
  description: <video description>
```

## Video Format

- Resolution: 1280x720 (720p)
- Format: MP4 (H.264 + AAC)
- Style: Slideshow with text overlays, 3-second slides
- Duration: ~60 seconds per episode

## License

MIT
