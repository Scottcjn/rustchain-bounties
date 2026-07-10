#!/usr/bin/env python3
"""
Guard: flag bounty-submission PRs from untrusted authors that touch
protected automation/payout paths (closes the class of bug seen in #14981,
where a "solution" PR to an onboarding bounty gutted .github/scripts/*.py
automation instead of adding a submission file).

This is deliberately NOT a blanket "everything outside submissions/ is
banned" rule. Real merged bounty work in this repo routinely touches
docs/, apple2_miner/, museum/, star_tracker.py, bounties/<issue>/, and
plenty of other paths depending on what the bounty asked for (see #2093,
#2095, #142, #173, #2699). Banning that would break legitimate
contributors. Likewise, trusted contributors (OWNER/MEMBER/COLLABORATOR/
CONTRIBUTOR) routinely and legitimately touch scripts/ and .github/ as
part of normal maintenance (see #14990, #14546) -- that is not the
problem this guard exists to catch.

What actually differentiated the #14981 incident:
  - author_association == NONE (first-time, non-collaborator)
  - the PR touched automation/payout-critical paths
    (.github/workflows, .github/scripts, .github/actions,
     scripts/, bounties.json, BOUNTY_LEDGER.md, ...)

So the guard only fires when BOTH are true. It never blocks a trusted
contributor, and it never blocks an untrusted contributor whose PR stays
out of protected paths (which covers the overwhelming majority of real
bounty submissions).

On a hit, this posts an explanatory PR comment, applies a
`needs-maintainer-review` label, and exits non-zero so the check shows
red -- a request for human review, not a permanent block. A maintainer
can always merge past a failing, non-required check.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Iterable

import requests

API = "https://api.github.com"

# Authors at this trust level are never gated by this guard. Getting to
# CONTRIBUTOR already requires a prior merged PR reviewed by a human.
TRUSTED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"}

# Path prefixes that carry real blast radius: CI automation, payout
# scripts, and the ledger/registry files the payout scripts read.
PROTECTED_PREFIXES = (
    ".github/workflows/",
    ".github/scripts/",
    ".github/actions/",
    ".github/mcp_server/",
    "scripts/",
)
PROTECTED_EXACT_FILES = {
    ".github/dependabot.yml",
    ".github/supply-chain-allowlist.yml",
    "bounties.json",
    "BOUNTY_LEDGER.md",
    "expected_miners.txt",
}

LABEL_NAME = "needs-maintainer-review"
LABEL_COLOR = "d93f0b"
LABEL_DESCRIPTION = "Touches protected automation/payout paths -- flagged by guard-bounty-pr for human review"


def is_protected_path(path: str) -> bool:
    if path in PROTECTED_EXACT_FILES:
        return True
    return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def fetch_changed_files(owner: str, repo: str, pr_number: int, headers: dict) -> list[str]:
    paths: list[str] = []
    page = 1
    while True:
        resp = requests.get(
            f"{API}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=headers,
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        paths.extend(item["filename"] for item in batch)
        if len(batch) < 100:
            break
        page += 1
    return paths


def ensure_label(owner: str, repo: str, headers: dict) -> None:
    resp = requests.get(f"{API}/repos/{owner}/{repo}/labels/{LABEL_NAME}", headers=headers, timeout=30)
    if resp.status_code == 200:
        return
    requests.post(
        f"{API}/repos/{owner}/{repo}/labels",
        headers=headers,
        json={"name": LABEL_NAME, "color": LABEL_COLOR, "description": LABEL_DESCRIPTION},
        timeout=30,
    )


def apply_label(owner: str, repo: str, pr_number: int, headers: dict) -> None:
    ensure_label(owner, repo, headers)
    requests.post(
        f"{API}/repos/{owner}/{repo}/issues/{pr_number}/labels",
        headers=headers,
        json={"labels": [LABEL_NAME]},
        timeout=30,
    )


def post_comment(owner: str, repo: str, pr_number: int, protected_hits: Iterable[str], author: str, headers: dict) -> None:
    hit_list = "\n".join(f"- `{p}`" for p in sorted(protected_hits))
    body = (
        "**guard-bounty-pr**: this PR is from a first-time/non-collaborator "
        f"contributor (`{author}`) and touches automation or payout-critical paths:\n\n"
        f"{hit_list}\n\n"
        "Bounty/onboarding submissions are normally expected to add their own "
        "content (docs, a submissions/ entry, a small standalone script, etc.), "
        "not modify existing CI workflows, `.github/scripts/`, `scripts/`, or "
        "the bounty ledger/registry files. This is exactly the pattern seen in "
        "#14981, where a \"solution\" PR replaced working automation scripts "
        "with stubs.\n\n"
        "This is **not** an automatic rejection -- a maintainer needs to look "
        "at the diff before this merges. If the changes to these paths are "
        "legitimate and intentional, a maintainer can dismiss this and merge "
        "normally."
    )
    requests.post(
        f"{API}/repos/{owner}/{repo}/issues/{pr_number}/comments",
        headers=headers,
        json={"body": body},
        timeout=30,
    )


def main() -> None:
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if not github_token:
        sys.exit("GITHUB_TOKEN environment variable is required")

    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not os.path.exists(event_path):
        sys.exit("GITHUB_EVENT_PATH not found -- this script must run inside a pull_request(_target) job")

    repo_slug = os.environ.get("GITHUB_REPOSITORY", "Scottcjn/rustchain-bounties")
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    with open(event_path, encoding="utf-8") as f:
        event = json.load(f)

    pr = event.get("pull_request")
    if not pr:
        print("No pull_request in event payload, nothing to do.")
        return

    owner, repo = repo_slug.split("/", 1)
    pr_number = pr["number"]
    author = pr["user"]["login"]
    association = (pr.get("author_association") or "NONE").upper()

    if association in TRUSTED_ASSOCIATIONS:
        print(f"Author {author} has association {association} (trusted) -- skipping guard.")
        return

    changed = fetch_changed_files(owner, repo, pr_number, headers)
    protected_hits = [p for p in changed if is_protected_path(p)]

    if not protected_hits:
        print(f"Author {author} ({association}) touched no protected paths -- skipping guard.")
        return

    print(f"Author {author} ({association}) touched protected paths:")
    for p in protected_hits:
        print(f"  - {p}")

    post_comment(owner, repo, pr_number, protected_hits, author, headers)
    apply_label(owner, repo, pr_number, headers)

    sys.exit(
        "guard-bounty-pr: PR from a non-collaborator touches protected "
        "automation/payout paths -- flagged for maintainer review "
        f"(see {len(protected_hits)} path(s) above and the PR comment)."
    )


if __name__ == "__main__":
    main()
