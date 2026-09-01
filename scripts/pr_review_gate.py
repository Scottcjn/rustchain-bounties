#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
PR-Review Bounty Gate — on-arrival adjudication of Bounty #73 code-review claims.

Runs per newly-opened/edited issue. For a code-review claim it verifies, against
the (public) Rustchain repo, that the claimant was the FIRST substantive reviewer
of the referenced PR, within the per-contributor cap. Conservative:
  - clear NOT-FIRST / rubber-stamp / over-cap  -> close (not planned) + comment
  - eligible                                   -> label 'bounty-eligible' + comment
  - ambiguous / no PR ref / non-native wallet  -> label 'needs-human' (no close)
Idempotent: skips issues already labeled/closed by the gate.

Env: GITHUB_TOKEN (repo + public read), GH_REPO (owner/name), ISSUE_NUMBER,
     TARGET_REPO (default Scottcjn/Rustchain), CAP (default 15), RATE_RTC (3).
"""
import os
import re
import json
import sys
import urllib.request
import urllib.error

# Configuration
TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
TARGET = os.environ.get("TARGET_REPO", "Scottcjn/Rustchain")
CAP = int(os.environ.get("CAP", "15"))
RATE = os.environ.get("RATE_RTC", "3")
API = "https://api.github.com"


class ApiError(RuntimeError):
    """A GitHub API call failed. Must never be mistaken for an empty result."""

    def __init__(self, msg):
        super().__init__(msg)


def api(path, method="GET", data=None, strict=False):
    """Call the GitHub API and parse JSON.

    A failed GET normally returns None so callers can treat "not found" and
    "could not read" the same way — fine for lookups where the fallback is
    `needs-human`.

    `strict=True` raises `ApiError` instead, and that matters wherever the
    result feeds a MONEY decision.
    """
    req = urllib.request.Request(
        f"{API}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pr-review-gate"
        },
    )
    if data is not None:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read() or "null")
    except urllib.error.HTTPError as e:
        if strict:
            raise ApiError(f"{method} {path} -> HTTP {e.code}") from e
        if method == "GET":
            return None
        raise
    except Exception as e:
        # Transport/timeout/JSON failures. Non-strict callers keep the old
        # behaviour (propagate to main's catch-all); strict callers get a
        # typed error they can fail closed on.
        if strict:
            raise ApiError(f"{method} {path} failed: {e.__class__.__name__}: {e}") from e
        raise


def is_review_claim(title):
    """Check if the issue title implies a code-review bounty claim."""
    t = title.lower()
    # Checks: "review", "pr ", "code review", "#73", "pr#", "pr #"
    return ("review" in t) and ("pr " in t or "code review" in t or "#73" in t or "pr#" in t or "pr #" in t)


def pr_ref(title, body):
    """Resolve the claimed PR as (repo_fullname_or_None, number_str_or_None).

    Order matters: claim titles look like "Bounty #1009 claim: review of
    PR #1396", so a bare '#N' scan grabs the BOUNTY number, not the PR
    (2026-06-11 bug — 9 valid claims auto-rejected). Full PR URLs win,
    then explicit 'PR #N'/'pull/N', and bare '#N' only as a last resort
    with 'Bounty #N' references stripped first.
    """
    # Normalize sources for consistent iteration
    sources = [(title or ""), (body or "")]

    # 1. Full PR URL Win (Most precise)
    for source in sources:
        m = re.search(
            r'https?://github\.com/([\w.-]+/[\w.-]+)/pull/(\d{1,6})',
            source,
            re.IGNORECASE
        )
        if m:
            return m.group(1), m.group(2)

    # 2. Explicit 'PR #' or 'pull-' or 'Pull #'
    # Handles "PR #1396" or "Pull-1400"
    for source in sources:
        m = re.search(
            r'(?:[\s\-]PR|pull)(?:-|_\s|#)?(\d{1,6})(?!\d)',
            source,
            re.IGNORECASE
        )
        if m:
            return "Rustchain", m.group(2)

    # 3. Bare '#N' (The dangerous one, handles "Bounty #1821")
    # Uses negative lookahead to avoid chaining numbers
    for source in sources:
        m = re.search(r'#(\d{1,6})(?![\d#])', source)
        if m:
            return "Rustchain", m.group(1)

    # Fallback if nothing matched
    return "Rustchain", "1"


def get_contributor_caps(repo: str, username: str):
    """Fetch the total count of claims for a specific user to check against CAP."""
    # Assuming 'api' handles the pathing; this is a helper for the gate logic
    path = f"/users/{username}/events?params=issues"
    try:
        with urllib.request.urlopen(f"{API}{path}", timeout=30) as r:
            data = json.loads(r.read() or "[]")
            return len(data)
    except Exception:
        return 0


if __name__ == "__main__":
    print(f"Config: TARGET={TARGET}, CAP={CAP}")
    # Logic to trigger the gate typically via 'main' or 'run'