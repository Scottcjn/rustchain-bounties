#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Regression for payout audit #16471: gate backfill must not exit green on bad gh JSON.

`list_unprocessed()` used to catch `json.JSONDecodeError` and return `([], [])`.
A `gh issue list` that exited 0 but emitted malformed stdout therefore became an
authoritative empty queue: the sweep printed "0 never-adjudicated" and exited
green while stranded claims were never processed.
"""
import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_orig_run = subprocess.run


def _load():
    spec = importlib.util.spec_from_file_location(
        "pr_review_gate_backfill_test",
        ROOT / "scripts" / "pr_review_gate_backfill.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bf = _load()


class _FakeGate:
    @staticmethod
    def is_review_claim(title):
        return "review" in (title or "").lower()


class ListFailClosedTests(unittest.TestCase):
    def test_malformed_json_raises(self):
        class R:
            stdout = "{"
            stderr = ""
            returncode = 0

        with mock.patch("subprocess.run", return_value=R()):
            with self.assertRaises(bf.GhListError):
                bf.list_unprocessed(_FakeGate())

    def test_nonzero_gh_exit_raises(self):
        class R:
            stdout = ""
            stderr = "rate limit"
            returncode = 1

        with mock.patch("subprocess.run", return_value=R()):
            with self.assertRaises(bf.GhListError):
                bf.list_unprocessed(_FakeGate())

    def test_valid_json_is_parsed(self):
        payload = [
            {"number": 1, "title": "Bounty claim: PR Review - foo", "labels": []},
            {"number": 2, "title": "not a review", "labels": []},
        ]

        class R:
            stdout = json.dumps(payload)
            stderr = ""
            returncode = 0

        with mock.patch("subprocess.run", return_value=R()):
            never, stranded = bf.list_unprocessed(_FakeGate())
        self.assertEqual(never, [1])
        self.assertEqual(stranded, [])

    def test_main_fails_closed_when_listing_fails(self):
        with mock.patch.object(bf, "_load_gate", return_value=_FakeGate()):
            with mock.patch.object(
                bf, "list_unprocessed", side_effect=bf.GhListError("bad json")
            ):
                self.assertEqual(bf.main(), 1)


if __name__ == "__main__":
    unittest.main()
