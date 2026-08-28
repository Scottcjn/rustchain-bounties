# SPDX-License-Identifier: MIT
"""Regression tests for pr_review_gate substantive-review attribution.

Fixes silent wrong-effect paths where:
- the summary-length check used the claimant's first review (often LGTM)
  instead of their qualifying substantive review; and
- inline comments were attributed per-author instead of per-review.
"""
import importlib.util
from pathlib import Path


def load_gate_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate_body_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _review(rid, login, body, submitted_at):
    return {
        "id": rid,
        "user": {"login": login},
        "body": body,
        "state": "COMMENTED",
        "submitted_at": submitted_at,
    }


def test_body_len_uses_substantive_review_not_earlier_rubber_stamp():
    gate = load_gate_module()
    reviews = [
        _review(1, "alice", "LGTM", "2026-06-08T10:00:00Z"),
        _review(2, "alice", "Ref: `app/foo.py:42` — missing null check on result",
                "2026-06-08T11:00:00Z"),
    ]
    substantive = gate.substantive_reviews(reviews, [])
    assert gate.claimant_substantive_review("alice", substantive) is reviews[1]
    body_len = len(substantive[0].get("body") or "")
    assert body_len >= 40


def test_later_inline_does_not_upgrade_earlier_rubber_stamp():
    gate = load_gate_module()
    reviews = [
        _review(10, "alice", "LGTM", "2026-06-08T10:00:00Z"),
        _review(20, "bob", "Ref: `app/foo.py:1` — real finding here for length",
                "2026-06-08T11:00:00Z"),
    ]
    inline = [
        {"pull_request_review_id": 20, "user": {"login": "bob"}},
    ]
    substantive = gate.substantive_reviews(reviews, inline)
    assert len(substantive) == 1
    assert substantive[0]["id"] == 20


def test_inline_attributed_to_matching_review_only():
    gate = load_gate_module()
    reviews = [
        _review(100, "alice", "LGTM", "2026-06-08T10:00:00Z"),
        _review(200, "alice", "", "2026-06-08T11:00:00Z"),
    ]
    inline = [{"pull_request_review_id": 200, "user": {"login": "alice"}}]
    substantive = gate.substantive_reviews(reviews, inline)
    assert len(substantive) == 1
    assert substantive[0]["id"] == 200
