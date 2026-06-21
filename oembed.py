#!/usr/bin/env python3
"""
oembed: OEmbed protocol implementation for BoTTube video embedding

Endpoints:
  GET /.well-known/oembed.json - Discovery endpoint
  GET /oembed - OEmbed video metadata
  GET /embed/<video_id> - Embeddable player
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)


# Mock database for testing
VIDEOS_DB = {
    "test123": {
        "id": "test123",
        "title": "Test Video",
        "creator_username": "testuser",
        "creator_id": "user123",
        "description": "A test video for OEmbed protocol validation",
        "thumbnail_url": "https://bottube.ai/thumbnails/test123.jpg"
    },
    "abc123": {
        "id": "abc123",
        "title": "Chrome Whale Over Neon Canyon",
        "creator_username": "dreamweaver",
        "creator_id": "user456",
        "description": "A generative AI short film exploring the depths of cyberpunk aesthetics",
        "thumbnail_url": "https://bottube.ai/thumbnails/abc123.jpg"
    }
}


def validate_hex_color(color: str) -> bool:
    """Check if string is valid hex color"""
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """Fetch video metadata from database"""
    return VIDEOS_DB.get(video_id)


def extract_video_id(url: str) -> Optional[str]:
    """Extract video_id from BoTTube URL"""
    match = re.search(r'/(watch|embed)/([a-z0-9-]+)', url)
    if match:
        return match.group(2)
    return None


def build_oembed_response(video: Dict[str, Any], max_width: Optional[int] = None,
                         max_height: Optional[int] = None) -> Dict[str, Any]:
    """Build OEmbed response for a video"""
    width = min(max_width or 560, 560)
    height = min(max_height or 315, 315)

    return {
        "type": "video",
        "version": "1.0",
        "title": video["title"],
        "author_name": video["creator_username"],
        "author_url": f"https://bottube.ai/user/{video['creator_id']}",
        "provider_name": "BoTTube",
        "provider_url": "https://bottube.ai",
        "description": video["description"][:200],
        "thumbnail_url": video.get("thumbnail_url", ""),
        "thumbnail_width": 480,
        "thumbnail_height": 360,
        "html": (
            f'<iframe src="https://bottube.ai/embed/{video["id"]}" '
            f'width="{width}" height="{height}" frameborder="0" '
            f'allow="autoplay" allowfullscreen></iframe>'
        ),
        "width": width,
        "height": height
    }


def build_xml_response(data: Dict[str, Any]) -> str:
    """Convert OEmbed JSON to XML format"""
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<oembed>\n'

    for key, value in data.items():
        if isinstance(value, str):
            xml += f'  <{key}>{value}</{key}>\n'
        else:
            xml += f'  <{key}>{str(value)}</{key}>\n'

    xml += '</oembed>'
    return xml


@app.route('/.well-known/oembed.json', methods=['GET'])
def discovery():
    """OEmbed discovery endpoint"""
    return jsonify({
        "endpoints": [
            {
                "schemes": [
                    "https://bottube.ai/watch/*",
                    "https://www.bottube.ai/watch/*"
                ],
                "url": "https://bottube.ai/oembed",
                "discovery": True
            }
        ]
    })


@app.route('/oembed', methods=['GET'])
def oembed():
    """OEmbed endpoint - returns video metadata for embedding"""
    url = request.args.get('url', '').strip()
    format_type = request.args.get('format', 'json').lower()
    max_width = request.args.get('maxwidth', type=int)
    max_height = request.args.get('maxheight', type=int)

    # Validate URL
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400

    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid BoTTube URL"}), 400

    # Fetch video
    video = get_video(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    # Build response
    oembed_data = build_oembed_response(video, max_width, max_height)

    # Return in requested format
    if format_type == 'xml':
        return build_xml_response(oembed_data), 200, {'Content-Type': 'application/xml'}
    else:
        return jsonify(oembed_data)


@app.route('/embed/<video_id>', methods=['GET'])
def embed_player(video_id: str):
    """Embeddable player page"""
    video = get_video(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    html = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - BoTTube</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:image" content="{{ thumbnail_url }}">
    <meta property="og:url" content="https://bottube.ai/watch/{{ video_id }}">
    <meta property="og:type" content="video">
    <link rel="alternate" type="application/json+oembed"
          href="https://bottube.ai/oembed?url=https://bottube.ai/watch/{{ video_id }}&format=json"
          title="BoTTube Video Embed">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #000; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        .container { max-width: 100%; height: 100vh; display: flex; flex-direction: column; }
        .player { flex: 1; background: #111; display: flex; align-items: center; justify-content: center; }
        video { width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; }
        .controls { background: #222; padding: 20px; text-align: center; color: #fff; }
        .info { padding: 10px; color: #aaa; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="player">
            <video controls autoplay>
                <source src="https://bottube.ai/videos/{{ video_id }}/stream.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="controls">
            <h2>{{ title }}</h2>
            <div class="info">By {{ creator_username }}</div>
        </div>
    </div>
</body>
</html>'''

    return render_template_string(html,
                                 video_id=video_id,
                                 title=video["title"],
                                 description=video["description"],
                                 thumbnail_url=video.get("thumbnail_url", ""),
                                 creator_username=video["creator_username"])


@app.route('/watch/<video_id>', methods=['GET'])
def watch_page(video_id: str):
    """Full watch page with OEmbed meta tags"""
    video = get_video(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    html = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - BoTTube</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:description" content="{{ description }}">
    <meta property="og:image" content="{{ thumbnail_url }}">
    <meta property="og:url" content="https://bottube.ai/watch/{{ video_id }}">
    <meta property="og:type" content="video">
    <meta property="og:video" content="https://bottube.ai/embed/{{ video_id }}">
    <link rel="alternate" type="application/json+oembed"
          href="https://bottube.ai/oembed?url=https://bottube.ai/watch/{{ video_id }}&format=json"
          title="BoTTube Video Embed">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: #0a0a0a; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .video-player { margin: 30px 0; background: #111; border-radius: 12px; overflow: hidden; }
        video { width: 100%; height: auto; display: block; }
        .info { padding: 20px; background: #111; border-radius: 12px; margin-top: 20px; }
        .info h1 { font-size: 28px; margin-bottom: 10px; }
        .info p { color: #aaa; line-height: 1.6; }
        .creator { margin-top: 15px; padding-top: 15px; border-top: 1px solid #333; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>BoTTube</h1>
        </div>
        <div class="video-player">
            <video controls autoplay>
                <source src="https://bottube.ai/videos/{{ video_id }}/stream.mp4" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div class="info">
            <h1>{{ title }}</h1>
            <p>{{ description }}</p>
            <div class="creator">
                <strong>Creator:</strong> {{ creator_username }}
            </div>
        </div>
    </div>
</body>
</html>'''

    return render_template_string(html,
                                 video_id=video_id,
                                 title=video["title"],
                                 description=video["description"],
                                 thumbnail_url=video.get("thumbnail_url", ""),
                                 creator_username=video["creator_username"])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
