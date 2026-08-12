#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Static regression guard for confirm-pending's delivery postcondition."""
from pathlib import Path
import unittest


WORKFLOW = (Path(__file__).resolve().parents[1] /
            ".github/workflows/confirm-pending.yml")


class ConfirmPendingWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text()

    def test_application_refusal_fails(self):
        self.assertIn("if d.get('ok') is not True:", self.text)

    def test_counts_are_required_integers(self):
        self.assertIn('invalid confirmed_count', self.text)
        self.assertIn('invalid stale_pending_count', self.text)

    def test_stale_backlog_after_loop_fails(self):
        self.assertIn('if [ "${stale:-0}" -gt 0 ]; then', self.text)
        self.assertIn('stale transfer(s) undelivered', self.text)
        self.assertIn('exit 1', self.text)


if __name__ == "__main__":
    unittest.main()
