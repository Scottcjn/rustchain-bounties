#!/usr/bin/env python3
"""
RustChain Bounty Verification Bot

Auto-verifies star/badge/follow/emoji claims on rustchain-bounties issues.
Runs as a GitHub Action every 6 hours, or manually via workflow_dispatch.

Checks:
  1. Star claims   - Did the user star the specified repos?
  2. Badge claims   - Does the user's profile README mention RustChain/Elyan?
  3. Follow claims  - Does the user follow Scottcjn?
  4. Emoji claims   - Did the user react to the specified issue?

Posts a verification comment on the bounty issue with results.
"""

import os
import sys
import json
import time
import base64
import re
import logging
from datetime import datetime, timezone
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    sys.exit("GITHUB_TOKEN environment variable is required")

OWNER = "Scottcjn"
BOUNTY_REPO = "rustchain-bounties"

# Repos we track stars on (case-sensitive as they appear on GitHub)
STAR_REPOS = [
    "Rustchain",
    "bottube",
    "rustchain-bounties",
    "beacon-skill",
    "grazer-skill",
    "ram-coffers",
    "llama-power8",
    "elyan-site",
    "rust-ppc-tiger",
    "rustchain-mcp",
    "shaprai",
    "beacon-rs",
    "trashclaw",
]

# Issue numbers by bounty type
STAR_BOUNTY_ISSUES = [2175, 47, 773, 1595]
BADGE_BOUNTY_ISSUES = [2177]
FOLLOW_BOUNTY_ISSUES = [2173, 2155]
EMOJI_BOUNTY_ISSUES = [1611, 2180]
# Issue #747 — Bounty Verification Bot (multi-check: star+follow+wallet+article+duplicate)
BOT_BOUNTY_ISSUES = [747]

# Bot signature so we can detect our own comments and avoid duplicates
BOT_SIGNATURE = "<!-- bounty-verify-bot -->"
BOT_TAG = "Bounty Verification Bot"

# Rate-limit safety: sleep between paginated API calls
API_SLEEP = 0.25  # seconds

# Badge keywords (case-insensitive) that count as a RustChain profile badge
BADGE_KEYWORDS = [
    "rustchain",
    "elyan labs",
    "elyanlabs",
    "rtc token",
    "proof of antiquity",
    "rustchain-bounties",
    "bottube",
]

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("verify-bounties")

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
})


def gh_get(url: str, params: dict | None = None) -> requests.Response:
    """GET with rate-limit awareness."""
    r = SESSION.get(url, params=params or {})
    remaining = int(r.headers.get("X-RateLimit-Remaining", 999))
    if remaining < 50:
        reset_ts = int(r.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset_ts - int(time.time()), 1)
        log.warning("Rate limit low (%d remaining), sleeping %ds", remaining, wait)
        time.sleep(wait)
    elif remaining < 200:
        time.sleep(API_SLEEP)
    return r


def paginate_all(url: str, params: dict | None = None) -> list:
    """Paginate through all results for a GitHub API endpoint."""
    results = []
    params = dict(params or {})
    params.setdefault("per_page", 100)
    page = 1
    while True:
        params["page"] = page
        r = gh_get(url, params)
        if r.status_code != 200:
            log.warning("API %s returned %d: %s", url, r.status_code, r.text[:200])
            break
        data = r.json()
        if not data:
            break
        results.extend(data)
        if len(data) < int(params["per_page"]):
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# Verification functions
# ---------------------------------------------------------------------------

def get_stargazers(repo: str) -> set[str]:
    """Return set of usernames who starred OWNER/repo."""
    users = paginate_all(f"https://api.github.com/repos/{OWNER}/{repo}/stargazers")
    return {u["login"] for u in users if isinstance(u, dict) and "login" in u}


def get_all_stargazers() -> dict[str, set[str]]:
    """Return {repo: set(usernames)} for all tracked repos."""
    result = {}
    for repo in STAR_REPOS:
        log.info("Fetching stargazers for %s/%s ...", OWNER, repo)
        result[repo] = get_stargazers(repo)
        log.info("  -> %d stargazers", len(result[repo]))
    return result


