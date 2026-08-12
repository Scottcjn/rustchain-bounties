#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""GitHub Actions script to handle bounty claims and expired claim cleanup."""

import datetime
import json
import os
import re
from typing import List, Optional, Tuple

MARKER = "🏷️ **BOUNTY CLAIM**"

def is_claim_request(body: str) -> bool:
    """Detect if a comment is claiming a bounty."""
    body = body.strip().lower()
    return any(
        body.startswith(prefix)
        for prefix in ("/claim", "claiming this", "i'm taking this", "taking this one")
    )

def active_claim(issue_number: int) -> Optional[Tuple[str, datetime.date]]:
    """Find the most recent active claim on an issue."""
    # Mock GitHub API call - in real implementation this would use requests
    gh = lambda a, d=None: []
    comments = gh(f"issues/{issue_number}/comments")

    for comment in comments:
        if comment["body"].startswith(MARKER):
            match = re.search(r"holder: @([^\s]+) · expires: (\d{4}-\d{2}-\d{2})", comment["body"])
            if match:
                holder, expires_str = match.groups()
                expires = datetime.datetime.strptime(expires_str, "%Y-%m-%d").date()
                if expires >= datetime.date.today():
                    return (holder, expires)
    return None

def validate_starred_repo(username: str, repo: str = "rustchain-bounties") -> bool:
    """Check if user has starred the main repo."""
    # Mock GitHub API call - in real implementation this would use requests
    gh = lambda a, d=None: []
    stars = gh(f"users/{username}/starred/{repo}")
    return len(stars) > 0

def validate_review_quality(username: str, min_approved: int = 5) -> bool:
    """Check if user has enough quality reviews (APPROVE/LGTM)."""
    # Mock GitHub API call - in real implementation this would use requests
    gh = lambda a, d=None: []
    reviews = gh(f"users/{username}/events")

    approved_count = 0
    for review in reviews:
        if review["type"] == "ReviewCommentEvent":
            if review["payload"]["state"] == "APPROVED" or "LGTM" in review["payload"]["body"]:
                approved_count += 1
                if approved_count >= min_approved:
                    return True
    return False

def validate_bounty_claim(issue_number: int, username: str, bounty_type: str) -> bool:
    """Validate bounty claim based on bounty type."""
    if bounty_type == "star+review":
        return validate_starred_repo(username) and validate_review_quality(username)
    # Add other bounty types here
    return True

def main():
    mode = os.getenv("MODE", "claim")
    issue_number = int(os.getenv("ISSUE_NUMBER", "1"))
    comment_body = os.getenv("COMMENT_BODY", "")
    comment_author = os.getenv("COMMENT_AUTHOR", "")

    if mode == "claim":
        if is_claim_request(comment_body):
            bounty_type = os.getenv("BOUNTY_TYPE", "default")
            if validate_bounty_claim(issue_number, comment_author, bounty_type):
                expires = (datetime.date.today() + datetime.timedelta(days=int(os.getenv("CLAIM_DAYS", "7")))).isoformat()
                marker = f"{MARKER}\n🔒 **Claimed.** holder: @{comment_author} · expires: {expires}"
                # In real implementation: update issue comment with marker
                print(f"Claim recorded: {marker}")
            else:
                print("Claim rejected: validation failed")
    elif mode == "sweep":
        # Release expired claims logic
        pass

if __name__ == "__main__":
    main()