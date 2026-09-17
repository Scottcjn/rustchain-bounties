# SPDX-License-Identifier: MIT
"""Verification suite for issue #16973 canonical wallet registration."""

import base64
import hashlib
import os
import re
import unittest
from pathlib import Path

WALLET_RE = re.compile(r"\bRTC[0-9a-fA-F]{40}\b")
REPO_ROOT = Path(__file__).resolve().parent.parent
CLAIMANTS_FILE = REPO_ROOT / "docs" / "CLAIMANTS.md"
TARGET_HANDLE = "rushikeshgarad2024-dev"
STELLAR_ADDRESS = "GC5U46IS25KYFKNHDXEHR3KTQB3DVIBM4NW5BH4MVUE2G77STCJP4IHF"
EXPECTED_ED25519_PUBKEY = "bb4e7912d75582a9a71dc878ed5380763aa02ce36dd09f8cad09a37ff29892fe"
EXPECTED_RTC_WALLET = "RTCa6c9cd13d0cced53b86f7adbd3efd06c81032fe9"


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


class TestClaimantRegistration16973(unittest.TestCase):
    """Test suite verifying contributor registration for issue #16973."""

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

    def test_claimants_file_contains_registered_entry(self):
        """Verify docs/CLAIMANTS.md contains target contributor entry."""
        self.assertTrue(CLAIMANTS_FILE.is_file())
        mapping = parse_canonical_table(CLAIMANTS_FILE)
        self.assertIn(TARGET_HANDLE.lower(), mapping)
        self.assertEqual(mapping[TARGET_HANDLE.lower()], EXPECTED_RTC_WALLET)


if __name__ == "__main__":
    unittest.main()
