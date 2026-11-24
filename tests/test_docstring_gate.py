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

    def test_fstring_prefixed_strings_are_not_docstrings(self):
        """f- and rf-prefixed strings are valid Python but not docstrings."""
        d = diff('+    f"""F-string expression."""', '+    rf"""Raw f-string expression."""')
        self.assertEqual(dg.count_added_docstrings(d)[0], 0)


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
                return [{"user": {"login": "github-actions[bot]"},
                         "body": f"<!-- rtc-payout-amount: {amounts[idx]} -->"}]
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


class UntrustedMarkerTests(unittest.TestCase):
    """Bounty #16471, reported by @fsalmon1991 (2026-09-22).

    `docstring_rtc_this_week()` summed the FIRST `rtc-payout-amount` marker on
    each prior claim with no author check. Issue comments are public input, so
    anyone could front-run the gate's marker: a large value made an honest
    contributor look over the weekly cap (held work), and a `0` undercounted
    prior earnings so the cap failed OPEN. Only markers from the identities the
    gate/payout actually post as may count; everything else is ignored.
    """

    BOT = "github-actions[bot]"

    def setUp(self):
        self._gh = dg.gh

    def tearDown(self):
        dg.gh = self._gh

    def _one_claim(self, comments):
        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 901, "body": ""}]}
            if "/comments" in joined:
                return comments
            return default
        dg.gh = fake

    @staticmethod
    def _c(login, amount):
        return {"user": {"login": login}, "body": f"<!-- rtc-payout-amount: {amount} -->"}

    def test_spoofed_marker_alone_fails_closed(self):
        comments = [self._c("random-user", 40)]
        self.assertIsNone(dg.trusted_payout_amount(comments))
        self._one_claim(comments)
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("victim")

    def test_genuine_bot_marker_counts(self):
        self._one_claim([self._c(self.BOT, 5)])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 5.0)

    def test_inflating_marker_before_gate_marker_is_ignored(self):
        """Front-run with 40: must not push an honest contributor over the cap."""
        self._one_claim([self._c("attacker", 40), self._c(self.BOT, 5)])
        self.assertEqual(dg.docstring_rtc_this_week("victim"), 5.0)

    def test_zero_marker_before_gate_marker_is_ignored(self):
        """Front-run with 0: must not undercount prior earnings (cap fail-open)."""
        self._one_claim([self._c("collaborator", 0), self._c(self.BOT, 5)])
        self.assertEqual(dg.docstring_rtc_this_week("farmer"), 5.0)

    def test_marker_after_gate_marker_is_ignored(self):
        self._one_claim([self._c(self.BOT, 5), self._c("attacker", 0)])
        self.assertEqual(dg.docstring_rtc_this_week("farmer"), 5.0)

    def test_lookalike_and_missing_author_are_untrusted(self):
        comments = [self._c("github-actions-bot", 9), self._c("scottcjn-fan", 9),
                    {"body": "<!-- rtc-payout-amount: 9 -->"},
                    {"user": None, "body": "<!-- rtc-payout-amount: 9 -->"}]
        self.assertIsNone(dg.trusted_payout_amount(comments))
        self._one_claim(comments)
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("someone")

    def test_maintainer_marker_counts_and_graphql_shape_is_read(self):
        self._one_claim([{"author": {"login": "Scottcjn"},
                          "body": "<!-- rtc-payout-amount: 3 -->"}])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 3.0)

    def test_unparseable_trusted_marker_is_skipped_not_a_crash(self):
        """`[\\d.]+` matches `...` and `1.2.3`; those used to reach float() and
        raise ValueError, which main() does not catch, killing the gate run."""
        for bad in ("...", "1.2.3", "."):
            self._one_claim([self._c(self.BOT, 5), self._c(self.BOT, bad)])
            self.assertEqual(dg.docstring_rtc_this_week("someone"), 5.0, bad)
            bad_only = [self._c(self.BOT, bad)]
            self.assertIsNone(dg.trusted_payout_amount(bad_only), bad)
            self._one_claim(bad_only)
            with self.assertRaises(dg.GhError):
                dg.docstring_rtc_this_week("someone")

    def test_author_key_wins_over_user_key_like_the_payout_runner(self):
        c = {"author": {"login": "attacker"}, "user": {"login": self.BOT},
             "body": "<!-- rtc-payout-amount: 9 -->"}
        self.assertIsNone(dg.trusted_payout_amount([c]))
        self._one_claim([c])
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("someone")

    def test_last_trusted_marker_wins_like_the_payout_runner(self):
        """bounty_payout.py pays the LAST trusted marker; the cap must count the
        same figure the payout will actually move, not a different one."""
        self._one_claim([self._c(self.BOT, 5), self._c("Scottcjn", 2.5)])
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 2.5)


