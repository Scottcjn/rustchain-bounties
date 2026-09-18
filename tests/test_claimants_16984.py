# SPDX-License-Identifier: MIT
"""Verification suite for issue #16984 canonical wallet registration and claim requirements."""

import importlib.util
import os
import re
import subprocess
import unittest
from pathlib import Path

WALLET_RE = re.compile(r"^RTC[0-9a-fA-F]{40}$")
REPO_ROOT = Path(__file__).resolve().parent.parent
CLAIMANTS_FILE = REPO_ROOT / "docs" / "CLAIMANTS.md"
TARGET_HANDLE = "Blackcode-cmd"
TARGET_WALLET = "RTCaefa6fef8bd9b1447320d96f997eb972ccac4863"
SUBMITTED_REPOS = [
    "Scottcjn/Rustchain",
    "Scottcjn/bottube",
    "Scottcjn/rustchain-bounties",
]
FLOWER_PROOF_URL = "https://github.com/Scottcjn/rustchain-bounties/pull/16982#issuecomment-5722881083"


def load_bounty_payout_module():
    """Dynamically load scripts/bounty_payout.py with isolated environment."""
    os.environ.setdefault("GITHUB_TOKEN", "dummy")
    os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
    os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
    os.environ.setdefault("GH_REPO", "owner/repo")
    os.environ.setdefault("RATE_RTC", "3")
    os.environ.setdefault("MAX_PER_RUN", "40")
    script_path = REPO_ROOT / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout", script_path)
    module = importlib.util.module_from_spec(spec)

    orig_run = subprocess.run

    def stub_run(*args, **kwargs):
        class Result:
            stdout = "[]"
            stderr = ""
            returncode = 0
        return Result()

    subprocess.run = stub_run
    try:
        spec.loader.exec_module(module)
    finally:
        subprocess.run = orig_run
    return module


def load_verify_bounties_module():
    """Dynamically load scripts/verify_bounties.py with mock environment variables."""
    os.environ.setdefault("GH_TOKEN", "dummy")
    os.environ.setdefault("GH_REPO", "owner/repo")
    script_path = REPO_ROOT / "scripts" / "verify_bounties.py"
    spec = importlib.util.spec_from_file_location("verify_bounties", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestClaimantRegistration16984(unittest.TestCase):
    """Test suite verifying claimant wallet registration and bounty validity for issue #16984."""

    def test_canonical_file_presence_and_format(self):
        """Verify docs/CLAIMANTS.md exists and contains the registered row for Blackcode-cmd."""
        self.assertTrue(CLAIMANTS_FILE.is_file())
        content = CLAIMANTS_FILE.read_text(encoding="utf-8")
        expected_row = f"| {TARGET_HANDLE} | {TARGET_WALLET} |"
        self.assertIn(expected_row, content)

    def test_wallet_format_specification(self):
        """Verify the payout wallet matches the canonical RTC 40-hex character pattern."""
        self.assertTrue(bool(WALLET_RE.match(TARGET_WALLET)))
        self.assertEqual(len(TARGET_WALLET), 43)

    def test_bounty_payout_resolver_canonical_priority(self):
        """Verify scripts/bounty_payout.py parses the registration and prioritizes canonical wallet."""
        bp = load_bounty_payout_module()
        canonical_wallets = bp._load_canonical_wallets()
        self.assertIn(TARGET_HANDLE.lower(), canonical_wallets)
        self.assertEqual(canonical_wallets[TARGET_HANDLE.lower()], TARGET_WALLET)

        issue_body = (
            "Claiming #9017.\n"
            f"GitHub: @{TARGET_HANDLE}\n"
            f"RTC wallet: {TARGET_WALLET}\n"
        )
        resolved_wallet, source = bp.resolve_wallet(issue_body, [], claimant_login=TARGET_HANDLE)
        self.assertEqual(resolved_wallet, TARGET_WALLET)
        self.assertEqual(source, "canonical")

    def test_may_flowers_star_pack_repo_eligibility(self):
        """Verify the repositories starred by Blackcode-cmd are valid tracked repositories."""
        vb = load_verify_bounties_module()
        tracked_normalized = {r.lower() for r in vb.STAR_REPOS}
        self.assertGreaterEqual(len(SUBMITTED_REPOS), 3)
        for repo_full in SUBMITTED_REPOS:
            owner, repo_name = repo_full.split("/")
            self.assertEqual(owner, "Scottcjn")
            self.assertIn(repo_name.lower(), tracked_normalized)

    def test_flower_proof_reference_structure(self):
        """Verify the proof comment link matches the repository PR comment format."""
        proof_pattern = re.compile(
            r"^https://github\.com/Scottcjn/rustchain-bounties/pull/\d+#issuecomment-\d+$"
        )
        self.assertTrue(bool(proof_pattern.match(FLOWER_PROOF_URL)))


if __name__ == "__main__":
    unittest.main()
