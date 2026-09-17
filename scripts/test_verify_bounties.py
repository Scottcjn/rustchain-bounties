#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for the three silent-success paths in the verification leg.

Run: python3 scripts/test_verify_bounties.py   (or `pytest scripts/test_verify_bounties.py`)

Each test below fails on the previous code and passes on the current code.

1. `is_issue_open` turned "could not read the issue" into `False`, so `run_phase`
   logged "Issue #N is closed, skipping", recorded no failure, and the sweep
   exited 0 having verified nobody on that bounty.
2. One literal threshold ("3 stars on any tracked repo") adjudicated five star
   bounties that ask for different things — verifying claimants who had not done
   the task, and publicly telling claimants who had done it that they had no
   stars.
3. The five phases discarded the boolean from `post_comment` / `update_comment`.
   For the Live-URL phase that meant the payable `live-url-verified` label was
   stamped on an issue whose evidence table had failed to post.
"""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("GITHUB_TOKEN", "test-token")

import verify_bounties as vb  # noqa: E402


class StarRuleTests(unittest.TestCase):
    """Each bounty is adjudicated by its own rule, not by a shared literal."""

    def test_16238_requires_rustchain_itself(self):
        rule = vb.STAR_BOUNTY_RULES[16238]
        # Three stars, none of them the repo the bounty names.
        self.assertIn("NOT MET", rule.verdict(["bottube", "shaprai", "trashclaw"]))
        self.assertIn("VERIFIED", rule.verdict(["Rustchain", "bottube", "shaprai"]))

    def test_378_is_the_bottube_bounty(self):
        rule = vb.STAR_BOUNTY_RULES[378]
        # Used to read VERIFIED (3 stars) without a BoTTube star anywhere.
        self.assertIn("NOT MET", rule.verdict(["Rustchain", "shaprai", "trashclaw"]))
        # Used to read "Partial (1 stars)" for exactly the right star.
        self.assertIn("VERIFIED", rule.verdict(["bottube"]))

    def test_171_accepts_one_star_out_of_fifty_five_repos(self):
        rule = vb.STAR_BOUNTY_RULES[171]
        self.assertIn("VERIFIED", rule.verdict(["trashclaw"]))
        # A favourite outside the repos this bot can see must never render as
        # an accusation. NOT CHECKED, not "No stars found".
        verdict = rule.verdict([])
        self.assertIn("NOT CHECKED", verdict)
        self.assertNotIn("No stars found", verdict)

    def test_9017_keeps_the_any_three_rule(self):
        rule = vb.STAR_BOUNTY_RULES[9017]
        self.assertIn("VERIFIED", rule.verdict(["Rustchain", "bottube", "shaprai"]))
        self.assertIn("Partial", rule.verdict(["Rustchain", "bottube"]))

    def test_every_adjudicated_issue_has_a_rule(self):
        for issue in vb.STAR_BOUNTY_ISSUES:
            self.assertIn(issue, vb.STAR_BOUNTY_RULES)

    def test_required_repos_are_tracked(self):
        # A required repo the star sweep never fetches would deny every claim.
        for issue, rule in vb.STAR_BOUNTY_RULES.items():
            for repo in rule.required:
                self.assertIn(repo, vb.STAR_REPOS, f"#{issue} requires untracked {repo}")


class StarPhaseTests(unittest.TestCase):
    """The rendered report for a real phase run, end to end."""

    def _run(self, issue, stars_by_repo):
        published = {}
        comments = [{"id": 1, "user": {"login": "claimant"}, "body": "starred, please verify"}]
        all_stars = {repo: set() for repo in vb.STAR_REPOS}
        for repo in stars_by_repo:
            all_stars[repo].add("claimant")
        with patch.object(vb, "get_issue_comments", return_value=comments), \
             patch.object(vb, "publish_report",
                          side_effect=lambda i, c, b: published.update(issue=i, body=b)):
            vb.verify_star_claims(issue, all_stars)
        return published["body"]

    def test_bottube_bounty_rejects_three_unrelated_stars(self):
        body = self._run(378, ["Rustchain", "shaprai", "trashclaw"])
        self.assertIn("NOT MET", body)
        self.assertIn("the BoTTube repo", body)

    def test_bottube_bounty_accepts_the_single_right_star(self):
        body = self._run(378, ["bottube"])
        self.assertIn("VERIFIED", body)

    def test_pick_your_favourite_never_accuses(self):
        body = self._run(171, [])
        self.assertIn("NOT CHECKED", body)
        self.assertNotIn("No stars found", body)


class _Resp:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = {}
        self.text = ""

    def json(self):
        return self._payload


class IssueStateTests(unittest.TestCase):
    """An unreadable issue is not a closed issue."""

    def test_non_200_is_unknown_not_closed(self):
        with patch.object(vb, "gh_get", return_value=_Resp(403)):
            self.assertIsNone(vb.is_issue_open(16238))

    def test_open_and_closed_still_answer_normally(self):
        with patch.object(vb, "gh_get", return_value=_Resp(200, {"state": "open"})):
            self.assertIs(vb.is_issue_open(16238), True)
        with patch.object(vb, "gh_get", return_value=_Resp(200, {"state": "closed"})):
            self.assertIs(vb.is_issue_open(16238), False)

    def test_unreadable_issue_fails_the_run_and_skips_no_work_silently(self):
        ran = []
        with patch.object(vb, "is_issue_open", return_value=None):
            failures = vb.run_phase("Phase X", [16238], lambda i: ran.append(i))
        self.assertEqual(ran, [])                 # nothing was verified
        self.assertEqual(len(failures), 1)        # and the run knows it
        self.assertIn("unreadable", failures[0])

    def test_closed_issue_is_still_a_clean_skip(self):
        ran = []
        with patch.object(vb, "is_issue_open", return_value=False):
            failures = vb.run_phase("Phase X", [16238], lambda i: ran.append(i))
        self.assertEqual(ran, [])
        self.assertEqual(failures, [])


class PublishReportTests(unittest.TestCase):
    """A verdict nobody can see is not a published verdict."""

    def test_failed_post_raises(self):
        with patch.object(vb, "post_comment", return_value=False):
            with self.assertRaises(vb.ReportNotPublished):
                vb.publish_report(16238, None, "body")

    def test_failed_update_raises(self):
        with patch.object(vb, "update_comment", return_value=False):
            with self.assertRaises(vb.ReportNotPublished):
                vb.publish_report(16238, 4242, "body")

    def test_successful_write_is_silent(self):
        with patch.object(vb, "post_comment", return_value=True):
            self.assertIsNone(vb.publish_report(16238, None, "body"))

    def test_run_phase_records_an_unpublished_report(self):
        def runner(_issue):
            raise vb.ReportNotPublished("#315: verification report was not published")

        with patch.object(vb, "is_issue_open", return_value=True):
            failures = vb.run_phase("Phase 6", [315], runner)
        self.assertEqual(len(failures), 1)
        self.assertIn("not published", failures[0])


class LiveUrlLabelTests(unittest.TestCase):
    """The payable label is never stamped on an unpublished report."""

    def _claims(self):
        return [{"username": "someone", "url": "https://bottube.ai/watch/abc", "platform": "bottube"}]

    def test_label_withheld_when_the_report_cannot_be_posted(self):
        labelled = []
        with patch.object(vb, "get_issue_comments", return_value=[]), \
             patch.object(vb, "extract_live_url_claims", return_value=self._claims()), \
             patch.object(vb, "find_existing_bot_comment", return_value=None), \
             patch.object(vb, "verify_live_url",
                          return_value={"status": "VERIFIED", "metric": "ok"}), \
             patch.object(vb, "post_comment", return_value=False), \
             patch.object(vb, "add_issue_label",
                          side_effect=lambda i, l: labelled.append((i, l)) or True):
            with self.assertRaises(vb.ReportNotPublished):
                vb.verify_distribution_claims(315)
        self.assertEqual(labelled, [], "live-url-verified stamped without a published report")

    def test_label_applied_when_the_report_lands(self):
        labelled = []
        with patch.object(vb, "get_issue_comments", return_value=[]), \
             patch.object(vb, "extract_live_url_claims", return_value=self._claims()), \
             patch.object(vb, "find_existing_bot_comment", return_value=None), \
             patch.object(vb, "verify_live_url",
                          return_value={"status": "VERIFIED", "metric": "ok"}), \
             patch.object(vb, "post_comment", return_value=True), \
             patch.object(vb, "add_issue_label",
                          side_effect=lambda i, l: labelled.append((i, l)) or True):
            vb.verify_distribution_claims(315)
        self.assertEqual(labelled, [(315, vb.LIVE_URL_VERIFIED_LABEL)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
