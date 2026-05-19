#!/usr/bin/env python3
"""Verify bounty claim comments and post an audit-friendly result.

This script is intended for the Bounty Verification Bot workflow. It reacts to
new or edited issue comments, extracts common claim fields, checks public GitHub
and RustChain signals, then posts or updates one bot report for that comment.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Callable, Iterable, Optional

OWNER = "Scottcjn"
REPO = "rustchain-bounties"
BOT_MARKER = "<!-- bounty-claim-verifier"
GITHUB_API = "https://api.github.com"
DEFAULT_RUSTCHAIN_BALANCE_URL = "https://rustchain.org/wallet/balance"
RUSTCHAIN_BALANCE_URL = os.environ.get("RUSTCHAIN_BALANCE_URL", DEFAULT_RUSTCHAIN_BALANCE_URL)
CLAIM_WORDS = ("claim", "claiming", "wallet", "miner", "stars", "github", "proof")
AUTOMATION_USERS = {"github-actions[bot]", "github-actions"}

WALLET_RE = re.compile(
    r"(?i)\b(?:wallet|wallet\s+address|miner[_\-\s]?id|address)\s*[:=]\s*([A-Za-z0-9_\-]{3,96})"
)
URL_RE = re.compile(r"https?://[^\s<>)\]]+")


@dataclass
class Check:
    name: str
    status: str
    detail: str


@dataclass
class Claim:
    user: str
    issue_number: int
    comment_id: int
    comment_url: str
    body: str
    wallet: str
    urls: list[str]


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return " ".join(self.parts)


def looks_like_claim(body: str) -> bool:
    text = body.lower()
    return any(word in text for word in CLAIM_WORDS) or bool(URL_RE.search(body))


def should_skip_comment(claim: "Claim") -> bool:
    if BOT_MARKER in claim.body:
        return True
    return claim.user.lower() in AUTOMATION_USERS


def extract_wallet(body: str) -> str:
    match = WALLET_RE.search(body)
    if match:
        return match.group(1).strip(".,;:)")
    rtc = re.search(r"\bRTC[a-fA-F0-9]{40}\b", body)
    return rtc.group(0) if rtc else ""


def extract_urls(body: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_RE.finditer(body):
        url = match.group(0).rstrip(".,;)")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def claim_from_event(event: dict[str, Any]) -> Claim:
    issue = event["issue"]
    comment = event["comment"]
    body = comment.get("body") or ""
    user = comment.get("user", {}).get("login", "")
    return Claim(
        user=user,
        issue_number=int(issue["number"]),
        comment_id=int(comment["id"]),
        comment_url=comment.get("html_url", ""),
        body=body,
        wallet=extract_wallet(body),
        urls=extract_urls(body),
    )


class GitHubClient:
    def __init__(self, token: str, opener: Callable[..., Any] = urllib.request.urlopen) -> None:
        self.token = token
        self.opener = opener

    def request(self, method: str, url: str, data: Optional[dict[str, Any]] = None) -> tuple[int, Any]:
        payload = None if data is None else json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method=method.upper())
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "rustchain-bounty-claim-verifier")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if payload is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with self.opener(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = raw
            return exc.code, body

    def get_paginated(self, path: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        page = 1
        while True:
            sep = "&" if "?" in path else "?"
            status, data = self.request("GET", f"{GITHUB_API}{path}{sep}per_page=100&page={page}")
            if status != 200 or not isinstance(data, list) or not data:
                break
            out.extend(data)
            if len(data) < 100:
                break
            page += 1
        return out

    def follows_owner(self, user: str) -> bool:
        status, _ = self.request("GET", f"{GITHUB_API}/users/{user}/following/{OWNER}")
        return status == 204

    def scottcjn_starred_repos(self, user: str) -> list[str]:
        stars = self.get_paginated(f"/users/{user}/starred")
        repos = []
        for repo in stars:
            owner = repo.get("owner", {}).get("login", "")
            if owner.lower() == OWNER.lower():
                repos.append(repo.get("name", ""))
        return sorted(set(filter(None, repos)))

    def issue_comments(self, issue_number: int) -> list[dict[str, Any]]:
        return self.get_paginated(f"/repos/{OWNER}/{REPO}/issues/{issue_number}/comments")

    def post_or_update_report(self, issue_number: int, comment_id: int, body: str) -> None:
        marker = f"{BOT_MARKER} comment:{comment_id} -->"
        comments = self.issue_comments(issue_number)
        existing = next((c for c in comments if marker in (c.get("body") or "")), None)
        if existing:
            self.request("PATCH", f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/comments/{existing['id']}", {"body": body})
        else:
            self.request("POST", f"{GITHUB_API}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments", {"body": body})


def check_wallet_exists(wallet: str, opener: Callable[..., Any] = urllib.request.urlopen) -> Check:
    if not wallet:
        return Check("Wallet", "needs-action", "No wallet or miner id found in the claim comment.")
    url = f"{RUSTCHAIN_BALANCE_URL}?{urllib.parse.urlencode({'miner_id': wallet})}"
    req = urllib.request.Request(url, headers={"User-Agent": "rustchain-bounty-claim-verifier"})
    try:
        with opener(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            if resp.status == 200:
                return Check("Wallet", "verified", f"`{wallet}` returned HTTP 200.")
            return Check("Wallet", "needs-review", f"`{wallet}` returned HTTP {resp.status}: {text[:120]}")
    except Exception as exc:
        return Check("Wallet", "needs-review", f"`{wallet}` could not be verified: {exc}")


def check_url_live(url: str, opener: Callable[..., Any] = urllib.request.urlopen) -> Check:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "rustchain-bounty-claim-verifier"})
    try:
        with opener(req, timeout=20) as resp:
            if 200 <= resp.status < 400:
                return Check("URL", "verified", f"{url} returned HTTP {resp.status}.")
            return Check("URL", "needs-review", f"{url} returned HTTP {resp.status}.")
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            return check_url_get(url, opener)
        return Check("URL", "needs-review", f"{url} returned HTTP {exc.code}.")
    except Exception as exc:
        return Check("URL", "needs-review", f"{url} could not be reached: {exc}")


def check_url_get(url: str, opener: Callable[..., Any] = urllib.request.urlopen) -> Check:
    req = urllib.request.Request(url, headers={"User-Agent": "rustchain-bounty-claim-verifier"})
    try:
        with opener(req, timeout=20) as resp:
            return Check("URL", "verified" if 200 <= resp.status < 400 else "needs-review", f"{url} GET returned HTTP {resp.status}.")
    except Exception as exc:
        return Check("URL", "needs-review", f"{url} GET failed: {exc}")


def devto_word_count(url: str, opener: Callable[..., Any] = urllib.request.urlopen) -> Check:
    if "dev.to/" not in url:
        return Check("Article word count", "skipped", "No dev.to article URL found.")
    req = urllib.request.Request(url, headers={"User-Agent": "rustchain-bounty-claim-verifier"})
    try:
        with opener(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return Check("Article word count", "needs-review", f"Could not fetch dev.to article: {exc}")
    parser = TextExtractor()
    parser.feed(html)
    words = re.findall(r"\b[\w'-]+\b", parser.text())
    status = "verified" if len(words) >= 800 else "needs-action"
    return Check("Article word count", status, f"Estimated {len(words)} words from dev.to page.")


def duplicate_claim_check(claim: Claim, comments: Iterable[dict[str, Any]]) -> Check:
    duplicate_users = 0
    duplicate_wallets = 0
    paid_mentions = 0
    wallet_lower = claim.wallet.lower()
    for comment in comments:
        body = comment.get("body") or ""
        if BOT_MARKER in body or int(comment.get("id", 0)) == claim.comment_id:
            continue
        user = comment.get("user", {}).get("login", "")
        if user.lower() == claim.user.lower() and looks_like_claim(body):
            duplicate_users += 1
        if wallet_lower and wallet_lower in body.lower():
            duplicate_wallets += 1
        if "paid" in body.lower() and (claim.user.lower() in body.lower() or (wallet_lower and wallet_lower in body.lower())):
            paid_mentions += 1
    if paid_mentions:
        return Check("Duplicate/Paid", "needs-review", "Possible prior PAID mention found for this user or wallet.")
    if duplicate_users or duplicate_wallets:
        return Check("Duplicate/Paid", "needs-review", f"Prior related claims: user={duplicate_users}, wallet={duplicate_wallets}.")
    return Check("Duplicate/Paid", "verified", "No earlier matching claim or PAID marker found on this issue.")


def build_checks(claim: Claim, gh: GitHubClient, opener: Callable[..., Any] = urllib.request.urlopen) -> list[Check]:
    checks: list[Check] = []
    follows = gh.follows_owner(claim.user)
    checks.append(Check("GitHub follow", "verified" if follows else "needs-action", f"@{claim.user} {'follows' if follows else 'does not follow'} @{OWNER}."))
    starred = gh.scottcjn_starred_repos(claim.user)
    checks.append(Check("Scottcjn stars", "verified" if starred else "needs-action", f"{len(starred)} Scottcjn repos starred: {', '.join(starred[:8]) or 'none'}."))
    checks.append(check_wallet_exists(claim.wallet, opener))
    checks.append(duplicate_claim_check(claim, gh.issue_comments(claim.issue_number)))
    for url in claim.urls[:5]:
        checks.append(check_url_live(url, opener))
    devto = next((url for url in claim.urls if "dev.to/" in url), "")
    checks.append(devto_word_count(devto, opener) if devto else Check("Article word count", "skipped", "No dev.to article URL found."))
    return checks


def render_report(claim: Claim, checks: list[Check]) -> str:
    marker = f"{BOT_MARKER} comment:{claim.comment_id} -->"
    rows = "\n".join(
        f"| {escape_cell(check.name)} | {escape_cell(check.status)} | {escape_cell(check.detail)} |" for check in checks
    )
    blockers = [check for check in checks if check.status == "needs-action"]
    review = [check for check in checks if check.status == "needs-review"]
    summary = "verified" if not blockers and not review else "needs maintainer review" if review else "needs claimant action"
    return "\n".join([
        marker,
        "## Automated Bounty Claim Verification",
        "",
        f"Claim comment: {claim.comment_url or f'#{claim.comment_id}'}",
        f"Claimant: @{claim.user}",
        f"Wallet/miner id: `{claim.wallet or 'not found'}`",
        f"Summary: **{summary}**",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
        rows,
        "",
        "This bot does not authorize payouts. Maintainers should review `needs-review` rows before marking a claim paid.",
    ])


def escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.event_path:
        raise SystemExit("GITHUB_EVENT_PATH or --event-path is required")
    with open(args.event_path, "r", encoding="utf-8") as fh:
        event = json.load(fh)
    claim = claim_from_event(event)
    if should_skip_comment(claim):
        print("Comment is an automated verifier report; skipping.")
        return 0
    if not looks_like_claim(claim.body):
        print("Comment does not look like a bounty claim; skipping.")
        return 0

    gh = GitHubClient(os.environ.get("GITHUB_TOKEN", ""))
    checks = build_checks(claim, gh)
    report = render_report(claim, checks)
    if args.dry_run:
        print(report)
        return 0
    gh.post_or_update_report(claim.issue_number, claim.comment_id, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
