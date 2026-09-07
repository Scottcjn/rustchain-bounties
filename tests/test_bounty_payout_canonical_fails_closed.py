#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The canonical wallet registry must fail CLOSED when it can't be read.

`_load_canonical_wallets()` used to catch every non-FileNotFoundError, print a
warning, and return a partial/empty map. `resolve_wallet()` then fell through to
an older native wallet or bare handle -- so a transient read/parse failure on
docs/CLAIMANTS.md could pay a REGISTERED contributor to the WRONG destination
while the run reported success, violating the "canonical registry ALWAYS wins"
invariant. Reported by @Nish916 under #16471.

Fail-closed contract pinned here:
  - file genuinely ABSENT  -> {} (no registry; per-claim resolution is fine)
  - file PRESENT but unreadable/unparseable -> raise CanonicalRegistryError
    (abort before any transfer)
"""
import importlib.util
import io
import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")
os.environ.setdefault("RATE_RTC", "3")
os.environ.setdefault("MAX_PER_RUN", "40")

_orig_run = subprocess.run


def _stub_run(*a, **kw):
    class _R:
        stdout = "[]"
        stderr = ""
        returncode = 0
    return _R()


subprocess.run = _stub_run
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
    SCRIPT = REPO_ROOT / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout_canon_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run


NATIVE_WALLET = "RTC" + "0" * 40


def _fake_open_ok(*a, **k):
    return io.StringIO(
        "| GitHub Handle | Native RTC Wallet |\n"
        "|---|---|\n"
        f"| alice | {NATIVE_WALLET} |\n"
    )


class CanonicalRegistryFailClosedTests(unittest.TestCase):
    def test_existing_but_unreadable_raises(self):
        """An OS/read error on an existing file must abort, not return {}."""
        with patch("builtins.open", side_effect=OSError("disk error")):
            with self.assertRaises(bp.CanonicalRegistryError):
                bp._load_canonical_wallets()

    def test_unicode_error_raises(self):
        """A decode error (corrupt/garbled file) must abort, not return {}."""
        err = UnicodeDecodeError("utf-8", b"", 0, 1, "bad byte")
        with patch("builtins.open", side_effect=err):
            with self.assertRaises(bp.CanonicalRegistryError):
                bp._load_canonical_wallets()

    def test_missing_file_returns_empty(self):
        """A genuinely absent registry is fine -> {} (per-claim resolution)."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            self.assertEqual(bp._load_canonical_wallets(), {})

    def test_valid_file_parses(self):
        """The normal path still maps a registered handle to its wallet."""
        with patch("builtins.open", _fake_open_ok):
            out = bp._load_canonical_wallets()
        self.assertEqual(out.get("alice"), NATIVE_WALLET)


if __name__ == "__main__":
    unittest.main()
