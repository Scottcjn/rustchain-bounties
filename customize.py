#!/usr/bin/env python3
"""
Video customization API endpoints

Allows creators to customize video page appearance:
- Background color/image
- Text styling
- Logo/branding
- Call-to-action button
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)


# Mock database
VIDEOS_DB = {
    "video123": {
        "id": "video123",
        "title": "Test Video",
        "creator_id": "user123",
        "creator_name": "Test Creator",
        "description": "A test video",
        "stream_url": "https://bottube.ai/videos/video123/stream.mp4"
    }
}

VIDEO_SETTINGS_DB = {}


def validate_hex_color(color: str) -> bool:
    """Validate hex color format"""
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    return url.startswith(('http://', 'https://'))


def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """Get video from database"""
    return VIDEOS_DB.get(video_id)


def get_customize_settings(video_id: str) -> Optional[Dict[str, Any]]:
    """Get custom settings for specific video"""
    return VIDEO_SETTINGS_DB.get(video_id)


def get_creator_default_settings(creator_id: str) -> Optional[Dict[str, Any]]:
    """Get creator's default settings (applies to all videos)"""
    for settings in VIDEO_SETTINGS_DB.values():
        if settings.get("creator_id") == creator_id and settings.get("video_id") is None:
            return settings
    return None


def save_customize_settings(video_id: str, creator_id: str, data: Dict[str, Any]) -> str:
    """Save customization settings"""
    settings_id = str(uuid4())

    settings = {
        "id": settings_id,
        "video_id": video_id,
        "creator_id": creator_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    # Copy allowed fields
    for field in [
        "background_color",
        "background_image_url",
        "text_color",
        "accent_color",
        "logo_url",
        "channel_name",
        "channel_description",
        "cta_button_text",
        "cta_button_url",
        "cta_button_color",
        "font_family"
    ]:
        if field in data:
            settings[field] = data[field]

    VIDEO_SETTINGS_DB[video_id] = settings
    return settings_id


@app.route('/api/videos/<video_id>/customize', methods=['GET', 'POST', 'PUT'])
def customize_video(video_id):
    """
    Customize video page appearance

    GET: Fetch customization for video or creator default
    POST: Create new customization
    PUT: Update customization
    """

    # Fetch video
    video = get_video(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    # Check authorization for write operations
    if request.method in ['POST', 'PUT']:
        # In production, check current_user.id
        # For testing, assume user is authorized
        pass

    if request.method == 'GET':
        # Try video-specific settings first
        settings = get_customize_settings(video_id)

        # Fall back to creator defaults
        if not settings:
            settings = get_creator_default_settings(video["creator_id"])

        if settings:
            return jsonify(settings)
        else:
            return jsonify({})

    if request.method in ['POST', 'PUT']:
        data = request.get_json() or {}

        # Validate colors
        for color_field in ["background_color", "text_color", "accent_color", "cta_button_color"]:
            if color_field in data:
                if not validate_hex_color(data[color_field]):
                    return jsonify({"error": f"Invalid color format: {color_field}"}), 400

        # Validate URLs
        for url_field in ["background_image_url", "logo_url", "cta_button_url"]:
            if url_field in data and data[url_field]:
                if not validate_url(data[url_field]):
                    return jsonify({"error": f"Invalid URL: {url_field}"}), 400

        # Validate font family
        valid_fonts = ["inter", "roboto", "opensans", "lato", "montserrat"]
        if "font_family" in data:
            if data["font_family"] not in valid_fonts:
                return jsonify({"error": f"Invalid font family: {data['font_family']}"}), 400

        # Save settings
        settings_id = save_customize_settings(video_id, video["creator_id"], data)

        result = {
            "id": settings_id,
            "video_id": video_id,
            "created_at": datetime.now().isoformat()
        }
        result.update(data)

        return jsonify(result), 201


@app.route('/watch/<video_id>', methods=['GET'])
def watch_page(video_id):
    """Watch page with dynamic customization"""
    video = get_video(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404

    # Get customization
    customize = get_customize_settings(video_id) or \
                get_creator_default_settings(video["creator_id"]) or {}

    # Build CSS variables
    css_vars = f"""
        --bg-color: {customize.get('background_color', '#ffffff')};
        --text-color: {customize.get('text_color', '#000000')};
        --accent-color: {customize.get('accent_color', '#0066ff')};
        --font-family: {customize.get('font_family', 'inter')};
    """

    html = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - BoTTube</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{{ title }}">
    <meta property="og:image" content="">
    <style>
        :root {
            {{ css_vars }}
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-family), sans-serif;
        }

        {% if background_image_url %}
        body {
            background-image: url('{{ background_image_url }}');
            background-size: cover;
            background-position: center;
        }
        {% endif %}

        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }

        .header-logo {
            {% if logo_url %}
            background-image: url('{{ logo_url }}');
            {% else %}
            background-image: url('/images/bottube-logo.png');
            {% endif %}
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background-size: contain;
            background-repeat: no-repeat;
        }

        h1, h2 { margin: 10px 0; }

        .video-player {
            margin: 30px 0;
            background: #111;
            border-radius: 12px;
            overflow: hidden;
        }

        video {
            width: 100%;
            height: auto;
            display: block;
        }

        .video-info {
            margin: 30px 0;
            padding: 20px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
        }

        .cta-button {
            display: inline-block;
            background-color: var(--accent-color);
            color: #ffffff;
            padding: 12px 24px;
            border-radius: 6px;
            text-decoration: none;
            margin: 20px 0;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }

        .cta-button:hover {
            opacity: 0.9;
        }

        .comments {
            margin-top: 40px;
        }

        .comment {
            padding: 15px;
            margin: 10px 0;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            {% if logo_url %}
            <div class="header-logo"></div>
            {% endif %}
            {% if channel_name %}
            <h1>{{ channel_name }}</h1>
            {% else %}
            <h1>{{ creator_name }}</h1>
            {% endif %}
            {% if channel_description %}
            <p>{{ channel_description }}</p>
            {% endif %}
        </header>

        <div class="video-player">
            <video controls>
                <source src="{{ stream_url }}" type="video/mp4">
            </video>
        </div>

        <div class="video-info">
            <h2>{{ title }}</h2>
            <p>{{ description }}</p>
        </div>

        {% if cta_button_text %}
        <a href="{{ cta_button_url }}" class="cta-button">
            {{ cta_button_text }}
        </a>
        {% else %}
        <a href="/channel/{{ creator_id }}" class="cta-button">
            Subscribe to Creator
        </a>
        {% endif %}

        <div class="comments">
            <h3>Comments</h3>
            <p>Comments section would go here...</p>
        </div>
    </div>

    <script>
        fetch('/api/videos/{{ video_id }}/customize')
            .then(r => r.json())
            .then(settings => {
                console.log('Customization loaded:', settings);
            })
            .catch(e => console.error('Failed to load customization:', e));
    </script>
</body>
</html>'''

    template_vars = {
        "video_id": video_id,
        "title": video["title"],
        "creator_name": video["creator_name"],
        "creator_id": video["creator_id"],
        "description": video["description"],
        "stream_url": video["stream_url"],
        "css_vars": css_vars,
    }
    # Add customize settings without overwriting existing vars
    for k, v in customize.items():
        if k not in template_vars:
            template_vars[k] = v

    return render_template_string(html, **template_vars)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
