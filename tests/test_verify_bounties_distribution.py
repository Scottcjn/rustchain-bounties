# SPDX-License-Identifier: MIT
"""Phase 6 of verify_bounties.py: off-platform Live-URL verification.

Pinned here: every verifier fails CLOSED. A network error, a non-200, or a
body without the expected field is UNVERIFIED — never VERIFIED. The report is
one idempotent bot comment per issue, and `live-url-verified` is applied only
when at least one link actually resolved.
"""
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path


def load_verify_bounties():
    os.environ.setdefault("GITHUB_TOKEN", "dummy-token-for-tests")
    requests_stub = types.SimpleNamespace(
        Session=lambda: types.SimpleNamespace(headers={}, get=None, post=None, patch=None),
        get=None,
    )
    sys.modules.setdefault("requests", requests_stub)
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "verify_bounties.py"
    spec = importlib.util.spec_from_file_location("verify_bounties_dist", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, status_code, payload=None, text="", bad_json=False):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = {"X-RateLimit-Remaining": "5000"}
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._payload


def install_http(mod, handler):
    """Route mod._http_get(url, params) through `handler(url, params)`."""
    calls = []

    def fake(url, params=None):
        calls.append((url, params or {}))
        out = handler(url, params or {})
        if isinstance(out, Exception):
            raise out
        return out

    mod._http_get = fake
    return calls


class BoTTubeVerifier(unittest.TestCase):
    def setUp(self):
        self.mod = load_verify_bounties()

    def test_verified_with_agent_name_and_metrics(self):
        calls = install_http(self.mod, lambda u, p: FakeResponse(
            200, {"agent_name": "keon446b032231", "views": 386, "created_at": "2026-05-04T10:00:00Z"}))
        res = self.mod.verify_bottube_url("https://bottube.ai/watch/zG3-osiYhfv")
        self.assertEqual(res["status"], "VERIFIED")
        self.assertIn("keon446b032231", res["metric"])
        self.assertIn("386", res["metric"])
        self.assertIn("2026-05-04", res["metric"])
        self.assertEqual(calls[0][0], "https://bottube.ai/api/videos/zG3-osiYhfv")

    def test_200_without_agent_name_is_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(200, {"id": "x"}))
        self.assertEqual(self.mod.verify_bottube_url("https://bottube.ai/watch/x")["status"], "UNVERIFIED")

    def test_404_and_network_error_are_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(404, {}))
        self.assertEqual(self.mod.verify_bottube_url("https://bottube.ai/watch/x")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: ConnectionError("boom"))
        res = self.mod.verify_bottube_url("https://bottube.ai/watch/x")
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertIn("ConnectionError", res["metric"])

    def test_malformed_json_is_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(200, bad_json=True))
        self.assertEqual(self.mod.verify_bottube_url("https://bottube.ai/watch/x")["status"], "UNVERIFIED")


class XVerifier(unittest.TestCase):
    def setUp(self):
        self.mod = load_verify_bounties()

    def test_verified_when_screen_name_matches_url(self):
        calls = install_http(self.mod, lambda u, p: FakeResponse(
            200, {"user": {"screen_name": "RustChain"}, "favorite_count": 7}))
        res = self.mod.verify_x_url("https://x.com/rustchain/status/1234567890")
        self.assertEqual(res["status"], "VERIFIED")
        self.assertIn("@RustChain", res["metric"])
        self.assertEqual(calls[0][0], "https://cdn.syndication.twimg.com/tweet-result")
        self.assertEqual(calls[0][1], {"id": "1234567890", "token": "x"})

    def test_screen_name_mismatch_is_unverified(self):
        """A real post by someone else, pasted under your own handle, does not count."""
        install_http(self.mod, lambda u, p: FakeResponse(200, {"user": {"screen_name": "other"}}))
        res = self.mod.verify_x_url("https://x.com/alice/status/1")
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertIn("@other", res["metric"])

    def test_missing_user_non200_and_error_are_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(200, {}))
        self.assertEqual(self.mod.verify_x_url("https://x.com/a/status/1")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: FakeResponse(200, {"user": {}}))
        self.assertEqual(self.mod.verify_x_url("https://x.com/a/status/1")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: FakeResponse(404, {}))
        self.assertEqual(self.mod.verify_x_url("https://x.com/a/status/1")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: TimeoutError())
        self.assertEqual(self.mod.verify_x_url("https://x.com/a/status/1")["status"], "UNVERIFIED")


class YouTubeVerifier(unittest.TestCase):
    def setUp(self):
        self.mod = load_verify_bounties()

    def test_oembed_200_verified(self):
        calls = install_http(self.mod, lambda u, p: FakeResponse(
            200, {"title": "RustChain on a G4", "author_name": "Alice"}))
        res = self.mod.verify_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(res["status"], "VERIFIED")
        self.assertIn("Alice", res["metric"])
        self.assertEqual(calls[0][0], "https://www.youtube.com/oembed")
        self.assertEqual(calls[0][1]["url"], "https://youtu.be/dQw4w9WgXcQ")

    def test_oembed_non200_or_error_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(401, {}))
        self.assertEqual(self.mod.verify_youtube_url("https://youtu.be/x")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: OSError())
        self.assertEqual(self.mod.verify_youtube_url("https://youtu.be/x")["status"], "UNVERIFIED")


