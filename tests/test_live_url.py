# SPDX-License-Identifier: MIT
"""Tests for scripts/live_url.py — the Live-URL parser and host allowlist.

What carries the weight: an off-list host (gist, GitHub Pages, a profile page
instead of a post) must NOT classify, or the field becomes the same "posting
now, will update" it exists to replace.
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "live_url.py"
spec = importlib.util.spec_from_file_location("live_url_under_test", SCRIPT)
lu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lu)


class ClassifyTests(unittest.TestCase):
    def test_allowlisted_hosts(self):
        cases = {
            "https://bottube.ai/watch/zG3-osiYhfv": "bottube",
            "https://www.bottube.ai/watch/Yd-8QzvWEDj/": "bottube",
            "https://x.com/rustchain/status/1234567890123456789": "x",
            "https://twitter.com/some_user/status/99": "x",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ": "youtube",
            "https://youtube.com/shorts/abcDEF12345": "youtube",
            "https://youtu.be/dQw4w9WgXcQ": "youtube",
            "https://hackaday.io/project/123456-rustchain-on-a-g4": "hackaday",
            "https://dev.to/alice/rustchain-on-powerpc-1abc": "devto",
            "https://alice.hashnode.dev/rustchain-mining": "hashnode",
            "https://medium.com/@alice/rustchain-abc123": "medium",
            "https://alice.medium.com/rustchain-abc123": "medium",
        }
        for url, want in cases.items():
            self.assertEqual(lu.classify_live_url(url), want, url)

    def test_off_list_hosts_rejected(self):
        for url in [
            "https://gist.github.com/alice/abc",
            "https://alice.github.io/post",
            "https://github.com/Scottcjn/rustchain-bounties/issues/2798",
            "https://example.com/bottube.ai/watch/abc",
            "https://bottube.ai.evil.com/watch/abc",
            "https://notdev.to/alice/post",
            "https://hashnode.dev/",  # bare apex, not a user blog
            "ftp://dev.to/alice/post",
            "https://x.com/rustchain",  # profile, not a post
            "https://www.youtube.com/@channel",  # channel, not a video
            "https://www.youtube.com/watch",  # no v=
            "https://bottube.ai/agent/keon446b032231",  # agent page, not a video
            "", None,
        ]:
            self.assertIsNone(lu.classify_live_url(url), url)

    def test_userinfo_and_port_do_not_spoof_host(self):
        self.assertIsNone(lu.classify_live_url("https://bottube.ai@evil.com/watch/abc"))
        self.assertEqual(lu.classify_live_url("https://bottube.ai:443/watch/abc"), "bottube")


class ExtractTests(unittest.TestCase):
    def test_finds_line_variants(self):
        for body in [
            "Live-URL: https://dev.to/a/b",
            "live-url: https://dev.to/a/b",
            "**Live-URL:** https://dev.to/a/b",
            "`Live-URL`: <https://dev.to/a/b>",
            "Done!\n\nLive-URL: https://dev.to/a/b\n\nthanks",
            "   Live-URL:   https://dev.to/a/b.",
        ]:
            self.assertEqual(lu.extract_live_urls(body), ["https://dev.to/a/b"], body)

    def test_ignores_urls_not_on_a_live_url_line(self):
        self.assertEqual(lu.extract_live_urls("Posted: https://dev.to/a/b"), [])
        self.assertEqual(lu.extract_live_urls("Here is my Live-URL: soon"), [])
        self.assertEqual(lu.extract_live_urls(""), [])
        self.assertEqual(lu.extract_live_urls(None), [])

    def test_multiple_lines(self):
        body = "Live-URL: https://dev.to/a/b\nLive-URL: https://x.com/u/status/1"
        self.assertEqual(len(lu.extract_live_urls(body)), 2)


class FindTests(unittest.TestCase):
    def test_missing(self):
        self.assertEqual(lu.find_live_url("/claim"), (None, None, "missing"))

    def test_rejected(self):
        url, platform, reason = lu.find_live_url("/claim\nLive-URL: https://gist.github.com/x")
        self.assertEqual((url, platform, reason), ("https://gist.github.com/x", None, "rejected"))

    def test_ok(self):
        url, platform, reason = lu.find_live_url("/claim\nLive-URL: https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual((platform, reason), ("youtube", "ok"))

    def test_first_allowlisted_wins_over_a_bad_one(self):
        body = "Live-URL: https://gist.github.com/x\nLive-URL: https://dev.to/a/b"
        self.assertEqual(lu.find_live_url(body)[1:], ("devto", "ok"))


if __name__ == "__main__":
    unittest.main()