def check_profile_badge(username: str) -> tuple[bool, str]:
    """Check if user's profile README mentions RustChain/Elyan.
    Returns (found, detail_string).
    """
    r = gh_get(f"https://api.github.com/repos/{username}/{username}/contents/README.md")
    if r.status_code == 404:
        return False, "No profile README found"
    if r.status_code != 200:
        return False, f"Could not fetch profile README (HTTP {r.status_code})"

    try:
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
    except Exception as e:
        return False, f"Could not decode README: {e}"

    content_lower = content.lower()
    found_keywords = [kw for kw in BADGE_KEYWORDS if kw in content_lower]
    if found_keywords:
        return True, f"Found keywords: {', '.join(found_keywords)}"
    return False, "No RustChain/Elyan keywords found in profile README"


def check_follows_owner(username: str) -> bool:
    """Check if username follows OWNER."""
    r = gh_get(f"https://api.github.com/users/{username}/following/{OWNER}")
    return r.status_code == 204


# ---------------------------------------------------------------------------
# New verification functions: wallet, article URL, word count, duplicate detection
# ---------------------------------------------------------------------------

RUSTCHAIN_NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "http://50.28.86.131:8080")


def check_wallet_exists(wallet_address: str) -> tuple[bool, str]:
    """Check if an RTC wallet address exists on the RustChain node.
    Returns (exists, detail_string).
    """
    try:
        r = requests.get(
            f"{RUSTCHAIN_NODE_URL}/wallet/balance",
            params={"miner_id": wallet_address},
            timeout=10,
        )
        if r.status_code == 200:
            try:
                data = r.json()
                balance = data.get("balance", data.get("result", "N/A"))
                return True, f"Exists — Balance: {balance} RTC"
            except Exception:
                return True, "Exists (balance unknown)"
        elif r.status_code == 404:
            return False, "Wallet not found"
        else:
            return False, f"Node returned HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        return False, "Node request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Node unreachable"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"


def check_article_url(url: str) -> tuple[bool, int, str]:
    """Check if an article URL (dev.to, Medium, etc.) is live and return word count.
    Returns (is_live, word_count, platform).
    """
    if not url:
        return False, 0, "unknown"
    
    url_lower = url.lower()
    if "dev.to" in url_lower or url_lower.startswith("https://dev.to"):
        platform = "dev.to"
    elif "medium.com" in url_lower:
        platform = "Medium"
    elif "mirror.xyz" in url_lower:
        platform = "Mirror"
    else:
        platform = "unknown"

    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            # Try GET for sites that require it
            r = requests.get(url, timeout=10, allow_redirects=True, stream=True)
        if r.status_code == 200:
            # Estimate word count from content
            try:
                content = r.text
                # Strip HTML tags roughly
                text = re.sub(r'<[^>]+>', ' ', content)
                words = len(text.split())
                return True, words, platform
            except Exception:
                return True, 0, platform
        else:
            return False, 0, platform
    except Exception:
        return False, 0, platform


def find_paid_claimants() -> dict[str, float]:
    """Scan past bounty issues for 'PAID' markers and return {username: amount}.
    Used for duplicate-claim detection.
    """
    paid: dict[str, float] = {}
    all_bounty_issues = STAR_BOUNTY_ISSUES + BADGE_BOUNTY_ISSUES + FOLLOW_BOUNTY_ISSUES + EMOJI_BOUNTY_ISSUES
    for issue in all_bounty_issues:
        comments = get_issue_comments(issue)
        for c in comments:
            body = c.get("body", "")
            if "PAID" in body.upper():
                # Try to extract username and amount: "PAID @user X RTC" or "PAID X RTC to @user"
                match = re.search(r"(?:PAID|paid)[:\s]+(?:(\d+(?:\.\d+)?)\s*RTC)?\s*(?:to\s+)?@?([a-zA-Z0-9_-]+)", body, re.IGNORECASE)
                if match:
                    amount_str, username = match.group(1), match.group(2)
                    amount = float(amount_str) if amount_str else 0.0
                    if username:
                        paid[username.lower()] = amount
    return paid


def get_issue_reactions(issue_number: int) -> dict[str, set[str]]:
    """Return {reaction_type: set(usernames)} for an issue."""
    reactions = paginate_all(
        f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/{issue_number}/reactions",
        params={"per_page": 100},
    )
    result: dict[str, set[str]] = {}
    for rxn in reactions:
        if not isinstance(rxn, dict):
            continue
        content = rxn.get("content", "")
        user = rxn.get("user", {}).get("login", "")
        if content and user:
            result.setdefault(content, set()).add(user)
    return result


