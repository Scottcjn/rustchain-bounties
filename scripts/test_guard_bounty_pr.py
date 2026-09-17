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

    def test_claimants_registry_is_protected(self):
        # docs/CLAIMANTS.md is the payout-destination registry: a single
        # appended row can silently redirect another contributor's payout,
        # so a non-collaborator edit must be flagged for human review.
        self.assertTrue(g.is_protected_path("docs/CLAIMANTS.md"))

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

    def _would_fire(self, association: str, files: list, has_write: bool = False) -> bool:
        """Mirrors main(): a repository role never fires; otherwise protected
        paths fire, and the CONTRIBUTOR exemption stops at the money tier
        unless real write permission is verified."""
        assoc = association.upper()
        if assoc in g.ROLE_ASSOCIATIONS:
            return False
        hits = [p for p in files if g.is_protected_path(p)]
        if not hits:
            return False
        money = [p for p in hits if g.is_money_path(p)]
        if assoc in g.TRUSTED_ASSOCIATIONS and not money:
            return False
        if assoc in g.TRUSTED_ASSOCIATIONS and money and has_write:
            return False
        return True

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


class CaseInsensitiveMatching(unittest.TestCase):
    """Audit #16471, finding 2: the match was case-sensitive, so a re-cased
    path read as untouched. `scripts/auto-pay.py` had already closed the same
    bypass on the auto-tier side and left the reasoning in the tree; that fix
    had never reached this guard."""

    def test_recased_protected_prefixes_are_still_protected(self):
        for p in (
            "Scripts/bounty_payout.py",
            "SCRIPTS/auto-pay.py",
            ".GitHub/workflows/bounty-payout.yml",
            ".github/Scripts/update_xp_tracker.py",
            ".GITHUB/actions/rtc-reward-action/action.yml",
        ):
            self.assertTrue(g.is_protected_path(p), p)

    def test_recased_registry_files_are_still_protected(self):
        for p in (
            "docs/Claimants.md",
            "docs/claimants.md",
            "bounty_ledger.md",
            "BOUNTIES.JSON",
            "Expected_Miners.txt",
        ):
            self.assertTrue(g.is_protected_path(p), p)

    def test_windows_separators_normalise(self):
        self.assertTrue(g.is_protected_path("scripts\\bounty_payout.py"))

    def test_recasing_does_not_protect_unrelated_paths(self):
        for p in ("Museum/index.html", "Docs/wrtc-pack/dexscreener-request.md"):
            self.assertFalse(g.is_protected_path(p), p)


class ActionDefinitionsAreProtected(unittest.TestCase):
    """Audit #16471, finding 3: `.github/actions/` was protected but six other
    action definitions were not, and `.github/workflows/glassworm.yml` runs one
    of them (`uses: ./glassworm-protocol`) with a writable GITHUB_TOKEN."""

    def test_action_definitions_outside_dot_github_are_protected(self):
        for p in (
            "glassworm-protocol/action.yml",
            "bounty-2864/action.yml",
            "actions/rtc-reward/action.yml",
            "rtc-reward-action/action.yml",
            "github-tip-bot/action.yml",
            "community/github-actions/rtc-reward/action.yml",
        ):
            self.assertTrue(g.is_protected_path(p), p)
            self.assertTrue(g.is_money_path(p), p)

    def test_a_plain_yaml_is_not_an_action_definition(self):
        self.assertFalse(g.is_action_definition("docs/actions.yml"))
        self.assertFalse(g.is_action_definition("submissions/foo/action-plan.yml"))


class DiscoveredActionDirectories(unittest.TestCase):
    """The protected set for CI-executed code is DERIVED from the base tree, so
    it cannot drift as actions are added, renamed or moved. A docker action is
    more than its action.yml: the Dockerfile and sources beside it are the code
    that actually runs."""

    def setUp(self):
        self._saved = g.ACTION_DIR_PREFIXES_LC
        g.ACTION_DIR_PREFIXES_LC = ("glassworm-protocol/", "bounty-2864/")

    def tearDown(self):
        g.ACTION_DIR_PREFIXES_LC = self._saved

    def test_sibling_files_of_an_action_are_protected(self):
        for p in (
            "glassworm-protocol/Dockerfile",
            "glassworm-protocol/src/sentinel.py",
            "Glassworm-Protocol/entrypoint.sh",
        ):
            self.assertTrue(g.is_protected_path(p), p)
            self.assertTrue(g.is_money_path(p), p)

    def test_unrelated_directories_stay_unprotected(self):
        self.assertFalse(g.is_protected_path("glassworm-notes/README.md"))

    def test_discovery_reads_action_dirs_and_local_uses(self):
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "my-action"))
            open(os.path.join(root, "my-action", "action.yml"), "w").close()
            wf = os.path.join(root, ".github", "workflows")
            os.makedirs(wf)
            with open(os.path.join(wf, "run.yml"), "w", encoding="utf-8") as fh:
                fh.write("jobs:\n  a:\n    steps:\n      - uses: ./runner-dir\n")
            found = g.discover_action_dirs(root)

        self.assertIn("my-action/", found)
        self.assertIn("runner-dir/", found)


