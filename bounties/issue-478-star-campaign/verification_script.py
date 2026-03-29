#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Star Verification Script for RustChain Bounty Campaign (#478)

Verifies GitHub stars claimed by contributors and calculates payouts
based on the tier system:
  - 2 RTC: main repo (Scottcjn/Rustchain) only
  - 3 RTC per repo: main + 5 other repos
  - 5 RTC per repo: main + ALL 86 repos

Usage:
  python3 verification_script.py --username GITHUB_USER [--repos JSON_FILE]
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "RustChain-StarVerifier/1.0",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

MAIN_REPO = "Scottcjn/Rustchain"
# Pre-fetched list of all Elyan Labs repos from the star campaign
ALL_REPOS = [
    "Scottcjn/Rustchain", "Scottcjn/bottube", "Scottcjn/beacon-skill",
    "Scottcjn/clawhub-sdk", "Scottcjn/grazer-skill",
    # Additional repos from star campaign (abbreviated list)
]


def gh_get(url: str) -> dict:
    """Make an authenticated GitHub API GET request."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  API error {e.code} for {url}", file=sys.stderr)
        return {"error": e.code}


def check_starred(username: str, repo: str) -> bool:
    """Check if user has starred a specific repository."""
    url = f"https://api.github.com/repos/{repo}/stargazers/{username}"
    result = gh_get(url)
    if "error" in result:
        return False
    return result.get("starred", False)


@dataclass
class TierResult:
    tier_name: str
    reward_per_repo: int
    repos_starrable: list
    repos_starred: list
    total_reward: int

    def as_markdown(self) -> str:
        starred = ", ".join(self.repos_starred) or "(none)"
        starrable = ", ".join(self.repos_starrable) or "(none)"
        lines = [
            f"### Tier: {self.tier_name}",
            f"- Reward per repo: **{self.reward_per_repo} RTC**",
            f"- Repos starred ({len(self.repos_starred)}): {starred}",
            f"- Repos NOT starred ({len(self.repos_starrable)}): {starrable}",
            f"- **Total reward: {self.total_reward} RTC**",
        ]
        return "\n".join(lines)


def evaluate_tiers(username: str, all_repos: list[str]) -> list[TierResult]:
    """Evaluate all three payout tiers for a given user."""
    main_starrable = [r for r in all_repos if r != MAIN_REPO]
    results = []

    # Tier 1: main repo only (2 RTC)
    t1_main_starred = check_starred(username, MAIN_REPO)
    if t1_main_starred:
        results.append(TierResult(
            tier_name="Tier 1 — Main repo only",
            reward_per_repo=2,
            repos_starrable=[MAIN_REPO],
            repos_starred=[MAIN_REPO],
            total_reward=2,
        ))

    # Tier 2: main + 5 other repos (3 RTC per repo)
    starred_t2 = []
    starrable_t2 = []
    if check_starred(username, MAIN_REPO):
        starred_t2.append(MAIN_REPO)
        others = main_starrable[:5]
        for r in others:
            if check_starred(username, r):
                starred_t2.append(r)
            else:
                starrable_t2.append(r)
        if len(starred_t2) >= 1:
            reward = len(starred_t2) * 3
            results.append(TierResult(
                tier_name=f"Tier 2 — Main + up to 5 others ({len(starred_t2)} starred)",
                reward_per_repo=3,
                repos_starrable=starrable_t2,
                repos_starred=starred_t2,
                total_reward=reward,
            ))

    # Tier 3: main + ALL repos (5 RTC per repo)
    starred_t3 = []
    starrable_t3 = []
    if check_starred(username, MAIN_REPO):
        starred_t3.append(MAIN_REPO)
        for r in main_starrable:
            if check_starred(username, r):
                starred_t3.append(r)
            else:
                starrable_t3.append(r)
        reward = len(starred_t3) * 5
        results.append(TierResult(
            tier_name=f"Tier 3 — All repos ({len(starred_t3)}/{len(all_repos)} starred)",
            reward_per_repo=5,
            repos_starrable=starrable_t3,
            repos_starred=starred_t3,
            total_reward=reward,
        ))

    return results


def generate_payout_report(username: str, all_repos: list[str]) -> str:
    """Generate a complete payout report for a user."""
    tiers = evaluate_tiers(username, all_repos)
    lines = [
        f"## Payout Report for @{username}",
        f"",
        f"Verified: {len(all_repos)} repos checked",
    ]
    for t in tiers:
        lines.append("")
        lines.append(t.as_markdown())
    if not tiers:
        lines.append("❌ No tiers met. User must star at minimum **Scottcjn/Rustchain**.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="RustChain Star Verification")
    parser.add_argument("--username", required=True, help="GitHub username to verify")
    parser.add_argument("--repos-file", help="JSON file with repo list")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    repos = ALL_REPOS
    if args.repos_file:
        with open(args.repos_file) as f:
            repos = json.load(f)

    report = generate_payout_report(args.username, repos)
    print(report)
    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"\n✅ Report saved to {args.output}")


if __name__ == "__main__":
    main()