def get_issue_comments(issue_number: int) -> list[dict]:
    """Return all comments on a bounty issue."""
    return paginate_all(
        f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/{issue_number}/comments"
    )


def post_comment(issue_number: int, body: str) -> bool:
    """Post a comment on a bounty issue. Returns True on success."""
    r = SESSION.post(
        f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/{issue_number}/comments",
        json={"body": body},
    )
    if r.status_code == 201:
        log.info("Posted verification comment on issue #%d", issue_number)
        return True
    log.error("Failed to post comment on #%d: %d %s", issue_number, r.status_code, r.text[:200])
    return False


def update_comment(comment_id: int, body: str) -> bool:
    """Update an existing comment. Returns True on success."""
    r = SESSION.patch(
        f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/comments/{comment_id}",
        json={"body": body},
    )
    if r.status_code == 200:
        log.info("Updated verification comment %d", comment_id)
        return True
    log.error("Failed to update comment %d: %d %s", comment_id, r.status_code, r.text[:200])
    return False


# ---------------------------------------------------------------------------
# Claim parsing
# ---------------------------------------------------------------------------

# Patterns people use to claim bounties
# We look for GitHub usernames in comments that aren't from bots or the owner
GITHUB_USERNAME_RE = re.compile(r"@([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})")
WALLET_RE = re.compile(r"(RTC[a-f0-9]{40}|[a-z0-9_-]{3,40})", re.IGNORECASE)


def extract_claimants(comments: list[dict], issue_number: int) -> list[dict]:
    """Extract unique claimants from issue comments.

    A claimant is anyone who commented on the issue (excluding the bot and
    the repo owner) and appears to be making a claim. We track:
      - username: GitHub login
      - comment_id: the comment where they claimed
      - wallet: any RTC wallet address mentioned
      - comment_body: raw text for context
    """
    seen = set()
    claimants = []
    for c in comments:
        user = c.get("user", {}).get("login", "")
        body = c.get("body", "")

        # Skip bot's own comments
        if BOT_SIGNATURE in body:
            continue
        # Skip owner
        if user.lower() == OWNER.lower():
            continue
        # Skip empty
        if not user or not body.strip():
            continue
        # Deduplicate by username
        if user.lower() in seen:
            continue
        seen.add(user.lower())

        # Try to extract a wallet address from the comment
        wallet_match = WALLET_RE.search(body)
        wallet = wallet_match.group(1) if wallet_match else ""

        claimants.append({
            "username": user,
            "comment_id": c["id"],
            "wallet": wallet,
            "body": body,
        })

    return claimants


def find_existing_bot_comment(comments: list[dict]) -> Optional[int]:
    """Find the bot's existing verification comment ID, if any."""
    for c in comments:
        if BOT_SIGNATURE in c.get("body", ""):
            return c["id"]
    return None


# ---------------------------------------------------------------------------
# Verification runners
# ---------------------------------------------------------------------------

def verify_star_claims(issue_number: int, all_stars: dict[str, set[str]]) -> None:
    """Verify star claims on a bounty issue."""
    log.info("=== Verifying star claims on issue #%d ===", issue_number)

    comments = get_issue_comments(issue_number)
    claimants = extract_claimants(comments, issue_number)
    existing_comment = find_existing_bot_comment(comments)

    if not claimants:
        log.info("No claimants found on #%d, skipping", issue_number)
        return

    lines = [
        BOT_SIGNATURE,
        f"## Star Verification Report",
        f"*{BOT_TAG} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        f"Checked **{len(claimants)}** claim(s) against **{len(STAR_REPOS)}** repos.",
        "",
        "| User | Stars | Repos Starred | Status |",
        "|------|-------|---------------|--------|",
    ]

    for cl in claimants:
        username = cl["username"]
        starred_repos = []
        for repo in STAR_REPOS:
            if username in all_stars.get(repo, set()):
                starred_repos.append(repo)

        count = len(starred_repos)
        repo_list = ", ".join(starred_repos[:5])
        if len(starred_repos) > 5:
            repo_list += f" +{len(starred_repos) - 5} more"

        if count == 0:
            status = "No stars found"
        elif count < 3:
            status = f"Partial ({count} stars)"
        else:
            status = f"VERIFIED ({count} stars)"

        lines.append(f"| @{username} | {count}/{len(STAR_REPOS)} | {repo_list or 'None'} | {status} |")

    lines.extend([
        "",
        "---",
        f"*Repos checked: {', '.join(STAR_REPOS)}*",
        "*Stars can take a few minutes to propagate. Re-run if you just starred.*",
    ])

    body = "\n".join(lines)

    if existing_comment:
        update_comment(existing_comment, body)
    else:
        post_comment(issue_number, body)


