#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for the wallet resolution in scripts/bounty_payout.py.

Validates:
  - native RTC address in body wins over handle
  - handle from issue body is used when no native address
  - handle from non-bot comment is used as fallback
  - bot-authored comments are skipped
  - claimant_login fallback works
  - "TBD"/"pending" labels fall through; no wallet returns (None, None)
  - bot claimant is rejected
  - invalid handle shapes (e.g. "id", "TBD") are rejected
"""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path

# Set dummy env vars BEFORE importing the module so its module-level
# os.environ reads succeed (we never call transfer() in these tests).
os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")
os.environ.setdefault("RATE_RTC", "3")
os.environ.setdefault("MAX_PER_RUN", "40")

# Pre-stub subprocess so the module-level code does nothing when no gh CLI is
# available in the test environment.
_orig_run = subprocess.run


def _stub_run(*a, **kw):
    class _R:
        stdout = "[]"
        stderr = ""
        returncode = 0
    return _R()


subprocess.run = _stub_run
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
    SCRIPT = REPO_ROOT / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout_under_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run

NATIVE_WALLET = "RTC" + "0" * 40


class ResolveWalletTests(unittest.TestCase):
    def test_native_wallet_in_body(self):
        body = f"Send to {NATIVE_WALLET} please."
        w, src = bp.resolve_wallet(body, [], claimant_login="alice")
        self.assertEqual(w, NATIVE_WALLET)
        self.assertEqual(src, "native")

    def test_handle_in_body_when_no_native(self):
        body = "Wallet: alice\n"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_native_wins_over_handle_in_same_body(self):
        body = f"Wallet: alice\nfallback: {NATIVE_WALLET}\n"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, NATIVE_WALLET)
        self.assertEqual(src, "native")

    def test_handle_in_newest_non_bot_comment(self):
        body = "no wallet in body"
        # comments are oldest -> newest; the newest (last) wins.
        comments = [
            {"user": {"login": "eviler", "type": "User"}, "body": "Wallet: carol"},
            {"user": {"login": "noise", "type": "User"}, "body": "Wallet: dave"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "dave")
        self.assertEqual(src, "handle")

    def test_bot_comment_handle_is_ignored(self):
        body = "no wallet in body"
        comments = [
            {"user": {"login": "ci-bot", "type": "Bot"}, "body": "Wallet: evilbot"},
            {"user": {"login": "realuser", "type": "User"}, "body": "Wallet: realuser"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "realuser")
        self.assertEqual(src, "handle")

    def test_bot_suffix_login_is_ignored(self):
        body = "no wallet in body"
        comments = [
            {"user": {"login": "dependabot[bot]"}, "body": "Wallet: dependabot"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        # comment is bot-authored, so skipped; no other handle -> claimant_login fallback
        self.assertEqual(w, "bob")
        self.assertEqual(src, "handle")

    def test_claimant_login_fallback(self):
        body = "no wallet in body"
        comments = []
        w, src = bp.resolve_wallet(body, comments, claimant_login="alice")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_bot_claimant_rejected(self):
        body = "no wallet in body"
        comments = []
        w, src = bp.resolve_wallet(body, comments, claimant_login="dependabot[bot]")
        self.assertIsNone(w)
        self.assertIsNone(src)

    def test_tbd_label_falls_through_to_claimant(self):
        # "Wallet: TBD" is not a real handle; the script should fall through
        # to the claimant_login fallback. This is the desired safety behavior:
        # TBD labels are filtered, but a non-bot claimant still has a path.
        body = "Wallet: TBD"
        comments = []
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "bob")
        self.assertEqual(src, "handle")

    def test_empty_body_no_comments_no_claimant(self):
        w, src = bp.resolve_wallet("", [], claimant_login=None)
        self.assertIsNone(w)
        self.assertIsNone(src)

    def test_tbd_label_without_claimant_returns_none(self):
        body = "Wallet: TBD"
        comments = []
        w, src = bp.resolve_wallet(body, comments, claimant_login=None)
        self.assertIsNone(w)
        self.assertIsNone(src)

    def test_handle_in_body_with_extra_whitespace(self):
        body = "\n  Wallet:   alice  \n"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_handle_in_body_with_inline_code(self):
        body = "Wallet: `alice`"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_label_word_rejected(self):
        # "Wallet: address" should NOT be treated as a handle.
        body = "Wallet: address"
        comments = []
        w, src = bp.resolve_wallet(body, comments, claimant_login="alice")
        # falls back to claimant_login
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")


class BotDetectionTests(unittest.TestCase):
    def test_bot_via_type(self):
        self.assertTrue(bp._is_bot_login("anything", {"type": "Bot"}))

    def test_bot_via_suffix(self):
        self.assertTrue(bp._is_bot_login("dependabot[bot]", None))

    def test_human_user(self):
        self.assertFalse(bp._is_bot_login("alice", {"type": "User"}))


class HandleShapeTests(unittest.TestCase):
    def test_native_rejected_as_handle(self):
        self.assertFalse(bp._looks_like_handle(NATIVE_WALLET))

    def test_typical_login_accepted(self):
        for h in ("alice", "dependabot", "user_name", "user-name", "A1"):
            self.assertTrue(bp._looks_like_handle(h), f"{h!r} should be accepted")

    def test_label_words_rejected(self):
        for w in (
            "address",
            "wallet",
            "id",
            "TBD",
            "TBA",
            "N/A",
            "none",
            "null",
            "the",
            "my",
            "your",
            "this",
            "pending",
            "see",
            "comment",
            "issue",
        ):
            self.assertFalse(bp._looks_like_handle(w), f"label {w!r} should be rejected")

    def test_empty_rejected(self):
        self.assertFalse(bp._looks_like_handle(""))

    def test_too_long_rejected(self):
        # GitHub login max 39 chars
        self.assertFalse(bp._looks_like_handle("a" * 40))


if __name__ == "__main__":
    unittest.main()
