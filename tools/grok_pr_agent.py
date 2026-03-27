#!/usr/bin/env python3
"""
Grok PR Review Agent for RustChain/BoTTube/rustchain-bounties

Uses xAI's Grok API to scan open PRs, review code quality,
detect bounty farming, and post review comments.

Usage:
    python3 grok_pr_agent.py                    # Scan all repos
    python3 grok_pr_agent.py --repo Rustchain   # Scan specific repo
    python3 grok_pr_agent.py --pr 265           # Review specific PR
    python3 grok_pr_agent.py --dry-run          # Preview without posting
"""

import os
import sys
import json
import argparse
import subprocess
import time

GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
GROK_MODEL = os.environ.get("GROK_MODEL", "grok-4-1-fast-non-reasoning")  # Fast, cheap, no reasoning overhead
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OWNER = "Scottcjn"
REPOS = ["Rustchain", "bottube", "rustchain-bounties"]

SYSTEM_PROMPT = """You are a code reviewer for the RustChain ecosystem. You review PRs for:

1. **Code quality**: Is the code clean, tested, and well-structured?
2. **Bounty farming detection**: Does this look like AI-generated slop submitted just for RTC rewards?
   Signs: generic README-only changes, copy-paste from templates, no real functionality, account age < 1 week
3. **Security**: Does the code expose admin keys, allow injection, or bypass auth?
4. **1 CPU = 1 Vote compliance**: Nothing that enables mining pools, VM farms, or Sybil attacks.
5. **Ecosystem fit**: Does this actually help RustChain/BoTTube/Beacon?

RustChain principles:
- Proof-of-Antiquity: vintage hardware earns more (G4=2.5x, G5=2.0x)
- Hardware fingerprinting prevents emulation
- No mining pools (violates 1 CPU = 1 Vote)
- Coalitions (governance groups) are OK, pools are NOT
- RTC wallets are string names, NOT ETH/SOL addresses
- No ICO, fair launch, utility token

Be concise. Output a JSON object with:
{
  "verdict": "approve" | "request_changes" | "needs_maintainer" | "reject",
  "confidence": 0.0-1.0,
  "summary": "1-2 sentence summary",
  "issues": ["list of specific issues found"],
  "bounty_farming_score": 0-10,
  "security_concerns": ["list or empty"],
  "suggested_comment": "what to post as review comment"
}"""


def grok_chat(messages, model=None):
    """Call Grok API and return response text."""
    payload = json.dumps({
        "messages": messages,
        "model": model or GROK_MODEL,
        "stream": False,
        "temperature": 0.1
    })

    result = subprocess.run(
        ["curl", "-s", "https://api.x.ai/v1/chat/completions",
         "-H", "Content-Type: application/json",
         "-H", f"Authorization: Bearer {GROK_API_KEY}",
         "-d", payload],
        capture_output=True, text=True, timeout=120
    )

    data = json.loads(result.stdout)
    if "error" in data:
        raise Exception(data["error"].get("message", str(data["error"])))

    return data["choices"][0]["message"]["content"]


def gh(args):
    """Run gh CLI command and return output."""
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = GITHUB_TOKEN
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True, text=True, env=env
    )
    return result.stdout.strip()


def get_open_prs(repo):
    """Get list of open PRs for a repo."""
    raw = gh(["pr", "list", "--repo", f"{OWNER}/{repo}", "--json",
              "number,title,author,additions,deletions,files,createdAt",
              "--limit", "20"])
    return json.loads(raw) if raw else []


def get_pr_diff(repo, number):
    """Get PR diff (truncated to save tokens)."""
    diff = gh(["pr", "diff", str(number), "--repo", f"{OWNER}/{repo}"])
    # Truncate large diffs to save Grok credits
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... [TRUNCATED — full diff is {} chars]".format(len(diff))
    return diff


def get_pr_files(repo, number):
    """Get list of changed files."""
    raw = gh(["pr", "view", str(number), "--repo", f"{OWNER}/{repo}",
              "--json", "files", "--jq", ".files[].path"])
    return raw.split("\n") if raw else []


def check_author_profile(username):
    """Quick check on author's GitHub profile."""
    raw = gh(["api", f"users/{username}", "--jq",
              r'"\(.login) | created: \(.created_at) | repos: \(.public_repos) | followers: \(.followers)"'])
    return raw


