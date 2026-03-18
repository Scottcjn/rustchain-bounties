#!/usr/bin/env python3
"""
Bounty Verification Bot - MVP
Automatically verifies bounty claims on GitHub issues.
Checks: GitHub follow status, star count, wallet existence, article URL validity.
"""

import os
import re
import sys
import json
import time
import logging
import urllib.request
import urllib.error
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bounty-bot")

# Configuration
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
RUSTCHAIN_NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
TARGET_OWNER = "Scottcjn"
CLAIM_KEYWORDS = ["claiming", "wallet:", "stars:", "github:", "claim", "bounty claim"]
PAID_PATTERN = re.compile(r"\*\*PAID\*\*|\bPAID\b", re.IGNORECASE)


@dataclass
class VerificationResult:
    """Result of verifying a bounty claim."""
    follows_owner: bool = False
    star_count: int = 0
    wallet_exists: bool = False
    wallet_balance: float = 0.0
    article_live: bool = False
    article_url: str = ""
    already_paid: bool = False
    errors: List[str] = field(default_factory=list)


def gh_api(endpoint: str, method: str = "GET", data: Optional[dict] = None) -> Tuple[int, dict]:
    """Make authenticated GitHub API request."""
    url = f"https://api.github.com{endpoint}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "bounty-verification-bot/1.0",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, headers=headers, method=method, data=body)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {"error": str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


def extract_claims(comment_body: str) -> Dict[str, str]:
    """Extract claim details from a comment body."""
    claims = {}

    # Extract wallet address
    wallet_match = re.search(r"[Ww]allet[:\s]+([A-Za-z0-9]{20,})", comment_body)
    if wallet_match:
        claims["wallet"] = wallet_match.group(1)

    # Extract GitHub username
    github_match = re.search(r"[Gg]it[Hh]ub[:\s]+@?([A-Za-z0-9-]+)", comment_body)
    if github_match:
        claims["github_username"] = github_match.group(1)

    # Extract article URL
    url_match = re.search(r"https?://(?:dev\.to|medium\.com|hashnode\.dev)/[^\s]+", comment_body)
    if url_match:
        claims["article_url"] = url_match.group(0)

    return claims


def check_follows(username: str, target: str = TARGET_OWNER) -> bool:
    """Check if username follows the target GitHub user."""
    status, data = gh_api(f"/users/{username}/following/{target}")
    return status == 204


def count_stars(username: str, target: str = TARGET_OWNER) -> int:
    """Count how many repos by target user the username has starred."""
    page = 1
    count = 0
    while True:
        status, data = gh_api(f"/users/{username}/starred?per_page=100&page={page}")
        if status != 200 or not isinstance(data, list):
            break
        for repo in data:
            if repo.get("owner", {}).get("login", "").lower() == target.lower():
                count += 1
        if len(data) < 100:
            break
        page += 1
    return count


def check_wallet(wallet: str) -> Tuple[bool, float]:
    """Check if a RustChain wallet exists and get its balance."""
    url = f"{RUSTCHAIN_NODE_URL}/wallet/balance?miner_id={wallet}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "bounty-bot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            balance = float(data.get("balance", 0))
            return True, balance
    except Exception as e:
        logger.warning(f"Wallet check failed: {e}")
        return False, 0.0


