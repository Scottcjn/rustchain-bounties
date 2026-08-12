#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for confirm-pending's delivery postcondition."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


WORKFLOW = (Path(__file__).resolve().parents[1] /
            ".github/workflows/confirm-pending.yml")


class ConfirmPendingWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()
        lines = cls.text.splitlines()
        start = lines.index("        run: |") + 1
        body = []
        for line in lines[start:]:
            if line and not line.startswith("          "):
                break
            body.append(line[10:] if line else "")
        cls.script = "\n".join(body) + "\n"

    def run_response(self, payload):
        fake_curl = """
curl() {
  printf '%s' "$RESPONSE_JSON" > resp.json
  printf '200'
}
"""
        env = os.environ.copy()
        env.update({
            "RTC_VPS_HOST": "node.invalid",
            "RTC_ADMIN_KEY": "test-key",
            "RESPONSE_JSON": json.dumps(payload),
        })
        with tempfile.TemporaryDirectory() as workdir:
            return subprocess.run(
                ["bash", "-c", fake_curl + self.script],
                cwd=workdir,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_application_refusal_fails(self):
        self.assertIn("if d.get('ok') is not True:", self.text)

    def test_counts_are_required_integers(self):
        self.assertIn('invalid confirmed_count', self.text)
        self.assertIn('invalid stale_pending_count', self.text)

    def test_stale_backlog_after_loop_fails(self):
        self.assertIn('if [ "${stale:-0}" -gt 0 ]; then', self.text)
        self.assertIn('stale transfer(s) undelivered', self.text)
        self.assertIn('exit 1', self.text)

    def test_drained_response_exits_successfully(self):
        result = self.run_response({
            "ok": True,
            "confirmed_count": 2,
            "stale_pending_count": 0,
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("queue drained", result.stdout)
        self.assertIn("confirmed 2 transfer(s) this run", result.stdout)

    def test_application_refusal_exits_nonzero(self):
        result = self.run_response({
            "ok": False,
            "error": "delivery unavailable",
            "confirmed_count": 0,
            "stale_pending_count": 7,
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("confirm refused: delivery unavailable", result.stderr)

    def test_stale_no_progress_response_exits_nonzero(self):
        result = self.run_response({
            "ok": True,
            "confirmed_count": 0,
            "stale_pending_count": 7,
            "errors": ["row 42 locked"],
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no progress this iter; stopping", result.stdout)
        self.assertIn("7 stale transfer(s) undelivered", result.stdout)
        self.assertIn("row 42 locked", result.stdout)


if __name__ == "__main__":
    unittest.main()
