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
PR_URL_RE = re.compile(r"https://github\.com/([^/\s]+/[^/\s]+)/pull/(\d+)")
NUM_TOKEN_RE = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)([km])?\b", flags=re.IGNORECASE)


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


def gh_get_safe(path: str, token: str = "", fallback: Any = None) -> Any:
    try:
        return gh_get(path, token=token)
    except (HTTPError, URLError, TimeoutError, http.client.RemoteDisconnected):
        return fallback


def gh_post(path: str, payload: Dict[str, Any], token: str = "") -> Any:
    if not token:
        raise ValueError("GitHub token is required for POST actions")
    base = "https://api.github.com"
    url = path if path.startswith("http") else f"{base}{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "agent-bounty-hunter")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _pick(values: List[float], default: float = 0.0) -> float:
    return max(values) if values else default


def _suffix_multiplier(suffix: str) -> float:
    s = (suffix or "").lower()
    if s == "k":
        return 1000.0
    if s == "m":
        return 1_000_000.0
    return 1.0


def _extract_amounts(text: str, suffix_pattern: str) -> List[float]:
    values: List[float] = []
    for raw, suffix in re.findall(rf"{NUM_TOKEN_RE.pattern}\s*{suffix_pattern}", text, flags=re.IGNORECASE):
        value = float(raw.replace(",", "")) * _suffix_multiplier(suffix)
        values.append(value)
    return values


def _extract_usd_amounts(text: str) -> List[float]:
    values: List[float] = []
    for raw, suffix in re.findall(rf"\$\s*{NUM_TOKEN_RE.pattern}", text, flags=re.IGNORECASE):
        value = float(raw.replace(",", "")) * _suffix_multiplier(suffix)
        values.append(value)
    return values


def parse_reward(body: str, title: str) -> Tuple[float, float]:
    text = f"{title}\n{body or ''}"

    # Prefer explicit title declaration, e.g. "(75 RTC)" / "($200)".
    title_rtc = _extract_amounts(title or "", r"RTC(?:\)|\b)") if "pool" not in (title or "").lower() else []
    title_usd = _extract_usd_amounts(title or "")

    reward_rtc = _pick(title_rtc, 0.0)
    reward_usd = _pick(title_usd, 0.0)

    # Fallback to body/title line cues; avoid "pool/prize pool" overestimation.
    if reward_rtc == 0.0 and reward_usd == 0.0:
        rtc_values: List[float] = []
        usd_values: List[float] = []
        for line in text.splitlines():
            low = line.lower()
            if "pool" in low:
                continue
            if any(k in low for k in ("reward", "bounty", "earn", "payout", "prize")):
                rtc_values.extend(_extract_amounts(line, r"RTC\b"))
                usd_values.extend(_extract_usd_amounts(line))
        reward_rtc = _pick(rtc_values, 0.0)
        reward_usd = _pick(usd_values, 0.0)

    # Pool-based bounty programs often represent shared budgets, not per-task payout.
    if reward_rtc == 0.0 and reward_usd == 0.0 and "pool" in (title or "").lower():
        return 0.0, 0.0

    # Last resort generic parse.
    if reward_rtc == 0.0 and reward_usd == 0.0:
        reward_rtc = _pick(_extract_amounts(text, r"RTC\b"), 0.0)
        reward_usd = _pick(_extract_usd_amounts(text), 0.0)
        # If only pool-like language exists, treat as unknown instead of overestimating.
        if "pool" in text.lower() and not re.search(r"(?i)\b(reward|earn|payout)\b", text):
            reward_rtc = 0.0
            reward_usd = 0.0

    if reward_usd == 0 and reward_rtc > 0:
        reward_usd = reward_rtc * RTC_USD_REF
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
        pr_no = t.get("pr")
        label = t.get("label", f"{issue_repo}#{issue_no}")

        issue = gh_get_safe(f"/repos/{issue_repo}/issues/{issue_no}", token, fallback={})
        issue_comments = gh_get_safe(f"/repos/{issue_repo}/issues/{issue_no}/comments?per_page=100", token, fallback=[])
        payout_signal = payout_signal_from_comments(issue_comments if isinstance(issue_comments, list) else [])

        merged = False
        pr_state = "missing"
        if pr_no is not None:
            pr = gh_get_safe(f"/repos/{pr_repo}/pulls/{pr_no}", token, fallback={})
            merged = bool(pr.get("merged", False)) if isinstance(pr, dict) else False
            pr_state = pr.get("state", "unknown") if isinstance(pr, dict) else "unknown"
        issue_state = issue.get("state", "unknown")

        payout_action = classify_payout_action(merged, pr_state, issue_state, payout_signal)

        rows.append(
            {
                "label": label,
                "issue": f"https://github.com/{issue_repo}/issues/{issue_no}",
                "pr": (f"https://github.com/{pr_repo}/pull/{pr_no}" if pr_no is not None else ""),
                "issue_state": issue_state,
                "pr_state": pr_state,
                "merged": merged,
                "payout_signal": payout_signal,
                "payout_action": payout_action,
            }
        )
    return rows


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
    search_q = urllib.parse.quote(f"repo:{owner}/{repo} commenter:{handle}")
    found = gh_get_safe(f"/search/issues?q={search_q}&per_page=100", token, fallback={})
    items = found.get("items", []) if isinstance(found, dict) else []
    if not isinstance(items, list):
        return []
    out: List[Dict[str, Any]] = []
    seen: set[Tuple[str, int, str, Optional[int]]] = set()
    for item in items[:limit]:
        issue_repo = ((item.get("repository_url", "") or "").split("/repos/")[-1]) if item.get("repository_url") else ""
        issue_no = item.get("number")
        if not issue_repo or not issue_no:
            continue
        comments = gh_get_safe(f"/repos/{issue_repo}/issues/{issue_no}/comments?per_page=100", token, fallback=[])
        if not isinstance(comments, list):
            continue
        for c in comments:
            user = ((c.get("user") or {}).get("login") or "").lower()
            if user != handle.lower():
                continue
            body = c.get("body", "") or ""
            prs = PR_URL_RE.findall(body)
            if not prs:
                key = (issue_repo, int(issue_no), issue_repo, None)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"issue_repo": issue_repo, "issue": int(issue_no), "pr_repo": issue_repo, "pr": None})
                continue
            for pr_repo, pr_no_str in prs:
                pr_no = int(pr_no_str)
                key = (issue_repo, int(issue_no), pr_repo, pr_no)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"issue_repo": issue_repo, "issue": int(issue_no), "pr_repo": pr_repo, "pr": pr_no})
    return out