class WeeklyCapPaginationTests(unittest.TestCase):
    """Issue #17054: paginate search/issues + comments and fail closed on unknown."""

    BOT = "github-actions[bot]"

    def setUp(self):
        self._saved = {k: getattr(dg, k) for k in ("gh", "gh_raw", "add_labels", "NUM")}

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(dg, k, v)

    @staticmethod
    def _page_arg(args):
        for a in args:
            if a.startswith("page="):
                return int(a.split("=", 1)[1])
            if "?page=" in a or "&page=" in a:
                return int(a.rsplit("page=", 1)[1])
        return 1

    def test_150_comments_with_trusted_marker_at_position_120(self):
        comments = [
            {"user": {"login": "spammer"}, "body": f"noise {i}"}
            for i in range(1, 151)
        ]
        # 1-based position 120 -> index 119 (on page 2).
        comments[119] = {
            "user": {"login": self.BOT},
            "body": "<!-- rtc-payout-amount: 12.5 -->",
        }

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"total_count": 1, "incomplete_results": False, "items": [{"number": 901}]}
            if "/comments" in joined:
                p = self._page_arg(args)
                return comments[(p - 1) * 100 : p * 100]
            return default

        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("alice"), 12.5)

    def test_exact_100_comments_boundary(self):
        comments = [{"user": {"login": "chatter"}, "body": f"c{i}"} for i in range(1, 101)]
        comments[99] = {"user": {"login": self.BOT}, "body": "<!-- rtc-payout-amount: 4.25 -->"}
        seen_pages = []

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"total_count": 1, "items": [{"number": 902}]}
            if "/comments" in joined:
                p = self._page_arg(args)
                seen_pages.append(p)
                return comments if p == 1 else []
            return default

        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("alice"), 4.25)
        self.assertEqual(seen_pages, [1, 2])

    def test_comment_pagination_page2_error_or_non_list_fails_closed(self):
        page1 = [{"user": {"login": self.BOT}, "body": "<!-- rtc-payout-amount: 5 -->"}] * 100

        def fake_err(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 903}]}
            if "/comments" in joined:
                if self._page_arg(args) == 1:
                    return page1
                raise dg.GhError("rate limit on page 2")
            return default

        dg.gh = fake_err
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

        def fake_none(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 903}]}
            if "/comments" in joined:
                return page1 if self._page_arg(args) == 1 else None
            return default

        dg.gh = fake_none
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_comment_pagination_exceeds_max_pages_fails_closed(self):
        full_page = [{"user": {"login": self.BOT}, "body": "<!-- rtc-payout-amount: 1 -->"}] * 100

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return {"items": [{"number": 904}]}
            if "/comments" in joined:
                return full_page
            return default

        dg.gh = fake
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_search_pagination_sums_over_100_claims_and_skips_self(self):
        dg.NUM = "1050"
        all_items = [{"number": 1000 + i} for i in range(125)]
        # Duplicate issue #1005 at page 2 boundary to confirm no double-count.
        page2_items = [{"number": 1005}] + all_items[100:]

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                p = self._page_arg(args)
                return {
                    "total_count": 125,
                    "incomplete_results": False,
                    "items": all_items[:100] if p == 1 else page2_items,
                }
            if "/comments" in joined:
                num = int(joined.split("/issues/")[1].split("/")[0])
                if num == 1050:
                    raise AssertionError("self-claim must be skipped before fetching comments")
                return [{"user": {"login": self.BOT}, "body": "<!-- rtc-payout-amount: 0.5 -->"}]
            return default

        dg.gh = fake
        # 124 other claims x 0.5 RTC = 62.0 RTC
        self.assertEqual(dg.docstring_rtc_this_week("alice"), 62.0)

    def test_search_pagination_incomplete_shortfall_and_over_cap_fail_closed(self):
        cases = [
            lambda p: {"total_count": 1, "incomplete_results": True, "items": [{"number": 1}]},
            lambda p: {"total_count": 150, "items": [{"number": i} for i in range(100)] if p == 1 else []},
            lambda p: {"total_count": 1001, "items": [{"number": i} for i in range(100)]},
            lambda p: {"items": [{"number": p * 100 + i} for i in range(100)]},
        ]
        for builder in cases:
            def fake(args, default=None, strict=False, _b=builder):
                if "search/issues" in " ".join(args):
                    return _b(self._page_arg(args))
                return default
            dg.gh = fake
            with self.assertRaises(dg.GhError):
                dg.docstring_rtc_this_week("alice")

    def test_main_holds_needs_human_when_prior_claim_lacks_trusted_marker(self):
        labels, comments = [], []
        dg.NUM = "777"
        dg.add_labels = lambda *names: labels.extend(names) or True
        dg.gh_raw = lambda args: (
            "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n"
            '+    """Added doc."""\n'
        )

        def fake(args, default=None, strict=False):
            joined = " ".join(args)
            if args[:2] == ["issue", "view"]:
                return {"title": "Docstring batch", "body": "https://github.com/Scottcjn/bottube/pull/9",
                        "labels": [], "author": {"login": "alice"}, "state": "OPEN"}
            if args[:2] == ["pr", "view"]:
                return {"state": "MERGED", "author": {"login": "alice"}}
            if "search/issues" in joined:
                return {"total_count": 1, "items": [{"number": 700}]}
            if "/comments" in joined:
                return [{"user": {"login": "attacker"}, "body": "<!-- rtc-payout-amount: 0 -->"}]
            if args[:2] == ["issue", "comment"]:
                comments.append(args[args.index("--body") + 1])
                return None
            return default

        dg.gh = fake
        rc = dg.main()
        self.assertEqual(rc, 0)
        self.assertIn("needs-human", labels)
        self.assertNotIn("bounty-eligible", labels)
        self.assertNotIn("docstring-verified", labels)
        self.assertFalse(any("rtc-payout-amount" in c for c in comments))


if __name__ == "__main__":
    unittest.main()
