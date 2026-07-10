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
from unittest.mock import MagicMock, patch

import requests

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


class TransferRetry(unittest.TestCase):
    """Regression tests for the transient-failure retry added to
    transfer_rtc() (issue: a brief VPS restart caused
    requests.exceptions.ConnectionError to crash the whole job with no
    retry, spamming CI failure notifications for what was really a few
    seconds of downtime).

    Retrying must stay fail-safe: no more than one HTTP call may ever
    "succeed" per invocation (checked via call_count), and a genuine HTTP
    error response (a real answer from the node, e.g. insufficient
    balance) must NOT be retried — only dropped-connection / timeout
    cases are.
    """

    def _call(self, **overrides):
        kwargs = dict(
            vps_host="203.0.113.1",
            admin_key="k",
            to_wallet="alice",
            amount=3.0,
            memo="test",
            idempotency_key="idem-1",
            max_attempts=3,
            retry_delay=0,  # no real sleeping in tests
        )
        kwargs.update(overrides)
        return auto_pay.transfer_rtc(**kwargs)

    @patch("time.sleep", return_value=None)
    @patch("requests.post")
    def test_succeeds_after_transient_connection_errors(self, mock_post, _sleep):
        ok_resp = MagicMock()
        ok_resp.raise_for_status.return_value = None
        ok_resp.json.return_value = {"ok": True, "pending_id": "p1"}

        mock_post.side_effect = [
            requests.exceptions.ConnectionError("refused"),
            requests.exceptions.Timeout("timed out"),
            ok_resp,
        ]

        result = self._call()

        self.assertEqual(result, {"ok": True, "pending_id": "p1"})
        self.assertEqual(mock_post.call_count, 3)

    @patch("time.sleep", return_value=None)
    @patch("requests.post")
    def test_raises_after_exhausting_retries(self, mock_post, _sleep):
        mock_post.side_effect = requests.exceptions.ConnectionError("refused")

        with self.assertRaises(requests.exceptions.ConnectionError):
            self._call(max_attempts=3)

        # Exactly max_attempts calls — bounded, no runaway retry loop.
        self.assertEqual(mock_post.call_count, 3)

    @patch("time.sleep", return_value=None)
    @patch("requests.post")
    def test_http_error_is_not_retried(self, mock_post, _sleep):
        bad_resp = MagicMock()
        bad_resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error", response=MagicMock(status_code=400, text="bad")
        )
        mock_post.return_value = bad_resp

        with self.assertRaises(requests.exceptions.HTTPError):
            self._call(max_attempts=3)

        # A real rejection from the node is surfaced immediately — retrying
        # a 4xx/5xx response wouldn't change the answer.
        self.assertEqual(mock_post.call_count, 1)

    @patch("time.sleep", return_value=None)
    @patch("requests.post")
    def test_single_attempt_never_double_calls(self, mock_post, _sleep):
        """Baseline: the common case (VPS reachable) makes exactly one
        HTTP call — the retry loop must not add extra calls on success."""
        ok_resp = MagicMock()
        ok_resp.raise_for_status.return_value = None
        ok_resp.json.return_value = {"ok": True}
        mock_post.return_value = ok_resp

        self._call()

        self.assertEqual(mock_post.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
