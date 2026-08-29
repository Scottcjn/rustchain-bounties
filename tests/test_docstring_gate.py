#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/docstring_gate.py.

The check that carries the weight is `count_added_docstrings`: without it, a
claim saying "I added 40 docstrings" would pay out for 40 added lines of
anything at all. These pin that it counts docstrings and nothing else.
"""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

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
                return [{"body": f"<!-- rtc-payout-amount: {amounts[idx]} -->"}]
            return default
        dg.gh = fake

    def test_sums_prior_week(self):
        self._with_prior([5.0, 7.5, 6.0])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 18.5)

    def test_no_prior_claims_is_zero(self):
        self._with_prior([])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 0.0)

    def test_ceiling_is_higher_than_typical_top_earner(self):
        """Measured 2026-08-10: top contributors earn 20-50 RTC/week across ALL
        bounty types. A docstring-only ceiling below that would be punitive."""
        self.assertGreaterEqual(dg.MAX_RTC_PER_WEEK, 40)

    def test_per_claim_ceiling_alone_would_not_bound_volume(self):
        """Documents why the weekly cap exists: a typical batch is far under
        the per-claim ceiling, so volume is unbounded without it."""
        typical_batch_rtc = 10 * dg.RATE     # 10 functions
        self.assertLess(typical_batch_rtc, dg.MAX_RTC)


class GhRawFailureTests(unittest.TestCase):
    def tearDown(self):
        subprocess.run = self._run

    def setUp(self):
        self._run = subprocess.run

    def test_gh_raw_raises_on_nonzero_exit(self):
        class R:
            stdout = ""
            stderr = "rate limit"
            returncode = 1

        subprocess.run = lambda *a, **k: R()
        with self.assertRaises(dg.GhError):
            dg.gh_raw(["pr", "diff", "1", "-R", "o/r"])


class LabelWriteFailClosedTests(unittest.TestCase):
    """Regression for #16662: ignored label REST failures must not exit green."""

    def setUp(self):
        self._run = subprocess.run
        dg.NUM = "16662"
        dg.REPO = "Scottcjn/rustchain-bounties"

    def tearDown(self):
        subprocess.run = self._run

    def test_strict_add_labels_raises_on_rest_failure(self):
        class R:
            stdout = ""
            stderr = "rate limit"
            returncode = 1

        subprocess.run = lambda *a, **k: R()
        with self.assertRaises(dg.GhError):
            dg.add_labels("bounty-eligible", "docstring-verified", strict=True)

    def test_strict_add_labels_uses_single_post(self):
        seen = []

        class R:
            stdout = "[]"
            stderr = ""
            returncode = 0

        def capture(args, **kwargs):
            seen.append(args)
            return R()

        subprocess.run = capture
        dg.add_labels("bounty-eligible", "docstring-verified", strict=True)
        self.assertEqual(len(seen), 1)
        joined = " ".join(seen[0])
        self.assertIn("labels[]=bounty-eligible", joined)
        self.assertIn("labels[]=docstring-verified", joined)


class DiffReadFailureTests(unittest.TestCase):
    def setUp(self):
        self._num = dg.NUM
        self._gh = dg.gh
        self._gh_raw = dg.gh_raw
        dg.NUM = "123"
        self.comments = []

        def fake_gh(args, default=None, strict=False):
            joined = " ".join(args)
            if args[:2] == ["issue", "view"]:
                return {
                    "title": "Claim: docs batch 1",
                    "body": "PR: https://github.com/example/project/pull/7\nFunctions documented: 1",
                    "labels": [],
                    "author": {"login": "alice"},
                    "state": "OPEN",
                }
            if args[:2] == ["pr", "view"]:
                return {
                    "state": "MERGED",
                    "additions": 4,
                    "deletions": 0,
                    "files": [],
                    "author": {"login": "alice"},
                    "mergedAt": "2026-01-01",
                }
            if len(args) >= 2 and args[0] == "issue" and args[1] == "comment":
                self.comments.append(args)
            if "search/issues" in joined:
                return {"items": []}
            return default

        dg.gh = fake_gh

    def tearDown(self):
        dg.NUM = self._num
        dg.gh = self._gh
        dg.gh_raw = self._gh_raw

    def test_diff_read_failure_exits_nonzero_without_needs_human(self):
        dg.gh_raw = lambda args: (_ for _ in ()).throw(dg.GhError("diff read failed"))
        rc = dg.main()
        self.assertEqual(rc, 1)
        self.assertEqual(self.comments, [])


class PayablePathFailClosedTests(unittest.TestCase):
    def setUp(self):
        self._num = dg.NUM
        dg.NUM = "999"

    def tearDown(self):
        dg.NUM = self._num

    def test_payable_path_fails_closed_when_labels_do_not_stick(self):
        comments = []

        def fake_gh(args, default=None, strict=False):
            joined = " ".join(args)
            if "issue view" in joined or joined.startswith("gh issue view"):
                return {
                    "title": "Bounty claim: BoTTube docstring PR #9999",
                    "body": "https://github.com/Scottcjn/bottube/pull/1696\nFunctions documented: 2",
                    "labels": [],
                    "author": {"login": "claimant"},
                    "state": "OPEN",
                }
            if "pr view" in joined:
                return {
                    "state": "MERGED",
                    "additions": 4,
                    "deletions": 0,
                    "files": [],
                    "author": {"login": "claimant"},
                    "mergedAt": "2026-01-01",
                }
            if len(args) >= 2 and args[0] == "issue" and args[1] == "comment":
                comments.append(args)
            if "search/issues" in joined:
                return {"items": []}
            return default

        dg.gh = fake_gh
        dg.gh_raw = lambda args: (
            'diff --git a/x.py b/x.py\n'
            '+++ b/x.py\n'
            '+    """One."""\n'
            '+    """Two."""\n'
        )

        with mock.patch.object(dg, "add_labels", side_effect=dg.GhError("label write failed")):
            rc = dg.main()
        self.assertEqual(rc, 1)
        self.assertTrue(any("could not apply the payout labels" in (c[3] if len(c) > 3 else "")
                            for c in comments) or comments)
