#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for the bounty-PR protected-paths guard.

Run: python3 scripts/test_guard_bounty_pr.py   (or `pytest scripts/test_guard_bounty_pr.py`)

Focus: `is_protected_path` and `TRUSTED_ASSOCIATIONS` must reproduce the
exact split seen in real history --

  - #14981 ("solution" PR that gutted .github/scripts/*.py) SHOULD hit
    the guard (untrusted author + protected paths).
  - #14990 and #14546 (legit maintenance touching scripts/ and
    .github/workflows/) SHOULD NOT hit the guard, because they came
    from OWNER/CONTRIBUTOR.
  - #12741, #2094, #2095, #2093, #173 (real merged bounty submissions
    touching docs/, museum/, apple2_miner/, star_tracker.py, etc.)
    SHOULD NOT hit the guard even though the author was untrusted,
    because none of those paths are protected.

These tests pin that behavior so a future edit to the prefix/exact-file
lists can't silently reintroduce false positives on legitimate
contributors or false negatives on the #14981 pattern.
"""

import unittest

import guard_bounty_pr as g


class ProtectedPathDetection(unittest.TestCase):
    def test_github_scripts_are_protected(self):
        # The exact #14981 file set.
        for p in (
            ".github/scripts/backfill_xp_from_ledger_issue104.py",
            ".github/scripts/file_bug_report.py",
            ".github/scripts/update_xp_tracker.py",
        ):
            self.assertTrue(g.is_protected_path(p), p)

    def test_github_workflows_actions_mcp_are_protected(self):
        for p in (
            ".github/workflows/bounty-payout.yml",
            ".github/actions/rtc-reward-action/action.yml",
            ".github/mcp_server/rustchain_mcp/server.py",
        ):
            self.assertTrue(g.is_protected_path(p), p)

    def test_root_scripts_dir_is_protected(self):
        for p in ("scripts/auto-pay.py", "scripts/bounty_payout.py", "scripts/verify_bounties.py"):
            self.assertTrue(g.is_protected_path(p), p)

    def test_ledger_and_registry_files_are_protected(self):
        for p in (
            "bounties.json",
            "BOUNTY_LEDGER.md",
            "expected_miners.txt",
            ".github/dependabot.yml",
            ".github/supply-chain-allowlist.yml",
        ):
            self.assertTrue(g.is_protected_path(p), p)

    def test_real_merged_submission_paths_are_not_protected(self):
        # Drawn from actual merged bounty-submission PRs: #12741, #2094,
        # #2095, #2093, #173. None of these should ever trip the guard.
        for p in (
            "submissions/block-explorer-517-jonasxzb/report.md",
            "star_tracker.py",
            "museum/index.html",
            "apple2_miner/Makefile",
            "apple2_miner/miner.c",
            "docs/wrtc-onboarding/README.md",
            "docs/wrtc-pack/dexscreener-request.md",
        ):
            self.assertFalse(g.is_protected_path(p), p)

    def test_tests_dir_is_not_protected(self):
        # tests/ is a normal contribution area (e.g. #14990 adds a test
        # alongside a scripts/ fix); it is not itself protected. The
        # guard still fires on that PR because of the scripts/ file,
        # not because of the tests/ file.
        self.assertFalse(g.is_protected_path("tests/test_auto_triage_claims.py"))


class TrustedAssociations(unittest.TestCase):
    def test_owner_member_collaborator_contributor_are_trusted(self):
        for assoc in ("OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"):
            self.assertIn(assoc, g.TRUSTED_ASSOCIATIONS)

    def test_none_and_first_timer_are_not_trusted(self):
        for assoc in ("NONE", "FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER"):
            self.assertNotIn(assoc, g.TRUSTED_ASSOCIATIONS)


class RealWorldShapes(unittest.TestCase):
    """End-to-end shape checks: association + changed files -> would the
    guard fire? Mirrors the exact PRs referenced above."""

    def _would_fire(self, association: str, files: list) -> bool:
        if association.upper() in g.TRUSTED_ASSOCIATIONS:
            return False
        return any(g.is_protected_path(p) for p in files)

    def test_pr_14981_bad_solution_fires(self):
        self.assertTrue(
            self._would_fire(
                "NONE",
                [
                    ".github/scripts/backfill_xp_from_ledger_issue104.py",
                    ".github/scripts/file_bug_report.py",
                    ".github/scripts/update_xp_tracker.py",
                ],
            )
        )

    def test_pr_14990_owner_maintenance_does_not_fire(self):
        self.assertFalse(
            self._would_fire(
                "OWNER",
                [
                    ".github/workflows/auto-triage-claims.yml",
                    "scripts/auto_triage_claims.py",
                    "tests/test_auto_triage_claims.py",
                ],
            )
        )

    def test_pr_14546_contributor_maintenance_does_not_fire(self):
        self.assertFalse(
            self._would_fire("CONTRIBUTOR", ["scripts/auto-pay.py", "scripts/test_auto_pay.py"])
        )

    def test_pr_12741_legit_submission_does_not_fire(self):
        self.assertFalse(
            self._would_fire(
                "NONE",
                [
                    "submissions/block-explorer-517-jonasxzb/report.md",
                    "submissions/block-explorer-517-jonasxzb/anchors-404.png",
                ],
            )
        )

    def test_hypothetical_ledger_tamper_fires(self):
        self.assertTrue(self._would_fire("FIRST_TIME_CONTRIBUTOR", ["bounties.json"]))


if __name__ == "__main__":
    unittest.main()
