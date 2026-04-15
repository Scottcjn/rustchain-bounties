"""
BountyScanner — queries GitHub for open RustChain bounties via gh CLI.
No GitHub token required beyond gh auth.
"""
import json
import subprocess
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Bounty:
    number: int
    title: str
    body: str
    labels: list[str]
    reward_rtc: Optional[float]
    is_multi_claim: bool
    url: str
    repo: str = "Scottcjn/rustchain-bounties"

    def short(self) -> str:
        reward = f"{self.reward_rtc} RTC" if self.reward_rtc else "?"
        mc = " [multi]" if self.is_multi_claim else ""
        return f"#{self.number} ({reward}{mc}): {self.title[:60]}"


def _gh(*args) -> str:
    result = subprocess.run(["gh", *args], capture_output=True, text=True, check=True)
    return result.stdout


def _extract_rtc(title: str, body: str) -> Optional[float]:
    for text in [title, body[:500]]:
        m = re.search(r"BOUNTY[:\s]+(\d+(?:\.\d+)?)\s*RTC", text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None


def scan_open_bounties(repo: str = "Scottcjn/rustchain-bounties", limit: int = 50) -> list[Bounty]:
    """Return all open issues labelled 'bounty'."""
    raw = _gh(
        "issue", "list",
        "--repo", repo,
        "--label", "bounty",
        "--state", "open",
        "--limit", str(limit),
        "--json", "number,title,body,labels,url",
    )
    issues = json.loads(raw)
    bounties = []
    for issue in issues:
        labels = [l["name"] for l in issue.get("labels", [])]
        bounties.append(Bounty(
            number=issue["number"],
            title=issue["title"],
            body=issue.get("body") or "",
            labels=labels,
            reward_rtc=_extract_rtc(issue["title"], issue.get("body") or ""),
            is_multi_claim="multi-claim" in labels,
            url=issue["url"],
            repo=repo,
        ))
    return sorted(bounties, key=lambda b: (b.reward_rtc or 0), reverse=True)


def has_open_pr(bounty: Bounty) -> bool:
    """Return True if there's already an open PR for this bounty."""
    raw = _gh(
        "pr", "list",
        "--repo", bounty.repo,
        "--state", "open",
        "--search", f"#{bounty.number}",
        "--json", "number",
    )
    return bool(json.loads(raw))
