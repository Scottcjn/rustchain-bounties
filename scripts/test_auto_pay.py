#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for the auto-pay sensitive-path guard.

Run: python3 scripts/test_auto_pay.py   (or `pytest scripts/test_auto_pay.py`)

Focus: `is_sensitive_path` must reject consensus / money / CI paths
*case-insensitively*. A case-sensitive `startswith` let a PR touch those
paths under a re-cased prefix (e.g. `Scripts/`, `.GitHub/`) and still slip
into the conservative auto-tier — an automatic RTC award the guard exists
to deny. These tests pin the bypass shut.
"""

import importlib.util
import os
import unittest

# The module file name contains a hyphen, so load it by path.
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "auto_pay", os.path.join(_HERE, "auto-pay.py")
)
auto_pay = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(auto_pay)


class SensitivePathGuard(unittest.TestCase):
    def test_lowercase_sensitive_paths_flagged(self):
        for p in (
            "node/consensus.py",
            "rips/rip-300.md",
            "scripts/auto-pay.py",
            ".github/workflows/pay.yml",
            "BOUNTY_LEDGER.md",
        ):
            self.assertTrue(
                auto_pay.is_sensitive_path(p), f"{p} should be sensitive"
            )

    def test_recased_sensitive_paths_still_flagged(self):
        # The bypass vectors from the report — each maps to a sensitive file
        # on a case-insensitive checkout, so the guard must catch them too.
        for p in (
            "Scripts/auto-pay.py",
            "SCRIPTS/auto-pay.py",
            "Node/consensus.py",
            "NODE/consensus.py",
            "Rips/rip-300.md",
            ".GitHub/workflows/pay.yml",
            ".GITHUB/workflows/pay.yml",
            "BOUNTY_LEDGER.MD",
            "Bounty_Ledger.md",
        ):
            self.assertTrue(
                auto_pay.is_sensitive_path(p),
                f"{p} re-cased must still be sensitive",
            )

    def test_non_sensitive_paths_not_flagged(self):
        for p in (
            "README.md",
            "docs/guide.md",
            "bounties/0123-foo.json",
            "src/app.py",
            "nodes_overview.md",       # 'node' substring but not the 'node/' dir
            "scripts_notes.txt",        # 'scripts' substring but not 'scripts/'
        ):
            self.assertFalse(
                auto_pay.is_sensitive_path(p),
                f"{p} should NOT be sensitive",
            )

    def test_prefixes_lc_matches_source_tuple(self):
        self.assertEqual(
            auto_pay.SENSITIVE_PREFIXES_LC,
            tuple(p.lower() for p in auto_pay.SENSITIVE_PREFIXES),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
