#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Regression tests for issue #16660 in scripts/bounty_payout.py.

`_list()` used to catch `json.JSONDecodeError` and return `[]`. A `gh`
invocation that exited 0 but emitted malformed/truncated JSON therefore
became an authoritative empty candidate set: the payout run printed
"0 candidate issues ... 0 paid" and exited green while every eligible
payout was silently skipped.

Validates:
  - malformed JSON from a SUCCESSFUL gh call raises GhError (fail closed)
  - empty stdout still means an empty set (gh succeeded with no output)
  - valid JSON is returned unchanged
  - the candidate-enumeration sequence (label pass + recent sweep) cannot
    produce a green zero-candidate run when CLI output is malformed
"""
import importlib.util
import os
import subprocess
import unittest
from pathlib import Path

# Set dummy env vars BEFORE importing the module so its module-level
# os.environ reads succeed (we never call transfer() in these tests).
os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")
os.environ.setdefault("RATE_RTC", "3")
os.environ.setdefault("MAX_PER_RUN", "40")

# Pre-stub subprocess so the module-level _list() calls do nothing when no gh
# CLI is available in the test environment (same pattern as the sibling tests).
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
    spec = importlib.util.spec_from_file_location("bounty_payout_list_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run


class ListFailClosedTests(unittest.TestCase):
    def _with_gh(self, stdout, fn):
        """Run fn() with bp.gh stubbed to return `stdout` (exit 0)."""
        orig = bp.gh
        bp.gh = lambda args, _check=True: stdout
        try:
            return fn()
        finally:
            bp.gh = orig

    def test_malformed_json_raises(self):
        # The issue reproduction: exit code 0, stdout "{"
        with self.assertRaises(bp.GhError):
            self._with_gh("{", lambda: bp._list(["--limit", "400"]))

    def test_truncated_json_raises(self):
        with self.assertRaises(bp.GhError):
            self._with_gh('[{"number": 1, "title": "x"', 
                          lambda: bp._list(["--limit", "400"]))

    def test_error_message_includes_diagnostic(self):
        try:
            self._with_gh("{", lambda: bp._list(["--limit", "400"]))
        except bp.GhError as e:
            self.assertIn("malformed JSON", str(e))
            self.assertIn("{", str(e))
        else:
            self.fail("GhError not raised")

    def test_empty_stdout_is_empty_set(self):
        # gh succeeded and printed nothing: a genuine empty set is valid.
        out = self._with_gh("", lambda: bp._list(["--limit", "400"]))
        self.assertEqual(out, [])

    def test_valid_json_returned_unchanged(self):
        payload = [{"number": 1, "title": "claim", "labels": []}]
        out = self._with_gh(
            '[{"number": 1, "title": "claim", "labels": []}]',
            lambda: bp._list(["--limit", "400"]))
        self.assertEqual(out, payload)

    def test_candidate_enumeration_cannot_be_green_on_malformed_output(self):
        # Mirrors the runner: label pass + recent sweep. Either pass hitting
        # malformed successful output must raise, not yield 0 candidates.
        def run():
            issues = bp._list(["--label", "bounty-eligible", "--limit", "1000"])
            seen = {i["number"] for i in issues}
            issues += [i for i in bp._list(["--limit", "400"])
                       if i["number"] not in seen]
            return issues

        with self.assertRaises(bp.GhError):
            self._with_gh("{", run)


if __name__ == "__main__":
    unittest.main()
