#!/usr/bin/env python3
"""
TestAutomaton Bounty Hunter Agent
===================================
Sovereign AI agent that autonomously finds, evaluates, and claims
RustChain GitHub bounties to earn RTC tokens.

Architecture:
  scanner  → scan open bounties via gh CLI
  evaluator → score each bounty (Claude API or heuristic)
  implementer → fork repo + generate solution (Claude API or template)
  submitter → push branch + open PR
  tracker → log submissions and earnings

Usage:
  python agent.py                     # auto-select best bounty
  python agent.py --bounty 2861       # target specific bounty
  python agent.py --scan-only         # list bounties without claiming
  python agent.py --summary           # show earnings log

Environment:
  ANTHROPIC_API_KEY   required for AI-powered evaluation + generation
  WALLET_NAME         your RustChain wallet name (for PR claims)
  GITHUB_TOKEN        optional, gh CLI uses its own auth by default
"""

import argparse
import os
import sys

from scanner import scan_open_bounties, has_open_pr, Bounty
from evaluator import score_bounties
from implementer import fork_and_implement
from submitter import submit_pr
from tracker import record_submission, print_summary


WALLET = os.getenv("WALLET_NAME", "testautomaton")
MIN_SCORE = float(os.getenv("MIN_SCORE", "5.0"))
SKIP_IF_PR_OPEN = os.getenv("SKIP_IF_PR_OPEN", "true").lower() != "false"


def run_scan(verbose: bool = False) -> list[tuple[float, Bounty]]:
    print("🔍 Scanning open bounties...")
    bounties = scan_open_bounties()
    print(f"   Found {len(bounties)} bounties with 'bounty' label")

    scored = score_bounties(bounties)
    print(f"\n{'Score':>5}  {'RTC':>6}  Title")
    print("-" * 70)
    for score, b in scored[:15]:
        print(f"{score:>5.1f}  {b.reward_rtc or 0:>6.0f}  {b.short()}")
    return scored


def run_claim(bounty: Bounty):
    print(f"\n🎯 Targeting bounty #{bounty.number}: {bounty.title}")

    if SKIP_IF_PR_OPEN and has_open_pr(bounty):
        print("   ⚠️  Open PR already exists — skipping to avoid duplicate.")
        sys.exit(0)

    print("🍴 Forking repo and generating implementation...")
    workdir, branch = fork_and_implement(bounty, WALLET)
    print(f"   Branch: {branch}")

    print("📤 Submitting PR...")
    pr_url = submit_pr(bounty, workdir, branch, WALLET)
    print(f"   ✅ PR submitted: {pr_url}")

    record_submission(
        bounty_number=bounty.number,
        title=bounty.title,
        reward_rtc=bounty.reward_rtc or 0,
        pr_url=pr_url,
        wallet=WALLET,
    )
    return pr_url


def main():
    parser = argparse.ArgumentParser(description="RustChain Autonomous Bounty Hunter")
    parser.add_argument("--bounty", type=int, help="Target a specific bounty by issue number")
    parser.add_argument("--scan-only", action="store_true", help="List bounties without claiming")
    parser.add_argument("--summary", action="store_true", help="Show earnings summary")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE)
    args = parser.parse_args()

    if args.summary:
        print_summary()
        return

    scored = run_scan(verbose=True)

    if args.scan_only:
        return

    if args.bounty:
        # Find specific bounty in scored list
        matches = [b for _, b in scored if b.number == args.bounty]
        if not matches:
            print(f"❌ Bounty #{args.bounty} not found in open bounty list")
            sys.exit(1)
        target = matches[0]
    else:
        # Pick highest-scored bounty above minimum threshold
        eligible = [(s, b) for s, b in scored if s >= args.min_score]
        if not eligible:
            print(f"❌ No bounties scored >= {args.min_score}. Lower --min-score or check manually.")
            sys.exit(1)
        _, target = eligible[0]

    run_claim(target)


if __name__ == "__main__":
    main()
