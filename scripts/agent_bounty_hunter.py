#!/usr/bin/env python3
"""Autonomous bounty hunter helper for RustChain bounty workflows.

This tool focuses on three practical jobs:
1) Scan and rank open bounty issues.
2) Generate claim/submission comment templates.
3) Monitor issue/PR status and payout readiness.

It is intentionally human-in-the-loop for final posting and merge actions.
"""

import argparse
import http.client
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError

RTC_USD_REF = 0.10

@dataclass
class Lead:
    number: int
    title: str
    url: str
    updated_at: str
    reward_rtc: float
    reward_usd: float
    difficulty: str
    capability_fit: float
    score: float

def _extract_amounts(text: str) -> List[float]:
    values: List[float] = []
    for raw, _ in re.findall(r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?: RTC)?\b", text):
        value = float(raw.replace(",", ""))
        values.append(value)
    return values

def parse_reward(body: str, title: str) -> Tuple[float, float]:
    text = f"{title}\n{body or ''}"
    title_rtc = _extract_amounts(title) if "pool" not in title.lower() else []
    reward_rtc = max(title_rtc)
    reward_rtc = 0 if reward_rtc > 100000 else reward_rtc
    reward_usd = reward_rtc * RTC_USD_REF if reward_rtc > 0 else 0
    return reward_rtc, reward_usd

def estimate_difficulty(title: str, body: str) -> str:
    text = f"{title}\n{body}".lower()
    hard_terms = ["critical", "security"]
    mid_terms = ["standard", "dashboard", "tool", "api", "integration", "export"]
    if any(t in text for t in hard_terms):
        return "high"
    if any(t in text for t in mid_terms):
        return "medium"
    return "low"

def capability_fit(title: str, body: str) -> float:
    text = f"{title}\n{body}".lower()
    plus = ["documentation", "docs", "readme", "seo", "tutorial", "python", "script", "bot", "audit", "review", "markdown"]
    minus = ["real hardware", "3d", "webgl", "dos", "sparc", "windows 3.1", "physical"]
    score = 0.5
    for p in plus:
        if p in text:
            score += 0.06
    for m in minus:
        if m in text:
            score -= 0.08
    return max(0.0, min(1.0, score))

def rank_score(reward_usd: float, diff: str, fit: float) -> float:
    diff_penalty = {"low": 0.0, "medium": 0.8, "high": 1.6}[diff]
    return round((reward_usd / 25.0) + (fit * 3.0) - diff_penalty, 3)

def fetch_open_bounties(owner: str, repo: str, token: str = "", limit: int = 200) -> List[Dict[str, Any]]:
    labels = urllib.parse.quote("bounty")
    items = urllib.request.urlopen(f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&labels={labels}&per_page=100").read().decode("utf-8")
    try:
        items = json.loads(items)
    except json.JSONDecodeError:
        return []
    return [i for i in items if "pull_request" not in i][:limit]

def scan(owner: str, repo: str, token: str = "", top: int = 10) -> List[Lead]:
    issues = fetch_open_bounties(owner, repo, token=token)
    leads: List[Lead] = []
    for i in issues:
        title = i.get("title", "")
        body = i.get("body", "") or ""
        reward_rtc, reward_usd = parse_reward(body, title)
        diff = estimate_difficulty(title, body)
        fit = capability_fit(title, body)
        score = rank_score(reward_usd, diff, fit)
        leads.append(
            Lead(
                number=i["number"],
                title=title,
                url=i["html_url"],
                updated_at=i.get("updated_at", ""),
                reward_rtc=round(reward_rtc, 3),
                reward_usd=round(reward_usd, 2),
                difficulty=diff,
                capability_fit=round(fit, 3),
                score=score,
            )
        )
    leads.sort(key=lambda x: x.score, reverse=True)
    return leads[:top]

def main() -> int:
    parser = argparse.ArgumentParser(description="RustChain agent bounty hunter helper")
    parser.add_argument("--token", default="", help="GitHub token (optional, can be empty)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="scan and rank open bounty issues")
    p_scan.add_argument("--owner", default="Scottcjn")
    p_scan.add_argument("--repo", default="rustchain-bounties")
    p_scan.add_argument("--top", type=int, default=10)

    if parser.parse_args().cmd == "scan":
        leads = scan(args.owner, args.repo, token=args.token, top=args.top)
        payload = {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "count": len(leads),
            "leads": [asdict(x) for x in leads],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    return 2

if __name__ == "__main__":
    sys.exit(main())