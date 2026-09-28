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
  - a docstring-verified prior claim with NO reachable trusted marker is
    UNKNOWN, never 0 -> GhError -> the caller's needs-human hold.
  - pagination that cannot complete fails closed, never silently short.

Post-#17053 coordination: markers only count when written by a
TRUSTED_MARKER_AUTHORS identity, so every fixture comment now carries an
author, and a stranger-authored marker is pinned to count as UNKNOWN (not
their figure, and not 0 either).

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


GATE_BOT = "github-actions[bot]"


def marker_comment(amount: float, author: str = GATE_BOT) -> dict:
    return {"author": {"login": author},
            "body": f"🤖 Docstring gate: verified. <!-- rtc-payout-amount: {amount} -->"}


def plain_comment(i: int) -> dict:
    return {"author": {"login": f"commenter-{i}"},
            "body": f"review chatter #{i} -- no marker here"}


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
                raise dg.GhError("gh api failed: API rate limit exceeded")
        if "search/issues" in joined:
            return self.search_pages.get(page, {"total_count": 0, "items": []})
        if "/comments" in joined:
            num = int(joined.split("/issues/", 1)[1].split("/comments", 1)[0])
            return self.comments_by_issue.get(num, {}).get(page, [])
        raise AssertionError(f"unexpected gh call: {args}")


class PaginationTests(unittest.TestCase):
    def setUp(self):
        self._orig_gh = dg.gh

    def tearDown(self):
        dg.gh = self._orig_gh

    def test_marker_at_position_120_of_150_counted(self):
        """THE issue's acceptance criterion: marker deep in page 2 must count."""
        comments = [plain_comment(i) for i in range(1, 151)]   # 150 comments
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
        comments = [plain_comment(i) for i in range(1, 251)]   # 250 comments
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

    def test_stranger_marker_is_unknown_not_their_figure(self):
        """#17053 coordination: an untrusted marker is not a figure and not 0.

        A stranger writing <!-- rtc-payout-amount: 99 --> on a verified claim
        must neither steer the cap (their figure) nor silently undercount
        (0): with no TRUSTED marker anywhere the earnings are UNKNOWN.
        """
        comments = [plain_comment(i) for i in range(1, 120)]
        comments[60] = marker_comment(99.0, author="rando-stranger")
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(3101)]}},
            comments_by_issue={3101: {1: comments[:100], 2: comments[100:]}},
        )
        dg.gh = fake
        with self.assertRaises(dg.GhError) as cm:
            dg.docstring_rtc_this_week("someone")
        self.assertIn("UNKNOWN", str(cm.exception))
        self.assertIn("3101", str(cm.exception))

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
        comments = [plain_comment(i) for i in range(1, 131)]    # 130 comments
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
        comments = [plain_comment(i) for i in range(1, 151)]    # 150 comments
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
        comments = [plain_comment(i) for i in range(1, 101)]    # 100 comments
        comments[99] = marker_comment(7.0)   # last of the 100 (position 100)
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(7001)]}},
            comments_by_issue={7001: {1: comments, 2: []}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("someone"), 7.0)

    def test_search_page_cap_overrun_refuses(self):
        """More than max_pages of full search pages -> GhError, never a truncation.

        The cap is 10 pages: GitHub search cannot serve past result 1000, so a
        window that size is refused with this message rather than a raw 422
        from page 11.
        """
        full_page = {"total_count": 10_000, "items": [issue_item(8000 + i) for i in range(100)]}
        fake = FakeGh(search_pages={}, comments_by_issue={})
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
        self.assertIn("10", str(cm.exception))


class RecoveryPathTests(unittest.TestCase):
    """The manual-recovery path must not poison the claimant (#17055 review item 1).

    A claim whose labels were applied by hand after a gate label-API failure
    used to end up docstring-verified with NO payout marker anywhere, so every
    later claim by that contributor raised "no trusted marker" forever. The
    hold comment now carries the gate's own marker; these tests pin that.
    """

    def setUp(self):
        self._orig_gh = dg.gh

    def tearDown(self):
        dg.gh = self._orig_gh

    def test_label_failure_hold_body_carries_gate_marker(self):
        """The hold body embeds a parseable marker for the computed amount."""
        body = dg._label_failure_hold_body("Scottcjn/rustchain-bounties", 4321, 37, 4.35)
        m = dg.PAYOUT_MARKER_RE.search(body)
        self.assertIsNotNone(m, "hold body must contain the rtc-payout-amount marker")
        self.assertTrue(dg.PAYOUT_AMOUNT_RE.fullmatch(m.group(1)))
        self.assertEqual(float(m.group(1)), 4.35)
        # the human instructions survive alongside the marker
        self.assertIn("bounty-eligible", body)
        self.assertIn("docstring-verified", body)

    def test_hand_recovered_hold_comment_resolves_as_trusted(self):
        """A claim whose ONLY marker is the gate's hold comment is machine-readable.

        This is the poisoning scenario from the review: the human applies the
        two labels by hand after a label-API failure. The hold comment is
        authored by the gate's own identity, so the weekly cap reads its figure
        instead of raising UNKNOWN on every future claim of this contributor.
        """
        hold = {"author": {"login": "github-actions[bot]"},
                "body": dg._label_failure_hold_body("Scottcjn/rustchain-bounties", 4321, 37, 4.35)}
        self.assertEqual(dg.trusted_payout_amount([hold]), 4.35)
        # and inside a full thread it unblocks the weekly-cap sum
        fake = FakeGh(
            search_pages={1: {"total_count": 1, "items": [issue_item(9001)]}},
            comments_by_issue={9001: {1: [hold] + [plain_comment(i) for i in range(99)]}},
        )
        dg.gh = fake
        self.assertEqual(dg.docstring_rtc_this_week("recovered-contributor"), 4.35)

    def test_hold_marker_from_a_stranger_is_not_trusted(self):
        """The same hold text pasted by a stranger still counts for nothing."""
        hold = {"author": {"login": "rando-stranger"},
                "body": dg._label_failure_hold_body("Scottcjn/rustchain-bounties", 4321, 37, 99.0)}
        self.assertIsNone(dg.trusted_payout_amount([hold]))

    def test_maintainer_override_of_hold_marker_wins(self):
        """#17053 coordination: a later maintainer marker overrides the hold figure."""
        hold = {"author": {"login": "github-actions[bot]"},
                "body": dg._label_failure_hold_body("Scottcjn/rustchain-bounties", 4321, 37, 4.35)}
        override = {"author": {"login": "scottcjn"},
                    "body": "Corrected after review: <!-- rtc-payout-amount: 3.00 -->"}
        self.assertEqual(dg.trusted_payout_amount([hold, override]), 3.00)


if __name__ == "__main__":
    unittest.main(verbosity=2)