class RenamesAreSeen(unittest.TestCase):
    """Audit #16471, finding 4: `previous_filename` was ignored, so renaming a
    protected file out of a protected path presented as one safe path."""

    class _Resp:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def test_previous_filename_is_collected(self):
        batches = [
            [
                {"filename": "docs/payout-notes.py", "previous_filename": "scripts/bounty_payout.py"},
                {"filename": "README.md"},
            ],
            [],
        ]

        def fake_get(url, headers=None, params=None, timeout=None):
            page = params["page"]
            payload = batches[page - 1] if page <= len(batches) else []
            return RenamesAreSeen._Resp(payload)

        saved = g.requests.get
        g.requests.get = fake_get
        try:
            paths = g.fetch_changed_files("o", "r", 1, {})
        finally:
            g.requests.get = saved

        self.assertIn("scripts/bounty_payout.py", paths)
        self.assertTrue(any(g.is_protected_path(p) for p in paths))


class ContributorIsNotTrustOnMoneyPaths(unittest.TestCase):
    """Audit #16471, finding 1. GitHub sets author_association=CONTRIBUTOR after
    ONE commit lands. Measured 2026-09-17: @K4bain has exactly one PR (#16969)
    and one commit in this repo, a +1/-0 README badge with zero review comments,
    merged 2026-09-16 for the 2 RTC bounty #13949, and is CONTRIBUTOR today. So
    the price of a permanent exemption was one line of README. CONTRIBUTOR still
    exempts ordinary automation maintenance (#14546 is real and flagging it would
    be noise); it no longer exempts the payout registry or CI-executed code."""

    def _would_fire(self, association, files, has_write=False):
        return RealWorldShapes._would_fire(self, association, files, has_write)

    def test_contributor_editing_the_payout_registry_fires(self):
        self.assertTrue(self._would_fire("CONTRIBUTOR", ["docs/CLAIMANTS.md"]))

    def test_contributor_editing_the_ledger_fires(self):
        self.assertTrue(self._would_fire("CONTRIBUTOR", ["BOUNTY_LEDGER.md"]))
        self.assertTrue(self._would_fire("CONTRIBUTOR", ["bounties.json"]))

    def test_contributor_editing_an_executed_action_fires(self):
        self.assertTrue(self._would_fire("CONTRIBUTOR", ["glassworm-protocol/action.yml"]))

    def test_verified_write_permission_still_exempts(self):
        self.assertFalse(self._would_fire("CONTRIBUTOR", ["docs/CLAIMANTS.md"], has_write=True))

    def test_role_associations_never_fire_even_on_money_paths(self):
        for assoc in ("OWNER", "MEMBER", "COLLABORATOR"):
            self.assertFalse(self._would_fire(assoc, ["docs/CLAIMANTS.md"]), assoc)

    def test_contributor_maintenance_on_non_money_paths_still_does_not_fire(self):
        # The #14546 pin, restated against the two-tier rule.
        self.assertFalse(
            self._would_fire("CONTRIBUTOR", ["scripts/auto-pay.py", "scripts/test_auto_pay.py"])
        )

    def test_contributor_is_still_trusted_for_tier_one_only(self):
        self.assertIn("CONTRIBUTOR", g.TRUSTED_ASSOCIATIONS)
        self.assertNotIn("CONTRIBUTOR", g.ROLE_ASSOCIATIONS)


class WriteAccessFailsClosed(unittest.TestCase):
    """The permission lookup decides whether a money-path edit may skip human
    review, so every unhappy path must answer no."""

    class _Resp:
        def __init__(self, status, payload=None, bad_json=False):
            self.status_code = status
            self._payload = payload
            self._bad_json = bad_json

        def json(self):
            if self._bad_json:
                raise ValueError("not json")
            return self._payload

    def _answer(self, resp_or_exc):
        saved = g.requests.get

        def fake_get(url, headers=None, timeout=None):
            if isinstance(resp_or_exc, Exception):
                raise resp_or_exc
            return resp_or_exc

        g.requests.get = fake_get
        try:
            return g.has_write_access("o", "r", "u", {})
        finally:
            g.requests.get = saved

    def test_write_and_admin_are_yes(self):
        for perm in ("admin", "write", "maintain"):
            self.assertTrue(self._answer(WriteAccessFailsClosed._Resp(200, {"permission": perm})), perm)

    def test_read_and_none_are_no(self):
        for perm in ("read", "none", "triage", ""):
            self.assertFalse(self._answer(WriteAccessFailsClosed._Resp(200, {"permission": perm})), perm)

    def test_http_error_is_no(self):
        for code in (403, 404, 500):
            self.assertFalse(self._answer(WriteAccessFailsClosed._Resp(code, {"permission": "admin"})), code)

    def test_non_json_is_no(self):
        self.assertFalse(self._answer(WriteAccessFailsClosed._Resp(200, bad_json=True)))

    def test_transport_error_is_no(self):
        self.assertFalse(self._answer(g.requests.RequestException("boom")))



if __name__ == "__main__":
    unittest.main()
