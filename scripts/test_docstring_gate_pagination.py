#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for the weekly-cap pagination fix (issue #17054).

docstring_rtc_this_week() previously fetched ONE page (per_page=100) of both
its lookups -- the search for prior docstring-verified claims, and each prior
claim's comments. The gate's rtc-payout-amount marker sits at the END of a
claim's comment list, so on an active claim it could be pushed past position
100, the sum undercounted prior earnings, and the 40 RTC/week cap FAILED OPEN
while every run stayed green.

The acceptance bar from the issue:
  - 150 comments with the marker at position 120 must be counted.
  - prior claims past the first search page must be counted.
  - a docstring-verified prior claim with NO reachable marker is UNKNOWN,
    never 0 -> GhError -> the caller's needs-human hold.
  - pagination that cannot complete fails closed, never silently short.

These tests never touch the network: `gh` is monkeypatched with canned
GitHub-shaped pages, so they run anywhere (CI included) in milliseconds.
"""
from __future__ import annotations

import os
import sys
import unittest

os.environ.setdefault("GH_REPO", "Scottcjn/rustchain-bounties")
os.environ.setdefault("ISSUE_NUMBER", "99999")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import docstring_gate as dg  # noqa: E402


def marker_comment(amount: float) -> dict:
    return {"body": f"🤖 Docstring gate: verified. <!-- rtc-payout-amount: {amount} -->"}


def plain_comment(i: int) -> dict:
    return {"body": f"review chatter #{i} -- no marker here"}


def issue_item(number: int) -> dict:
    return {"number": number, "body": "claim body", "title": f"docstring claim {number}"}


class FakeGh:
    """Canned multi-page GitHub API responses shaped like the real endpoints."""

    def __init__(self, search_pages, comments_by_issue, fail_on=None):
        self.search_pages = search_pages          # page -> response dict
        self.comments_by_issue = comments_by_issue  # issue -> page -> list
        self.fail_on = fail_on or set()           # (endpoint-frag, page) to fail
        self.calls = []

    def __call__(self, args, default=None, strict=False):
        self.calls.append(args)
        joined = " ".join(args)
        page = 1
        for a in args:
            if a.startswith("page="):
                page = int(a.split("=", 1)[1])
        for frag, fpage in self.fail_on:
            if frag in joined and page == fpage:
                err = subprocess_error = "API rate limit exceeded"
                import subprocess as _sp
                raise dg.GhError(f"gh api failed: {err}")
        if "search/issues" in joined:
            return self.search_pages.get(page, {"total_count": 0, "items": []})
        if "/comments" in joined:
            num = int(joined.split("/issues/", 1)[1].split("/comments", 1)[0])
            return self.comments_by_issue.get(num, {}).get(page, [])
        raise AssertionError(f"unexpected gh call: {args}")


class PaginationTests(unittest.TestCase):
    def setUp(self):
        self._orig_gh = dg.gh
        self._orig_num = dg.NUM

    def tearDown(self):
        dg.gh = self._orig_gh

    def test_marker_at_position_120_of_150_counted(self):
        """THE issue's acceptance criterion: marker deep in page 2 must count."""
        comments = [plain_comment(i) for i in range(1, 150)]
        comments[119] = marker_comment(12.5)   # position 120 (1-indexed)
        # 150 comments = page 1 full (100) + page 2 short (50)
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(1001)]}},
            comments_by_issue={1001: {1: comments[:100], 2: comments[100:]}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 12.5)
        # prove pagination actually happened: 1 search + 2 comment calls
        comment_calls = [c for c in fake.calls if "/comments" in " ".join(c)]
        self.assertEqual(len(comment_calls), 2)

    def test_marker_beyond_two_pages_counted(self):
        """250 comments: marker at 205 survives three pages, still counted."""
        comments = [plain_comment(i) for i in range(1, 250)]
        comments[204] = marker_comment(3.75)   # position 205
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(1002)]}},
            comments_by_issue={1002: {1: comments[:100], 2: comments[100:200],
                                      3: comments[200:]}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 3.75)

    def test_prior_claims_past_first_search_page_counted(self):
        """150 prior claims across 2 search pages: every marker summed."""
        items = [issue_item(2000 + i) for i in range(150)]
        comments_by_issue = {
            2000 + i: {1: [marker_comment(0.5)]} for i in range(150)
        }
        fake = FakeGh(
            search_pages={1: {"total_count": 150, "items": items[:100]},
                          2: {"total_count": 150, "items": items[100:]}},
            comments_by_issue=comments_by_issue,
        )
        dg.gh = fake
        # 150 claims x 0.5 RTC (the claim under adjudication is excluded, so
        # make sure NUM is not among the fixtures)
        self.assertNotIn(str(dg.NUM), {str(i["number"]) for i in items})
        self.assertAlmostEqual(dg.docstring_rtc_this_week("prolific"), 75.0)

    def test_markerless_verified_claim_is_unknown_not_zero(self):
        """docstring-verified with NO reachable marker = GhError, never 0."""
        fake = FakeGh(
            search_pages={1: {"total_count": 2, "items": [issue_item(3001),
                                                          issue_item(3002)]}},
            comments_by_issue={
                3001: {1: [marker_comment(5.0)]},
                3002: {1: [plain_comment(i) for i in range(40)]},  # no marker
            },
        )
        dg.gh = fake
        with self.assertRaises(dg.GhError) as cm:
            dg.docstring_rtc_this_week("someone")
        self.assertIn("UNKNOWN", str(cm.exception))
        self.assertIn("3002", str(cm.exception))

    def test_search_shortfall_fails_closed(self):
        """total_count says 150 but page 2 is empty -> GhError, not a short sum."""
        items = [issue_item(4000 + i) for i in range(100)]
        comments_by_issue = {4000 + i: {1: [marker_comment(1.0)]}
                             for i in range(100)}
        fake = FakeGh(
            search_pages={1: {"total_count": 150, "items": items},
                          2: {"total_count": 150, "items": []}},
            comments_by_issue=comments_by_issue,
        )
        dg.gh = fake
        with self.assertRaises(dg.GhError) as cm:
            dg.docstring_rtc_this_week("someone")
        self.assertIn("did not converge", str(cm.exception))

    def test_page_fetch_failure_fails_closed(self):
        """A failing page raise GhError -- never a silently partial history."""
        comments = [plain_comment(i) for i in range(1, 130)]
        comments[119] = marker_comment(9.0)
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(5001)]}},
            comments_by_issue={5001: {1: comments[:100]}},
            fail_on={("/comments", 2)},
        )
        dg.gh = fake
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("someone")

    def test_claim_under_adjudication_still_excluded(self):
        """The claim being adjudicated is never counted (prior behaviour kept)."""
        comments = [plain_comment(i) for i in range(1, 150)]
        comments[119] = marker_comment(99.0)
        fake = FakeGh(
            search_pages={1: {"total_count": 2,
                              "items": [issue_item(int(dg.NUM)), issue_item(6001)]}},
            comments_by_issue={6001: {1: comments[:100], 2: comments[100:]},
                               int(dg.NUM): {1: [marker_comment(99.0)]}},
        )
        dg.gh = fake
        # only #6001's marker counts; the claim under review (dg.NUM) is skipped
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 99.0)

    def test_self_claim_markerless_does_not_block(self):
        """A markerless SELF claim must not raise -- it is skipped before the scan."""
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(int(dg.NUM))]}},
            comments_by_issue={int(dg.NUM): {1: [plain_comment(1)]}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 0.0)

    def test_exactly_one_full_page_then_empty_short_page(self):
        """100 comments exactly: one extra page proves the short-page stop."""
        comments = [plain_comment(i) for i in range(1, 101)]
        comments[99] = marker_comment(7.0)   # last of the 100 (position 100)
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(7001)]}},
            comments_by_issue={7001: {1: comments, 2: []}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 7.0)

    def test_search_page_cap_overrun_refuses(self):
        """More than max_pages of full search pages -> GhError, never a truncation.

        (Consolidated from the earlier test_docstring_gate.py in this branch.)
        """
        full_page = {"total_count": 10_000, "items": [issue_item(8000 + i) for i in range(100)]}
        fake = FakeGh(search_pages={}, comments_by_issue={})
        fake.search_pages = {}  # every page returns a full page of 100
        original_call = fake.__call__

        def endless(args, default=None, strict=False):
            joined = " ".join(args)
            if "search/issues" in joined:
                return full_page
            return original_call(args, default, strict)

        dg.gh = endless
        with self.assertRaises(dg.GhError) as cm:
            dg.docstring_rtc_this_week("someone")
        self.assertIn("exceeded", str(cm.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
