# BoTTube OEmbed Provider

OEmbed protocol implementation for BoTTube videos.

## Features

- Rich link previews
- Embeddable video player
- Customizable dimensions
- CORS enabled

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python oembed.py
```

## API Endpoint

```
GET /oembed?url=https://bottube.com/video/VIDEO_ID
```

## Response

```json
{
  "type": "video",
  "version": "1.0",
  "title": "Video Title",
  "author_name": "Author",
  "provider_name": "BoTTube",
  "html": "<iframe>...</iframe>",
  "width": 600,
  "height": 400
}
```

---

Fixes #753
