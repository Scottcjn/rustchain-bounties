# SPDX-License-Identifier: MIT
"""Verification suite for issue #16986 canonical wallet registration and claim verification."""

import base64
import hashlib
import importlib.util
import os
import re
import subprocess
import unittest
from pathlib import Path

WALLET_RE = re.compile(r"^RTC[0-9a-fA-F]{40}$")
REPO_ROOT = Path(__file__).resolve().parent.parent
CLAIMANTS_FILE = REPO_ROOT / "docs" / "CLAIMANTS.md"
TARGET_HANDLE = "rushikeshgarad2024-dev"
STELLAR_ADDRESS = "GC5U46IS25KYFKNHDXEHR3KTQB3DVIBM4NW5BH4MVUE2G77STCJP4IHF"
EXPECTED_ED25519_PUBKEY = "bb4e7912d75582a9a71dc878ed5380763aa02ce36dd09f8cad09a37ff29892fe"
EXPECTED_RTC_WALLET = "RTCa6c9cd13d0cced53b86f7adbd3efd06c81032fe9"
SUBMITTED_REPOS = [
    "Scottcjn/Rustchain",
    "Scottcjn/rustchain-bounties",
    "Scottcjn/bottube",
]
FLOWER_PROOF_URL = "https://github.com/Scottcjn/rustchain-bounties/issues/9017#issuecomment-5730184582"


def compute_crc16_xmodem(data: bytes) -> int:
    """Calculate CRC16-XModem checksum according to SEP-0023."""
    crc = 0x0000
    for byte in data:
        code = (crc >> 8) & 0xFF
        code ^= byte
        code ^= code >> 4
        crc = (crc << 8) & 0xFFFF
        crc ^= code
        code = (code << 5) & 0xFFFF
        crc ^= code
        code = (code << 7) & 0xFFFF
        crc ^= code
    return crc


def parse_canonical_table(filepath: Path) -> dict:
    """Parse a markdown claimants table into a handle-to-wallet mapping."""
    out = {}
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            if "|" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            handle, wallet = cells[0], cells[1]
            m = WALLET_RE.search(wallet)
            if handle and m and not handle.lower().startswith(("github handle", "---")):
                out[handle.lower()] = m.group(0)
    return out


def load_bounty_payout_module():
    """Dynamically load scripts/bounty_payout.py with isolated environment."""
    os.environ.setdefault("GITHUB_TOKEN", "dummy")
    os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
    os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
    os.environ.setdefault("GH_REPO", "owner/repo")
    os.environ.setdefault("RATE_RTC", "3")
    os.environ.setdefault("MAX_PER_RUN", "40")
    script_path = REPO_ROOT / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout_test_16986", script_path)
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
    """Dynamically load scripts/verify_bounties.py with isolated environment."""
    os.environ.setdefault("GITHUB_TOKEN", "dummy")
    os.environ.setdefault("GH_TOKEN", "dummy")
    os.environ.setdefault("GH_REPO", "owner/repo")
    script_path = REPO_ROOT / "scripts" / "verify_bounties.py"
    spec = importlib.util.spec_from_file_location("verify_bounties_test_16986", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestClaimantRegistration16986(unittest.TestCase):
    """Test suite verifying claimant wallet registration and bounty validity for issue #16986."""

    def test_stellar_strkey_derivation_to_rtc(self):
        """Verify cryptographic derivation from Stellar StrKey to native RTC address."""
        raw_bytes = base64.b32decode(STELLAR_ADDRESS)
        self.assertEqual(len(raw_bytes), 35)

        version_byte = raw_bytes[0]
        self.assertEqual(version_byte, 0x30)

        pubkey = raw_bytes[1:33]
        self.assertEqual(pubkey.hex(), EXPECTED_ED25519_PUBKEY)

        payload = raw_bytes[:-2]
        expected_crc = int.from_bytes(raw_bytes[-2:], "little")
        calculated_crc = compute_crc16_xmodem(payload)
        self.assertEqual(expected_crc, calculated_crc)

        digest = hashlib.sha256(pubkey).hexdigest()
        derived_wallet = f"RTC{digest[:40]}"
        self.assertEqual(derived_wallet, EXPECTED_RTC_WALLET)
        self.assertTrue(bool(WALLET_RE.fullmatch(derived_wallet)))

    def test_canonical_file_presence_and_format(self):
        """Verify docs/CLAIMANTS.md exists and contains the registered row for rushikeshgarad2024-dev."""
        self.assertTrue(CLAIMANTS_FILE.is_file())
        content = CLAIMANTS_FILE.read_text(encoding="utf-8")
        expected_row = f"| {TARGET_HANDLE} | {EXPECTED_RTC_WALLET} |"
        self.assertIn(expected_row, content)

    def test_wallet_format_specification(self):
        """Verify the payout wallet matches the canonical RTC 40-hex character pattern."""
        self.assertTrue(bool(WALLET_RE.match(EXPECTED_RTC_WALLET)))
        self.assertEqual(len(EXPECTED_RTC_WALLET), 43)

    def test_bounty_payout_resolver_canonical_priority(self):
        """Verify scripts/bounty_payout.py parses the registration and prioritizes canonical wallet."""
        bp = load_bounty_payout_module()
        canonical_wallets = bp._load_canonical_wallets()
        self.assertIn(TARGET_HANDLE.lower(), canonical_wallets)
        self.assertEqual(canonical_wallets[TARGET_HANDLE.lower()], EXPECTED_RTC_WALLET)

        issue_body = (
            "Claiming #9017.\n"
            f"GitHub: @{TARGET_HANDLE}\n"
            f"RTC wallet: {EXPECTED_RTC_WALLET}\n"
        )
        resolved_wallet, source = bp.resolve_wallet(issue_body, [], claimant_login=TARGET_HANDLE)
        self.assertEqual(resolved_wallet, EXPECTED_RTC_WALLET)
        self.assertEqual(source, "canonical")

    def test_may_flowers_star_pack_repo_eligibility(self):
        """Verify the repositories starred by claimant are valid tracked repositories."""
        vb = load_verify_bounties_module()
        tracked_normalized = {r.lower() for r in vb.STAR_REPOS}
        self.assertGreaterEqual(len(SUBMITTED_REPOS), 3)
        for repo_full in SUBMITTED_REPOS:
            owner, repo_name = repo_full.split("/")
            self.assertEqual(owner, "Scottcjn")
            self.assertIn(repo_name.lower(), tracked_normalized)
        self.assertIn(9017, vb.STAR_BOUNTY_ISSUES)

    def test_flower_proof_reference_structure(self):
        """Verify the proof comment link matches the repository issue comment format."""
        proof_pattern = re.compile(
            r"^https://github\.com/Scottcjn/rustchain-bounties/issues/\d+#issuecomment-\d+$"
        )
        self.assertTrue(bool(proof_pattern.match(FLOWER_PROOF_URL)))


if __name__ == "__main__":
    unittest.main()
