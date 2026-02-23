#!/usr/bin/env python3
"""M1 skeleton for RustChain bounty hunter agent.

This CLI does three things:
1) scan open bounty issues from GitHub,
2) rank/filter by capability/risk heuristics (skip hardware-dependent tasks),
3) generate a minimal implementation plan (JSON + markdown) for a selected bounty.

All write actions are intentionally safe by default: posting comments is dry-run unless
explicitly disabled.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Tuple

API_BASE = "https://api.github.com"

DEFAULT_OWNER = "Scottcjn"
DEFAULT_REPO = "rustchain-bounties"

CAPABILITY_KEYWORDS = {
    "python": 0.20,
    "doc": 0.18,
    "docs": 0.18,
    "readme": 0.16,
    "tutorial": 0.14,
    "markdown": 0.14,
    "test": 0.12,
    "ci": 0.12,
    "workflow": 0.12,
    "script": 0.10,
    "github": 0.10,
    "badge": 0.10,
    "api": 0.10,
}

RISK_KEYWORDS = {
    "high": {
        "hardware": 1.0,
        "arduino": 1.0,
        "raspberry": 1.0,
        "esp": 1.0,
        "3d": 0.8,
        "physical": 0.8,
        "i2c": 0.6,
        "spi": 0.6,
        "usb": 0.6,
        "fpga": 1.0,
        "sdr": 0.9,
    },
    "medium": {
        "security": 0.55,
        "wallet": 0.45,
        "consensus": 0.45,
        "validator": 0.35,
        "node": 0.25,
    },
}


@dataclass
class BountyLead:
    number: int
    title: str
    url: str
    updated_at: str
    capability_score: float
    risk_level: str
    reward_rtc: float
    reward_usd: float


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gh_request(path: str, token: str = "") -> Any:
    req = urllib.request.Request(f"{API_BASE}{path}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "rustchain-bounty-hunter-m1")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def gh_issue(owner: str, repo: str, issue_number: int, token: str = "") -> Dict[str, Any]:
    return gh_request(f"/repos/{owner}/{repo}/issues/{issue_number}", token=token)


def gh_open_bounties(owner: str, repo: str, token: str = "") -> List[Dict[str, Any]]:
    # GitHub issue endpoint may include PRs; filter those out.
    payload = gh_request(
        f"/repos/{owner}/{repo}/issues?state=open&labels=bounty&per_page=100&sort=updated&direction=desc",
        token=token,
    )
    issues: List[Dict[str, Any]] = []
    for item in (payload if isinstance(payload, list) else []):
        if "pull_request" in item:
            continue
        issues.append(item)
    return issues


def parse_reward(body: str, title: str = "") -> Tuple[float, float]:
    """Parse reward hints from bounty text with lightweight heuristics.

    Supports both:
    - parse_reward(text)
    - parse_reward(body, title)
    """

    combined = f"{title}\n{body}" if title else body
    if not combined:
        return 0.0, 0.0

    def parse_amount(raw: str, suffix: str) -> float:
        num = float(raw.replace(",", ""))
        if suffix == "k":
            return num * 1000.0
        if suffix == "m":
            return num * 1_000_000.0
        return num

    # Prefer non-pool lines for explicit reward signals.
    lines = [ln for ln in combined.splitlines() if "pool" not in ln.lower()]
    text = "\n".join(lines) if lines else combined

    usd_match = re.findall(r"\$\s*([0-9][0-9,]*\.?[0-9]*)([km]?)", text, flags=re.IGNORECASE)
    rtc_match = re.findall(r"([0-9][0-9,]*\.?[0-9]*)([km]?)\s*RTC", text, flags=re.IGNORECASE)

    usd = 0.0
    rtc = 0.0
    if rtc_match:
        raw, suf = rtc_match[0]
        rtc = parse_amount(raw, (suf or "").lower())
    elif usd_match:
        raw, suf = usd_match[0]
        usd = parse_amount(raw, (suf or "").lower())
        rtc = usd * 10.0

    # Title-only fallback for formats like "(... 75 RTC)"
    if rtc == 0.0 and usd == 0.0:
        fallback = re.findall(r"([0-9][0-9,]*\.?[0-9]*)([km]?)\s*RTC", title or "", flags=re.IGNORECASE)
        if fallback:
            raw, suf = fallback[0]
            rtc = parse_amount(raw, (suf or "").lower())

    if rtc and not usd:
        usd = round(rtc / 10.0, 2)

    if rtc == 0.0 and usd == 0.0 and "$" in combined:
        fallback_usd = re.findall(r"\$\s*([0-9][0-9,]*\.?[0-9]*)([km]?)", combined, flags=re.IGNORECASE)
        if fallback_usd:
            raw, suf = fallback_usd[0]
            usd = parse_amount(raw, (suf or "").lower())
            rtc = usd * 10.0

    return round(rtc, 3), round(usd, 2)


def assess_capability(text: str) -> float:
    low = text.lower()
    score = 0.0
    for key, w in CAPABILITY_KEYWORDS.items():
        if key in low:
            score += w
    return round(min(1.0, max(0.0, score)), 3)


def assess_risk(text: str) -> str:
    low = text.lower()
    risk = 0.0
    for level, kws in RISK_KEYWORDS.items():
        for k in kws:
            if k in low:
                if level == "high":
                    risk = max(risk, 0.8)
                else:
                    risk = max(risk, 0.5)
    if risk >= 0.8:
        return "high"
    if risk >= 0.5:
        return "medium"
    return "low"


def scan_open_bounties(
    owner: str,
    repo: str,
    token: str = "",
    min_capability: float = 0.0,
    max_risk: str = "medium",
    include_hardware: bool = False,
) -> List[BountyLead]:
    issues = gh_open_bounties(owner, repo, token=token)
    out: List[BountyLead] = []

    for it in issues:
        title = it.get("title", "")
        body = it.get("body", "") or ""
        text = f"{title} {body}"

        capability = assess_capability(text)
        risk = assess_risk(text)

        if capability < min_capability:
            continue
        if (risk == "high") and not include_hardware:
            continue
        if max_risk == "low" and risk != "low":
            continue
        if max_risk == "medium" and risk == "high":
            continue

        rtc, usd = parse_reward(text)
        out.append(
            BountyLead(
                number=it["number"],
                title=title,
                url=it["html_url"],
                updated_at=it.get("updated_at", ""),
                capability_score=capability,
                risk_level=risk,
                reward_rtc=rtc,
                reward_usd=usd,
            )
        )

    return sorted(out, key=lambda l: (l.capability_score, l.reward_rtc), reverse=True)


def make_plan(issue: Dict[str, Any]) -> Dict[str, Any]:
    title = issue.get("title", "")
    text = f"{title} {issue.get('body', '')}"
    return {
        "issue": f"#{issue['number']}",
        "title": title,
        "steps": [
            "Inspect bounty details and confirm acceptance rules.",
            "Draft minimal implementation matching the requirement.",
            "Run a quick validation check and prepare evidence summary.",
        ],
        "risk": assess_risk(text),
        "capability_fit": assess_capability(text),
        "generated_at": now_iso(),
    }


def build_plan_markdown(issue: Dict[str, Any], plan: Dict[str, Any]) -> str:
    lines = [
        f"# Plan for #{issue['number']}: {issue.get('title', '')}",
        f"- URL: {issue.get('html_url')}",
        f"- Risk: {plan['risk']}",
        f"- Capability fit: {plan['capability_fit']}",
        "",
        "## Steps",
    ]
    for idx, step in enumerate(plan["steps"], 1):
        lines.append(f"{idx}. {step}")
    return "\n".join(lines)


# Legacy compatibility aliases for prior script behavior (keeps existing imports/tests stable).
def capability_fit(title: str, body: str = "") -> float:
    return assess_capability(f"{title} {body}")

def estimate_difficulty(title: str, body: str = "") -> str:
    lowered = f"{title} {body}".lower()
    if any(k in lowered for k in ("security", "hardening", "consensus", "wallet", "node")):
        return "high"
    if any(k in lowered for k in ("api", "integration", "script", "dashboard", "test")):
        return "medium"
    return "low"

def payout_signal_from_comments(comments: List[Dict[str, Any]]) -> str:
    text = "\n".join((c.get("body", "") or "").lower() for c in comments)
    if any(k in text for k in ("payout queued", "queued id", "pending id")):
        return "queued"
    if any(k in text for k in ("paid", "payout sent", "confirmed payout")):
        return "paid"
    if any(k in text for k in ("changes requested", "please update", "partial progress")):
        return "needs_update"
    return "none"

def classify_payout_action(merged: bool, pr_state: str, issue_state: str, payout_signal: str) -> str:
    if payout_signal == "paid":
        return "complete"
    if payout_signal == "queued":
        return "wait_payout_queue"
    if payout_signal == "needs_update":
        return "address_review"
    if merged:
        return "request_payout"
    if pr_state == "closed":
        return "check_followup"
    if issue_state == "closed":
        return "verify_closure"
    return "wait_for_review"

def discover_monitor_targets(owner: str, repo: str, handle: str, token: str = "", limit: int = 200) -> List[Dict[str, Any]]:
    query = urllib.parse.quote(f"repo:{owner}/{repo} commenter:{handle}")
    payload = gh_get(f"/search/issues?q={query}&per_page=100", token=token) if 'gh_get' in globals() else gh_request(f"/search/issues?q={query}&per_page=100", token=token)
    items = (payload.get("items", []) if isinstance(payload, dict) else [])

    out: List[Dict[str, Any]] = []
    seen = set()
    for item in items[:limit] if isinstance(items, list) else []:
        issue_no = item.get("number")
        repo_url = item.get("repository_url", "")
        issue_repo = repo_url.split("/repos/")[-1] if repo_url else ""
        if not issue_no or not issue_repo:
            continue

        comments = gh_get(f"/repos/{issue_repo}/issues/{issue_no}/comments?per_page=100", token=token)
        if not isinstance(comments, list):
            comments = []

        matched = False
        for c in comments:
            if ((c.get("user") or {}).get("login", "").lower() != handle.lower()):
                continue
            matched = True
            body = c.get("body", "") or ""
            for pr_repo, pr_no in re.findall(r"https://github.com/([^/\s]+/[^/\s]+)/pull/(\d+)", body):
                key = (issue_repo, int(issue_no), pr_repo, int(pr_no))
                if key in seen:
                    continue
                seen.add(key)
                out.append({"issue_repo": issue_repo, "issue": int(issue_no), "pr_repo": pr_repo, "pr": int(pr_no)})
        if not matched:
            key = (issue_repo, int(issue_no), issue_repo, None)
            if key not in seen:
                seen.add(key)
                out.append({"issue_repo": issue_repo, "issue": int(issue_no), "pr_repo": issue_repo, "pr": None})

    return out



def gh_get(path: str, token: str = "") -> Any:
    return gh_request(path, token)

def post_comment_payload(owner: str, repo: str, issue_no: int, body: str, token: str = "", dry_run: bool = True) -> Dict[str, Any]:
    target = f"{owner}/{repo}#{issue_no}"
    if dry_run:
        return {"mode": "dry-run", "target": target, "posted": False, "preview": body[:240]}

    if not token:
        return {"mode": "blocked", "target": target, "posted": False, "reason": "token required for live post"}

    req = urllib.request.Request(
        f"{API_BASE}/repos/{owner}/{repo}/issues/{issue_no}/comments",
        data=json.dumps({"body": body}).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "rustchain-bounty-hunter-m1",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        comment = json.loads(resp.read().decode("utf-8"))
    return {"mode": "live", "target": target, "posted": True, "comment_url": comment.get("html_url")}


def command_scan(args: argparse.Namespace) -> None:
    leads = scan_open_bounties(
        owner=args.owner,
        repo=args.repo,
        token=args.token,
        min_capability=args.min_capability,
        max_risk=args.max_risk,
        include_hardware=args.include_hardware,
    )
    payload = {
        "generated_at": now_iso(),
        "count": len(leads),
        "leads": [
            {
                "number": l.number,
                "title": l.title,
                "url": l.url,
                "updated_at": l.updated_at,
                "capability_score": l.capability_score,
                "risk_level": l.risk_level,
                "reward_rtc": l.reward_rtc,
                "reward_usd": l.reward_usd,
            }
            for l in leads
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_plan(args: argparse.Namespace) -> None:
    issue = gh_issue(args.owner, args.repo, args.issue, token=args.token)
    plan = make_plan(issue)
    payload = {
        "issue": issue.get("number"),
        "title": issue.get("title"),
        "plan": plan,
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(build_plan_markdown(issue, plan))


def command_post_comment(args: argparse.Namespace) -> None:
    payload = post_comment_payload(
        owner=args.owner,
        repo=args.repo,
        issue_no=args.issue,
        body=args.body,
        token=args.token,
        dry_run=args.dry_run,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser("RustChain bounty hunter M1")
    parser.add_argument("--token", default="", help="GitHub token (optional)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    scan_cmd = sub.add_parser("scan", help="scan open bounties")
    scan_cmd.add_argument("--owner", default=DEFAULT_OWNER)
    scan_cmd.add_argument("--repo", default=DEFAULT_REPO)
    scan_cmd.add_argument("--min-capability", type=float, default=0.0)
    scan_cmd.add_argument("--max-risk", choices=["low", "medium", "high"], default="high")
    scan_cmd.add_argument("--include-hardware", action="store_true", help="include high-risk/hardware tasks")
    scan_cmd.set_defaults(func=command_scan)

    plan_cmd = sub.add_parser("plan", help="build minimal plan for one bounty")
    plan_cmd.add_argument("--owner", default=DEFAULT_OWNER)
    plan_cmd.add_argument("--repo", default=DEFAULT_REPO)
    plan_cmd.add_argument("--issue", type=int, required=True)
    plan_cmd.add_argument("--format", choices=["json", "md"], default="json")
    plan_cmd.set_defaults(func=command_plan)

    post_cmd = sub.add_parser("post-comment", help="post issue comment")
    post_cmd.add_argument("--owner", default=DEFAULT_OWNER)
    post_cmd.add_argument("--repo", default=DEFAULT_REPO)
    post_cmd.add_argument("--issue", type=int, required=True)
    post_cmd.add_argument("--body", required=True)
    post_cmd.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="dry-run is default. use --no-dry-run for live posting",
    )
    post_cmd.set_defaults(func=command_post_comment)

    return parser.parse_args(list(argv))


def main() -> int:
    args = parse_args(sys.argv[1:])
    try:
        args.func(args)
        return 0
    except urllib.error.HTTPError as exc:
        print(json.dumps({"status": exc.code, "reason": str(exc), "mode": "error"}))
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"status": "network-error", "reason": str(exc), "mode": "error"}))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
