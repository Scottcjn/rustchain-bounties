#!/usr/bin/env python3
import subprocess
import sys
import json

def claim_bounty(repo: str, issue_number: int, miner_id: str, plan: str, is_welcome_grant: bool = False):
    """
    Autonomously claims a bounty using the GitHub CLI.
    Welcome Grants require maintainer nomination and cannot be self-claimed.
    """
    if is_welcome_grant:
        print("❌ Welcome Grants cannot be self-claimed. They require maintainer nomination.")
        print("Please wait for a maintainer to nominate you based on your contributions.")
        sys.exit(1)
    
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
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to claim bounty: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 bounty_claimer.py <repo> <issue_number> <miner_id> <plan> [--welcome-grant]")
        sys.exit(1)
    
    is_welcome_grant = "--welcome-grant" in sys.argv
    claim_bounty(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], is_welcome_grant)
