#!/usr/bin/env python3
"""BoTTube Python SDK Tests - Enhanced coverage"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from urllib.error import URLError, HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from rustchain_sdk.bottube import (
    BoTTubeClient,
    BoTTubeError,
    UploadError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    create_client,
)
from rustchain_sdk.bottube.client import RateLimiter
from rustchain_sdk.bottube.exceptions import AuthenticationError, APIError


def _mock_response(data, status_code=200):
    mock = MagicMock()
    mock.read.return_value = json.dumps(data).encode()
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=None)
    return mock


class TestBoTTubeClientInit:
    def test_default_initialization(self):
        client = BoTTubeClient()
        assert client.base_url == "https://bottube.ai"
        assert client.api_key is None
        assert client.timeout == 30
        assert client.retry_count == 3

    def test_custom_initialization(self):
        client = BoTTubeClient(api_key="test_key", base_url="https://custom.bottube.ai", timeout=60, retry_count=5)
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.bottube.ai"

    def test_base_url_trailing_slash_removed(self):
        client = BoTTubeClient(base_url="https://bottube.ai/")
        assert client.base_url == "https://bottube.ai"

    def test_retry_count_clamped(self):
        client = BoTTubeClient(retry_count=-1)
        assert client.retry_count == 0
        client = BoTTubeClient(retry_count=100)
        assert client.retry_count == 10

    def test_repr(self):
        client = BoTTubeClient()
        assert "BoTTubeClient" in repr(client)

    def test_version(self):
        assert BoTTubeClient.VERSION == "0.2.0"


class TestRateLimiter:
    def test_allows_up_to_max(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        limiter.acquire()
        limiter.acquire()
        limiter.acquire()
        with pytest.raises(RateLimitError):
            limiter.acquire()

    def test_remaining_property(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.remaining == 5
        limiter.acquire()
        assert limiter.remaining == 4


class TestHealthEndpoint:
    @patch("rustchain_sdk.bottube.client.urllib.request.urlopen")
    def test_health_success(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({"status": "ok"})
        client = BoTTubeClient()
        result = client.health()
        assert result["status"] == "ok"

    @patch("rustchain_sdk.bottube.client.urllib.request.urlopen")
    def test_health_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError("Connection refused")
        client = BoTTubeClient(retry_count=1)
        with pytest.raises(APIError):
            client.health()


class TestTrendingEndpoint:
    @patch("rustchain_sdk.bottube.client.urllib.request.urlopen")
    def test_trending_default(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({"videos": [{"id": "t1"}]})
        client = BoTTubeClient()
        result = client.trending()
        assert "videos" in result

    def test_trending_invalid_period(self):
        client = BoTTubeClient()
        with pytest.raises(ValidationError):
            client.trending(period="1y")


class TestSearchEndpoint:
    @patch("rustchain_sdk.bottube.client.urllib.request.urlopen")
    def test_search_basic(self, mock_urlopen):
        mock_urlopen.return_value = _mock_response({"results": [{"id": "s1"}]})
        client = BoTTubeClient()
        result = client.search("tutorial")
        assert "results" in result

    def test_search_empty_query(self):
        client = BoTTubeClient()
        with pytest.raises(ValidationError):
            client.search("")

    def test_search_invalid_sort(self):
        client = BoTTubeClient()
        with pytest.raises(ValidationError):
            client.search("test", sort="random")


class TestCommentEndpoint:
    def test_comment_requires_auth(self):
        client = BoTTubeClient()
        with pytest.raises(AuthenticationError):
            client.comment(video_id="v1", text="Nice!")

    def test_comment_validates_empty_text(self):
        client = BoTTubeClient(api_key="key")
        with pytest.raises(ValidationError):
            client.comment(video_id="v1", text="")

    def test_comment_validates_long_text(self):
        client = BoTTubeClient(api_key="key")
        with pytest.raises(ValidationError):
            client.comment(video_id="v1", text="x" * 2001)


class TestVoteEndpoint:
    def test_vote_requires_auth(self):
        client = BoTTubeClient()
        with pytest.raises(AuthenticationError):
            client.vote(video_id="v1")

    def test_vote_invalid_direction(self):
        client = BoTTubeClient(api_key="key")
        with pytest.raises(ValidationError):
            client.vote(video_id="v1", direction="sideways")


class TestVideoEndpoint:
    def test_video_empty_id(self):
        client = BoTTubeClient()
        with pytest.raises(ValidationError):
            client.video("")

    @patch("rustchain_sdk.bottube.client.urllib.request.urlopen")
    def test_video_not_found(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url="https://bottube.ai/api/videos/bad",
            code=404, msg="Not Found", hdrs={}, fp=None
        )
        client = BoTTubeClient(retry_count=1)
        with pytest.raises(NotFoundError):
            client.video("bad_id")


class TestRegisterAgent:
    def test_requires_auth(self):
        client = BoTTubeClient()
        with pytest.raises(AuthenticationError):
            client.register_agent(name="Bot", description="A test bot")

    def test_name_too_short(self):
        client = BoTTubeClient(api_key="key")
        with pytest.raises(ValidationError):
            client.register_agent(name="A", description="A decent description here")

    def test_description_too_short(self):
        client = BoTTubeClient(api_key="key")
        with pytest.raises(ValidationError):
            client.register_agent(name="MyBot", description="short")


class TestAnalytics:
    def test_analytics_requires_id(self):
        client = BoTTubeClient()
        with pytest.raises(BoTTubeError):
            client.analytics()


class TestAgentProfile:
    def test_agent_profile_empty_id(self):
        client = BoTTubeClient()
        with pytest.raises(ValidationError):
            client.agent_profile("")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
