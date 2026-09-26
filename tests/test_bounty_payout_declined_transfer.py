#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Regression tests for issue #16390 in scripts/bounty_payout.py.

The bug: transfer() returned True whenever the HTTP POST did not raise. A
transport-level success carrying an application-level refusal (HTTP 200 with
`{"ok": false}`) was therefore treated as PAID, so the claim was closed and
publicly confirmed with no RTC actually sent.

Validates:
  - `{"ok": true}`   -> (True, response)
  - `{"ok": false}`  -> (False, "server_declined:...")
  - a declining server is NOT retried against the fallback endpoint
    (re-posting a request the server already processed risks a double debit)
  - a raising endpoint falls through to the plaintext fallback ONLY when
    RUSTCHAIN_PAYOUT_INSECURE=1; by default the admin key never leaves HTTPS
  - both endpoints raising -> (False, last error)
  - a non-dict body (e.g. an HTML error page) is not treated as success
"""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

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
    spec = importlib.util.spec_from_file_location("bounty_payout_declined_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run


class TransferResultTests(unittest.TestCase):
    def setUp(self):
        self._orig_post = bp._post
        self.calls = []

    def tearDown(self):
        bp._post = self._orig_post

    def _install(self, behaviours):
        """behaviours: list of callables applied per successive _post call."""
        seq = iter(behaviours)

        def fake_post(url, body):
            self.calls.append(url)
            return next(seq)(url)

        bp._post = fake_post

    def test_ok_true_is_success(self):
        self._install([lambda u: {"ok": True, "tx_hash": "abc", "phase": "pending"}])
        ok, resp = bp.transfer("alice", "memo", "idem-1")
        self.assertTrue(ok)
        self.assertEqual(resp["tx_hash"], "abc")
        self.assertEqual(len(self.calls), 1)

    def test_ok_false_is_failure(self):
        """The #16390 case: HTTP 200 carrying an application-level refusal."""
        self._install([lambda u: {"ok": False, "error": "Insufficient balance"}])
        ok, resp = bp.transfer("alice", "memo", "idem-2")
        self.assertFalse(ok)
        self.assertIn("server_declined", resp)
        self.assertIn("Insufficient balance", resp)

    def test_declining_server_is_not_retried_on_fallback(self):
        """A server that processed and refused must not be re-posted to."""
        self._install([
            lambda u: {"ok": False, "error": "rejected"},
            lambda u: {"ok": True},  # must never be reached
        ])
        ok, _ = bp.transfer("alice", "memo", "idem-3")
        self.assertFalse(ok)
        self.assertEqual(len(self.calls), 1, "fallback endpoint must not be tried")

    def test_raising_endpoint_falls_through_to_fallback_when_opted_in(self):
        def boom(_u):
            raise OSError("connection refused")

        self._install([boom, lambda u: {"ok": True, "tx_hash": "z"}])
        with mock.patch.dict(os.environ, {"RUSTCHAIN_PAYOUT_INSECURE": "1"}):
            ok, resp = bp.transfer("alice", "memo", "idem-4")
        self.assertTrue(ok)
        self.assertEqual(resp["tx_hash"], "z")
        self.assertEqual(len(self.calls), 2)

    def test_https_failure_never_downgrades_to_plaintext_by_default(self):
        """The admin key must not be re-sent over http:// just because 443 failed."""
        def boom(_u):
            raise OSError("connection reset")

        self._install([boom, lambda u: {"ok": True}])
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RUSTCHAIN_PAYOUT_INSECURE", None)
            ok, resp = bp.transfer("alice", "memo", "idem-7")
        self.assertFalse(ok)
        self.assertIn("connection reset", resp)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(all(u.startswith("https://") for u in self.calls), self.calls)

    def test_all_endpoints_raise_is_failure(self):
        def boom(_u):
            raise OSError("403 Forbidden")

        self._install([boom, boom])
        ok, resp = bp.transfer("alice", "memo", "idem-5")
        self.assertFalse(ok)
        self.assertIn("403", resp)

    def test_non_dict_body_is_not_success(self):
        """An HTML error page must not read as a completed payment."""
        self._install([lambda u: "<html>502 Bad Gateway</html>"])
        ok, resp = bp.transfer("alice", "memo", "idem-6")
        self.assertFalse(ok)
        self.assertIn("server_declined", resp)


if __name__ == "__main__":
    unittest.main()