def verify_badge_claims(issue_number: int) -> None:
    """Verify profile badge claims on a bounty issue."""
    log.info("=== Verifying badge claims on issue #%d ===", issue_number)

    comments = get_issue_comments(issue_number)
    claimants = extract_claimants(comments, issue_number)
    existing_comment = find_existing_bot_comment(comments)

    if not claimants:
        log.info("No claimants found on #%d, skipping", issue_number)
        return

    lines = [
        BOT_SIGNATURE,
        f"## Profile Badge Verification Report",
        f"*{BOT_TAG} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        f"Checked **{len(claimants)}** claim(s) for RustChain/Elyan mentions in profile README.",
        "",
        "| User | Badge Found | Details | Status |",
        "|------|-------------|---------|--------|",
    ]

    for cl in claimants:
        username = cl["username"]
        found, detail = check_profile_badge(username)
        status = "VERIFIED" if found else "NOT FOUND"
        lines.append(f"| @{username} | {'Yes' if found else 'No'} | {detail} | {status} |")

    lines.extend([
        "",
        "---",
        f"*Keywords checked: {', '.join(BADGE_KEYWORDS)}*",
        "*Add a RustChain badge/mention to your GitHub profile README to claim.*",
    ])

    body = "\n".join(lines)

    if existing_comment:
        update_comment(existing_comment, body)
    else:
        post_comment(issue_number, body)


def verify_follow_claims(issue_number: int) -> None:
    """Verify follow claims on a bounty issue."""
    log.info("=== Verifying follow claims on issue #%d ===", issue_number)

    comments = get_issue_comments(issue_number)
    claimants = extract_claimants(comments, issue_number)
    existing_comment = find_existing_bot_comment(comments)

    if not claimants:
        log.info("No claimants found on #%d, skipping", issue_number)
        return

    lines = [
        BOT_SIGNATURE,
        f"## Follow Verification Report",
        f"*{BOT_TAG} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        f"Checked **{len(claimants)}** claim(s) for following @{OWNER}.",
        "",
        "| User | Follows @{} | Status |".format(OWNER),
        "|------|-------------|--------|",
    ]

    for cl in claimants:
        username = cl["username"]
        follows = check_follows_owner(username)
        status = "VERIFIED" if follows else "NOT FOLLOWING"
        lines.append(f"| @{username} | {'Yes' if follows else 'No'} | {status} |")

    lines.extend([
        "",
        "---",
        f"*Follow [@{OWNER}](https://github.com/{OWNER}) to claim this bounty.*",
    ])

    body = "\n".join(lines)

    if existing_comment:
        update_comment(existing_comment, body)
    else:
        post_comment(issue_number, body)


