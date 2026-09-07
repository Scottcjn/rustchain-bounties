# SPDX-License-Identifier: MIT
"""The #73 gate must fail CLOSED when it cannot read inline review comments.

`is_substantive_review()` treats inline_count > 0 as a positive signal, so the
inline-comments lookup is money-decision evidence. It used to be read with the
non-strict helper and `or []`, so an HTTP 403/429/5xx became "zero inline
comments" -- indistinguishable from a real empty result. That could:
  1. drop a genuine first substantive reviewer (whose findings are inline) and
     approve a later reviewer for the RTC, or
  2. close a valid short-summary + inline-comments claim as a rubber stamp.
Both complete on a green run. Reported by @bgrubbs1 under #16471.

This test proves a failed inline-comments lookup holds the claim for a human
and neither approves nor closes it.
"""
import importlib.util
from pathlib import Path


def load_gate():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate_inlinefix", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUTHOR = "alice"
PR = "1396"
SHORT_BODY = "See inline findings."


class FakeApi:
    """api() stand-in whose inline-comments lookup fails with an HTTP error."""

    def __init__(self, api_error):
        self._api_error = api_error
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
        if "/pulls/" in path and path.endswith("/reviews"):
            return [{
                "user": {"login": AUTHOR},
                "body": SHORT_BODY,
                "submitted_at": "2026-08-01T00:00:00Z",
            }]
        if "/pulls/" in path and "/comments" in path:
            # The authoritative inline-comment read fails. Strict callers must
            # get an ApiError, not a swallowed None -> [].
            if strict:
                raise self._api_error("GET /pulls/.../comments -> HTTP 403")
            return None
        if path.startswith("/search/issues"):
            return {"total_count": 0}
        if path.endswith("/issues/42"):
            return {
                "state": "open",
                "labels": [],
                "title": f"Bounty #73 claim: review of PR #{PR}",
                "body": "wallet RTC" + "a" * 40,
                "user": {"login": AUTHOR},
            }
        raise AssertionError(f"unexpected API call: {method} {path}")


def run_gate():
    mod = load_gate()
    mod.NUM = "42"
    mod.REPO = "Scottcjn/rustchain-bounties"
    mod.TARGET = "Scottcjn/Rustchain"
    fake = FakeApi(mod.ApiError)
    mod.api = fake
    mod.main()
    return mod, fake


def test_inline_lookup_failure_holds_for_human():
    _, fake = run_gate()

    assert "needs-human" in fake.labels, (
        "a failed inline-comment read must hold the claim for a human"
    )
    assert "bounty-eligible" not in fake.labels, (
        "must not approve when the substantiveness evidence could not be read"
    )
    assert not any(p.get("state") == "closed" for p in fake.patches), (
        "must not close a valid claim just because the inline read failed"
    )
