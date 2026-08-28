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

from __future__ import annotations

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

# Token used for the stargazer sweep. The Actions-issued GITHUB_TOKEN is a
# GitHub App installation token, and GET /repos/{owner}/{repo}/stargazers
# answers every such token with 403 "Resource not accessible by integration"
# -- even for the workflow's own public repo. Every scheduled run since at
# least 2026-08-19 logged that 403 for all 13 STAR_REPOS and (until the
# fail-closed fix) reported "0 stargazers" as a green run. A user PAT
# (classic `public_repo`, or fine-grained with Metadata: read) can list
# stargazers, so the workflow passes one here; issue comments stay on
# GITHUB_TOKEN so they are still authored by github-actions[bot].
STAR_READ_TOKEN = os.environ.get("STAR_READ_TOKEN", "") or GITHUB_TOKEN

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
    "llama-cpp-power8",   # was "llama-power8" (404: repo is named llama-cpp-power8)
    "rust-ppc-tiger",
    "rustchain-mcp",
    "shaprai",
    "beacon-skill-rs",    # was "beacon-rs" (404: repo is named beacon-skill-rs)
    "trashclaw",
    # "elyan-site" removed: the site repos (elyan-labs-site, elyanlabs-ai-site) are private
    # and cannot be starred, so a sweep over them can never succeed.
]

# Issue numbers by bounty type
# Only OPEN bounty issues belong here: the phases skip closed issues, so a list of
# closed numbers makes the sweep succeed while checking nobody (2026-08-28: all four
# star entries had been closed for months while claims piled up on the live ones).
STAR_BOUNTY_ISSUES = [16238, 9017, 165, 171, 378]   # star 3 repos / May Flowers / ClawHub / pick-one / BoTTube
BADGE_BOUNTY_ISSUES = [13949]                        # RustChain badge in any README
FOLLOW_BOUNTY_ISSUES = [2155]                        # (2173 closed)
EMOJI_BOUNTY_ISSUES = [2180]                         # (1611 closed)

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