def verify_emoji_claims(issue_number: int) -> None:
    """Verify emoji reaction claims on a bounty issue."""
    log.info("=== Verifying emoji claims on issue #%d ===", issue_number)

    comments = get_issue_comments(issue_number)
    claimants = extract_claimants(comments, issue_number)
    existing_comment = find_existing_bot_comment(comments)

    if not claimants:
        log.info("No claimants found on #%d, skipping", issue_number)
        return

    # Get reactions on the issue itself
    reactions = get_issue_reactions(issue_number)
    all_reactors = set()
    for users in reactions.values():
        all_reactors.update(users)

    # Also check reactions on comments (some bounties ask for comment reactions)
    comment_reactors: dict[str, set[str]] = {}
    for c in comments:
        cid = c["id"]
        cr = paginate_all(
            f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/comments/{cid}/reactions",
            params={"per_page": 100},
        )
        for rxn in cr:
            if not isinstance(rxn, dict):
                continue
            user = rxn.get("user", {}).get("login", "")
            content = rxn.get("content", "")
            if user and content:
                comment_reactors.setdefault(user, set()).add(content)
                all_reactors.add(user)

    lines = [
        BOT_SIGNATURE,
        f"## Emoji Reaction Verification Report",
        f"*{BOT_TAG} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        f"Checked **{len(claimants)}** claim(s) for reactions on issue #{issue_number}.",
        "",
    ]

    # Show issue-level reaction summary
    if reactions:
        lines.append("**Issue reactions:**")
        for emoji, users in sorted(reactions.items()):
            lines.append(f"- {emoji}: {', '.join(sorted(users))}")
        lines.append("")

    lines.extend([
        "| User | Reacted | Reactions | Status |",
        "|------|---------|-----------|--------|",
    ])

    for cl in claimants:
        username = cl["username"]
        # Check both issue reactions and comment reactions
        issue_rxns = [e for e, users in reactions.items() if username in users]
        comment_rxns = list(comment_reactors.get(username, set()))
        all_rxns = sorted(set(issue_rxns + comment_rxns))

        reacted = len(all_rxns) > 0
        status = "VERIFIED" if reacted else "NO REACTION"
        rxn_str = ", ".join(all_rxns) if all_rxns else "None"
        lines.append(f"| @{username} | {'Yes' if reacted else 'No'} | {rxn_str} | {status} |")

    lines.extend([
        "",
        "---",
        "*React to the issue or its comments with any emoji to claim.*",
    ])

    body = "\n".join(lines)

    if existing_comment:
        update_comment(existing_comment, body)
    else:
        post_comment(issue_number, body)


def verify_bot_bounty(issue_number: int, all_stars: dict[str, set[str]]) -> None:
    """Comprehensive bounty verification: stars + follow + wallet + article URL + duplicate detection.
    Per issue #747 requirements:
      - Star/follow verification: 30 RTC
      - Wallet existence check: +10 RTC
      - Article/URL verification: +10 RTC
      - Dev.to word count + quality: +10 RTC
      - Duplicate claim detection: +15 RTC
    """
    log.info("=== Verifying comprehensive bot bounty on issue #%d ===", issue_number)

    comments = get_issue_comments(issue_number)
    claimants = extract_claimants(comments, issue_number)
    existing_comment = find_existing_bot_comment(comments)

    if not claimants:
        log.info("No claimants found on #%d, skipping", issue_number)
        return

    # Pre-fetch paid claimants for duplicate detection
    log.info("Checking for previous payments (duplicate detection)...")
    paid_claimants = find_paid_claimants()
    log.info("Found %d previously paid claimants", len(paid_claimants))

    lines = [
        BOT_SIGNATURE,
        f"## Comprehensive Bounty Verification Report",
        f"*{BOT_TAG} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
        f"Checked **{len(claimants)}** claim(s) across all verification dimensions.",
        "",
        "| User | Stars ✅ | Follows ✅ | Wallet ✅ | Article ✅ | Paid Before ⚠️ | Suggested Payout |",
        "|------|----------|----------|---------|---------|-------------|----------------|",
    ]

    for cl in claimants:
        username = cl["username"]
        wallet = cl.get("wallet", "")
        body = cl.get("body", "")
        stars_ok = False
        stars_count = 0
        follows_ok = False
        wallet_ok = False
        wallet_detail = ""
        article_ok = False
        article_words = 0
        article_platform = ""
        was_paid = False
        paid_amount = 0.0

        # 1. Star check
        for repo in STAR_REPOS:
            if username in all_stars.get(repo, set()):
                stars_ok = True
                stars_count += 1
        if stars_ok:
            stars_count = sum(1 for repo in STAR_REPOS if username in all_stars.get(repo, set()))

        # 2. Follow check
        follows_ok = check_follows_owner(username)

        # 3. Wallet existence
        if wallet:
            wallet_ok, wallet_detail = check_wallet_exists(wallet)

        # 4. Article URL check (dev.to, Medium, Mirror)
        url_match = re.search(
            r"(https?://[^\s<>\"']+(?:dev\.to|medium\.com|mirror\.xyz)[^\s<>\"']*)",
            body, re.IGNORECASE
        )
        if url_match:
            article_url = url_match.group(1)
            article_ok, article_words, article_platform = check_article_url(article_url)

        # 5. Duplicate detection
        if username.lower() in paid_claimants:
            was_paid = True
            paid_amount = paid_claimants[username.lower()]

        # Calculate suggested payout
        payout_parts = []
        payout = 0.0
        if stars_ok:
            payout += 30.0
            payout_parts.append("30 RTC (stars/follow)")
        if wallet_ok:
            payout += 10.0
            payout_parts.append("+10 RTC (wallet)")
        if article_ok:
            payout += 10.0
            payout_parts.append("+10 RTC (article)")
        if was_paid:
            payout += 15.0
            payout_parts.append("+15 RTC (duplicate detection)")

        stars_icon = "✅" if stars_ok else "❌"
        follows_icon = "✅" if follows_ok else "❌"
        wallet_icon = "✅" if wallet_ok else ("❌" if wallet else "—")
        article_icon = f"✅ ({article_words}w, {article_platform})" if article_ok else ("❌" if url_match else "—")
        dup_icon = f"⚠️ YES ({paid_amount} RTC)" if was_paid else "—"
        payout_str = f"{payout:.0f} RTC" if payout > 0 else "—"

        lines.append(
            f"| @{username} | {stars_icon} ({stars_count}) | {follows_icon} | "
            f"{wallet_icon} {wallet_detail[:20]} | {article_icon} | {dup_icon} | {payout_str} |"
        )

    lines.extend([
        "",
        "---",
        "**Milestone Rewards:** Star/follow=30 RTC, Wallet=+10 RTC, Article=+10 RTC, Duplicate=+15 RTC",
        f"*Repos checked for stars: {', '.join(STAR_REPOS)}*",
        "*Stars can take a few minutes to propagate after starring.*",
    ])

    body = "\n".join(lines)

    if existing_comment:
        update_comment(existing_comment, body)
    else:
        post_comment(issue_number, body)


