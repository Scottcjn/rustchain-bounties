#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/maintenance_sweep.py.

The correctness risk that matters: this org has TWO maintainer identities
(Scottcjn and sophiaeagent-beep). If only one is recognised, a reply from the
other is read as an external contributor speaking, and the thread is reported
as "waiting on us" forever. Conversely a bot's own comment must not clear a
thread that a human is still waiting on.
"""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "maintenance_sweep.py"
spec = importlib.util.spec_from_file_location("sweep_under_test", SCRIPT)
ms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ms)


class MaintainerIdentityTests(unittest.TestCase):
    def test_both_maintainer_identities_recognised(self):
        self.assertTrue(ms.is_maintainer("Scottcjn"))
        self.assertTrue(ms.is_maintainer("sophiaeagent-beep"))

    def test_case_insensitive(self):
        self.assertTrue(ms.is_maintainer("SCOTTCJN"))
        self.assertTrue(ms.is_maintainer("SophiaEagent-Beep"))

    def test_bots_count_as_us(self):
        for b in ["github-actions[bot]", "dependabot[bot]", "renovate", "copilot"]:
            self.assertTrue(ms.is_maintainer(b), b)

    def test_any_bot_suffix(self):
        self.assertTrue(ms.is_maintainer("some-random-thing[bot]"))

    def test_contributors_are_not_maintainers(self):
        for c in ["leanworld7-netizen", "jaxint", "2balmprune",
                  "Vyacheslav-Tomashevskiy", "waterWang"]:
            self.assertFalse(ms.is_maintainer(c), c)

    def test_empty_is_not_maintainer(self):
        self.assertFalse(ms.is_maintainer(""))
        self.assertFalse(ms.is_maintainer(None))

    def test_lookalike_is_not_maintainer(self):
        """A name merely containing a maintainer's is still external."""
        self.assertFalse(ms.is_maintainer("scottcjn-fan"))
        self.assertFalse(ms.is_maintainer("not-scottcjn"))




class MultiStreamTests(unittest.TestCase):
    """A PR has three comment streams; reading one loses maintainer questions.

    Regression for the LLVM case: an inline review comment went unanswered for
    four months because only the issue-comment stream was read.
    """

    def setUp(self):
        self._orig = ms.gh_json

    def tearDown(self):
        ms.gh_json = self._orig

    def _pr(self, author="alice", n=7):
        return {"user": {"login": author}, "comments": n, "comments_url": "/issues/7/comments",
                "created_at": "2026-04-01T00:00:00Z", "number": 7,
                "pull_request": {}, "repository_url": "https://api.github.com/repos/llvm/llvm-project"}

    def _streams(self, issue=(), review=(), reviews=()):
        def fake(args, default):
            u = args[1] if len(args) > 1 else ""
            if u.startswith("/issues"):
                return [{"created_at": t, "user": {"login": w}} for t, w in issue]
            if u.endswith("/comments?per_page=100"):
                return [{"created_at": t, "user": {"login": w}} for t, w in review]
            if "/reviews" in u:
                return [{"submitted_at": t, "user": {"login": w}} for t, w in reviews]
            return default
        ms.gh_json = fake

    def test_inline_review_comment_is_seen(self):
        """Maintainer spoke ONLY inline. Thread must not read as unanswered."""
        self._streams(issue=[("2026-04-01T00:00:00Z", "alice")],
                      review=[("2026-04-16T00:00:00Z", "Scottcjn")])
        b, who, _ = ms.classify(self._pr(), {})
        self.assertEqual(b, "MOVED_RECENTLY")
        self.assertEqual(who, "Scottcjn")

    def test_contributor_inline_reply_reopens_ball(self):
        self._streams(issue=[("2026-04-01T00:00:00Z", "Scottcjn")],
                      review=[("2026-04-20T00:00:00Z", "alice")])
        b, who, _ = ms.classify(self._pr(), {})
        self.assertEqual(b, "BALL_IN_OUR_COURT")
        self.assertEqual(who, "alice")

    def test_review_state_counts_as_activity(self):
        """An APPROVED review with no body is still a maintainer touching it."""
        self._streams(issue=[("2026-04-01T00:00:00Z", "alice")],
                      reviews=[("2026-04-05T00:00:00Z", "sophiaeagent-beep")])
        b, who, _ = ms.classify(self._pr(), {})
        self.assertEqual(b, "MOVED_RECENTLY")
        self.assertEqual(who, "sophiaeagent-beep")

    def test_latest_across_all_three_streams_wins(self):
        self._streams(issue=[("2026-04-01T00:00:00Z", "Scottcjn")],
                      review=[("2026-04-10T00:00:00Z", "Scottcjn")],
                      reviews=[("2026-04-25T00:00:00Z", "alice")])
        b, who, when = ms.classify(self._pr(), {})
        self.assertEqual(b, "BALL_IN_OUR_COURT")
        self.assertEqual(who, "alice")
        self.assertEqual(when, "2026-04-25")

    def test_no_activity_anywhere_is_never_answered(self):
        self._streams()
        b, _, _ = ms.classify(self._pr(n=0), {})
        self.assertEqual(b, "NEVER_ANSWERED")

    def test_our_own_silent_pr_is_not_owed_a_reply(self):
        self._streams()
        b, _, _ = ms.classify(self._pr(author="Scottcjn", n=0), {})
        self.assertIsNone(b)


if __name__ == "__main__":
    unittest.main()