def post_issue_comment(
    owner: str,
    repo: str,
    issue_no: int,
    body: str,
    token: str = "",
    dry_run: bool = True,
    confirm: bool = False,
) -> Dict[str, Any]:
    if dry_run or not confirm:
        return {
            "mode": "dry-run",
            "target": f"{owner}/{repo}#{issue_no}",
            "body_preview": body[:280],
            "posted": False,
        }
    posted = gh_post(f"/repos/{owner}/{repo}/issues/{issue_no}/comments", {"body": body}, token=token)
    return {
        "mode": "live",
        "target": f"{owner}/{repo}#{issue_no}",
        "posted": True,
        "comment_url": posted.get("html_url", ""),
    }


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
    p_monitor.add_argument("--targets-json", default="", help="path to JSON list of monitoring targets")
    p_monitor.add_argument("--auto-discover", action="store_true", help="discover targets from claimant comments")
    p_monitor.add_argument("--owner", default="Scottcjn")
    p_monitor.add_argument("--repo", default="rustchain-bounties")
    p_monitor.add_argument("--handle", default="David-code-tang")
    p_monitor.add_argument("--limit", type=int, default=200)

    p_post = sub.add_parser("post-comment", help="post issue comment with dry-run safety gate")
    p_post.add_argument("--owner", default="Scottcjn")
    p_post.add_argument("--repo", default="rustchain-bounties")
    p_post.add_argument("--issue", type=int, required=True)
    p_post.add_argument("--body", required=True)
    p_post.add_argument("--confirm", action="store_true", help="required with --no-dry-run for live posting")
    p_post.add_argument("--no-dry-run", action="store_true", help="enable live post (requires token + --confirm)")

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
        targets: List[Dict[str, Any]] = []
        if args.targets_json:
            with open(args.targets_json, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    targets.extend(loaded)
        if args.auto_discover:
            targets.extend(
                discover_monitor_targets(
                    owner=args.owner,
                    repo=args.repo,
                    handle=args.handle,
                    token=args.token,
                    limit=args.limit,
                )
            )
        if not targets:
            print_json({"generated_at": now_utc(), "rows": [], "note": "no monitor targets found"})
            return 0
        rows = monitor_targets(targets, token=args.token)
        print_json({"generated_at": now_utc(), "rows": rows})
        return 0

    if args.cmd == "post-comment":
        dry_run = not args.no_dry_run
        posted = post_issue_comment(
            owner=args.owner,
            repo=args.repo,
            issue_no=args.issue,
            body=args.body,
            token=args.token,
            dry_run=dry_run,
            confirm=args.confirm,
        )
        print_json(posted)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
