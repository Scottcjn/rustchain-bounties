#!/usr/bin/env python3
"""Auto-triage community bounty claims and update ledger issue block.

This script is designed for GitHub Actions. It checks claim comments on
configured bounty issues and marks each recent claim as:
- `eligible`
- `needs-action`

It does not queue payouts directly. It generates an audit-friendly report that
maintainers can use to process payments quickly and consistently.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set


DEFAULT_TARGETS = [
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 87,
        "min_account_age_days": 30,
        "required_stars": ["Rustchain", "bottube"],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": False,
        "name": "Community Support",
    },
    {
        "owner": "Scottcjn",
        "repo": "Rustchain",
        "issue": 47,
        "min_account_age_days": 30,
        "required_stars": ["Rustchain"],
        "require_wallet": True,
        "require_bottube_username": False,
        "require_proof_link": False,
        "name": "Rustchain Star",
    },
    {
        "owner": "Scottcjn",
        "repo": "bottube",
        "issue": 74,
        "min_account_age_days": 30,
        "required_stars": ["bottube"],
        "require_wallet": False,
        "require_bottube_username": True,
        "require_proof_link": False,
        "name": "BoTTube Star+Join",
    },
    {
        "owner": "Scottcjn",
        "repo": "rustchain-bounties",
        "issue": 103,
        "min_account_age_days": 30,
        "required_stars": [],
        "require_wallet": True,
        "require_bottube_username": True,
        "require_proof_link": True,
        "name": "X + BoTTube Social",
    },
]

MARKER_START = "<!-- auto-triage-report:start -->"
MARKER_END = "<!-- auto-triage-report:end -->"


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _gh_request(
    method: str,
    path: str,
    token: str,
    data: Optional[Dict[str, Any]] = None,
) -> Any:
    base = "https://api.github.com"
    url = path if path.startswith("http") else f"{base}{path}"
    payload = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method=method.upper())
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "elyan-auto-triage")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _gh_paginated(path: str, token: str) -> List[Dict[str, Any]]:
    page = 1
    out: List[Dict[str, Any]] = []
    while True:
        sep = "&" if "?" in path else "?"
        p = f"{path}{sep}per_page=100&page={page}"
        chunk = _gh_request("GET", p, token)
        if not isinstance(chunk, list) or not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def _extract_wallet(body: str) -> Optional[str]:
    # Strip light markdown formatting so patterns like **Wallet:** work.
    body = re.sub(r"[*_`]", "", body)
    patterns = [
        r"(?im)^\s*(?:rtc\s*)?wallet(?:\s*(?:name|id|address))?\s*[:\-]\s*`?([A-Za-z0-9_\-]{3,64})`?\s*$",
        r"(?im)wallet(?:\s*(?:name|id|address))?\s*[:\-]\s*`?([A-Za-z0-9_\-]{3,64})`?",
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return m.group(1).strip()
    return None


def _extract_bottube_user(body: str) -> Optional[str]:
    body = re.sub(r"[*_`]", "", body)
    patterns = [
        r"(?im)^\s*bottube(?:\s*(?:username|user|account))?\s*[:\-]\s*`?([A-Za-z0-9_\-]{2,64})`?\s*$",
        r"(?im)bottube(?:\s*(?:username|user|account))?\s*[:\-]\s*`?([A-Za-z0-9_\-]{2,64})`?",
        r"https?://(?:www\.)?bottube\.ai/@([A-Za-z0-9_\-]{2,64})",
        r"https?://(?:www\.)?bottube\.ai/agent/([A-Za-z0-9_\-]{2,64})",
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return m.group(1).strip()
    return None


def _has_proof_link(body: str) -> bool:
    return bool(re.search(r"https?://", body))


def _wallet_looks_external(wallet: str) -> bool:
    # Heuristic: very long base58/base62 tokens are usually external chain
    # addresses, not RTC wallet names used in these bounties.
    if re.fullmatch(r"[1-9A-HJ-NP-Za-km-z]{28,64}", wallet):
        return True
    if re.fullmatch(r"[A-Za-z0-9]{30,64}", wallet):
        return True
    return False


def _looks_like_claim(body: str) -> bool:
    text = body.lower()
    tokens = [
        "claim",
        "starred",
        "wallet",
        "proof",
        "bounty",
        "rtc",
    ]
    return any(t in text for t in tokens)


def _status_label(blockers: List[str]) -> str:
    return "eligible" if not blockers else "needs-action"


@dataclass
class ClaimResult:
    user: str
    issue_ref: str
    comment_url: str
    created_at: str
    account_age_days: Optional[int]
    wallet: Optional[str]
    bottube_user: Optional[str]
    blockers: List[str]

    @property
    def status(self) -> str:
        return _status_label(self.blockers)


def _build_report_md(
    generated_at: str,
    results_by_issue: Dict[str, List[ClaimResult]],
    since_hours: int,
) -> str:
    lines: List[str] = []
    lines.append(f"### Auto-Triage Report ({generated_at})")
    lines.append(f"Window: last `{since_hours}`h")
    lines.append("")
    for issue_ref, rows in results_by_issue.items():
        lines.append(f"#### {issue_ref}")
        if not rows:
            lines.append("_No recent claim comments._")
            lines.append("")
            continue
        lines.append(
            "| User | Status | Age(d) | Wallet | BoTTube | Blockers | Comment |"
        )
        lines.append("|---|---|---:|---|---|---|---|")
        for r in rows:
            age = "" if r.account_age_days is None else str(r.account_age_days)
            wallet = r.wallet or ""
            bt = r.bottube_user or ""
            blockers = ", ".join(r.blockers) if r.blockers else ""
            lines.append(
                f"| @{r.user} | `{r.status}` | {age} | `{wallet}` | `{bt}` | {blockers} | [link]({r.comment_url}) |"
            )
        lines.append("")
    return "\n".join(lines).strip()


def main() -> int:
    token = _env("GITHUB_TOKEN")
    since_hours = int(_env("SINCE_HOURS", "72"))
    targets_json = os.environ.get("TRIAGE_TARGETS_JSON", "").strip()
    if targets_json:
        targets = json.loads(targets_json)
    else:
        targets = DEFAULT_TARGETS

    # Build star cache only for repos we need.
    required_star_repos: Set[str] = set()
    for t in targets:
        for repo in t.get("required_stars", []):
            required_star_repos.add(repo)

    star_cache: Dict[str, Set[str]] = {}
    for repo in sorted(required_star_repos):
        users = _gh_paginated(f"/repos/Scottcjn/{repo}/stargazers", token)
        star_cache[repo] = {u.get("login") for u in users if u.get("login")}

    user_cache: Dict[str, Dict[str, Any]] = {}
    cutoff = _now_utc() - timedelta(hours=since_hours)

    results_by_issue: Dict[str, List[ClaimResult]] = {}
    for target in targets:
        owner = target["owner"]
        repo = target["repo"]
        issue = int(target["issue"])
        min_age = int(target.get("min_account_age_days", 0))
        req_wallet = bool(target.get("require_wallet", True))
        req_bt = bool(target.get("require_bottube_username", False))
        req_proof = bool(target.get("require_proof_link", False))
        req_stars = list(target.get("required_stars", []))

        issue_ref = f"{owner}/{repo}#{issue}"
        issue_obj = _gh_request("GET", f"/repos/{owner}/{repo}/issues/{issue}", token)
        comments_url = issue_obj["comments_url"]
        comments = _gh_paginated(comments_url, token)

        # Merge multi-comment claims per user (users often add follow-ups).
        per_user: Dict[str, Dict[str, Any]] = {}
        for c in comments:
            user = (c.get("user") or {}).get("login")
            if not user:
                continue
            # Ignore maintainer/system messages
            if user.lower() in {"scottcjn", "github-actions[bot]"}:
                continue
            created = c.get("created_at")
            if not created:
                continue
            created_dt = _parse_iso(created)
            if created_dt < cutoff:
                continue

            body = c.get("body") or ""
            if not _looks_like_claim(body):
                continue

            if user not in per_user:
                per_user[user] = {
                    "bodies": [],
                    "latest_created": created,
                    "latest_url": c.get("html_url") or "",
                }
            per_user[user]["bodies"].append(body)
            if _parse_iso(per_user[user]["latest_created"]) <= created_dt:
                per_user[user]["latest_created"] = created
                per_user[user]["latest_url"] = c.get("html_url") or ""

        rows: List[ClaimResult] = []
        for user, info in per_user.items():
            if user not in user_cache:
                try:
                    u = _gh_request("GET", f"/users/{user}", token)
                    created_at = u.get("created_at")
                    age_days = None
                    if created_at:
                        age_days = (_now_utc() - _parse_iso(created_at)).days
                    user_cache[user] = {"age_days": age_days}
                except urllib.error.HTTPError:
                    user_cache[user] = {"age_days": None}

            age_days = user_cache[user]["age_days"]
            merged_body = "\n\n".join(info["bodies"])
            wallet = _extract_wallet(merged_body)
            bottube_user = _extract_bottube_user(merged_body)
            blockers: List[str] = []

            if age_days is not None and age_days < min_age:
                blockers.append(f"account_age<{min_age}")
            if req_wallet and not wallet:
                blockers.append("missing_wallet")
            if wallet and _wallet_looks_external(wallet):
                blockers.append("wallet_external_format")
            if req_bt and not bottube_user:
                blockers.append("missing_bottube_username")
            if req_proof and not _has_proof_link(merged_body):
                blockers.append("missing_proof_link")

            for star_repo in req_stars:
                if user not in star_cache.get(star_repo, set()):
                    blockers.append(f"missing_star:{star_repo}")

            rows.append(
                ClaimResult(
                    user=user,
                    issue_ref=issue_ref,
                    comment_url=info["latest_url"],
                    created_at=info["latest_created"],
                    account_age_days=age_days,
                    wallet=wallet,
                    bottube_user=bottube_user,
                    blockers=blockers,
                )
            )

        # Deterministic ordering
        rows.sort(key=lambda r: (r.status != "eligible", r.user.lower()))
        results_by_issue[issue_ref] = rows

    generated_at = _now_utc().isoformat().replace("+00:00", "Z")
    report = _build_report_md(generated_at, results_by_issue, since_hours)
    print(report)

    ledger_repo = os.environ.get("LEDGER_REPO", "").strip()
    ledger_issue = os.environ.get("LEDGER_ISSUE", "").strip()
    if ledger_repo and ledger_issue:
        issue_path = f"/repos/Scottcjn/{ledger_repo}/issues/{int(ledger_issue)}"
        ledger = _gh_request("GET", issue_path, token)
        body = ledger.get("body") or ""
        new_block = f"{MARKER_START}\n{report}\n{MARKER_END}"
        if MARKER_START in body and MARKER_END in body:
            start = body.index(MARKER_START)
            end = body.index(MARKER_END) + len(MARKER_END)
            updated = f"{body[:start]}{new_block}{body[end:]}"
        else:
            updated = f"{body}\n\n{new_block}\n"
        _gh_request("PATCH", issue_path, token, data={"body": updated})
        print(f"\nUpdated ledger issue: Scottcjn/{ledger_repo}#{ledger_issue}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - runtime safety for actions logs
        print(f"auto-triage failed: {exc}", file=sys.stderr)
        raise
