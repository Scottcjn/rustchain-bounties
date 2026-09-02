#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression for audit bounty #16471: corrupt CLAIMANTS.md must fail closed."""
import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")

ROOT = Path(__file__).resolve().parent.parent
_orig_run = subprocess.run


def _load_bp():
    def stub(*a, **k):
        class R:
            stdout = "[]"
            stderr = ""
            returncode = 0
        return R()

    subprocess.run = stub
    try:
        spec = importlib.util.spec_from_file_location(
            "bounty_payout_canonical_test", ROOT / "scripts" / "bounty_payout.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        subprocess.run = _orig_run


bp = _load_bp()


class CanonicalWalletLoadTests(unittest.TestCase):
    def test_missing_claimants_file_returns_empty(self):
        with mock.patch("builtins.open", side_effect=FileNotFoundError):
            self.assertEqual(bp._load_canonical_wallets(), {})

    def test_corrupt_claimants_file_raises(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"\xff\xfe")
            path = f.name
        try:
            with mock.patch.object(bp.os.path, "join", return_value=path):
                with self.assertRaises(bp.CanonicalWalletError):
                    bp._load_canonical_wallets()
        finally:
            os.unlink(path)

    def test_valid_claimants_file_parses(self):
        wallets = bp._load_canonical_wallets()
        self.assertIsInstance(wallets, dict)
        if wallets:
            for handle, wallet in wallets.items():
                self.assertTrue(handle)
                self.assertRegex(wallet, r"^RTC[0-9a-fA-F]{40}$")


if __name__ == "__main__":
    unittest.main()