class ArticleVerifier(unittest.TestCase):
    def setUp(self):
        self.mod = load_verify_bounties()

    def test_200_verified_else_unverified(self):
        install_http(self.mod, lambda u, p: FakeResponse(200))
        self.assertEqual(self.mod.verify_article_url("https://dev.to/a/b")["status"], "VERIFIED")
        install_http(self.mod, lambda u, p: FakeResponse(404))
        self.assertEqual(self.mod.verify_article_url("https://dev.to/a/b")["status"], "UNVERIFIED")
        install_http(self.mod, lambda u, p: ConnectionError())
        self.assertEqual(self.mod.verify_article_url("https://dev.to/a/b")["status"], "UNVERIFIED")

    def test_off_allowlist_url_is_never_fetched(self):
        calls = install_http(self.mod, lambda u, p: FakeResponse(200))
        res = self.mod.verify_live_url("https://gist.github.com/a/b")
        self.assertEqual(res["status"], "UNVERIFIED")
        self.assertEqual(calls, [])


class DistributionPhase(unittest.TestCase):
    def setUp(self):
        self.mod = load_verify_bounties()
        self.posted, self.updated, self.labels = [], [], []
        self.mod.post_comment = lambda n, b: self.posted.append((n, b)) or True
        self.mod.update_comment = lambda cid, b: self.updated.append((cid, b)) or True
        self.mod.add_issue_label = lambda n, lbl: self.labels.append((n, lbl)) or True

    def _comments(self, *items):
        self.mod.get_issue_comments = lambda n: list(items)

    def test_one_comment_and_label_when_one_verified(self):
        self._comments(
            {"id": 1, "user": {"login": "alice"}, "body": "/claim\nLive-URL: https://dev.to/alice/p"},
            {"id": 2, "user": {"login": "bob"}, "body": "Live-URL: https://gist.github.com/bob/x"},
            {"id": 3, "user": {"login": "carol"}, "body": "posting now, will update"},
        )
        install_http(self.mod, lambda u, p: FakeResponse(200))
        self.mod.verify_distribution_claims(2798)
        self.assertEqual(len(self.posted), 1)
        self.assertEqual(self.updated, [])
        body = self.posted[0][1]
        self.assertIn(self.mod.BOT_SIGNATURE, body)
        self.assertIn("| @alice | https://dev.to/alice/p | devto | VERIFIED |", body)
        self.assertIn("| @bob | https://gist.github.com/bob/x | - | UNVERIFIED |", body)
        self.assertNotIn("@carol", body)
        self.assertEqual(self.labels, [(2798, "live-url-verified")])

    def test_no_label_when_nothing_verified(self):
        self._comments({"id": 1, "user": {"login": "alice"}, "body": "Live-URL: https://dev.to/a/p"})
        install_http(self.mod, lambda u, p: FakeResponse(404))
        self.mod.verify_distribution_claims(315)
        self.assertEqual(len(self.posted), 1)
        self.assertEqual(self.labels, [])

    def test_existing_bot_comment_is_updated_not_duplicated(self):
        self._comments(
            {"id": 9, "user": {"login": "github-actions[bot]"}, "body": f"{self.mod.BOT_SIGNATURE}\nold"},
            {"id": 1, "user": {"login": "alice"}, "body": "Live-URL: https://dev.to/a/p"},
        )
        install_http(self.mod, lambda u, p: FakeResponse(200))
        self.mod.verify_distribution_claims(399)
        self.assertEqual(self.posted, [])
        self.assertEqual(len(self.updated), 1)
        self.assertEqual(self.updated[0][0], 9)

    def test_no_live_url_claims_posts_nothing(self):
        self._comments({"id": 1, "user": {"login": "alice"}, "body": "/claim"})
        self.mod.verify_distribution_claims(282)
        self.assertEqual(self.posted, [])
        self.assertEqual(self.labels, [])

    def test_incomplete_comment_read_posts_no_verdict(self):
        def boom(n):
            raise self.mod.IncompleteSweep("HTTP 403")
        self.mod.get_issue_comments = boom
        with self.assertRaises(self.mod.IncompleteSweep):
            self.mod.verify_distribution_claims(16497)
        self.assertEqual(self.posted, [])

    def test_bot_and_owner_comments_are_not_claims(self):
        self._comments(
            {"id": 1, "user": {"login": self.mod.OWNER}, "body": "Live-URL: https://dev.to/a/p"},
            {"id": 2, "user": {"login": "x"}, "body": f"{self.mod.BOT_SIGNATURE}\nLive-URL: https://dev.to/a/p"},
        )
        self.assertEqual(self.mod.extract_live_url_claims(self.mod.get_issue_comments(1)), [])

    def test_issue_list_matches_audit(self):
        self.assertEqual(self.mod.DISTRIBUTION_BOUNTY_ISSUES, [315, 16601, 16497, 282, 399, 2798, 14481])


if __name__ == "__main__":
    unittest.main()
