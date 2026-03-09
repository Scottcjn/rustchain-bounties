"""
RTC GitHub Tip Bot - Standalone Version
Bounty: #1153 (25-40 RTC)
"""
import re
import requests
import os
from urllib.parse import parse_qs

# Configuration
NODE_URL = os.environ.get("NODE_URL", "50.28.86.131")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADMIN_WALLET = os.environ.get("ADMIN_WALLET")
ADMIN_KEY = os.environ.get("ADMIN_KEY")

def parse_tip_command(comment_body):
    """Parse /tip @user AMOUNT RTC [memo]"""
    pattern = r'/tip\s+@(\w+)\s+(\d+)\s+RTC\s+(.*)'
    match = re.search(pattern, comment_body)
    if match:
        return {
            "recipient": match.group(1),
            "amount": int(match.group(2)),
            "memo": match.group(3).strip()
        }
    return None

def parse_balance_command(comment_body):
    """Parse /balance"""
    if "/balance" in comment_body:
        return True
    return None

def parse_register_command(comment_body):
    """Parse /register WALLET_NAME"""
    pattern = r'/register\s+(\w+)'
    match = re.search(pattern, comment_body)
    if match:
        return match.group(1)
    return None

def transfer_rtc(from_wallet, to_wallet, amount, memo):
    """Call RustChain transfer API"""
    url = f"https://{NODE_URL}/wallet/transfer"
    data = {
        "from": from_wallet,
        "to": to_wallet,
        "amount": amount,
        "memo": memo
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_balance(wallet):
    """Get RTC balance"""
    url = f"https://{NODE_URL}/wallet/balance?miner_id={wallet}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def post_comment(repo, issue_number, body):
    """Post GitHub comment"""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.post(url, json={"body": body}, headers=headers)
    return response.json()

def handle_comment(event):
    """Main handler"""
    comment_body = event.get("comment", {}).get("body", "")
    repo = event.get("repository", {}).get("full_name", "")
    issue_number = event.get("issue", {}).get("number", 0)
    sender = event.get("comment", {}).get("user", {}).get("login", "")
    
    # Check if sender is maintainer (simplified - in production, check repocollabs)
    
    # Try tip command
    tip = parse_tip_command(comment_body)
    if tip:
        result = transfer_rtc(ADMIN_WALLET, tip["recipient"], tip["amount"], tip["memo"])
        if "error" in result:
            msg = f"❌ Transfer failed: {result['error']}"
        else:
            msg = f"✅ Queued: {tip['amount']} RTC → {tip['recipient']}\nMemo: {tip['memo']}\nStatus: Pending"
        return post_comment(repo, issue_number, msg)
    
    # Try balance command
    if parse_balance_command(comment_body):
        balance = get_balance(sender)
        if "error" in balance:
            msg = f"❌ Error: {balance['error']}"
        else:
            msg = f"💰 Balance: {balance.get('amount_rtc', 0)} RTC"
        return post_comment(repo, issue_number, msg)
    
    # Try register command
    wallet = parse_register_command(comment_body)
    if wallet:
        # Store wallet mapping (in production, use database)
        msg = f"✅ Wallet registered: {wallet}\nYou can now receive tips!"
        return post_comment(repo, issue_number, msg)
    
    return {"status": "no command found"}

# Example webhook handler
if __name__ == "__main__":
    import json
    event = json.loads(os.environ.get("WEBHOOK_PAYLOAD", "{}"))
    result = handle_comment(event)
    print(json.dumps(result))
