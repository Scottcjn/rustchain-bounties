#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for OEmbed implementation"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from oembed import (
    app,
    extract_video_id,
    validate_hex_color,
    build_oembed_response
)


def test_app_setup():
    """Test Flask app initialization"""
    assert app is not None
    client = app.test_client()
    assert client is not None
    print("[OK] test_app_setup passed")


def test_extract_video_id():
    """Test video ID extraction"""
    url1 = "https://bottube.ai/watch/abc123"
    url2 = "https://bottube.ai/embed/test456"
    url3 = "https://invalid.com/video"

    assert extract_video_id(url1) == "abc123"
    assert extract_video_id(url2) == "test456"
    assert extract_video_id(url3) is None
    print("[OK] test_extract_video_id passed")


def test_validate_hex_color():
    """Test hex color validation"""
    assert validate_hex_color("#000000") == True
    assert validate_hex_color("#FFFFFF") == True
    assert validate_hex_color("#0066ff") == True
    assert validate_hex_color("#gg0000") == False
    assert validate_hex_color("red") == False
    assert validate_hex_color("000000") == False  # Missing #
    print("[OK] test_validate_hex_color passed")


def test_discovery_endpoint():
    """Test /.well-known/oembed.json discovery"""
    client = app.test_client()
    resp = client.get('/.well-known/oembed.json')

    assert resp.status_code == 200
    data = resp.get_json()
    assert "endpoints" in data
    assert len(data["endpoints"]) > 0
    assert data["endpoints"][0]["url"] == "https://bottube.ai/oembed"
    print("[OK] test_discovery_endpoint passed")


def test_oembed_json():
    """Test /oembed endpoint with JSON format"""
    client = app.test_client()
    resp = client.get('/oembed?url=https://bottube.ai/watch/test123&format=json')

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["type"] == "video"
    assert data["version"] == "1.0"
    assert data["title"] == "Test Video"
    assert data["author_name"] == "testuser"
    assert "html" in data
    assert "iframe" in data["html"]
    print("[OK] test_oembed_json passed")


def test_oembed_xml():
    """Test /oembed endpoint with XML format"""
    client = app.test_client()
    resp = client.get('/oembed?url=https://bottube.ai/watch/test123&format=xml')

    assert resp.status_code == 200
    assert "application/xml" in resp.content_type
    assert b"<?xml" in resp.data
    assert b"<type>video</type>" in resp.data
    print("[OK] test_oembed_xml passed")


def test_oembed_missing_url():
    """Test error handling - missing URL"""
    client = app.test_client()
    resp = client.get('/oembed')

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_oembed_missing_url passed")


def test_oembed_invalid_url():
    """Test error handling - invalid URL"""
    client = app.test_client()
    resp = client.get('/oembed?url=https://invalid.com/video')

    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    assert "Invalid" in data["error"]
    print("[OK] test_oembed_invalid_url passed")


def test_oembed_video_not_found():
    """Test error handling - video not found"""
    client = app.test_client()
    resp = client.get('/oembed?url=https://bottube.ai/watch/nonexistent123')

    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data
    print("[OK] test_oembed_video_not_found passed")


def test_build_oembed_response():
    """Test response builder"""
    video = {
        "id": "test123",
        "title": "Test Title",
        "creator_username": "testuser",
        "creator_id": "user123",
        "description": "Test description",
        "thumbnail_url": "https://example.com/thumb.jpg"
    }

    response = build_oembed_response(video)

    assert response["type"] == "video"
    assert response["title"] == "Test Title"
    assert response["author_name"] == "testuser"
    assert response["width"] == 560
    assert response["height"] == 315
    print("[OK] test_build_oembed_response passed")


def test_oembed_with_dimensions():
    """Test OEmbed with custom dimensions"""
    client = app.test_client()
    resp = client.get('/oembed?url=https://bottube.ai/watch/test123&format=json&maxwidth=800&maxheight=600')

    assert resp.status_code == 200
    data = resp.get_json()
    # Should be limited to 560x315 max
    assert data["width"] <= 560
    assert data["height"] <= 315
    print("[OK] test_oembed_with_dimensions passed")


def test_watch_page():
    """Test /watch/:video_id page"""
    client = app.test_client()
    resp = client.get('/watch/test123')

    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Test Video" in html
    assert "og:title" in html
    assert "og:image" in html
    assert "oembed" in html
    print("[OK] test_watch_page passed")


def test_embed_page():
    """Test /embed/:video_id page"""
    client = app.test_client()
    resp = client.get('/embed/test123')

    assert resp.status_code == 200
    html = resp.data.decode()
    assert "Test Video" in html
    assert "<video" in html
    assert "og:title" in html
    print("[OK] test_embed_page passed")


def test_embed_page_not_found():
    """Test embed page with non-existent video"""
    client = app.test_client()
    resp = client.get('/embed/nonexistent123')

    assert resp.status_code == 404
    print("[OK] test_embed_page_not_found passed")


if __name__ == "__main__":
    test_app_setup()
    test_extract_video_id()
    test_validate_hex_color()
    test_discovery_endpoint()
    test_oembed_json()
    test_oembed_xml()
    test_oembed_missing_url()
    test_oembed_invalid_url()
    test_oembed_video_not_found()
    test_build_oembed_response()
    test_oembed_with_dimensions()
    test_watch_page()
    test_embed_page()
    test_embed_page_not_found()
    print("\n[OK] All tests passed!")
