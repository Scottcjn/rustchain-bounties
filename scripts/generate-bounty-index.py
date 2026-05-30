#!/usr/bin/env python3
"""
Generate a machine-readable bounty index (bounties.json) from open GitHub issues.

Usage:
    python3 scripts/generate-bounty-index.py

Requires: gh CLI authenticated, or set GITHUB_TOKEN env var.

Output: bounties.json in the repo root.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


REPO = os.environ.get("BOUNTY_REPO", "Scottcjn/rustchain-bounties")
OUTPUT_FILE = os.environ.get("BOUNTY_OUTPUT", "bounties.json")


def run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"gh error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def fetch_open_bounties() -> list[dict]:
    """Fetch all open issues labeled 'bounty'."""
    raw = run_gh([
        "issue", "list",
        "--repo", REPO,
        "--label", "bounty",
        "--state", "open",
        "--limit", "200",
        "--json", "number,title,labels,assignees,createdAt,updatedAt,url",
    ])
    return json.loads(raw)


def parse_reward(title: str) -> dict:
    """Extract reward amount from title."""
    patterns = [
        (r"\[BOUNTY[:\s]*(\d+(?:\.\d+)?)(?:\s*-\s*(\d+(?:\.\d+)?))?\s*RTC\]", "RTC"),
        (r"\[GRANT[:\s]*(\d+(?:\.\d+)?)\s*RTC", "RTC"),
        (r"\[Bounty\s*\$?([\d,]+)\]", "USD"),
        (r"\[(\d+(?:\.\d+)?)\s*MRG\]", "MRG"),
        (r"\$(\d[\d,]*(?:\.\d+)?)", "USD"),
    ]

    for pattern, currency in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            amount_min = float(match.group(1).replace(",", ""))
            amount_max = float(match.group(2).replace(",", "")) if (match.lastindex or 0) >= 2 and match.group(2) else amount_min
            return {"reward_min": amount_min, "reward_max": amount_max, "currency": currency}

    # Fallback: look for standalone RTC amounts
    match = re.search(r"(\d+(?:\.\d+)?)\s*RTC", title, re.IGNORECASE)
    if match:
        return {"reward_min": float(match.group(1)), "reward_max": float(match.group(1)), "currency": "RTC"}

    return {"reward_min": 0, "reward_max": 0, "currency": "RTC"}


def categorize(labels: list[dict]) -> str:
    """Determine bounty category from labels."""
    label_names = {l["name"].lower() for l in labels}

    mapping = {
        "content": ["content", "article", "blog"],
        "documentation": ["documentation"],
        "translation": ["translation", "localization", "i18n"],
        "security": ["red-team", "hardening", "security"],
        "code": ["feature", "bug", "enhancement", "integration"],
        "community": ["community", "propagation", "ecosystem"],
        "testing": ["testing"],
        "maintenance": ["maintenance"],
        "visualization": ["visualization"],
    }

    for cat, keywords in mapping.items():
        if label_names & set(keywords):
            return cat

    return "general"


def difficulty_from_labels(labels: list[dict]) -> str:
    """Map labels to difficulty string."""
    label_names = {l["name"].lower() for l in labels}
    if "critical" in label_names or "red-team" in label_names:
        return "critical"
    if "major" in label_names:
        return "major"
    if "easy" in label_names or "micro" in label_names or "good first issue" in label_names:
        return "easy"
    return "standard"


def build_index(issues: list[dict]) -> dict:
    """Build the complete bounty index."""
    bounties = []

    for issue in issues:
        labels = issue.get("labels", [])
        reward = parse_reward(issue["title"])

        bounty = {
            "id": issue["number"],
            "title": issue["title"],
            "url": issue["url"],
            "reward_min": reward["reward_min"],
            "reward_max": reward["reward_max"],
            "currency": reward["currency"],
            "category": categorize(labels),
            "difficulty": difficulty_from_labels(labels),
            "state": "open",
            "assignees": [a["login"] for a in issue.get("assignees", [])],
            "labels": [l["name"] for l in labels],
            "created_at": issue.get("createdAt", ""),
            "updated_at": issue.get("updatedAt", ""),
        }
        bounties.append(bounty)

    # Sort: highest reward first, then unassigned first, then newest first
    bounties.sort(key=lambda b: (-b["reward_max"], len(b["assignees"]), b["created_at"]))

    total_rtc = sum(b["reward_max"] for b in bounties if b["currency"] == "RTC")
    total_usd = sum(b["reward_max"] for b in bounties if b["currency"] == "USD")
    total_mrg = sum(b["reward_max"] for b in bounties if b["currency"] == "MRG")

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repo": REPO,
        "total_bounties": len(bounties),
        "total_reward_rtc": total_rtc,
        "total_reward_usd": total_usd,
        "total_reward_mrg": total_mrg,
        "bounties": bounties,
    }


def main():
    print(f"Fetching open bounties from {REPO}...")
    issues = fetch_open_bounties()
    print(f"Found {len(issues)} open bounty issues.")

    index = build_index(issues)

    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), OUTPUT_FILE)
    with open(output_path, "w") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Generated {output_path} with {index['total_bounties']} bounties.")
    print(f"Total RTC: {index['total_reward_rtc']} | USD: {index['total_reward_usd']} | MRG: {index['total_reward_mrg']}")


if __name__ == "__main__":
    main()
