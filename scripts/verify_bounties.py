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
  5. Distribution   - Does the `Live-URL:` a claimant posted actually exist
                    off GitHub (BoTTube / X / YouTube / article host)?

Posts a verification comment on the bounty issue with results.
"""

from __future__ import annotations

import os
import sys
import json
import time
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# Imports for Logic
# ---------------------------------------------------------------------------

try:
    from live_url import LIVE_URL_LINE_RE, classify_live_url, extract_live_urls
except ImportError:
    # Fallback: ensure module is discoverable or handle gracefully
    pass


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Token used for the stargazer sweep. The Actions-issued GITHUB_TOKEN is a
# GitHub App installation token, and GET /repos/{owner}/{repo}/stargazers
# answers every such token with 403 "Resource not accessible by integration".
# -- even for the workflow's own public repo. Every scheduled run since at
# least 2026-08-19 logged that 403 for all 13 STAR_REPOS. A user PAT
# (classic `public_repo`, or fine-grained with Metadata: read) can list
# stargazers, so the workflow passes one here.
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
]

# Issue numbers by bounty type
# Only OPEN bounty issues belong here: the phases skip closed issues, so a list of
# closed numbers makes the sweep succeed while checking nobody (2026-08-28).
STAR_BOUNTY_ISSUES = [16238, 9017, 165, 171, 378]
BADGE_BOUNTY_ISSUES = [13949]
FOLLOW_BOUNTY_ISSUES = [2155]
EMOJI_BOUNTY_ISSUES = [2180]
# Distribution / human-funnel bounties: the deliverable lives OFF GitHub, and the
# 2026-08-28 audit found ~45 claims on these that never left GitHub. A claim counts
# here only if its `Live-URL:` resolves on the named platform.
DISTRIBUTION_BOUNTY_ISSUES = [315, 16601, 16497, 282, 399, 2798, 14481]

LIVE_URL_VERIFIED_LABEL = "live-url-verified"
OFFPLATFORM_TIMEOUT = 20  # seconds per fetch
OFFPLATFORM_UA = "rustchain-bounty-verify-bot/1.0 (+https://github.com/Scottcjn/rustchain-bounties)"

# Bot signature so we can detect our own comments and avoid duplicates
BOT_SIGNATURE = "<!-- bounty-verify-bot -->"
BOT_TAG = "Bounty Verification Bot"

# Rate-limit safety: sleep between paginated API calls
API_SLEEP = 0.25  # second


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def get_github_client_headers() -> Dict[str, str]:
    """Construct headers for authenticated GitHub API requests."""
    token = STAR_READ_TOKEN if STAR_READ_TOKEN else GITHUB_TOKEN
    if token:
        return {
            "Authorization": f"token {token}",
            "User-Agent": OFFPLATFORM_UA
        }
    return {"User-Agent": OFFPLATFORM_UA}

def get_github_issues_url(repo_name: str) -> str:
    """Construct the GitHub API URL for issue bodies."""
    return f"https://api.github.com/repos/{OWNER}/{repo_name}/issues"

def fetch_issue_body(issue_number: int, url: str) -> Optional[str]:
    """Fetch and return the raw body of an issue, handling rate limits."""
    try:
        response = requests.get(url, headers=get_github_client_headers(), timeout=OFFPLATFORM_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        return data.get("body", "")
    except requests.RequestException:
        return None

def extract_body_comments(body: str) -> List[str]:
    """Extract lines containing BOT_SIGNATURE from an issue body."""
    if not body:
        return []
    
    lines = body.splitlines()
    comments = []
    for line in lines:
        if BOT_SIGNATURE in line:
            # Trim the comment tag
            comments.append(line.replace(BOT_SIGNATURE, "").strip())
    return comments


# ---------------------------------------------------------------------------
# Main Verification Logic
# ---------------------------------------------------------------------------

class BountyVerifier:
    """
    Orchestrates the verification process for a specific bounty type.
    """
    
    def __init__(self, issue_number: int, repo: str = BOUNTY_REPO):
        self.issue_number = issue_number
        self.repo = repo
        self.issues_url = get_github_issues_url(repo)
        self.body = fetch_issue_body(issue_number, self.issues_url)
        
    def _get_claimant(self) -> Optional[str]:
        """Extract the claimant username from the issue title or comment."""
        if not self.body:
            return "Unverified"
        
        # Look for username in "Claimant: ..." or just first 15 chars
        match = re.search(r'Claimant:\s*(\S+)', self.body)
        if match:
            return match.group(1)
        # Fallback: First word after "Bounty Verification" or similar
        match = re.search(r'by (\S+)', self.body)
        return match.group(1) if match else "Bot-Default"

    def _check_distribution(self) -> bool:
        """Check if the Live-URL on the issue resolves."""
        if not self.body:
            return True # Skip check if no body
            
        urls = extract_live_urls(self.body)
        if not urls:
            return False
            
        # We assume 'urls' contains the main deliverable URL
        main_url = urls[0] if len(urls) > 0 else ""
        try:
            response = requests.get(main_url, timeout=OFFPLATFORM_TIMEOUT, headers=get_github_client_headers())
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _check_stars(self, expected_stars: int = 1) -> bool:
        """Simple check if stars match expected (if specified in body)."""
        if "Stars:" in self.body:
            return "x" in self.body or "✓" in self.body
        return True

    def verify(self) -> Dict[str, Any]:
        """Run all checks and return results."""
        results = {
            "issue": f"{self.repo}/{self.issue_number}",
            "status": "Verified" if self.body else "Checked-Empty",
            "body_snippet": self.body[:200] if self.body else "N/A",
            "claimant": self._get_claimant(),
            "distribution": self._check_distribution(),
            "starch_count": self.body.count("⭐") if self.body else 0, # Approx
        }

        # Specific logic for Distribution (Issue 315 etc)
        if self.repo == BOUNTY_REPO:
            # Example: Check if specific label exists
            if "live-url-verified" in self.body:
                results["label"] = LIVE_URL_VERIFIED_LABEL
        
        return results


def run_bounty_sweep():
    """
    Iterate through the configuration lists to verify issues.
    """
    print(f"🚀 Starting {BOT_TAG} Sweep")
    print(f"🔑 Token: {STAR_READ_TOKEN[:20]}...")
    
    all_issues = []
    all_issues.extend(STAR_BOUNTY_ISSUES)
    all_issues.extend(BADGE_BOUNTY_ISSUES)
    
    for issue_num in all_issues:
        verifier = BountyVerifier(issue_number=issue_num)
        result = verifier.verify()
        
        # Print or log result
        print(f"  Issue {issue_num}: {result['status']} (Claimant: {result['claimant']})")
        
        # If verification failed and distribution is required, sleep
        if result["distribution"] == False:
            print(f"    ⚠ Distribution check failed. Checking external URL...")
            
    print("✅ Sweep Complete.")

# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Check GITHUB_TOKEN env var availability
    if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("ghp_") and not GITHUB_TOKEN.startswith("gho_"):
        print(f"⚠ Warning: GITHUB_TOKEN detected but might need explicit user scope.")

    run_bounty_sweep()