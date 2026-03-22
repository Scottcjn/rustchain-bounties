"""Unit tests for BoTTube Telegram Bot (Bounty #2299)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent dir so we can import bot module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import bot


# ── format_video tests ──────────────────────────────────────────

def test_format_video_basic():
    v = {"id": "abc123", "title": "Test Video", "agent_name": "sophia", "views": 1234}
    result = bot.format_video(v)
    assert "Test Video" in result
    assert "sophia" in result
    assert "1,234" in result
    assert "abc123" in result


def test_format_video_with_index():
    v = {"id": "x1", "title": "My Video", "creator": "agent1", "views": 50}
    result = bot.format_video(v, index=1)
    assert result.startswith("1.")
    assert "My Video" in result


def test_format_video_fallback_fields():
    # Should use 'creator' when 'agent_name' is missing
    v = {"id": "id1", "title": "Vid", "creator": "creator1", "view_count": 999}
    result = bot.format_video(v)
    assert "creator1" in result
    assert "999" in result


def test_format_video_list_empty():
    assert bot.format_video_list([]) == "No videos found."


def test_format_video_list_multiple():
    videos = [
        {"id": f"v{i}", "title": f"Video {i}", "agent_name": "bot", "views": i * 10}
        for i in range(3)
    ]
    result = bot.format_video_list(videos)
    assert "1." in result
    assert "2." in result
    assert "3." in result
    assert "Video 0" in result
    assert "Video 2" in result


def test_format_video_long_title_truncated():
    long_title = "A" * 100
    v = {"id": "x", "title": long_title, "agent_name": "a", "views": 0}
    result = bot.format_video(v)
    # Title is truncated at 60 chars in format_video
    assert "A" * 60 in result
    assert "A" * 61 not in result


# ── Wallet store tests ──────────────────────────────────────────

def test_wallet_store_set_and_get():
    user_id = 999999
    bot._user_wallets[user_id] = "my-wallet-123"
    assert bot._user_wallets.get(user_id) == "my-wallet-123"


def test_wallet_store_missing():
    assert bot._user_wallets.get(0) is None


# ── API helper tests (mocked) ───────────────────────────────────

def make_mock_response(data, status=200):
    mock = MagicMock()
    mock.status_code = status
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


def test_fetch_latest_list_response():
    videos = [{"id": f"v{i}", "title": f"T{i}"} for i in range(5)]
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response(videos)
        result = bot.fetch_latest(5)
    assert len(result) == 5
    assert result[0]["id"] == "v0"


def test_fetch_latest_dict_response():
    videos = [{"id": f"v{i}"} for i in range(3)]
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response({"videos": videos})
        result = bot.fetch_latest(3)
    assert len(result) == 3


def test_fetch_trending_list_response():
    videos = [{"id": f"t{i}", "views": i * 100} for i in range(5)]
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response({"items": videos})
        result = bot.fetch_trending(5)
    assert len(result) == 5


def test_fetch_search_results():
    videos = [{"id": "s1", "title": "AI Video"}]
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response({"results": videos})
        result = bot.fetch_search("AI")
    assert len(result) == 1
    assert result[0]["title"] == "AI Video"


def test_fetch_video_found():
    video_data = {"id": "abc", "title": "My Video", "creator": "bot1", "views": 42}
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response(video_data)
        result = bot.fetch_video("abc")
    assert result["title"] == "My Video"


def test_fetch_video_not_found():
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response({}, status=404)
        result = bot.fetch_video("nonexistent")
    assert result is None


def test_fetch_agent_found():
    agent_data = {"name": "sophia", "video_count": 10, "total_views": 5000}
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response(agent_data)
        result = bot.fetch_agent("sophia")
    assert result["name"] == "sophia"
    assert result["video_count"] == 10


def test_fetch_agent_not_found():
    with patch("httpx.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = make_mock_response({}, status=404)
        result = bot.fetch_agent("nonexistent-agent")
    assert result is None


# ── Tip flow tests ──────────────────────────────────────────────

def test_send_tip_video_not_found():
    with patch("bot.fetch_video", return_value=None):
        result = bot.send_tip("bad_id", "my-wallet", 5.0)
    assert result["error"] == "Video not found"


def test_send_tip_no_creator_wallet():
    with patch("bot.fetch_video", return_value={"id": "v1", "title": "X"}):
        result = bot.send_tip("v1", "my-wallet", 5.0)
    assert "error" in result
    assert "wallet" in result["error"].lower()


def test_send_tip_success():
    video = {"id": "v1", "title": "X", "creator_wallet": "creator-wallet-abc"}
    with patch("bot.fetch_video", return_value=video):
        with patch("httpx.Client") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = make_mock_response({"tx_id": "tx123"})
            result = bot.send_tip("v1", "my-wallet", 5.0)
    assert result["tx_id"] == "tx123"


# ── Command handler tests (async) ───────────────────────────────

@pytest.mark.asyncio
async def test_cmd_start_sends_help():
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    context.args = []
    await bot.cmd_start(update, context)
    update.message.reply_text.assert_called_once()
    call_text = update.message.reply_text.call_args[0][0]
    assert "BoTTube" in call_text
    assert "/latest" in call_text


@pytest.mark.asyncio
async def test_cmd_latest_success():
    videos = [{"id": f"v{i}", "title": f"Video {i}", "agent_name": "bot", "views": i} for i in range(3)]
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    with patch("bot.fetch_latest", return_value=videos):
        await bot.cmd_latest(update, context)
    assert update.message.reply_text.call_count == 2  # "fetching..." + results


@pytest.mark.asyncio
async def test_cmd_latest_error():
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    with patch("bot.fetch_latest", side_effect=Exception("Network error")):
        await bot.cmd_latest(update, context)
    last_call = update.message.reply_text.call_args[0][0]
    assert "❌" in last_call


@pytest.mark.asyncio
async def test_cmd_watch_no_args():
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    context.args = []
    await bot.cmd_watch(update, context)
    call_text = update.message.reply_text.call_args[0][0]
    assert "Usage" in call_text


@pytest.mark.asyncio
async def test_cmd_watch_found():
    video = {"id": "v1", "title": "My Video", "creator": "bot1", "views": 99}
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    context.args = ["v1"]
    with patch("bot.fetch_video", return_value=video):
        await bot.cmd_watch(update, context)
    # Should reply with video info
    assert update.message.reply_text.called or update.message.reply_photo.called


@pytest.mark.asyncio
async def test_cmd_search_no_args():
    update = MagicMock()
    update.message = AsyncMock()
    context = MagicMock()
    context.args = []
    await bot.cmd_search(update, context)
    call_text = update.message.reply_text.call_args[0][0]
    assert "Usage" in call_text


@pytest.mark.asyncio
async def test_cmd_link_sets_wallet():
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.message = AsyncMock()
    context = MagicMock()
    context.args = ["my-rtc-wallet"]
    await bot.cmd_link(update, context)
    assert bot._user_wallets.get(12345) == "my-rtc-wallet"
    call_text = update.message.reply_text.call_args[0][0]
    assert "linked" in call_text.lower()


@pytest.mark.asyncio
async def test_cmd_tip_no_wallet():
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 99999  # no wallet linked
    update.message = AsyncMock()
    context = MagicMock()
    context.args = ["v1", "5"]
    bot._user_wallets.pop(99999, None)
    await bot.cmd_tip(update, context)
    call_text = update.message.reply_text.call_args[0][0]
    assert "wallet" in call_text.lower()


@pytest.mark.asyncio
async def test_cmd_tip_bad_amount():
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 77777
    update.message = AsyncMock()
    context = MagicMock()
    context.args = ["v1", "notanumber"]
    bot._user_wallets[77777] = "wallet-abc"
    await bot.cmd_tip(update, context)
    call_text = update.message.reply_text.call_args[0][0]
    assert "Invalid" in call_text or "invalid" in call_text


@pytest.mark.asyncio
async def test_inline_query_returns_results():
    videos = [
        {"id": f"v{i}", "title": f"Result {i}", "agent_name": "bot", "views": i * 10}
        for i in range(3)
    ]
    update = MagicMock()
    update.inline_query = AsyncMock()
    update.inline_query.query = "test query"
    context = MagicMock()
    with patch("bot.fetch_search", return_value=videos):
        await bot.inline_query(update, context)
    update.inline_query.answer.assert_called_once()
    results = update.inline_query.answer.call_args[0][0]
    assert len(results) == 3


@pytest.mark.asyncio
async def test_inline_query_empty_string():
    update = MagicMock()
    update.inline_query = AsyncMock()
    update.inline_query.query = ""
    context = MagicMock()
    await bot.inline_query(update, context)
    update.inline_query.answer.assert_not_called()
