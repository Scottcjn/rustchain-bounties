#!/usr/bin/env python3
"""Autonomous bounty hunter helper for RustChain bounty workflows.

This tool focuses on three practical jobs:
1) Scan and rank open bounty issues.
2) Generate claim/submission comment templates.
3) Monitor issue/PR status and payout readiness.

It is intentionally human-in-the-loop for final posting and merge actions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

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


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def gh_get(path: str, token: str = "") -> Any:
    base = "https://api.github.com"
    url = path if path.startswith("http") else f"{base}{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "agent-bounty-hunter")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_reward(body: str, title: str) -> Tuple[float, float]:
    text = f"{title}\n{body}"

    rtc_values = [float(x) for x in re.findall(r"(?i)\b(\d+(?:\.\d+)?)\s*RTC\b", text)]
    usd_values = [float(x) for x in re.findall(r"\$\s*(\d+(?:\.\d+)?)", text)]

    reward_rtc = max(rtc_values) if rtc_values else 0.0
    reward_usd = max(usd_values) if usd_values else reward_rtc * RTC_USD_REF

    if reward_rtc == 0 and reward_usd > 0:
        reward_rtc = reward_usd / RTC_USD_REF

    return reward_rtc, reward_usd


def estimate_difficulty(title: str, body: str) -> str:
    text = f"{title}\n{body}".lower()
    hard_terms = ["critical", "security", "red team", "hardening", "consensus", "major", "1000", "$1000"]
    mid_terms = ["standard", "dashboard", "tool", "api", "integration", "export"]

    if any(t in text for t in hard_terms):
        return "high"
    if any(t in text for t in mid_terms):
        return "medium"
    return "low"


def capability_fit(title: str, body: str) -> float:
    text = f"{title}\n{body}".lower()
    plus = [
        "documentation",
        "docs",
        "readme",
        "seo",
        "tutorial",
        "python",
        "script",
        "bot",
        "audit",
        "review",
        "markdown",
    ]
    minus = [
        "real hardware",
        "3d",
        "webgl",
        "dos",
        "sparc",
        "windows 3.1",
        "physical",
    ]

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
    items = gh_get(f"/repos/{owner}/{repo}/issues?state=open&labels={labels}&per_page=100", token)
    if not isinstance(items, list):
        return []
    # Filter out PRs returned by the issues endpoint.
    out = [i for i in items if "pull_request" not in i]
    return out[:limit]


def scan(owner: str, repo: str, token: str = "", top: int = 10, min_usd: float = 0.0) -> List[Lead]:
    issues = fetch_open_bounties(owner, repo, token=token)
    leads: List[Lead] = []

    for i in issues:
        title = i.get("title", "")
        body = i.get("body", "") or ""
        reward_rtc, reward_usd = parse_reward(body, title)
        if reward_usd < min_usd:
            continue
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


def issue_detail(owner: str, repo: str, issue_no: int, token: str = "") -> Dict[str, Any]:
    return gh_get(f"/repos/{owner}/{repo}/issues/{issue_no}", token)


def build_claim_template(issue: Dict[str, Any], wallet: str, handle: str) -> str:
    title = issue.get("title", "")
    issue_no = issue.get("number")
    return (
        f"Claiming this bounty.\\n\\n"
        f"- GitHub: @{handle}\\n"
        f"- RTC wallet (miner id): {wallet}\\n"
        f"- Target issue: #{issue_no} {title}\\n"
        f"- Plan: deliver a reviewable PR with validation evidence and bounty-thread submission links."
    )


def build_submission_template(
    wallet: str,
    handle: str,
    pr_links: List[str],
    summary: str,
) -> str:
    lines = [
        "Submission update:",
        "",
        f"- GitHub: @{handle}",
        f"- RTC wallet (miner id): {wallet}",
        "- PR links:",
    ]
    for idx, p in enumerate(pr_links, start=1):
        lines.append(f"  {idx}) {p}")
    lines.extend(["", "Summary:", summary])
    return "\n".join(lines)


def monitor_targets(targets: List[Dict[str, Any]], token: str = "") -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for t in targets:
        issue_repo = t["issue_repo"]
        pr_repo = t["pr_repo"]
        issue_no = t["issue"]
        pr_no = t["pr"]
        label = t.get("label", f"{issue_repo}#{issue_no}")

        issue = gh_get(f"/repos/{issue_repo}/issues/{issue_no}", token)
        pr = gh_get(f"/repos/{pr_repo}/pulls/{pr_no}", token)

        merged = bool(pr.get("merged", False))
        pr_state = pr.get("state", "unknown")
        issue_state = issue.get("state", "unknown")

        payout_action = "wait_for_review"
        if merged:
            payout_action = "request_payout"
        elif pr_state == "closed":
            payout_action = "check_followup"

        rows.append(
            {
                "label": label,
                "issue": f"https://github.com/{issue_repo}/issues/{issue_no}",
                "pr": f"https://github.com/{pr_repo}/pull/{pr_no}",
                "issue_state": issue_state,
                "pr_state": pr_state,
                "merged": merged,
                "payout_action": payout_action,
            }
        )
    return rows


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="RustChain agent bounty hunter helper")
    parser.add_argument("--token", default="", help="GitHub token (optional, can be empty)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="scan and rank open bounty issues")
    p_scan.add_argument("--owner", default="Scottcjn")
    p_scan.add_argument("--repo", default="rustchain-bounties")
    p_scan.add_argument("--top", type=int, default=10)
    p_scan.add_argument("--min-usd", type=float, default=0.0)

    p_claim = sub.add_parser("claim-template", help="generate claim template")
    p_claim.add_argument("--owner", default="Scottcjn")
    p_claim.add_argument("--repo", default="rustchain-bounties")
    p_claim.add_argument("--issue", type=int, required=True)
    p_claim.add_argument("--wallet", required=True)
    p_claim.add_argument("--handle", required=True)

    p_submit = sub.add_parser("submit-template", help="generate submission template")
    p_submit.add_argument("--wallet", required=True)
    p_submit.add_argument("--handle", required=True)
    p_submit.add_argument("--summary", required=True)
    p_submit.add_argument("--pr", action="append", required=True, help="repeat for multiple PR links")

    p_monitor = sub.add_parser("monitor", help="monitor issue/PR pairs")
    p_monitor.add_argument("--targets-json", required=True, help="path to JSON list of monitoring targets")

    args = parser.parse_args()

    if args.cmd == "scan":
        leads = scan(args.owner, args.repo, token=args.token, top=args.top, min_usd=args.min_usd)
        payload = {
            "generated_at": now_utc(),
            "count": len(leads),
            "leads": [asdict(x) for x in leads],
        }
        print_json(payload)
        return 0

    if args.cmd == "claim-template":
        issue = issue_detail(args.owner, args.repo, args.issue, token=args.token)
        print(build_claim_template(issue, wallet=args.wallet, handle=args.handle))
        return 0

    if args.cmd == "submit-template":
        print(build_submission_template(args.wallet, args.handle, args.pr, args.summary))
        return 0

    if args.cmd == "monitor":
        with open(args.targets_json, "r", encoding="utf-8") as f:
            targets = json.load(f)
        rows = monitor_targets(targets, token=args.token)
        print_json({"generated_at": now_utc(), "rows": rows})
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
