# SPDX-License-Identifier: MIT
"""A gate must not outlive the bounty it pays from.

Bounty #73 was closed on 2026-06-05 and its body marked
``paid: false  # RETIRED 2026-06-14 — pool closed``. The gate kept running:
``pr-review-gate-backfill.yml`` ("#73 safety net") fired every 4 hours and
succeeded as late as 2026-09-20 22:41 UTC, and its approval comment still read
"**3 RTC** pending payout". No replacement bounty was ever opened. Nothing
errored — the automation reported success the whole time, describing a world
that had stopped existing three months earlier.

These tests also pin the three terms of #73 that the gate never enforced:

    "Per-contributor cap: 3 PR reviews / 24h, 15 total"   <- only 15 total was checked
    "The 200 RTC pool is finite."                         <- nothing tracked the pool
    "Eligible Repositories: Rustchain, bottube,
     rustchain-bounties, ram-coffers"                     <- an owner-prefix test
                                                             accepted ANY Scottcjn repo
"""
import importlib.util
from pathlib import Path

import pytest


def load_gate():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate_lifecycle", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SUBSTANTIVE_BODY = (
    "The retry loop in `scripts/auto-pay.py` swallows the HTTPError on line 88 and "
    "reports success; that is a real bug and it needs a guard before merge."
)


class FakeApi:
    def __init__(self, author="alice", pr="1396", bounty_state="open",
                 total_claims=0, claims_24h=0, pool_claims=0, claim_repo=None,
                 bounty_raises=False):
        self.author, self.pr = author, pr
        self.bounty_state, self.bounty_raises = bounty_state, bounty_raises
        self.total_claims, self.claims_24h, self.pool_claims = total_claims, claims_24h, pool_claims
        self.claim_repo = claim_repo
        self.labels, self.comments, self.patches, self.deleted = [], [], [], []
        self.ApiError = None  # set by run_gate

    def __call__(self, path, method="GET", data=None, strict=False):
        if method == "POST" and path.endswith("/labels"):
            self.labels.extend(data["labels"]); return {}
        if method == "DELETE" and "/labels/" in path:
            self.deleted.append(path.rsplit("/", 1)[-1]); return {}
        if method == "POST" and path.endswith("/comments"):
            self.comments.append(data["body"]); return {}
        if method == "PATCH":
            self.patches.append(data); return {}
        if path.endswith("/issues/73"):
            if self.bounty_raises:
                raise self.ApiError("GET /repos/.../issues/73 -> HTTP 403")
            return {"state": self.bounty_state, "number": 73}
        if path.startswith("/search/issues"):
            # pool query has no author: filter
            if "author:" not in path:
                return {"total_count": self.pool_claims}
            if "created:%3E%3D" in path or "created:>=" in path:
                return {"total_count": self.claims_24h}
            return {"total_count": self.total_claims}
        if "/pulls/" in path and path.endswith("/reviews"):
            return [{"user": {"login": self.author}, "body": SUBSTANTIVE_BODY,
                     "submitted_at": "2026-08-01T00:00:00Z"}]
        if "/pulls/" in path and "/comments" in path:
            return []
        if path.endswith("/issues/42"):
            # pr_ref() only resolves a repo from a FULL PR URL; `owner/repo#N`
            # prose yields (None, n) and falls back to TARGET_REPO.
            ref = (f"https://github.com/{self.claim_repo}/pull/{self.pr}"
                   if self.claim_repo else f"PR #{self.pr}")
            return {"state": "open", "labels": [],
                    "title": "Bounty #73 claim: review",
                    "body": f"Reviewed {ref}\n\nwallet RTC" + "a" * 40,
                    "user": {"login": self.author}}
        raise AssertionError(f"unexpected API call: {method} {path}")


def run_gate(**kw):
    mod = load_gate()
    mod.NUM, mod.REPO, mod.TARGET = "42", "Scottcjn/rustchain-bounties", "Scottcjn/Rustchain"
    fake = FakeApi(**kw)
    fake.ApiError = mod.ApiError
    mod.api = fake
    mod.main()
    return mod, fake


# ---------------------------------------------------------------- lifecycle