def _make_session(token: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return s


SESSION = _make_session(GITHUB_TOKEN)          # issue reads + comment writes
STAR_SESSION = _make_session(STAR_READ_TOKEN)  # stargazer sweep only


def gh_get(url: str, params: dict | None = None,
           session: requests.Session = SESSION) -> requests.Response:
    """GET with rate-limit awareness."""
    r = session.get(url, params=params or {})
    remaining = int(r.headers.get("X-RateLimit-Remaining", 999))
    if remaining < 50:
        reset_ts = int(r.headers.get("X-RateLimit-Reset", 0))
        wait = max(reset_ts - int(time.time()), 1)
        log.warning("Rate limit low (%d remaining), sleeping %ds", remaining, wait)
        time.sleep(wait)
    elif remaining < 200:
        time.sleep(API_SLEEP)
    return r


class IncompleteSweep(RuntimeError):
    """A paginated sweep could not be completed.

    Must never be mistaken for "the complete set, which happens to be small".
    """


def paginate_all(url: str, params: dict | None = None,
                 session: requests.Session = SESSION) -> list:
    """Paginate through ALL results for a GitHub API endpoint, or raise.

    Raises `IncompleteSweep` on any non-200 page instead of returning what it
    managed to collect.

    Why this is not defensive over-engineering: this used to `break` on a
    non-200 and return the partial list with the same type and shape as a
    complete one, so the caller could not tell the difference. `Rustchain`
    alone is ~6,800 stars (~69 pages at per_page=100); one 403 secondary
    rate-limit on page 3 returned ~300 logins as if that were everybody. The
    star verifier then PUBLICLY posted, on the claimants' own issues, that
    real contributors had not starred — an accusation manufactured entirely
    by a swallowed HTTP error.

    A sweep that cannot complete must render no verdict about anyone.
    """
    results = []
    params = dict(params or {})
    params.setdefault("per_page", 100)
    page = 1
    while True:
        params["page"] = page
        r = gh_get(url, params, session=session)
        if r.status_code != 200:
            raise IncompleteSweep(
                f"{url} page {page} returned HTTP {r.status_code}: {r.text[:200]}"
            )
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
    """Return set of usernames who starred OWNER/repo.

    Raises `IncompleteSweep` if the stargazer list could not be read in full
    (including a 404, which would otherwise silently turn a renamed or moved
    repo into "nobody starred it").
    """
    try:
        users = paginate_all(f"https://api.github.com/repos/{OWNER}/{repo}/stargazers",
                             session=STAR_SESSION)
    except IncompleteSweep as e:
        raise IncompleteSweep(f"stargazers for {OWNER}/{repo}: {e}") from e
    return {u["login"] for u in users if isinstance(u, dict) and "login" in u}


def get_all_stargazers() -> dict[str, set[str]]:
    """Return {repo: set(usernames)} for all tracked repos.

    All-or-nothing on purpose. A partial map here becomes a public "you did
    not star this" verdict on someone's claim, so if any repo cannot be read
    in full the whole star phase is abandoned rather than reported.
    """
    result = {}
    for repo in STAR_REPOS:
        log.info("Fetching stargazers for %s/%s ...", OWNER, repo)
        result[repo] = get_stargazers(repo)
        log.info("  -> %d stargazers", len(result[repo]))
    return result


def check_profile_badge(username: str) -> tuple[Optional[bool], str]:
    """Check if user's profile README mentions RustChain/Elyan.

    Returns (found, detail_string), where `found` is None when the check
    could NOT be performed. Distinguishing "no badge" from "could not look"
    matters: both used to render as a public NOT FOUND verdict, so a 403
    rate-limit read to the claimant as an accusation.
    """
    r = gh_get(f"https://api.github.com/repos/{username}/{username}/contents/README.md")
    if r.status_code == 404:
        return False, "No profile README found"
    if r.status_code != 200:
        return None, f"Could not fetch profile README (HTTP {r.status_code}) — not checked"

    try:
        content = base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")
    except Exception as e:
        return None, f"Could not decode README ({e}) — not checked"

    content_lower = content.lower()
    found_keywords = [kw for kw in BADGE_KEYWORDS if kw in content_lower]
    if found_keywords:
        return True, f"Found keywords: {', '.join(found_keywords)}"
    return False, "No RustChain/Elyan keywords found in profile README"


def check_follows_owner(username: str) -> Optional[bool]:
    """Check if username follows OWNER.

    204 = follows, 404 = does not follow (an authoritative answer from
    GitHub). Anything else means the check did not happen — return None
    rather than reporting the claimant as NOT FOLLOWING off a rate-limit.
    """
    r = gh_get(f"https://api.github.com/users/{username}/following/{OWNER}")
    if r.status_code == 204:
        return True
    if r.status_code == 404:
        return False
    log.warning("Follow check for %s inconclusive: HTTP %d", username, r.status_code)
    return None


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
RTC_WALLET_RE = re.compile(r"(RTC[a-f0-9]{40})", re.IGNORECASE)
GENERIC_WALLET_RE = re.compile(
    r"(?:wallet\s+address|wallet|address)\s*[:=]?\s*([a-z0-9_-]{3,80})",
    re.IGNORECASE,
)


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
        wallet_match = RTC_WALLET_RE.search(body) or GENERIC_WALLET_RE.search(body)
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
        if found is None:
            # Could not look. Say so; do not report it as a missing badge.
            status, cell = "NOT CHECKED (retrying next run)", "?"
        elif found:
            status, cell = "VERIFIED", "Yes"
        else:
            status, cell = "NOT FOUND", "No"
        lines.append(f"| @{username} | {cell} | {detail} | {status} |")

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
        if follows is None:
            status, cell = "NOT CHECKED (retrying next run)", "?"
        elif follows:
            status, cell = "VERIFIED", "Yes"
        else:
            status, cell = "NOT FOLLOWING", "No"
        lines.append(f"| @{username} | {cell} | {status} |")

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

def run_phase(name: str, issues: list[int], runner) -> list[str]:
    """Run one verification phase, per issue, never on incomplete data.

    Every verify_* function does all of its fetching BEFORE it posts, so an
    `IncompleteSweep` raised mid-fetch means no comment was written for that
    issue. Returns a list of failure descriptions (empty == clean).
    """
    failures: list[str] = []
    log.info("--- %s ---", name)
    for issue in issues:
        if not is_issue_open(issue):
            log.info("Issue #%d is closed, skipping", issue)
            continue
        try:
            runner(issue)
        except IncompleteSweep as e:
            # No verdict is better than a verdict built on a truncated read.
            log.error("SKIPPED #%d — could not read all data: %s", issue, e)
            failures.append(f"{name} #{issue}: {e}")
    return failures


def main() -> int:
    log.info("=" * 60)
    log.info("RustChain Bounty Verification Bot starting")
    log.info("Owner: %s | Bounty repo: %s", OWNER, BOUNTY_REPO)
    log.info("=" * 60)

    failures: list[str] = []

    # Pre-fetch all stargazers once (most expensive operation).
    #
    # If this cannot complete, the ENTIRE star phase is skipped. Running it
    # on a partial map is how honest contributors got publicly told they had
    # not starred; a missing report is recoverable, a false accusation is not.
    log.info("--- Phase 1: Fetching stargazers ---")
    all_stars: dict[str, set[str]] | None = None
    try:
        all_stars = get_all_stargazers()
    except IncompleteSweep as e:
        log.error("Stargazer sweep INCOMPLETE — skipping all star bounties: %s", e)
        failures.append(f"stargazer sweep: {e}")
    else:
        total_unique = len(set().union(*all_stars.values())) if all_stars else 0
        log.info("Total unique stargazers across %d repos: %d", len(STAR_REPOS), total_unique)

    if all_stars is not None:
        failures += run_phase(
            "Phase 2: Star bounties", STAR_BOUNTY_ISSUES,
            lambda issue: verify_star_claims(issue, all_stars),
        )
    else:
        log.warning("Phase 2: Star bounties SKIPPED (no trustworthy stargazer data)")

    failures += run_phase("Phase 3: Badge bounties", BADGE_BOUNTY_ISSUES, verify_badge_claims)
    failures += run_phase("Phase 4: Follow bounties", FOLLOW_BOUNTY_ISSUES, verify_follow_claims)
    failures += run_phase("Phase 5: Emoji bounties", EMOJI_BOUNTY_ISSUES, verify_emoji_claims)

    log.info("=" * 60)
    if failures:
        # Exit non-zero so the run shows RED. A sweep that skipped work is
        # not a successful sweep, and a green check here previously meant
        # nothing at all.
        log.error("Bounty verification INCOMPLETE — %d check(s) skipped:", len(failures))
        for f in failures:
            log.error("  - %s", f)
        log.info("=" * 60)
        return 1
    log.info("Bounty verification complete")
    log.info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
