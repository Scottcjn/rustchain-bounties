#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/docstring_gate.py.

The check that carries the weight is `count_added_docstrings`: without it, a
claim saying "I added 40 docstrings" would pay out for 40 added lines of
anything at all. These pin that it counts docstrings and nothing else.
"""
import importlib.util
import os
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "docstring_gate.py"
spec = importlib.util.spec_from_file_location("docstring_gate_under_test", SCRIPT)
dg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dg)


def diff(*added_lines, path="a/x.py"):
    head = f"diff --git {path} b/{path.split('a/')[-1]}\n--- {path}\n+++ b/{path.split('a/')[-1]}\n@@ -1 +1 @@\n"
    return head + "\n".join(added_lines)


class CountingTests(unittest.TestCase):
    def test_counts_one_line_docstrings(self):
        d = diff('+    """Return the name."""', '+    """Do a thing."""')
        self.assertEqual(dg.count_added_docstrings(d)[0], 2)

    def test_multiline_docstring_counts_once(self):
        d = diff('+    """Summary line.', '+', '+    More detail here.', '+    """')
        doc, total, _ = dg.count_added_docstrings(d)
        self.assertEqual(doc, 1, "a multi-line docstring is one unit, not four")
        self.assertEqual(total, 4)

    def test_plain_code_is_not_a_docstring(self):
        d = diff('+x = 1', '+def f():', '+    return 2')
        self.assertEqual(dg.count_added_docstrings(d)[0], 0)

    def test_comments_are_not_docstrings(self):
        d = diff('+# this is a comment', '+    # another one')
        self.assertEqual(dg.count_added_docstrings(d)[0], 0)

    def test_string_assignment_is_not_a_docstring(self):
        """The abuse case: padding a diff with triple-quoted values."""
        d = diff('+SQL = """SELECT 1"""', '+    """A real docstring."""')
        # SQL = """...""" does not OPEN at line start, so only the real one counts.
        self.assertEqual(dg.count_added_docstrings(d)[0], 1)

    def test_single_quote_docstrings(self):
        d = diff("+    '''Alt quoting style.'''")
        self.assertEqual(dg.count_added_docstrings(d)[0], 1)

    def test_removed_lines_do_not_count(self):
        d = diff('+    """Kept."""', '-    """Deleted."""')
        self.assertEqual(dg.count_added_docstrings(d)[0], 1)

    def test_files_are_collected(self):
        d = diff('+    """Doc."""', path="a/generation/provider.py")
        self.assertIn("generation/provider.py", dg.count_added_docstrings(d)[2])

    def test_raw_and_unicode_prefixes(self):
        d = diff('+    r"""Raw docstring."""', '+    u"""Unicode docstring."""')
        self.assertEqual(dg.count_added_docstrings(d)[0], 2)


class ClaimParsingTests(unittest.TestCase):
    def test_recognises_docstring_claims(self):
        self.assertTrue(dg.is_docstring_claim("Claim: docs batch 49 - provider.py docstrings", ""))
        self.assertTrue(dg.is_docstring_claim("Bounty claim: BoTTube docstring PR #1683", ""))

    def test_ignores_review_claims(self):
        self.assertFalse(dg.is_docstring_claim("[Bounty Claim] PR Review - RustChain PR #5395", ""))

    def test_pr_url_extraction(self):
        m = dg.PR_RE.search("PR: https://github.com/Scottcjn/bottube/pull/1696")
        self.assertEqual((m.group(1), m.group(2)), ("Scottcjn/bottube", "1696"))

    def test_count_extraction(self):
        for text, want in [
            ("Functions documented: 7 (get_name, ...)", "7"),
            ("Added docstrings to 5 undocumented methods", "5"),
        ]:
            m = dg.COUNT_RE.search(text)
            self.assertIsNotNone(m, text)
            self.assertEqual(m.group(1), want)


if __name__ == "__main__":
    unittest.main()


class WeeklyCeilingTests(unittest.TestCase):
    """The per-claim ceiling bounds nothing: batches are ~5 RTC each, so the
    50th one passes just as easily as the 1st. The weekly ceiling is the one
    that actually bounds an unbounded bounty type."""

    def setUp(self):
        self._gh = dg.gh

    def tearDown(self):
        dg.gh = self._gh

    def _with_prior(self, amounts):
        """Fake N prior verified claims carrying these payout markers."""
        items = [{"number": 900 + i, "body": ""} for i in range(len(amounts))]

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": items}
            if "/comments" in joined:
                idx = int(joined.split("/issues/")[1].split("/")[0]) - 900
                return [{
                    "user": {"login": "github-actions[bot]"},
                    "body": f"<!-- rtc-payout-amount: {amounts[idx]} -->",
                }]
            return default
        dg.gh = fake

    def test_sums_prior_week(self):
        self._with_prior([5.0, 7.5, 6.0])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 18.5)

    def test_no_prior_claims_is_zero(self):
        self._with_prior([])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 0.0)

    def test_untrusted_preplanted_marker_does_not_poison_cap(self):
        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 900, "body": ""}]}
            if "/issues/900/comments" in joined:
                return [
                    {"user": {"login": "mallory"},
                     "body": "<!-- rtc-payout-amount: 40 -->"},
                    {"user": {"login": "github-actions[bot]"},
                     "body": "<!-- rtc-payout-amount: 0.5 -->"},
                ]
            return default
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 0.5)

    def test_verified_claim_without_trusted_marker_fails_closed(self):
        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 900, "body": ""}]}
            if "/issues/900/comments" in joined:
                return [{"user": {"login": "mallory"},
                         "body": "<!-- rtc-payout-amount: 40 -->"}]
            return default
        dg.gh = fake
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("someone")

    def test_ceiling_is_higher_than_typical_top_earner(self):
        """Measured 2026-08-10: top contributors earn 20-50 RTC/week across ALL
        bounty types. A docstring-only ceiling below that would be punitive."""
        self.assertGreaterEqual(dg.MAX_RTC_PER_WEEK, 40)

    def test_per_claim_ceiling_alone_would_not_bound_volume(self):
        """Documents why the weekly cap exists: a typical batch is far under
        the per-claim ceiling, so volume is unbounded without it."""
        typical_batch_rtc = 10 * dg.RATE     # 10 functions
        self.assertLess(typical_batch_rtc, dg.MAX_RTC)


class VerifiedTransitionTests(unittest.TestCase):
    def setUp(self):
        self.saved = {
            name: getattr(dg, name)
            for name in ("NUM", "gh", "gh_raw", "docstring_rtc_this_week",
                         "post_comment_checked", "add_labels")
        }
        dg.NUM = "99999"

        def fake_gh(args, default=None, strict=False):
            if args[:2] == ["issue", "view"]:
                return {
                    "title": "Docstring bounty claim",
                    "body": "https://github.com/Scottcjn/Rustchain/pull/123",
                    "labels": [], "author": {"login": "alice"}, "state": "OPEN",
                }
            if args[:2] == ["pr", "view"]:
                return {
                    "state": "MERGED", "additions": 1, "deletions": 0,
                    "files": [], "author": {"login": "alice"},
                    "mergedAt": "2026-08-14T00:00:00Z",
                }
            return default

        dg.gh = fake_gh
        dg.gh_raw = lambda args: '+++ b/x.py\n+    """Documented."""\n'
        dg.docstring_rtc_this_week = lambda author: 0.0

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(dg, name, value)

    def test_comment_failure_writes_no_terminal_labels(self):
        labels = []
        dg.post_comment_checked = lambda body: (_ for _ in ()).throw(
            dg.GhError("simulated comment failure")
        )
        dg.add_labels = lambda *names: labels.extend(names) or True

        self.assertEqual(dg.main(), 1)
        self.assertEqual(labels, [])

    def test_label_failure_is_not_reported_as_success(self):
        comments = []
        dg.post_comment_checked = lambda body: comments.append(body)
        dg.add_labels = lambda *names: False

        self.assertEqual(dg.main(), 1)
        self.assertEqual(len(comments), 1)
        self.assertIn("rtc-payout-amount: 0.5", comments[0])