def review_pr(repo, pr, dry_run=False):
    """Review a single PR using Grok."""
    number = pr["number"]
    title = pr["title"]
    author = pr["author"]["login"]

    print(f"\n{'='*60}")
    print(f"PR #{number}: {title}")
    print(f"Author: {author} | +{pr['additions']}/-{pr['deletions']} | {len(pr.get('files', []))} files")
    print(f"{'='*60}")

    # Gather context
    diff = get_pr_diff(repo, number)
    files = get_pr_files(repo, number)
    profile = check_author_profile(author)

    # Build prompt
    user_msg = f"""Review this PR for {OWNER}/{repo}:

**PR #{number}**: {title}
**Author**: {author}
**Profile**: {profile}
**Files changed**: {', '.join(files[:20])}
**Stats**: +{pr['additions']}/-{pr['deletions']}

**Diff**:
```
{diff}
```

Analyze and return JSON verdict."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg}
    ]

    print("  Asking Grok...")
    try:
        response = grok_chat(messages)
        print(f"  Grok response received ({len(response)} chars)")
    except Exception as e:
        print(f"  ERROR: Grok API failed: {e}")
        return None

    # Parse JSON from response
    try:
        # Try to extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        elif "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            json_str = response

        review = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        print(f"  WARNING: Could not parse Grok response as JSON")
        review = {
            "verdict": "needs_maintainer",
            "confidence": 0.0,
            "summary": "Grok response was not parseable",
            "raw_response": response[:500]
        }

    # Display results
    verdict = review.get("verdict", "unknown")
    confidence = review.get("confidence", 0)
    farming = review.get("bounty_farming_score", "?")
    summary = review.get("summary", "No summary")

    print(f"\n  VERDICT: {verdict} (confidence: {confidence})")
    print(f"  FARMING SCORE: {farming}/10")
    print(f"  SUMMARY: {summary}")

    issues = review.get("issues", [])
    if issues:
        print(f"  ISSUES:")
        for issue in issues:
            print(f"    - {issue}")

    security = review.get("security_concerns", [])
    if security:
        print(f"  SECURITY:")
        for concern in security:
            print(f"    ⚠ {concern}")

    # Post comment if not dry run and there's something to say
    comment = review.get("suggested_comment", "")
    if comment and not dry_run:
        if verdict in ("reject", "request_changes") or int(str(farming).replace("?", "0")) >= 7:
            print(f"\n  → Posting review comment...")
            # Only post if high confidence or clear issues
            if confidence >= 0.6:
                gh(["pr", "comment", str(number), "--repo", f"{OWNER}/{repo}",
                    "--body", f"**Grok Automated Review** (model: {GROK_MODEL})\n\n{comment}\n\n---\n*Automated review — maintainer will make final decision.*"])
                print(f"  → Comment posted!")
            else:
                print(f"  → Skipped posting (low confidence {confidence})")
        else:
            print(f"  → No comment needed (verdict: {verdict})")
    elif dry_run:
        print(f"\n  [DRY RUN] Would post: {comment[:200]}...")

    return review


def scan_all(repos=None, dry_run=False):
    """Scan all open PRs across repos."""
    repos = repos or REPOS
    results = {}

    for repo in repos:
        print(f"\n{'#'*60}")
        print(f"# Scanning {OWNER}/{repo}")
        print(f"{'#'*60}")

        prs = get_open_prs(repo)
        if not prs:
            print("  No open PRs")
            continue

        print(f"  Found {len(prs)} open PR(s)")

        for pr in prs:
            review = review_pr(repo, pr, dry_run=dry_run)
            if review:
                results[f"{repo}#{pr['number']}"] = review
            time.sleep(1)  # Rate limit

    # Summary
    print(f"\n{'='*60}")
    print("SCAN SUMMARY")
    print(f"{'='*60}")
    for key, review in results.items():
        v = review.get("verdict", "?")
        f = review.get("bounty_farming_score", "?")
        s = review.get("summary", "")[:80]
        print(f"  {key}: [{v}] farming={f}/10 — {s}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Grok PR Review Agent")
    parser.add_argument("--repo", help="Specific repo to scan")
    parser.add_argument("--pr", type=int, help="Specific PR number to review")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--model", default=None, help="Grok model to use")
    args = parser.parse_args()

    if args.model:
        global GROK_MODEL
        GROK_MODEL = args.model

    print(f"Grok PR Agent — Model: {GROK_MODEL}")
    print(f"Repos: {OWNER}/{', '.join(REPOS)}")
    if args.dry_run:
        print("MODE: DRY RUN (no comments will be posted)")

    if args.pr and args.repo:
        # Review specific PR
        prs = get_open_prs(args.repo)
        pr = next((p for p in prs if p["number"] == args.pr), None)
        if pr:
            review_pr(args.repo, pr, dry_run=args.dry_run)
        else:
            print(f"PR #{args.pr} not found in {args.repo}")
    elif args.repo:
        scan_all(repos=[args.repo], dry_run=args.dry_run)
    else:
        scan_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
