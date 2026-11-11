#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression tests for #16471 silent-success audit findings in pr_review_gate.py & pr_review_gate_backfill.py."""

import importlib.util
import json
import pathlib
import subprocess
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "scripts" / "pr_review_gate.py"
BACKFILL_PATH = ROOT / "scripts" / "pr_review_gate_backfill.py"


def _load_module(name, path, env_overrides=None):
    with mock.patch.dict("os.environ", env_overrides or {}, clear=False):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


class PrReviewGateSilentSuccess16471Test(unittest.TestCase):
    def test_issue_lookup_failure_fails_closed_instead_of_exiting_zero(self):
        gate = _load_module(
            "pr_review_gate_16471_1",
            GATE_PATH,
            {"ISSUE_NUMBER": "16999", "BOUNTY_ISSUE": ""},
        )
        with mock.patch.object(gate, "api", side_effect=gate.ApiError("GET /repos/.../issues/16999 -> HTTP 403")):
            with self.assertRaises(gate.ApiError):
                gate.main()

    def test_gate_processed_label_not_applied_before_verdict_when_downstream_fails(self):
        gate = _load_module(
            "pr_review_gate_16471_2",
            GATE_PATH,
            {"ISSUE_NUMBER": "16999", "BOUNTY_ISSUE": ""},
        )
        applied_labels = []

        def fake_api(path, method="GET", data=None, strict=False):
            if path.endswith("/issues/16999") and method == "GET":
                return {
                    "state": "open",
                    "title": "Bounty #73 code review claim for PR #8000",
                    "body": "Wallet: RTC" + "a" * 40,
                    "user": {"login": "reviewer1"},
                    "labels": [],
                }
            if path.endswith("/labels") and method == "POST":
                applied_labels.extend(data.get("labels", []))
                return {}
            if "/pulls/8000/reviews" in path:
                raise RuntimeError("transient network drop before verdict")
            return {}

        with mock.patch.object(gate, "api", side_effect=fake_api):
            with self.assertRaises(RuntimeError):
                gate.main()

        self.assertNotIn(
            "gate-processed",
            applied_labels,
            "gate-processed must not be applied before a verdict is reached",
        )

    def test_backfill_rescues_open_claim_stranded_with_gate_processed_only(self):
        backfill = _load_module("pr_review_gate_backfill_16471", BACKFILL_PATH)
        gate = _load_module("pr_review_gate_classifier_16471", GATE_PATH, {"BOUNTY_ISSUE": ""})
        fake_issues = [
            {
                "number": 1001,
                "title": "Bounty #73 code review for PR #100",
                "labels": [{"name": "gate-processed"}],
            },
            {
                "number": 1002,
                "title": "Bounty #73 code review for PR #101",
                "labels": [],
            },
        ]
        fake_proc = subprocess.CompletedProcess(
            args=["gh"], returncode=0, stdout=json.dumps(fake_issues), stderr=""
        )
        with mock.patch.object(backfill.subprocess, "run", return_value=fake_proc):
            never, stranded = backfill.list_unprocessed(gate)

        self.assertEqual(never, [1002])
        self.assertEqual(stranded, [1001])

    def test_author_with_short_first_comment_and_long_second_review_is_not_rejected(self):
        gate = _load_module(
            "pr_review_gate_16471_4",
            GATE_PATH,
            {"ISSUE_NUMBER": "17000", "BOUNTY_ISSUE": ""},
        )
        long_review_body = (
            "Ref: `scripts/bounty_payout.py` L:450 — detailed substantive finding "
            "showing why native RTC addresses in comment threads must be matched before handle fallback."
        )
        applied_labels = []
        deleted_paths = []

        def fake_api(path, method="GET", data=None, strict=False):
            if path.endswith("/issues/17000") and method == "GET":
                return {
                    "state": "open",
                    "title": "Bounty #73 code review for PR #8001",
                    "body": "Wallet: RTC" + "b" * 40,
                    "user": {"login": "alice"},
                    "labels": [{"name": "needs-human"}],
                }
            if "/pulls/8001/reviews" in path:
                return [
                    {"user": {"login": "alice"}, "body": "Taking a look", "submitted_at": "2026-10-01T00:00:00Z"},
                    {"user": {"login": "alice"}, "body": long_review_body, "submitted_at": "2026-10-01T00:05:00Z"},
                ]
            if "/pulls/8001/comments" in path:
                return []
            if path.startswith("/search/issues"):
                return {"total_count": 1}
            if path.endswith("/labels") and method == "POST":
                applied_labels.extend(data.get("labels", []))
                return {}
            if method == "DELETE":
                deleted_paths.append(path)
                return {}
            return {}

        with mock.patch.dict("os.environ", {"RETRY_NEEDS_HUMAN": "1"}, clear=False):
            with mock.patch.object(gate, "api", side_effect=fake_api):
                gate.main()

        self.assertIn("bounty-eligible", applied_labels)
        self.assertIn("gate-processed", applied_labels)
        self.assertTrue(any(p.endswith("/labels/needs-human") for p in deleted_paths))


if __name__ == "__main__":
    unittest.main()
