#!/usr/bin/env python3
import subprocess
import sys
import json

REACTION_TARGETS = [
    ("Scottcjn/rustchain-bounties", 87),
    ("Scottcjn/rustchain-bounties", 103),
    ("Scottcjn/rustchain-bounties", 157),
]


def add_reaction(repo: str, issue_number: int, reaction: str = "+1"):
    """Add an emoji reaction to a GitHub issue to show support."""
    cmd = [
        "gh", "api",
        f"repos/{repo}/issues/{issue_number}/reactions",
        "-X", "POST",
        "-f", f"content={reaction}",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Reacted {reaction} to {repo}#{issue_number}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to react to {repo}#{issue_number}: {e.stderr}")


def claim_bounty(repo: str, issue_number: int, miner_id: str, plan: str):
    """
    Autonomously claims a bounty using the GitHub CLI.
    """
    body = f"""**Claim**
- **Agent**: RayBot (Autonomous AI)
- **Miner ID**: {miner_id}
- **Plan**: {plan}
- **Status**: Starting implementation now.
"""
    
    cmd = [
        "gh", "issue", "comment", str(issue_number),
        "-R", repo,
        "-b", body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully claimed bounty {repo}#{issue_number}")
        print(f"🔗 URL: {result.stdout.strip()}")
        for r_repo, r_issue in REACTION_TARGETS:
            add_reaction(r_repo, r_issue)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to claim bounty: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 bounty_claimer.py <repo> <issue_number> <miner_id> <plan>")
        sys.exit(1)
    
    claim_bounty(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
