# BoTTube Auto-Upload Bot 🤖🎬

> **RustChain Bounty #449** — Build a BoTTube Bot That Uploads Daily

Automated daily video uploader for the BoTTube platform. Uploads one video per day on a configurable schedule.

## Features

- ✅ **Daily Auto-Upload** — Uploads one video per day automatically
- ✅ **Scheduled Mode** — Runs continuously with configurable interval
- ✅ **Metadata Support** — Title, description, tags, visibility, scheduled publish time
- ✅ **File Archive** — Moves uploaded videos to archive folder
- ✅ **Multi-format** — Supports mp4, mkv, avi, mov, webm
- ✅ **Error Recovery** — Graceful error handling with detailed logging
- ✅ **API Auth** — Bearer token authentication with verification

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.json config.json
# Edit config.json with your BoTTube API token and channel ID
```

### 3. Prepare Videos

Place video files in the `./videos` directory:

```
videos/
├── day1.mp4
├── day2.mp4
└── day3.mp4
```

### 4. (Optional) Create Metadata

Create `metadata.json` for custom titles/descriptions:

```json
[
    {
        "filename": "day1.mp4",
        "title": "My Awesome Video #1",
        "description": "Description for video 1",
        "tags": ["bottube", "awesome"],
        "visibility": "public",
        "schedule_time": "2026-05-16T10:00:00Z"
    }
]
```

### 5. Run

**Single run (upload one video):**

```bash
python bot.py
```

**Scheduled mode (runs forever, uploads daily):**

Set `"mode": "scheduled"` in `config.json`, then:

```bash
python bot.py
```

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `api_token` | string | *required* | BoTTube API bearer token |
| `channel_id` | string | *required* | Your channel ID |
| `mode` | string | `"daily"` | `"daily"` for one run, `"scheduled"` for continuous |
| `interval_hours` | int | `24` | Hours between uploads (scheduled mode) |
| `video_directory` | string | `"./videos"` | Path to video files |
| `metadata_file` | string | `"./metadata.json"` | Path to metadata JSON |

## How It Works

1. **Authenticate** — Verifies API token with BoTTube
2. **Scan** — Lists video files in the configured directory
3. **Upload** — Initiates upload session → streams file → finalizes
4. **Archive** — Moves uploaded file to `./videos/uploaded/`
5. **Repeat** — Waits for next interval (scheduled mode)

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/auth/verify` | GET | Verify API credentials |
| `/v1/uploads/initiate` | POST | Start upload session |
| `/v1/uploads/{id}/data` | PUT | Stream video file |
| `/v1/uploads/{id}/finalize` | POST | Publish the video |

## Project Structure

```
bottube-bot-449/
├── bot.py                 # Main bot script
├── config.example.json    # Configuration template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## License

MIT

---

*Bounty submission by zp6 for RustChain #449*