def check_url_live(url: str) -> bool:
    """Check if an article URL returns 200."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "bounty-bot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def check_previous_paid(repo: str, issue_num: int, username: str) -> bool:
    """Check if this user has already been paid on this issue."""
    status, comments = gh_api(f"/repos/{repo}/issues/{issue_num}/comments?per_page=100")
    if status != 200:
        return False
    for comment in comments:
        body = comment.get("body", "")
        if PAID_PATTERN.search(body) and username.lower() in body.lower():
            return True
    return False


def verify_claim(repo: str, issue_num: int, username: str, claims: Dict[str, str]) -> VerificationResult:
    """Run all verification checks on a claim."""
    result = VerificationResult()

    # Check GitHub follow
    try:
        result.follows_owner = check_follows(username)
    except Exception as e:
        result.errors.append(f"Follow check failed: {e}")

    # Check star count
    try:
        result.star_count = count_stars(username)
    except Exception as e:
        result.errors.append(f"Star count failed: {e}")

    # Check wallet
    if "wallet" in claims:
        try:
            result.wallet_exists, result.wallet_balance = check_wallet(claims["wallet"])
        except Exception as e:
            result.errors.append(f"Wallet check failed: {e}")

    # Check article URL
    if "article_url" in claims:
        result.article_url = claims["article_url"]
        try:
            result.article_live = check_url_live(claims["article_url"])
        except Exception as e:
            result.errors.append(f"URL check failed: {e}")

    # Check for duplicate claims
    try:
        result.already_paid = check_previous_paid(repo, issue_num, username)
    except Exception as e:
        result.errors.append(f"Duplicate check failed: {e}")

    return result


def format_verification_comment(username: str, result: VerificationResult) -> str:
    """Format a verification result as a GitHub comment."""
    lines = [
        f"## Automated Verification for @{username}",
        "",
        "| Check | Result |",
        "|-------|--------|",
        f"| Follows @{TARGET_OWNER} | {'✅ Yes' if result.follows_owner else '❌ No'} |",
        f"| {TARGET_OWNER} repos starred | {result.star_count} |",
    ]

    if result.article_url:
        status = "✅ Live" if result.article_live else "❌ Not found"
        lines.append(f"| Article link | {status} |")

    if result.wallet_exists:
        lines.append(f"| Wallet exists | ✅ Balance: {result.wallet_balance} RTC |")
    elif result.wallet_exists is False and result.errors:
        pass  # Skip if wallet check had an error

    if result.already_paid:
        lines.append(f"| Previous claims | ⚠️ Already paid |")

    lines.append("")

    # Suggested payout based on stars
    if result.follows_owner and result.star_count >= 1:
        multiplier = 1.5 if result.follows_owner else 1.0
        base = result.star_count
        suggested = round(base * multiplier, 1)
        lines.append(f"**Suggested payout**: {result.star_count} stars × {multiplier} RTC (follows + star multiplier) = {suggested} RTC")
    else:
        lines.append("**Suggested payout**: Pending manual review (no follow or insufficient stars)")

    if result.errors:
        lines.append("")
        lines.append(f"⚠️ Note: Some checks had errors: {'; '.join(result.errors)}")

    lines.append("")
    lines.append("*_Verification by bounty-bot. Human approves payment — bot only verifies._*")

    return "\n".join(lines)


def post_comment(repo: str, issue_num: int, body: str) -> bool:
    """Post a comment on a GitHub issue."""
    status, data = gh_api(f"/repos/{repo}/issues/{issue_num}/comments", "POST", {"body": body})
    if status == 201:
        logger.info(f"Posted verification comment on {repo}#{issue_num}")
        return True
    else:
        logger.error(f"Failed to post comment: {status} - {data}")
        return False


def process_issue(repo: str, issue_num: int) -> int:
    """Process a single issue and verify all claims in comments."""
    status, issue = gh_api(f"/repos/{repo}/issues/{issue_num}")
    if status != 200:
        logger.error(f"Could not fetch issue {repo}#{issue_num}")
        return 0

    # Also fetch all comments
    status, comments = gh_api(f"/repos/{repo}/issues/{issue_num}/comments?per_page=100")
    if status != 200:
        comments = []

    verified = 0

    # Check issue body too
    all_texts = [{"body": issue.get("body", ""), "user": issue.get("user", {})}]
    all_texts.extend(comments)

    for item in all_texts:
        body = item.get("body", "")
        user = item.get("user", {})
        username = user.get("login", "")

        if not username or username.lower() == TARGET_OWNER.lower():
            continue

        body_lower = body.lower()
        if not any(kw in body_lower for kw in CLAIM_KEYWORDS):
            continue

        # Skip if already verified by this bot (avoid re-verification)
        if "automated verification" in body_lower and "bounty-bot" in body_lower:
            continue

        logger.info(f"Found claim by @{username} in {repo}#{issue_num}")
        claims = extract_claims(body)
        claims.setdefault("github_username", username)

        result = verify_claim(repo, issue_num, username, claims)
        comment = format_verification_comment(username, result)

        if post_comment(repo, issue_num, comment):
            verified += 1

        time.sleep(1)  # Rate limit protection

    return verified


def main():
    """Main entry point for the bot."""
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable is required")
        sys.exit(1)

    repo = os.environ.get("TARGET_REPO", f"{TARGET_OWNER}/rustchain-bounties")
    issue_num = os.environ.get("TARGET_ISSUE", "")

    if issue_num:
        # Process single issue
        count = process_issue(repo, int(issue_num))
        logger.info(f"Verified {count} claims in {repo}#{issue_num}")
    else:
        # Process recent open issues with bounty label
        status, issues = gh_api(f"/repos/{repo}/issues?labels=bounty&state=open&per_page=20")
        if status != 200:
            logger.error(f"Could not fetch issues from {repo}")
            sys.exit(1)

        total = 0
        for issue in issues:
            count = process_issue(repo, issue["number"])
            total += count
            time.sleep(2)  # Rate limit

        logger.info(f"Total: Verified {total} claims across {len(issues)} issues")


if __name__ == "__main__":
    main()