# ---------------------------------------------------------------------------
# Issue-state check: only process open issues
# ---------------------------------------------------------------------------

def is_issue_open(issue_number: int) -> bool:
    """Check if issue is still open."""
    r = gh_get(f"https://api.github.com/repos/{OWNER}/{BOUNTY_REPO}/issues/{issue_number}")
    if r.status_code != 200:
        log.warning("Could not fetch issue #%d: %d", issue_number, r.status_code)
        return False
    return r.json().get("state") == "open"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 60)
    log.info("RustChain Bounty Verification Bot starting")
    log.info("Owner: %s | Bounty repo: %s", OWNER, BOUNTY_REPO)
    log.info("=" * 60)

    # Pre-fetch all stargazers once (most expensive operation)
    log.info("--- Phase 1: Fetching stargazers ---")
    all_stars = get_all_stargazers()
    total_unique = len(set().union(*all_stars.values()))
    log.info("Total unique stargazers across %d repos: %d", len(STAR_REPOS), total_unique)

    # Star verification
    log.info("--- Phase 2: Star bounties ---")
    for issue in STAR_BOUNTY_ISSUES:
        if is_issue_open(issue):
            verify_star_claims(issue, all_stars)
        else:
            log.info("Issue #%d is closed, skipping", issue)

    # Badge verification
    log.info("--- Phase 3: Badge bounties ---")
    for issue in BADGE_BOUNTY_ISSUES:
        if is_issue_open(issue):
            verify_badge_claims(issue)
        else:
            log.info("Issue #%d is closed, skipping", issue)

    # Follow verification
    log.info("--- Phase 4: Follow bounties ---")
    for issue in FOLLOW_BOUNTY_ISSUES:
        if is_issue_open(issue):
            verify_follow_claims(issue)
        else:
            log.info("Issue #%d is closed, skipping", issue)

    # Emoji verification
    log.info("--- Phase 5: Emoji bounties ---")
    for issue in EMOJI_BOUNTY_ISSUES:
        if is_issue_open(issue):
            verify_emoji_claims(issue)
        else:
            log.info("Issue #%d is closed, skipping", issue)

    # Comprehensive bot bounty verification (#747)
    log.info("--- Phase 6: Comprehensive Bot Bounty (#747) ---")
    for issue in BOT_BOUNTY_ISSUES:
        if is_issue_open(issue):
            verify_bot_bounty(issue, all_stars)
        else:
            log.info("Issue #%d is closed, skipping", issue)

    log.info("=" * 60)
    log.info("Bounty verification complete")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
