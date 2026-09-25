#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for the docstring gate's weekly-cap lookups (#17054).

WHY THIS EXISTS
---------------
docstring_rtc_this_week() used to read ONE page of both the prior-claims
search and each prior claim's comments, so the 40 RTC/week cap failed
open. The exploit shape (reported in #17054, found during review of
#17053): comment 100+ times on a public claim while it sits in
awaiting-merge, and the gate's rtc-payout-amount marker lands at position
101+ -- the cap then sums 0 for that claim and approves past the ceiling
with a green run.

These tests pin the fixed behaviour:
  1. A marker at position 120 of 150 comments IS counted (the exact
     regression case from the issue).
  2. A docstring-verified prior claim with NO marker anywhere in its
     fully-paginated thread is an unknown, not a 0 -- GhError, never a
     silent undercount.
  3. A page that fails to fetch fails closed: GhError, never a partial sum.
  4. More than one page of prior verified claims is summed completely.
  5. A search window bigger than search can serve (past result 1000)
     refuses rather than undercounting.
  6. The claim currently being adjudicated is never counted.

The gh() CLI wrapper is faked per test, so these run offline with no
network, no token, and no side effects.
"""

import re
import unittest

import docstring_gate as dg


def fake_gh(search_items=None, comment_pages=None, fail_search_pages=()):
    """Build a gh() stand-in serving canned pages.

    search_items:  full list of issue dicts; served back 100 per page with
                   an honest total_count, the way search/issues behaves.
    comment_pages: {issue_number: [page1_list, page2_list, ...]} -- already
                   chunked the way /issues/{n}/comments chunks them.
    fail_search_pages: page numbers that raise (simulating a failed fetch).
    """
    search_items = search_items if search_items is not None else []
    comment_pages = comment_pages or {}
    fail_search_pages = set(fail_search_pages)

    def gh(args, default=None, strict=False):
        joined = " ".join(str(a) for a in args)
        if "search/issues" in joined:
            # NB: match the standalone -f page=N field, NOT the tail of
            # per_page=100 (whose "page=100" substring would win otherwise).
            m = re.search(r"(?:^|\s)page=(\d+)", joined)
            page = int(m.group(1)) if m else 1
            if page in fail_search_pages:
                if strict:
                    raise dg.GhError(f"search/issues page {page} failed (canned)")
                return default
            chunk = search_items[(page - 1) * 100:page * 100]
            return {"items": chunk, "total_count": len(search_items)}
        m = re.search(r"/issues/(\d+)/comments", joined)
        if m:
            n = int(m.group(1))
            # [?&] boundary: "per_page=100" also contains "page=100".
            pm = re.search(r"[?&]page=(\d+)", joined)
            page = int(pm.group(1)) if pm else 1
            pages = comment_pages.get(n, [])
            return pages[page - 1] if page <= len(pages) else []
        raise AssertionError(f"unexpected gh call: {args!r}")

    return gh


def thread_with_marker_at(count, position, amount):
    """A comment thread of `count` bodies with the marker at 1-based `position`."""
    bodies = [{"body": "ordinary comment"} for _ in range(count)]
    bodies[position - 1] = {
        "body": f"verified 3 docstrings\n\n<!-- rtc-payout-amount: {amount} -->"
    }
    return [bodies[0:100], bodies[100:]]  # how the API pages per_page=100


class WeeklyCapPagination(unittest.TestCase):
    def setUp(self):
        self._real_gh = dg.gh

    def tearDown(self):
        dg.gh = self._real_gh

    def test_marker_at_position_120_of_150_is_counted(self):
        # The exact regression from #17054.
        dg.gh = fake_gh(
            search_items=[{"number": 4242, "body": "claim"}],
            comment_pages={4242: thread_with_marker_at(150, 120, 3.25)},
        )
        self.assertEqual(dg.docstring_rtc_this_week("alice"), 3.25)

    def test_verified_claim_without_marker_is_unknown_not_zero(self):
        # Fully-read thread, no marker anywhere: an old gate, a deleted
        # comment, or a hand-applied label. Must hold, never sum 0.
        dg.gh = fake_gh(
            search_items=[{"number": 4243, "body": "claim"}],
            comment_pages={4243: [[{"body": "no marker here"} for _ in range(5)]]},
        )
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_failed_comment_page_fails_closed(self):
        # Page 2 of the thread 500s: a partial read is not a sum.
        bodies = [{"body": "noise"} for _ in range(150)]
        bodies[149] = {"body": "<!-- rtc-payout-amount: 2.0 -->"}

        def gh(args, default=None, strict=False):
            joined = " ".join(str(a) for a in args)
            if "/issues/4244/comments" in joined and re.search(r"[?&]page=2\b", joined):
                if strict:
                    raise dg.GhError("comments page 2 of #4244 failed (canned)")
                return default
            return fake_gh(
                search_items=[{"number": 4244, "body": "claim"}],
                comment_pages={4244: [bodies[0:100], bodies[100:150]]},
            )(args, default, strict)

        dg.gh = gh
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_failed_search_page_fails_closed(self):
        dg.gh = fake_gh(
            search_items=[{"number": 4245, "body": "claim"}],
            comment_pages={4245: thread_with_marker_at(10, 3, 1.5)},
            fail_search_pages=(1,),
        )
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_every_prior_claim_across_search_pages_is_summed(self):
        # 150 prior verified claims: page 1 serves 100, page 2 serves 50.
        priors = [{"number": 5000 + i, "body": "claim"} for i in range(150)]
        pages = {p["number"]: [[{"body": "<!-- rtc-payout-amount: 0.1 -->"}]] for p in priors}
        dg.gh = fake_gh(search_items=priors, comment_pages=pages)
        self.assertEqual(dg.docstring_rtc_this_week("alice"), 15.0)

    def test_window_past_search_limit_refuses(self):
        # search/issues cannot serve past result 1000; a window of 1001
        # claims is unreadable, so the sum must refuse, not truncate.
        priors = [{"number": 6000 + i, "body": "claim"} for i in range(1001)]
        dg.gh = fake_gh(search_items=priors, comment_pages={})
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("alice")

    def test_current_claim_is_never_counted(self):
        # The claim being adjudicated (dg.NUM) is excluded even though the
        # search returns it.
        dg.NUM = "4242"
        try:
            dg.gh = fake_gh(
                search_items=[{"number": 4242, "body": "claim"}],
                comment_pages={4242: thread_with_marker_at(150, 120, 3.25)},
            )
            self.assertEqual(dg.docstring_rtc_this_week("alice"), 0.0)
        finally:
            dg.NUM = ""


if __name__ == "__main__":
    unittest.main()
