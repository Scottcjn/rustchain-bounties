#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regressions for the payout authorization defects reported under bounty #16471.

Reported by @AInoAKARI on 2026-08-12, all confirmed against main and all of the
same family: **a public issue comment was being treated as an authorization.**
Anyone with a GitHub account can write a comment on a public repo, so a comment
can never authorize money movement on its own.

  1. Any commenter could write "Verified eligible" and be paid.
  2. Any non-bot commenter could post `Wallet: <handle>` on somebody ELSE's
     claim and silently redirect that payout to themselves.
  3. Any commenter could append a larger `rtc-payout-amount` marker and be paid
     it — which also bypassed the gate's per-claim ceiling, since the ceiling is
     enforced before the extra comment exists.
  4. `gh()` ignored the process return code, so a CLI/auth/rate-limit failure
     became an empty result. In the payout that meant zero candidates and a
     green run that paid nobody; in the docstring gate it meant "0 RTC earned
     this week" and a financial cap that failed OPEN.
"""
import importlib.util
import json
import os
import subprocess
import unittest
from pathlib import Path

os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")

ROOT = Path(__file__).resolve().parent.parent
_orig_run = subprocess.run


def _load(name):
    def stub(*a, **k):
        class R:
            stdout = "[]"
            stderr = ""
            returncode = 0
        return R()
    subprocess.run = stub
    try:
        spec = importlib.util.spec_from_file_location(f"{name}_auth_test", ROOT / "scripts" / f"{name}.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        subprocess.run = _orig_run


bp = _load("bounty_payout")
dg = _load("docstring_gate")


class TrustedIdentityTests(unittest.TestCase):
    def test_maintainers_and_bot_are_trusted(self):
        for who in ("Scottcjn", "sophiaeagent-beep", "github-actions[bot]"):
            self.assertTrue(bp._is_trusted(who), who)

    def test_ordinary_contributors_are_not(self):
        for who in ("attacker", "leanworld7-netizen", "AInoAKARI", "", None):
            self.assertFalse(bp._is_trusted(who), repr(who))

    def test_lookalike_is_not_trusted(self):
        self.assertFalse(bp._is_trusted("scottcjn-fan"))
        self.assertFalse(bp._is_trusted("not-scottcjn"))


class WalletRedirectionTests(unittest.TestCase):
    """Defect 2: a third party could name the payout destination."""

    NATIVE = "RTC" + "b" * 40

    def _comment(self, author, body):
        return {"author": {"login": author}, "body": body}

    def test_stranger_cannot_redirect_payout(self):
        comments = [self._comment("attacker", "Wallet: attacker-handle")]
        w, src = bp.resolve_wallet("no wallet in body", comments, claimant_login="victim")
        self.assertNotEqual(w, "attacker-handle",
                            "a third party must not be able to name the destination")
        self.assertEqual(w, "victim")

    def test_claimant_may_name_their_own_wallet(self):
        comments = [self._comment("victim", "Wallet: victim-payout")]
        w, src = bp.resolve_wallet("no wallet in body", comments, claimant_login="victim")
        self.assertEqual(w, "victim-payout")

    def test_maintainer_may_set_it_for_them(self):
        comments = [self._comment("Scottcjn", "Wallet: corrected-handle")]
        w, src = bp.resolve_wallet("no wallet in body", comments, claimant_login="victim")
        self.assertEqual(w, "corrected-handle")

    def test_stranger_cannot_override_a_later_claimant_comment(self):
        comments = [self._comment("victim", "Wallet: victim-payout"),
                    self._comment("attacker", "Wallet: attacker-handle")]
        w, _ = bp.resolve_wallet("", comments, claimant_login="victim")
        self.assertEqual(w, "victim-payout")

    def test_native_wallet_in_body_still_wins(self):
        w, src = bp.resolve_wallet(f"pay {self.NATIVE}",
                                   [self._comment("attacker", "Wallet: attacker-handle")],
                                   claimant_login="victim")
        self.assertEqual(w, self.NATIVE)
        self.assertEqual(src, "native")


class GhFailureTests(unittest.TestCase):
    """Defect 4: a failed CLI call must not read as an empty result."""

    def tearDown(self):
        subprocess.run = _orig_run

    def _fail(self):
        class R:
            stdout = ""
            stderr = "gh: API rate limit exceeded"
            returncode = 1
        subprocess.run = lambda *a, **k: R()

    def test_payout_gh_raises_on_nonzero(self):
        self._fail()
        with self.assertRaises(bp.GhError):
            bp.gh(["issue", "list"])

    def test_gate_gh_strict_raises(self):
        self._fail()
        with self.assertRaises(dg.GhError):
            dg.gh(["api", "x"], {}, strict=True)

    def test_gate_gh_non_strict_still_defaults(self):
        """Non-money lookups may still degrade rather than crash the run."""
        self._fail()
        self.assertEqual(dg.gh(["api", "x"], {"fallback": 1}), {"fallback": 1})

    def test_weekly_cap_fails_closed_not_open(self):
        """The reported defect: a failed lookup reported 0 RTC earned."""
        self._fail()
        with self.assertRaises(dg.GhError):
            dg.docstring_rtc_this_week("someone-over-the-cap")


if __name__ == "__main__":
    unittest.main()
