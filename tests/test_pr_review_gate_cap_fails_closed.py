# SPDX-License-Identifier: MIT
"""The Bounty #73 per-contributor cap must fail CLOSED.

The cap counted an author's existing `bounty-eligible` claims with
`api("/search/issues?...") or {}`. `api()` returned None on any HTTPError, so
a 403 secondary rate-limit — routine, because /search/issues has its own
30 req/min budget — became `{}`, became `total_count = 0`, became "this
author has claimed nothing yet". The claim was then approved past the cap, at
3 RTC each, with nothing bounding how often that could recur.

These tests pin the two halves of the fix:
  1. `api(strict=True)` raises `ApiError` instead of returning None.
  2. A cap lookup that cannot complete holds the claim for a human and does
     NOT apply `bounty-eligible`.
"""
import importlib.util
import urllib.error
from pathlib import Path

import pytest


def load_gate():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate_capfix", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUBSTANTIVE_BODY = (
    "The retry loop in `scripts/auto-pay.py` swallows the HTTPError on line 88 and "
    "reports success; that is a real bug and it needs a guard before merge."
)


class FakeApi:
    """Stand-in for `api()`, with a scripted failure for the cap lookup."""

    def __init__(self, cap_lookup_result, author="alice", pr="1396"):
        self.cap_lookup_result = cap_lookup_result
        self.author = author
        self.pr = pr
        self.labels = []
        self.comments = []
        self.patches = []

    def __call__(self, path, method="GET", data=None, strict=False):
        if method == "POST" and path.endswith("/labels"):
            self.labels.extend(data["labels"])
            return {}
        if method == "POST" and path.endswith("/comments"):
            self.comments.append(data["body"])
            return {}
        if method == "PATCH":
            self.patches.append(data)
            return {}
        if path.startswith("/search/issues"):
            if isinstance(self.cap_lookup_result, Exception):
                raise self.cap_lookup_result
            return self.cap_lookup_result
        if "/pulls/" in path and path.endswith("/reviews"):
            return [{
                "user": {"login": self.author},
                "body": SUBSTANTIVE_BODY,
                "submitted_at": "2026-08-01T00:00:00Z",
            }]
        if "/pulls/" in path and "/comments" in path:
            return []
        if path.endswith("/issues/42"):
            return {
                "state": "open",
                "labels": [],
                "title": f"Bounty #73 claim: review of PR #{self.pr}",
                "body": "wallet RTC" + "a" * 40,
                "user": {"login": self.author},
            }
        raise AssertionError(f"unexpected API call: {method} {path}")


# Sentinel: the cap lookup should raise the loaded module's OWN ApiError.
RAISE_API_ERROR = object()


def run_gate(cap_lookup_result):
    mod = load_gate()
    mod.NUM = "42"
    mod.REPO = "Scottcjn/rustchain-bounties"
    mod.TARGET = "Scottcjn/Rustchain"
    if cap_lookup_result is RAISE_API_ERROR:
        cap_lookup_result = mod.ApiError("GET /search/issues -> HTTP 403")
    fake = FakeApi(cap_lookup_result)
    mod.api = fake
    mod.main()
    return mod, fake


def test_cap_lookup_failure_does_not_approve():
    """A 403 on the cap lookup must not read as 'zero claims so far'."""
    _, fake = run_gate(RAISE_API_ERROR)

    assert "bounty-eligible" not in fake.labels, (
        "cap lookup failed, so the cap is unknown — the claim must not be approved"
    )
    assert "needs-human" in fake.labels
    assert not fake.patches, "an undecidable claim must not be closed either"
    assert any("cap" in c.lower() for c in fake.comments)


def test_cap_lookup_unreadable_shape_does_not_approve():
    """A 200 whose body has no total_count is also not an authoritative zero."""
    _, fake = run_gate({"unexpected": "shape"})

    assert "bounty-eligible" not in fake.labels
    assert "needs-human" in fake.labels


def test_under_cap_still_approves():
    """The fix must not break the normal path."""
    _, fake = run_gate({"total_count": 2})

    assert "bounty-eligible" in fake.labels
    assert "needs-human" not in fake.labels


def test_over_cap_still_closes():
    _, fake = run_gate({"total_count": 15})

    assert "bounty-eligible" not in fake.labels
    assert fake.patches == [{"state": "closed", "state_reason": "not_planned"}]


def test_api_strict_raises_instead_of_returning_none(monkeypatch):
    """The seam itself: strict=True converts a swallowed None into ApiError."""
    mod = load_gate()

    def boom(req, timeout=30):
        raise urllib.error.HTTPError(req.full_url, 403, "rate limited", {}, None)

    monkeypatch.setattr(mod.urllib.request, "urlopen", boom)

    # Legacy behaviour, still used by lookups whose fallback is needs-human.
    assert mod.api("/search/issues?q=x") is None

    # Money path.
    with pytest.raises(mod.ApiError):
        mod.api("/search/issues?q=x", strict=True)
