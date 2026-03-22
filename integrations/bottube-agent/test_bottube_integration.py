#!/usr/bin/env python3
"""Test suite for BoTTube Agent integration.

All network calls are mocked so the suite runs offline.
Run with:
    python3 test_bottube_integration.py
or via pytest from the repo root:
    pytest integrations/bottube-agent/test_bottube_integration.py -v
"""

import json
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
import pytest

# Allow running as a standalone script from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bottube_agent import BoTTubeClient, BoTTubeAgent

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _mock_response(payload, status_code=200):
    """Return a mock requests.Response with a .json() method."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


HEALTH_OK = {"status": "ok", "version": "1.0.0"}
HEALTH_UP  = {"status": "up", "version": "2.0.0"}

VIDEOS_PAYLOAD = {
    "items": [
        {"id": "v1", "title": "First video"},
        {"id": "v2", "title": "Second video"},
    ],
    "total": 2,
    "page": 1,
}

FEED_PAYLOAD = {
    "items": [
        {"id": "f1", "title": "Trending A"},
        {"id": "f2", "title": "Trending B"},
    ]
}

UPLOAD_PAYLOAD = {"video_id": "v99", "status": "processing"}


# ─── BoTTubeClient tests ─────────────────────────────────────────────────────

class TestBoTTubeClientHealth:
    """Tests for GET /health"""

    def test_health_returns_dict(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_OK)):
            result = client.health()
        assert isinstance(result, dict)

    def test_health_status_ok(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_OK)):
            result = client.health()
        assert result["status"] == "ok"

    def test_health_status_up(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_UP)):
            result = client.health()
        assert result["status"] == "up"

    def test_health_hits_correct_path(self):
        client = BoTTubeClient(base_url="https://bottube.ai")
        mock_get = MagicMock(return_value=_mock_response(HEALTH_OK))
        with patch.object(client.session, "get", mock_get):
            client.health()
        called_url = mock_get.call_args[0][0]
        assert called_url.endswith("/health")

    def test_health_has_version(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_OK)):
            result = client.health()
        assert "version" in result


class TestBoTTubeClientVideos:
    """Tests for GET /api/videos"""

    def test_get_videos_returns_dict(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            result = client.get_videos()
        assert isinstance(result, dict)

    def test_get_videos_has_items(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            result = client.get_videos()
        assert "items" in result

    def test_get_videos_items_count(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            result = client.get_videos()
        assert len(result["items"]) == 2

    def test_get_videos_query_param(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(VIDEOS_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_videos(query="cats", limit=3)
        params = mock_get.call_args[1]["params"]
        assert params["q"] == "cats"
        assert params["limit"] == 3

    def test_get_videos_no_query_omits_q(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(VIDEOS_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_videos()
        params = mock_get.call_args[1]["params"]
        assert "q" not in params

    def test_get_videos_hits_correct_path(self):
        client = BoTTubeClient(base_url="https://bottube.ai")
        mock_get = MagicMock(return_value=_mock_response(VIDEOS_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_videos()
        called_url = mock_get.call_args[0][0]
        assert "/api/videos" in called_url

    def test_get_videos_pagination_params(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(VIDEOS_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_videos(page=2)
        params = mock_get.call_args[1]["params"]
        assert params["page"] == 2


class TestBoTTubeClientFeed:
    """Tests for GET /api/feed"""

    def test_get_feed_returns_dict(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            result = client.get_feed()
        assert isinstance(result, dict)

    def test_get_feed_has_items(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            result = client.get_feed()
        assert "items" in result

    def test_get_feed_items_count(self):
        client = BoTTubeClient()
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            result = client.get_feed()
        assert len(result["items"]) == 2

    def test_get_feed_default_type(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(FEED_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_feed()
        params = mock_get.call_args[1]["params"]
        assert params["type"] == "trending"

    def test_get_feed_custom_type(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(FEED_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_feed(feed_type="latest")
        params = mock_get.call_args[1]["params"]
        assert params["type"] == "latest"

    def test_get_feed_limit_param(self):
        client = BoTTubeClient()
        mock_get = MagicMock(return_value=_mock_response(FEED_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_feed(limit=20)
        params = mock_get.call_args[1]["params"]
        assert params["limit"] == 20

    def test_get_feed_hits_correct_path(self):
        client = BoTTubeClient(base_url="https://bottube.ai")
        mock_get = MagicMock(return_value=_mock_response(FEED_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            client.get_feed()
        called_url = mock_get.call_args[0][0]
        assert "/api/feed" in called_url


class TestBoTTubeClientUpload:
    """Tests for POST /api/upload"""

    def test_upload_returns_dict(self, tmp_path):
        video_file = tmp_path / "clip.mp4"
        video_file.write_bytes(b"\x00" * 16)
        client = BoTTubeClient()
        with patch.object(client.session, "post", return_value=_mock_response(UPLOAD_PAYLOAD)):
            result = client.upload_video(str(video_file), title="Test clip")
        assert isinstance(result, dict)

    def test_upload_returns_video_id(self, tmp_path):
        video_file = tmp_path / "clip.mp4"
        video_file.write_bytes(b"\x00" * 16)
        client = BoTTubeClient()
        with patch.object(client.session, "post", return_value=_mock_response(UPLOAD_PAYLOAD)):
            result = client.upload_video(str(video_file), title="Test clip")
        assert result["video_id"] == "v99"

    def test_upload_hits_correct_path(self, tmp_path):
        video_file = tmp_path / "clip.mp4"
        video_file.write_bytes(b"\x00" * 16)
        client = BoTTubeClient(base_url="https://bottube.ai")
        mock_post = MagicMock(return_value=_mock_response(UPLOAD_PAYLOAD))
        with patch.object(client.session, "post", mock_post):
            client.upload_video(str(video_file), title="T")
        called_url = mock_post.call_args[0][0]
        assert "/api/upload" in called_url


class TestBoTTubeClientAuth:
    """Tests for API key handling"""

    def test_no_key_no_auth_header(self):
        client = BoTTubeClient(api_key="")
        assert "Authorization" not in client.session.headers

    def test_api_key_sets_bearer_header(self):
        client = BoTTubeClient(api_key="test-key-123")
        assert client.session.headers["Authorization"] == "Bearer test-key-123"

    def test_custom_base_url(self):
        client = BoTTubeClient(base_url="http://localhost:8080")
        assert client.base_url == "http://localhost:8080"

    def test_trailing_slash_stripped(self):
        client = BoTTubeClient(base_url="https://bottube.ai/")
        assert not client.base_url.endswith("/")


# ─── BoTTubeAgent tests ──────────────────────────────────────────────────────

class TestBoTTubeAgentStartup:
    """Tests for BoTTubeAgent.startup()"""

    def test_startup_returns_true_when_ok(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_OK)):
            assert agent.startup() is True

    def test_startup_stores_health_state(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(HEALTH_OK)):
            agent.startup()
        assert agent.state["health"]["status"] == "ok"

    def test_startup_returns_false_on_network_error(self):
        import requests as req
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", side_effect=req.ConnectionError("unreachable")):
            assert agent.startup() is False

    def test_startup_stores_error_on_failure(self):
        import requests as req
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", side_effect=req.ConnectionError("down")):
            agent.startup()
        assert agent.state["health"]["status"] == "unreachable"

    def test_startup_accepts_healthy_status(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get",
                          return_value=_mock_response({"status": "healthy"})):
            assert agent.startup() is True

    def test_startup_accepts_up_status(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get",
                          return_value=_mock_response({"status": "up"})):
            assert agent.startup() is True


class TestBoTTubeAgentDiscoverVideos:
    """Tests for BoTTubeAgent.discover_videos()"""

    def test_returns_list(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            result = agent.discover_videos()
        assert isinstance(result, list)

    def test_returns_correct_count(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            result = agent.discover_videos()
        assert len(result) == 2

    def test_stores_in_state(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(VIDEOS_PAYLOAD)):
            agent.discover_videos()
        assert len(agent.state["last_videos"]) == 2

    def test_returns_empty_on_error(self):
        import requests as req
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", side_effect=req.ConnectionError()):
            result = agent.discover_videos()
        assert result == []

    def test_passes_query_to_client(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        mock_get = MagicMock(return_value=_mock_response(VIDEOS_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            agent.discover_videos(query="rustchain")
        params = mock_get.call_args[1]["params"]
        assert params["q"] == "rustchain"


class TestBoTTubeAgentFetchFeed:
    """Tests for BoTTubeAgent.fetch_feed()"""

    def test_returns_list(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            result = agent.fetch_feed()
        assert isinstance(result, list)

    def test_returns_correct_count(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            result = agent.fetch_feed()
        assert len(result) == 2

    def test_stores_in_state(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", return_value=_mock_response(FEED_PAYLOAD)):
            agent.fetch_feed()
        assert "last_feed" in agent.state

    def test_returns_empty_on_error(self):
        import requests as req
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        with patch.object(client.session, "get", side_effect=req.ConnectionError()):
            result = agent.fetch_feed()
        assert result == []

    def test_passes_feed_type(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        mock_get = MagicMock(return_value=_mock_response(FEED_PAYLOAD))
        with patch.object(client.session, "get", mock_get):
            agent.fetch_feed(feed_type="latest")
        params = mock_get.call_args[1]["params"]
        assert params["type"] == "latest"


class TestBoTTubeAgentRun:
    """Tests for BoTTubeAgent.run()"""

    def _patched_agent(self):
        client = BoTTubeClient()
        agent = BoTTubeAgent(client=client)
        # All GET calls return appropriate mocks in sequence:
        # health, feed, videos (three calls per cycle)
        responses = [
            _mock_response(HEALTH_OK),
            _mock_response(FEED_PAYLOAD),
            _mock_response(VIDEOS_PAYLOAD),
        ]
        client.session.get = MagicMock(side_effect=responses)
        return agent

    def test_run_returns_dict(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert isinstance(result, dict)

    def test_run_has_cycle_key(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert result["cycle"] == 1

    def test_run_has_healthy_key(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert "healthy" in result

    def test_run_has_feed_count(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert result["feed_count"] == 2

    def test_run_has_video_count(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert result["video_count"] == 2

    def test_run_healthy_true_when_ok(self):
        agent = self._patched_agent()
        result = agent.run(cycles=1)
        assert result["healthy"] is True


# ─── standalone runner ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import importlib
    import traceback

    passed = 0
    failed = 0

    test_classes = [
        TestBoTTubeClientHealth,
        TestBoTTubeClientVideos,
        TestBoTTubeClientFeed,
        TestBoTTubeClientUpload,
        TestBoTTubeClientAuth,
        TestBoTTubeAgentStartup,
        TestBoTTubeAgentDiscoverVideos,
        TestBoTTubeAgentFetchFeed,
        TestBoTTubeAgentRun,
    ]

    import tempfile, pathlib

    for cls in test_classes:
        print(f"\n📌 {cls.__name__}")
        obj = cls()
        for name in dir(obj):
            if not name.startswith("test_"):
                continue
            method = getattr(obj, name)
            try:
                # inject tmp_path for upload tests
                import inspect
                sig = inspect.signature(method)
                if "tmp_path" in sig.parameters:
                    with tempfile.TemporaryDirectory() as td:
                        method(tmp_path=pathlib.Path(td))
                else:
                    method()
                print(f"  ✅ {name}")
                passed += 1
            except Exception:
                print(f"  ❌ {name}")
                traceback.print_exc()
                failed += 1

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
