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
  - certificate and hostname verification remain enabled
  - the admin-authenticated request is HTTPS-only with no plaintext fallback
  - a transport exception fails closed after one request
  - a non-dict body (e.g. an HTML error page) is not treated as success
"""
import importlib.util
import io
import json
import os
import ssl
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

    def test_declining_server_is_not_retried(self):
        """A server that processed and refused must not be re-posted to."""
        self._install([
            lambda u: {"ok": False, "error": "rejected"},
            lambda u: {"ok": True},  # must never be reached
        ])
        ok, _ = bp.transfer("alice", "memo", "idem-3")
        self.assertFalse(ok)
        self.assertEqual(len(self.calls), 1, "fallback endpoint must not be tried")

    def test_raising_endpoint_fails_closed_without_plaintext_fallback(self):
        def boom(_u):
            raise OSError("connection refused")

        self._install([boom])
        ok, resp = bp.transfer("alice", "memo", "idem-5")
        self.assertFalse(ok)
        self.assertIn("connection refused", resp)
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(self.calls[0].startswith("https://"))
        self.assertNotIn(":8099/", self.calls[0])

    def test_non_dict_body_is_not_success(self):
        """An HTML error page must not read as a completed payment."""
        self._install([lambda u: "<html>502 Bad Gateway</html>"])
        ok, resp = bp.transfer("alice", "memo", "idem-6")
        self.assertFalse(ok)
        self.assertIn("server_declined", resp)


class VerifiedTransportTests(unittest.TestCase):
    class _Response(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    def test_post_keeps_default_certificate_and_hostname_verification(self):
        captured = {}

        def fake_urlopen(request, *, timeout, context):
            captured.update(request=request, timeout=timeout, context=context)
            return self._Response(json.dumps({"ok": True}).encode())

        with mock.patch.object(bp.urllib.request, "urlopen", side_effect=fake_urlopen):
            response = bp._post("https://node.example/wallet/transfer", b"{}")

        self.assertEqual(response, {"ok": True})
        self.assertTrue(captured["context"].check_hostname)
        self.assertEqual(captured["context"].verify_mode, ssl.CERT_REQUIRED)
        self.assertEqual(captured["request"].full_url,
                         "https://node.example/wallet/transfer")
        self.assertEqual(captured["request"].get_header("X-admin-key"), "dummy")


class EndpointCompatibilityTests(unittest.TestCase):
    def test_legacy_production_ip_uses_certificate_hostname(self):
        self.assertEqual(
            bp._certificate_host("50.28.86.131"),
            "bulbous-bouffant.metalseed.net",
        )

    def test_custom_hostname_is_preserved(self):
        self.assertEqual(
            bp._certificate_host("node.internal.example"),
            "node.internal.example",
        )

    def test_ip_prefix_is_not_broadly_rewritten(self):
        self.assertEqual(
            bp._certificate_host("50.28.86.131.attacker.example"),
            "50.28.86.131.attacker.example",
        )


if __name__ == "__main__":
    unittest.main()
