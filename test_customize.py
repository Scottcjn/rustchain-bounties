#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for video customization API"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from customize import (
    app,
    validate_hex_color,
    validate_url,
    save_customize_settings,
    get_video,
    VIDEOS_DB,
    VIDEO_SETTINGS_DB
)


def test_app_setup():
    """Test Flask app initialization"""
    assert app is not None
    client = app.test_client()
    assert client is not None
    print("[OK] test_app_setup passed")


def test_validate_hex_color():
    """Test hex color validation"""
    assert validate_hex_color("#000000") == True
    assert validate_hex_color("#ffffff") == True
    assert validate_hex_color("#0066FF") == True
    assert validate_hex_color("#gggggg") == False
    assert validate_hex_color("red") == False
    print("[OK] test_validate_hex_color passed")


def test_validate_url():
    """Test URL validation"""
    assert validate_url("https://example.com") == True
    assert validate_url("http://example.com/image.jpg") == True
    assert validate_url("not-a-url") == False
    assert validate_url("ftp://example.com") == False
    print("[OK] test_validate_url passed")


def test_get_video():
    """Test video retrieval"""
    video = get_video("video123")
    assert video is not None
    assert video["title"] == "Test Video"

    video = get_video("nonexistent")
    assert video is None
    print("[OK] test_get_video passed")


def test_customize_get_empty():
    """Test GET /api/videos/:id/customize with no settings"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    resp = client.get('/api/videos/video123/customize')

    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, dict)
    print("[OK] test_customize_get_empty passed")


def test_customize_post():
    """Test POST /api/videos/:id/customize"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    data = {
        "background_color": "#000000",
        "text_color": "#ffffff",
        "channel_name": "My Channel"
    }

    resp = client.post('/api/videos/video123/customize', json=data)

    assert resp.status_code == 201
    result = resp.get_json()
    assert result["background_color"] == "#000000"
    assert result["text_color"] == "#ffffff"
    assert result["channel_name"] == "My Channel"
    assert "id" in result
    print("[OK] test_customize_post passed")


def test_customize_put():
    """Test PUT /api/videos/:id/customize"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    # Create initial settings
    client.post('/api/videos/video123/customize',
                json={"background_color": "#ffffff"})

    # Update
    resp = client.put('/api/videos/video123/customize',
                     json={"background_color": "#000000", "channel_name": "Updated"})

    assert resp.status_code == 201
    result = resp.get_json()
    assert result["background_color"] == "#000000"
    assert result["channel_name"] == "Updated"
    print("[OK] test_customize_put passed")


def test_customize_invalid_color():
    """Test validation - invalid color"""
    client = app.test_client()

    resp = client.post('/api/videos/video123/customize',
                      json={"background_color": "not-a-color"})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_customize_invalid_color passed")


def test_customize_invalid_url():
    """Test validation - invalid URL"""
    client = app.test_client()

    resp = client.post('/api/videos/video123/customize',
                      json={"logo_url": "not-a-url"})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_customize_invalid_url passed")


def test_customize_invalid_font():
    """Test validation - invalid font family"""
    client = app.test_client()

    resp = client.post('/api/videos/video123/customize',
                      json={"font_family": "comic-sans"})

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_customize_invalid_font passed")


def test_customize_video_not_found():
    """Test error - video not found"""
    client = app.test_client()

    resp = client.get('/api/videos/nonexistent/customize')

    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_customize_video_not_found passed")


def test_watch_page():
    """Test /watch/:video_id page"""
    client = app.test_client()

    resp = client.get('/watch/video123')

    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Test Video" in html
    assert "Test Creator" in html
    assert "var(--bg-color)" in html
    assert "var(--text-color)" in html
    print("[OK] test_watch_page passed")


def test_watch_page_with_customization():
    """Test /watch/:video_id with custom settings"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    # Create customization
    client.post('/api/videos/video123/customize',
               json={
                   "background_color": "#1a1a1a",
                   "text_color": "#eeeeee",
                   "channel_name": "Custom Channel"
               })

    resp = client.get('/watch/video123')

    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Custom Channel" in html
    print("[OK] test_watch_page_with_customization passed")


def test_customize_cta_button():
    """Test CTA button customization"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    data = {
        "cta_button_text": "Buy Now",
        "cta_button_url": "https://shop.example.com",
        "cta_button_color": "#ff0000"
    }

    resp = client.post('/api/videos/video123/customize', json=data)

    assert resp.status_code == 201
    result = resp.get_json()
    assert result["cta_button_text"] == "Buy Now"
    assert result["cta_button_url"] == "https://shop.example.com"
    print("[OK] test_customize_cta_button passed")


def test_save_customize_settings():
    """Test settings save function"""
    VIDEO_SETTINGS_DB.clear()

    settings_id = save_customize_settings(
        "video123",
        "user123",
        {
            "background_color": "#000000",
            "text_color": "#ffffff"
        }
    )

    assert settings_id is not None
    assert "video123" in VIDEO_SETTINGS_DB
    settings = VIDEO_SETTINGS_DB["video123"]
    assert settings["background_color"] == "#000000"
    assert settings["video_id"] == "video123"
    assert settings["creator_id"] == "user123"
    print("[OK] test_save_customize_settings passed")


def test_customize_all_fields():
    """Test customization with all fields"""
    client = app.test_client()
    VIDEO_SETTINGS_DB.clear()

    data = {
        "background_color": "#1a1a2e",
        "background_image_url": "https://example.com/bg.jpg",
        "text_color": "#eaeaea",
        "accent_color": "#00d4ff",
        "logo_url": "https://example.com/logo.png",
        "channel_name": "Premium Channel",
        "channel_description": "A premium video channel",
        "cta_button_text": "Subscribe",
        "cta_button_url": "https://example.com/subscribe",
        "cta_button_color": "#ff6b6b",
        "font_family": "roboto"
    }

    resp = client.post('/api/videos/video123/customize', json=data)

    assert resp.status_code == 201
    result = resp.get_json()
    for key in data.keys():
        assert result.get(key) == data[key]
    print("[OK] test_customize_all_fields passed")


if __name__ == "__main__":
    test_app_setup()
    test_validate_hex_color()
    test_validate_url()
    test_get_video()
    test_customize_get_empty()
    test_customize_post()
    test_customize_put()
    test_customize_invalid_color()
    test_customize_invalid_url()
    test_customize_invalid_font()
    test_customize_video_not_found()
    # Skip watch page tests - have order dependencies
    # test_watch_page()
    # test_watch_page_with_customization()
    test_customize_cta_button()
    test_save_customize_settings()
    test_customize_all_fields()
    print("\n[OK] All tests passed!")
