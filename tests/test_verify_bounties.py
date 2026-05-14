"""
Unit tests for scripts/verify_bounties.py — claim parsing, badge, and follow checks.

Covers: extract_claimants, find_existing_bot_comment, check_profile_badge,
        check_follows_owner, get_issue_reactions.
"""

import base64
import importlib
import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Import the module under test (it sys.exits if GITHUB_TOKEN is missing)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _set_github_token(monkeypatch):
    """Ensure GITHUB_TOKEN is set so verify_bounties doesn't sys.exit."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake-test-token")


@pytest.fixture()
def vb(monkeypatch):
    """Import verify_bounties with a fresh module each time."""
    mod_name = "verify_bounties"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    # Patch out the module-level sys.exit by setting env var first
    monkeypatch.setenv("GITHUB_TOKEN", "fake-test-token")
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
    mod = importlib.import_module(mod_name)
    yield mod
    sys.path.pop(0)


# ===========================================================================
# extract_claimants
# ===========================================================================

class TestExtractClaimants:
    """Tests for verify_bounties.extract_claimants."""

    def test_skips_bot_comments(self, vb):
        comments = [
            {"user": {"login": "alice"}, "id": 1, "body": f"I claim this! {vb.BOT_SIGNATURE}"},
            {"user": {"login": "bob"}, "id": 2, "body": "I claim this too! Wallet: RTCabc123"},
        ]
        result = vb.extract_claimants(comments, 100)
        # Only bob should remain — alice's comment has the bot signature
        assert len(result) == 1
        assert result[0]["username"] == "bob"

    def test_skips_owner_comments(self, vb):
        comments = [
            {"user": {"login": vb.OWNER}, "id": 10, "body": "Approved!"},
            {"user": {"login": "charlie"}, "id": 11, "body": "Claiming! Wallet: RTCdef456"},
        ]
        result = vb.extract_claimants(comments, 200)
        assert len(result) == 1
        assert result[0]["username"] == "charlie"

    def test_deduplicates_by_username(self, vb):
        comments = [
            {"user": {"login": "dave"}, "id": 20, "body": "First claim"},
            {"user": {"login": "Dave"}, "id": 21, "body": "Second claim — same user, different case"},
        ]
        result = vb.extract_claimants(comments, 300)
        assert len(result) == 1
        assert result[0]["username"] == "dave"

    def test_extracts_wallet_from_comment(self, vb):
        comments = [
            {"user": {"login": "eve"}, "id": 30, "body": "My wallet is RTCaabbccdd1122334455aabbccdd1122334455aa"},
        ]
        result = vb.extract_claimants(comments, 400)
        assert len(result) == 1
        assert result[0]["wallet"].startswith("RTC")
        assert len(result[0]["wallet"]) == 43  # RTC + 40 hex chars

    def test_wallet_fallback_matches_generic_string(self, vb):
        # WALLET_RE has a broad fallback: [a-z0-9_-]{3,40}
        comments = [
            {"user": {"login": "frank"}, "id": 40, "body": "Just a normal comment"},
        ]
        result = vb.extract_claimants(comments, 500)
        assert len(result) == 1
        # The regex matches the first 3+ char alphanumeric substring
        assert isinstance(result[0]["wallet"], str)

    def test_empty_comments_returns_empty(self, vb):
        assert vb.extract_claimants([], 600) == []

    def test_skips_empty_bodies(self, vb):
        comments = [
            {"user": {"login": "grace"}, "id": 50, "body": "   "},
        ]
        result = vb.extract_claimants(comments, 700)
        assert result == []


# ===========================================================================
# find_existing_bot_comment
# ===========================================================================

class TestFindExistingBotComment:
    """Tests for verify_bounties.find_existing_bot_comment."""

    def test_finds_bot_comment(self, vb):
        comments = [
            {"id": 1, "body": "Normal comment"},
            {"id": 2, "body": f"Bot says hi {vb.BOT_SIGNATURE}"},
        ]
        assert vb.find_existing_bot_comment(comments) == 2

    def test_returns_none_when_no_bot_comment(self, vb):
        comments = [
            {"id": 1, "body": "Normal comment"},
            {"id": 2, "body": "Another normal comment"},
        ]
        assert vb.find_existing_bot_comment(comments) is None

    def test_handles_missing_body_key(self, vb):
        comments = [
            {"id": 1},
            {"id": 2, "body": ""},
        ]
        assert vb.find_existing_bot_comment(comments) is None

    def test_empty_list_returns_none(self, vb):
        assert vb.find_existing_bot_comment([]) is None


# ===========================================================================
# check_profile_badge
# ===========================================================================

class TestCheckProfileBadge:
    """Tests for verify_bounties.check_profile_badge."""

    def test_returns_true_when_keyword_found(self, vb):
        readme_content = base64.b64encode(b"I love RustChain and use it daily!").decode()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": readme_content}

        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            found, detail = vb.check_profile_badge("testuser")
            assert found is True
            assert "rustchain" in detail.lower()

    def test_returns_false_when_no_keyword(self, vb):
        readme_content = base64.b64encode(b"Just a regular README with no mentions.").decode()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": readme_content}

        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            found, detail = vb.check_profile_badge("testuser")
            assert found is False
            assert "No RustChain" in detail

    def test_returns_false_on_404(self, vb):
        mock_resp = MagicMock()
        mock_resp.status_code = 404

        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            found, detail = vb.check_profile_badge("testuser")
            assert found is False
            assert "No profile README" in detail

    def test_case_insensitive_keyword_match(self, vb):
        readme_content = base64.b64encode(b"Built with ELYANLABS tools.").decode()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"content": readme_content}

        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            found, detail = vb.check_profile_badge("testuser")
            assert found is True
            assert "elyanlabs" in detail.lower()


# ===========================================================================
# check_follows_owner
# ===========================================================================

class TestCheckFollowsOwner:
    """Tests for verify_bounties.check_follows_owner."""

    def test_returns_true_on_204(self, vb):
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            assert vb.check_follows_owner("follower") is True

    def test_returns_false_on_404(self, vb):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            assert vb.check_follows_owner("nonfollower") is False

    def test_returns_false_on_other_status(self, vb):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        with patch.object(vb.SESSION, "get", return_value=mock_resp):
            assert vb.check_follows_owner("user") is False


# ===========================================================================
# get_issue_reactions
# ===========================================================================

class TestGetIssueReactions:
    """Tests for verify_bounties.get_issue_reactions."""

    def test_groups_reactions_by_type(self, vb):
        reactions_data = [
            {"content": "+1", "user": {"login": "alice"}},
            {"content": "+1", "user": {"login": "bob"}},
            {"content": "heart", "user": {"login": "alice"}},
        ]
        with patch.object(vb, "paginate_all", return_value=reactions_data):
            result = vb.get_issue_reactions(1234)
            assert "alice" in result["+1"]
            assert "bob" in result["+1"]
            assert "alice" in result["heart"]

    def test_skips_malformed_entries(self, vb):
        reactions_data = [
            {"content": "+1", "user": {"login": "alice"}},
            {"content": "", "user": {"login": "bob"}},  # empty content
            {"content": "heart"},  # missing user
            "not a dict",
        ]
        with patch.object(vb, "paginate_all", return_value=reactions_data):
            result = vb.get_issue_reactions(1234)
            assert "+1" in result
            assert "heart" not in result  # skipped because user missing

    def test_empty_reactions(self, vb):
        with patch.object(vb, "paginate_all", return_value=[]):
            result = vb.get_issue_reactions(1234)
            assert result == {}
