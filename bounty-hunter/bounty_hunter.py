#!/usr/bin/env python3
"""
RustChain Bounty Hunter Agent
Autonomously finds, evaluates, and claims RustChain bounties.

Usage:
    python bounty_hunter.py              # Scan and report
    python bounty_hunter.py --claim      # Scan and auto-claim best bounty
    python bounty_hunter.py --watch      # Continuous monitoring mode

Requirements:
    - Python 3.8+
    - requests (pip install requests)
    - GITHUB_TOKEN environment variable
"""

import json
import os
import re
import sys
import time
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

STATE_DIR = Path.home() / ".bounty-hunter"
STATE_FILE = STATE_DIR / "state.json"
REPORT_FILE = STATE_DIR / "report.json"
SEEN_FILE = STATE_DIR / "seen.json"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
NODE_URL = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
WALLET_ADDRESS = os.environ.get("RUSTCHAIN_WALLET", "")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "RustChain-Bounty-Hunter/1.0"
}

MIN_BOUNTY = 1  # Minimum RTC to consider
PREFERRED_LANGS = ["python", "typescript", "javascript", "rust", "go"]


def load_json(path, default=None):
    try:
        if Path(path).exists():
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default or {}


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def search_bounties():
    """Search GitHub for RustChain bounties."""
    repos = [
        "Scottcjn/rustchain-bounties",
        "Scottcjn/Rustchain",
    ]
    bounties = []
    
    for repo in repos:
        try:
            url = f"https://api.github.com/repos/{repo}/issues?labels=bounty&state=open&sort=created&direction=desc&per_page=30"
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                for issue in r.json():
                    if issue.get("pull_request") or issue.get("assignee"):
                        continue
                    
                    title = issue.get("title", "")
                    body = issue.get("body", "") or ""
                    labels = [l["name"] for l in issue.get("labels", [])]
                    
                    # Extract RTC amount
                    rtc = 0
                    m = re.search(r"(\d+)\s*RTC", title)
                    if m:
                        rtc = int(m.group(1))
                    
                    # Extract USD value
                    usd = 0
                    m2 = re.search(r"~\$(\d+(?:\.\d+)?)", title + body)
                    if m2:
                        usd = float(m2.group(1))
                    
                    # Check if we can do it
                    lang_match = any(
                        lang in (title + body + " ".join(labels)).lower()
                        for lang in PREFERRED_LANGS
                    )
                    
                    bounties.append({
                        "repo": repo,
                        "number": issue["number"],
                        "title": title[:80],
                        "url": issue["html_url"],
                        "rtc": rtc,
                        "usd": usd,
                        "labels": labels,
                        "body_preview": body[:300],
                        "comments": issue.get("comments", 0),
                        "created": issue.get("created_at", "")[:10],
                        "lang_match": lang_match,
                    })
        except Exception as e:
            print(f"  Error scanning {repo}: {e}", file=sys.stderr)
    
    return bounties


def score_bounty(b):
    """Score a bounty for attractiveness."""
    score = 0
    
    # Amount
    score += min(b["rtc"], 100)  # Up to 100 points for amount
    
    # Language match
    if b["lang_match"]:
        score += 30
    
    # Lower competition (fewer comments = less attention)
    if b["comments"] <= 5:
        score += 15
    elif b["comments"] <= 15:
        score += 5
    
    # Recency
    try:
        dt = datetime.fromisoformat(b["created"] + "T00:00:00+00:00")
        age = (datetime.now(timezone.utc) - dt).days
        if age <= 7:
            score += 20
        elif age <= 30:
            score += 10
    except Exception:
        pass
    
    b["score"] = score
    return b


def claim_bounty(bounty):
    """Claim a bounty by commenting on the issue."""
    if not GITHUB_TOKEN:
        print("  Error: GITHUB_TOKEN not set", file=sys.stderr)
        return False
    
    comment = f"""I would like to claim this bounty.

**My approach:** {summarize_approach(bounty)}

I have experience with Python/TypeScript and will submit a clean PR. Starting work now.
"""
    
    url = f"https://api.github.com/repos/{bounty['repo']}/issues/{bounty['number']}/comments"
    r = requests.post(url, headers=HEADERS, json={"body": comment}, timeout=10)
    
    if r.status_code == 201:
        print(f"  Claimed! Comment: {r.json().get('html_url', 'OK')}")
        return True
    else:
        print(f"  Claim failed: {r.status_code}", file=sys.stderr)
        return False


def summarize_approach(bounty):
    """Generate a brief approach summary based on the bounty."""
    body = bounty.get("body_preview", "").lower()
    
    if "bug" in body or "fix" in body:
        return "I'll analyze the issue, identify the root cause, and submit a tested fix."
    elif "feature" in body or "implement" in body:
        return "I'll review the requirements, implement the feature with tests, and submit a PR."
    elif "security" in body or "audit" in body:
        return "I'll perform a thorough security audit and report findings."
    elif "build" in body or "create" in body:
        return "I'll build the requested tool/component following the spec."
    else:
        return "I'll analyze the requirements and implement a clean solution."


def run_scan():
    """Main scan cycle."""
    seen = load_json(str(SEEN_FILE), {})
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning RustChain bounties...")
    
    bounties = search_bounties()
    
    # Filter out seen
    fresh = []
    for b in bounties:
        key = f"{b['repo']}#{b['number']}"
        if key not in seen:
            fresh.append(b)
            seen[key] = datetime.now().isoformat()
    
    # Score and sort
    scored = sorted([score_bounty(b) for b in fresh], key=lambda x: x["score"], reverse=True)
    
    save_json(str(SEEN_FILE), seen)
    
    # Report
    print(f"\n{'='*55}")
    print(f"  BOUNTY SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Found: {len(bounties)} | New: {len(fresh)}")
    print(f"{'='*55}")
    
    for i, b in enumerate(scored[:10]):
        print(f"  #{i+1} [{b['rtc']:>3} RTC] score:{b['score']:3d} {b['title'][:55]}")
        print(f"       {b['url']}")
    
    print(f"{'='*55}\n")
    
    report = {"time": datetime.now().isoformat(), "bounties": scored}
    save_json(str(REPORT_FILE), report)
    
    return scored


def main():
    parser = argparse.ArgumentParser(description="RustChain Bounty Hunter Agent")
    parser.add_argument("--claim", action="store_true", help="Auto-claim best bounty")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring (every 10 min)")
    parser.add_argument("--watch-interval", type=int, default=600, help="Watch interval in seconds")
    args = parser.parse_args()
    
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.watch:
        print("Starting continuous bounty monitoring...")
        while True:
            bounties = run_scan()
            if args.claim and bounties:
                best = bounties[0]
                print(f"Claiming best: {best['title']}")
                claim_bounty(best)
            print(f"Next scan in {args.watch_interval}s...")
            time.sleep(args.watch_interval)
    else:
        bounties = run_scan()
        if args.claim and bounties:
            best = bounties[0]
            print(f"Claiming best: {best['title']}")
            claim_bounty(best)


if __name__ == "__main__":
    main()
