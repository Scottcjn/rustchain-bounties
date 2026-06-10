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


class MarkdownFormRegressionTests(unittest.TestCase):
    """Regression tests for the v2 HANDLE_RE loosening.

    Each test mirrors the exact text that real claim bodies/comments
    used, so future changes to the regex are forced to keep matching
    the field-tested forms.
    """

    def test_markdown_h2_header(self):
        body = "## Wallet: jdjioe5-cpu (GitHub handle)"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "jdjioe5-cpu")
        self.assertEqual(src, "handle")

    def test_markdown_bold_label(self):
        body = "**Wallet:** `jdjioe5-cpu` (GitHub handle, no native `RTC…` address on file)"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "jdjioe5-cpu")
        self.assertEqual(src, "handle")

    def test_markdown_bold_alternate(self):
        # `**Wallet**: handle` (no colon inside the bold) is also a real form.
        body = "**Wallet**: jdjioe5-cpu"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "jdjioe5-cpu")
        self.assertEqual(src, "handle")

    def test_markdown_h3_header(self):
        body = "### Recipient: alice"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_real_claim_body_13415(self):
        # Exact text of the first comment on issue #13415.
        body = "## Wallet: jdjioe5-cpu (GitHub handle)\n\nPer the maintainer's `feat(rtc-reward): fall back to GitHub handle as wallet` (PR #13394), \nthe GitHub handle is now a valid wallet identifier."
        w, src = bp.resolve_wallet(body, [], claimant_login="other")
        self.assertEqual(w, "jdjioe5-cpu")
        self.assertEqual(src, "handle")

    def test_bullet_list_label(self):
        # Bounty claims often look like: `- **Wallet:** \`handle\``
        body = "- **Wallet:** `alice` — please send RTC here"
        w, src = bp.resolve_wallet(body, [], claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")


class GraphQLAuthorShapeTests(unittest.TestCase):
    """Regression tests for the v2 `_is_bot_login` and `_comment_author_login`.

    `gh issue view --json comments` returns comments with an `author` field
    (GraphQL shape), NOT a `user` field (REST shape). The previous version
    only read `c.get("user")`, so the bot exclusion was a no-op against
    real production data.
    """

    def test_graphql_author_with_bot_login_is_detected(self):
        body = "no wallet in body"
        comments = [
            {"author": {"login": "github-actions"}, "body": "Wallet: evilbot"},
            {"author": {"login": "realuser"}, "body": "Wallet: realuser"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "realuser")
        self.assertEqual(src, "handle")

    def test_graphql_author_with_known_bot_login(self):
        # Real production: claim #13415 has a github-actions[bot] comment.
        body = "no wallet in body"
        comments = [
            {"author": {"login": "github-actions"}, "body": "Verified eligible"},
            {"author": {"login": "alice"}, "body": "Wallet: alice"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_graphql_author_with_dependabot_suffix(self):
        body = "no wallet in body"
        comments = [
            {"author": {"login": "dependabot[bot]"}, "body": "Wallet: dependabot"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        # comment is bot-authored, skipped -> claimant_login fallback
        self.assertEqual(w, "bob")
        self.assertEqual(src, "handle")

    def test_graphql_author_type_bot_field(self):
        # Some GraphQL responses include `__typename` or `is_bot`.
        body = "no wallet in body"
        comments = [
            {"author": {"login": "ci-bot", "__typename": "Bot"}, "body": "Wallet: evil"},
            {"author": {"login": "carol"}, "body": "Wallet: carol"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "carol")
        self.assertEqual(src, "handle")

    def test_rest_user_shape_still_works(self):
        # Backward compat: REST `user` shape still bot-detected.
        body = "no wallet in body"
        comments = [
            {"user": {"login": "ci-bot", "type": "Bot"}, "body": "Wallet: evil"},
            {"user": {"login": "dave"}, "body": "Wallet: dave"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="bob")
        self.assertEqual(w, "dave")
        self.assertEqual(src, "handle")

    def test_helper_returns_author_login(self):
        c = {"author": {"login": "alice"}}
        login, obj = bp._comment_author_login(c)
        self.assertEqual(login, "alice")
        self.assertEqual(obj, {"login": "alice"})

    def test_helper_returns_rest_login(self):
        c = {"user": {"login": "bob"}}
        login, obj = bp._comment_author_login(c)
        self.assertEqual(login, "bob")
        self.assertEqual(obj, {"login": "bob"})

    def test_helper_handles_non_dict(self):
        self.assertEqual(bp._comment_author_login(None), (None, None))
        self.assertEqual(bp._comment_author_login("string"), (None, None))


class BotDetectionTests(unittest.TestCase):
    def test_bot_via_type(self):
        self.assertTrue(bp._is_bot_login("anything", {"type": "Bot"}))

    def test_bot_via_suffix(self):
        self.assertTrue(bp._is_bot_login("dependabot[bot]", None))

    def test_human_user(self):
        self.assertFalse(bp._is_bot_login("alice", {"type": "User"}))

    def test_known_bot_login(self):
        # github-actions is a real CI bot that has commented on #13415.
        # It does NOT use `[bot]` suffix and does NOT expose `type: "Bot"`
        # in the GraphQL comment shape — only a plain `login`. The
        # KNOWN_BOT_LOGINS fallback must catch it.
        self.assertTrue(bp._is_bot_login("github-actions", None))
        self.assertTrue(bp._is_bot_login("github-actions", {"login": "github-actions"}))

    def test_known_bot_login_case_insensitive(self):
        self.assertTrue(bp._is_bot_login("GitHub-Actions", None))

    def test_typename_bot(self):
        self.assertTrue(bp._is_bot_login("ci-bot", {"__typename": "Bot"}))

    def test_is_bot_true(self):
        self.assertTrue(bp._is_bot_login("ci-bot", {"is_bot": True}))


class IntegrationTests(unittest.TestCase):
    """End-to-end integration of the main-loop fields and resolve_wallet.

    These mirror the data shape produced by
    `gh issue view $NUM -R $REPO --json body,comments,author`
    so the script's call site is exercised as a whole.
    """

    def test_full_claim_13415(self):
        # Real data from issue #13415 (verified via `gh issue view`).
        body = "## Code Review Bounty Claim — PR #7022 (Bounty #73)\n\n- **Bounty:** #73\n- **Wallet:** TBD\n- **Reviewer:** @jdjioe5-cpu\n"
        comments = [
            {"author": {"login": "github-actions"},
             "body": "✅ 🤖 Gate: **verified eligible** — @jdjioe5-cpu is the first substantive reviewer of Scottcjn/Rustchain#7022. **3 RTC** pending payout."},
            {"author": {"login": "jdjioe5-cpu"},
             "body": "## Wallet: jdjioe5-cpu (GitHub handle)\n\nPer the maintainer's `feat(rtc-reward): fall back to GitHub handle as wallet` (PR #13394), the GitHub handle is now a valid wallet identifier."},
        ]
        author = {"login": "jdjioe5-cpu"}
        # The main loop extracts claimant_login from the issue author.
        w, src = bp.resolve_wallet(body, comments, claimant_login=author.get("login"))
        # The body has `Wallet: TBD` (label word, not handle), so the
        # comment thread is consulted. The github-actions comment is
        # bot-detected and skipped. The jdjioe5-cpu comment has the
        # Markdown `## Wallet: jdjioe5-cpu (GitHub handle)` form which
        # the loosened HANDLE_RE matches.
        self.assertEqual(w, "jdjioe5-cpu")
        self.assertEqual(src, "handle")

    def test_claimant_login_fallback_for_unparseable_body(self):
        # Body has no Wallet: line. Comments are all bot-authored.
        body = "Just a claim, no wallet marker here."
        comments = [
            {"author": {"login": "github-actions"},
             "body": "Gate label applied"},
        ]
        # The main loop passes the issue author's login. v2 must reach it.
        w, src = bp.resolve_wallet(body, comments, claimant_login="alice")
        self.assertEqual(w, "alice")
        self.assertEqual(src, "handle")

    def test_claimant_login_is_none_when_no_author(self):
        # v1 behavior preserved: when no comments and no author, no wallet.
        w, src = bp.resolve_wallet("Wallet: TBD", [], claimant_login=None)
        self.assertIsNone(w)
        self.assertIsNone(src)

    def test_bot_claimant_rejected_even_with_comment_handle(self):
        # A bot author (rare, but possible if the issue was opened by a
        # bot for some reason) must NOT receive payment via the
        # claimant_login fallback.
        body = "no wallet marker"
        comments = [
            {"author": {"login": "dependabot"}, "body": "Wallet: realuser"},
        ]
        w, src = bp.resolve_wallet(body, comments, claimant_login="dependabot[bot]")
        # dependabot comment is bot-authored, skipped. dependabot
        # claimant is bot, rejected. -> (None, None).
        self.assertIsNone(w)
        self.assertIsNone(src)


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
