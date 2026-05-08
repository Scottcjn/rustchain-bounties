#!/usr/bin/env python3
"""RustChain RTC Reward GitHub Action

Awards RTC tokens to contributors when their PR is merged.
"""

import os
import sys
import re
import requests
from typing import Optional

def get_wallet_from_pr(pr_body: str, repo: str, pr_number: str, token: str) -> Optional[str]:
    """Extract RTC wallet from PR body or .rtc-wallet file"""
    # Check PR body for wallet pattern
    match = re.search(r'RTC[:\s]+([a-zA-Z0-9\-_]+)', pr_body)
    if match:
        return match.group(1)
    
    # Check .rtc-wallet file in repo
    try:
        api_url = f"https://api.github.com/repos/{repo}/contents/.rtc-wallet"
        headers = {"Authorization": f"token {token}"}
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            import base64
            content = base64.b64decode(resp.json()['content']).decode()
            return content.strip()
    except:
        pass
    
    return None

def award_rtc(node_url: str, amount: str, wallet_to: str, admin_key: str, dry_run: bool) -> bool:
    """Award RTC to wallet via RustChain node API"""
    if dry_run:
        print(f"🧪 DRY-RUN: Would award {amount} RTC to {wallet_to}")
        return True
    
    try:
        api_url = f"{node_url}/api/reward"
        payload = {
            "amount": amount,
            "wallet": wallet_to,
            "admin_key": admin_key
        }
        resp = requests.post(api_url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Error awarding RTC: {e}")
        return False

def post_comment_comment(repo: str, pr_number: str, message: str, token: str):
    """Post comment on PR"""
    api_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    requests.post(api_url, headers=headers, json={"body": message})

def main():
    # Inputs from GitHub Actions
    node_url = os.environ.get("INPUT_NODE_URL", "https://50.28.86.131")
    amount = os.environ.get("INPUT_AMOUNT", "5")
    wallet_from = os.environ.get("INPUT_WALLET_FROM", "project-fund")
    admin_key = os.environ.get("INPUT_ADMIN_KEY", "")
    dry_run = os.environ.get("INPUT_DRY_RUN", "false").lower() == "true"
    
    # GitHub context
    github_repository = os.environ.get("GITHUB_REPOSITORY", "")
    github_event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")
    
    # Read event payload
    import json
    with open(github_event_path) as f:
        event = json.load(f)
    
    pr_number = event["pull_request"]["number"]
    pr_body = event["pull_request"]["body"] or ""
    merged = event["pull_request"]["merged"]
    contributor = event["pull_request"]["user"]["login"]
    
    print(f"🤖 RTC Reward Action")
    print(f"Repository: {github_repository}")
    print(f"PR #{pr_number} by @{contributor}")
    print(f"Merged: {merged}")
    
    if not merged:
        print("Not a merge, skipping reward")
        return
    
    # Get wallet
    wallet = get_wallet_from_pr(pr_body, github_repository, str(pr_number), github_token)
    if not wallet:
        # Default to contributor's GitHub username as wallet
        wallet = contributor
        print(f"No wallet found, using contributor username: {wallet}")
    
    # Award RTC
    success = award_rtc(node_url, amount, wallet, admin_key, dry_run)
    
    # Post comment
    if success:
        msg = f"✅ **RTC Reward Sent!**\n\n{amount} RTC awarded to `@{wallet}` for PR #{pr_number}\n\n_Wallet: `{wallet}`_"
    else:
        msg = f"⚠️ RTC reward processing for `@{wallet}`. Check logs for details."
    
    post_comment_comment(github_repository, str(pr_number), msg, github_token)

if __name__ == "__main__":
    main()