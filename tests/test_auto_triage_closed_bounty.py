# SPDX-License-Identifier: MIT
"""A closed bounty can never make a claim `eligible`.

Auto-triage runs hourly against a fixed list of bounty issues and grades each
fresh claim comment as `eligible` or `needs-action`. On 2026-09-21 six of the
seven DEFAULT_TARGETS were CLOSED (#87 since 2026-02-17, Rustchain#47 since
03-09, bottube#74 since 04-07, bottube#122 since 03-09, #157 since 07-07,
#158 since 02-18) and the run was still succeeding and still capable of
grading a claim on any of them as `eligible`.

`eligible` is a promise of money drawn on a pool that has closed. These tests
pin the fail-closed contract: a closed, missing, or unreadable bounty state
attaches a blocker to every claim on that bounty, and only a literal "open"
state leaves eligibility to the ordinary checks.
"""
import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest import mock

from scripts import auto_triage_claims as atc


def _recent_iso():
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace("+00:00", "Z")


def _claim_comment(user, body):
    return {
        "user": {"login": user},
        "created_at": _recent_iso(),
        "html_url": f"https://example.com/{user}",
        "body": body,
    }


GOOD_CLAIM = "Claiming this bounty.\nWallet: abc_wallet_123\nProof: https://example.com/p"


class ClosedBountyBlockerTests(unittest.TestCase):
    def test_open_state_yields_no_blocker(self):
        self.assertIsNone(atc._bounty_closed_blocker({"state": "open"}))

    def test_closed_state_is_a_blocker(self):
        self.assertEqual(atc._bounty_closed_blocker({"state": "closed"}), "bounty_closed")

    def test_missing_state_fails_closed(self):
        self.assertEqual(atc._bounty_closed_blocker({}), "bounty_state_unreadable")

    def test_non_dict_response_fails_closed(self):
        self.assertEqual(atc._bounty_closed_blocker(["not", "an", "issue"]), "bounty_state_unreadable")
        self.assertEqual(atc._bounty_closed_blocker(None), "bounty_state_unreadable")

    def test_empty_state_fails_closed(self):
        self.assertEqual(atc._bounty_closed_blocker({"state": ""}), "bounty_state_unreadable")


class MainRefusesEligibilityOnClosedBounty(unittest.TestCase):
    """Drive main() end-to-end with the GitHub API mocked out."""

    def _run(self, issue_state):
        target = {
            "owner": "Scottcjn", "repo": "rustchain-bounties", "issue": 87,
            "min_account_age_days": 0, "required_stars": [],
            "require_wallet": True, "require_bottube_username": False,
            "require_proof_link": False, "name": "Community Support",
        }

        def fake_request(method, path, token, data=None):
            if path.endswith("/issues/87"):
                obj = {"comments_url": "https://api.github.com/x/comments"}
                if issue_state is not None:
                    obj["state"] = issue_state
                return obj
            if path.startswith("/users/"):
                return {"created_at": "2020-01-01T00:00:00Z"}
            raise AssertionError(f"unexpected request {method} {path}")

        def fake_paginated(path, token):
            return [_claim_comment("alice", GOOD_CLAIM)]

        env = {
            "GITHUB_TOKEN": "tok", "DRY_RUN": "1",
            "TRIAGE_TARGETS_JSON": json.dumps([target]),
        }
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.object(atc, "_gh_request", side_effect=fake_request), \
             mock.patch.object(atc, "_gh_paginated", side_effect=fake_paginated), \
             mock.patch.object(atc, "_fetch_star_cache", return_value=({}, {})), \
             redirect_stdout(out), redirect_stderr(err):
            rc = atc.main()
        return rc, out.getvalue(), err.getvalue()

    def test_open_bounty_still_grades_a_complete_claim_eligible(self):
        rc, out, err = self._run("open")
        self.assertEqual(rc, 0)
        self.assertIn("`eligible`", out)
        self.assertNotIn("bounty_closed", out)
        self.assertNotIn("is not open", err)

    def test_closed_bounty_never_grades_eligible(self):
        rc, out, err = self._run("closed")
        self.assertEqual(rc, 0)
        self.assertIn("@alice", out, "the claim is still reported for a human")
        self.assertNotIn("`eligible`", out)
        self.assertIn("bounty_closed", out)
        self.assertIn("is not open", err)

    def test_unreadable_bounty_state_never_grades_eligible(self):
        rc, out, err = self._run(None)
        self.assertEqual(rc, 0)
        self.assertNotIn("`eligible`", out)
        self.assertIn("bounty_state_unreadable", out)


if __name__ == "__main__":
    unittest.main()