def test_closed_bounty_is_not_adjudicated_at_all():
    """The production condition: #73 closed, gate still scheduled."""
    _, fake = run_gate(bounty_state="closed")
    assert fake.labels == [], "a retired bounty must not mark claims eligible"
    assert fake.comments == [], "a retired bounty must not promise a payout"
    assert fake.patches == [], "and must not close the claim either"


def test_closed_bounty_never_says_rtc_pending():
    _, fake = run_gate(bounty_state="closed")
    assert not any("RTC" in c for c in fake.comments)


def test_unreadable_bounty_lookup_fails_closed():
    """A failed lookup is not permission to keep promising money."""
    _, fake = run_gate(bounty_raises=True)
    assert fake.labels == [] and fake.comments == []


def test_open_bounty_still_approves_a_good_claim():
    _, fake = run_gate(bounty_state="open")
    assert "bounty-eligible" in fake.labels
    assert any("verified eligible" in c for c in fake.comments)


# ------------------------------------------------------------- #73's terms

def test_daily_cap_holds_rather_than_closes():
    """'3 PR reviews / 24h' -- a rate limit is not a disqualification."""
    _, fake = run_gate(claims_24h=3, total_claims=5)
    assert "bounty-eligible" not in fake.labels
    assert fake.patches == [], "hitting a rate cap must not close the claim"
    assert any("24h" in c for c in fake.comments)


def test_under_daily_cap_approves():
    _, fake = run_gate(claims_24h=2, total_claims=5)
    assert "bounty-eligible" in fake.labels


def test_exhausted_pool_closes_with_an_explanation():
    """'The 200 RTC pool is finite.' 67 eligible claims x 3 RTC = 201 > 200."""
    _, fake = run_gate(pool_claims=67)
    assert "bounty-eligible" not in fake.labels
    assert fake.patches, "an exhausted pool should close the claim"
    assert any("pool" in c.lower() for c in fake.comments)
    assert any("nothing was wrong with it" in c for c in fake.comments)


def test_pool_with_room_approves():
    _, fake = run_gate(pool_claims=10)
    assert "bounty-eligible" in fake.labels


# ------------------------------------------------------- eligible repos

@pytest.mark.parametrize("repo", [
    "Scottcjn/Rustchain", "Scottcjn/bottube",
    "Scottcjn/rustchain-bounties", "Scottcjn/ram-coffers",
])
def test_the_four_eligible_repos_are_accepted(repo):
    _, fake = run_gate(claim_repo=repo)
    assert "bounty-eligible" in fake.labels, f"{repo} is eligible under #73"


def test_other_maintainer_repos_are_no_longer_accepted():
    """The owner-prefix test accepted every repo the maintainer owns."""
    _, fake = run_gate(claim_repo="Scottcjn/some-personal-project")
    assert "bounty-eligible" not in fake.labels
    assert any("not one of the repositories eligible" in c for c in fake.comments)


def test_third_party_repo_still_rejected():
    _, fake = run_gate(claim_repo="someoneelse/their-repo")
    assert "bounty-eligible" not in fake.labels


# ------------------------------------------------------------------ TOCTOU

def test_concurrent_claim_over_cap_yields_after_labelling():
    """Read-then-label is a TOCTOU, and GitHub's search index lags writes.

    The pre-label count is under the cap; once this claim's own label exists the
    count is over. The claim that just arrived is the one that yields.
    """
    mod = load_gate()
    mod.NUM, mod.REPO, mod.TARGET = "42", "Scottcjn/rustchain-bounties", "Scottcjn/Rustchain"
    fake = FakeApi(total_claims=14)
    fake.ApiError = mod.ApiError
    state = {"labelled": False}
    inner = fake.__call__

    def api(path, method="GET", data=None, strict=False):
        # main() applies `gate-processed` early; only the eligibility label
        # is the one whose visibility this test is about.
        if method == "POST" and path.endswith("/labels") \
                and "bounty-eligible" in (data or {}).get("labels", []):
            state["labelled"] = True
        if path.startswith("/search/issues") and "author:" in path \
                and "created" not in path and state["labelled"]:
            return {"total_count": 16}      # now visible, and over CAP=15
        return inner(path, method, data, strict)

    mod.api = api
    mod.main()
    assert "bounty-eligible" in fake.deleted, "the over-cap label must be removed again"
    assert fake.patches, "and the claim closed"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
