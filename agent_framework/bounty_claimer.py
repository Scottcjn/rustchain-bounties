#!/usr/bin/env python3
import subprocess
import sys
import json
import shutil

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
        # Ensure GitHub CLI is available before attempting to run it
        if shutil.which("gh") is None:
            print("❌ 'gh' (GitHub CLI) not found in PATH. Install from https://cli.github.com/ and retry.")
            sys.exit(2)

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully claimed bounty {repo}#{issue_number}")
        url = result.stdout.strip()
        if not url:
            # GitHub CLI may not always print a URL on success; provide a sensible fallback
            url = f"https://github.com/{repo}/issues/{issue_number}"
        print(f"🔗 URL: {url}")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else ""
        print(f"❌ Failed to claim bounty: {stderr}")
        # Avoid printing the full body/command (might contain sensitive info); show minimal debug hint
        print("Command attempted:", " ".join(cmd[:3]) + " ...")
        sys.exit(e.returncode if getattr(e, "returncode", None) is not None else 1)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 bounty_claimer.py <repo> <issue_number> <miner_id> <plan>")
        sys.exit(1)
    
    claim_bounty(sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4])
