#!/usr/bin/env python3
"""
GitHub RTC Tip Bot
Listens for /tip, /balance, /leaderboard, /register commands in GitHub comments.
"""

import os
import re
import json
import requests
from github import Github

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RUSTCHAIN_NODE = os.getenv("RUSTCHAIN_NODE", "https://50.28.86.131")
RUSTCHAIN_ADMIN_KEY = os.getenv("RUSTCHAIN_ADMIN_KEY", "")

# In-memory storage for demo (use database in production)
registered_wallets = {}  # github_username -> wallet_name
tip_ledger = []  # [(from, to, amount, memo, timestamp)]

def check_balance(wallet_name: str) -> dict:
    """Check RTC balance for a wallet."""
    try:
        r = requests.get(
            f"{RUSTCHAIN_NODE}/wallet/balance",
            params={"miner_id": wallet_name},
            timeout=10,
            verify=False
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def register_wallet(github_user: str, wallet_name: str) -> bool:
    """Register a wallet for a GitHub user."""
    registered_wallets[github_user] = wallet_name
    return True

def process_tip(from_user: str, to_wallet: str, amount: float, memo: str = "") -> dict:
    """
    Process a tip transfer.
    Note: Requires admin key for actual transfers.
    """
    # Validate recipient has registered wallet
    recipient = None
    for user, wallet in registered_wallets.items():
        if wallet == to_wallet:
            recipient = user
            break
    
    if not recipient:
        return {"status": "error", "message": f"Wallet {to_wallet} not registered. Use /register WALLET_NAME first."}
    
    # Queue the tip (in production, call /wallet/transfer API with admin key)
    tip_ledger.append((from_user, to_wallet, amount, memo))
    
    return {
        "status": "queued",
        "amount": amount,
        "to": to_wallet,
        "from": from_user,
        "memo": memo
    }

def get_leaderboard() -> list:
    """Get top tipped contributors."""
    totals = {}
    for frm, to, amount, _ in tip_ledger:
        totals[to] = totals.get(to, 0) + amount
    
    sorted_users = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_users[:10]

def parse_command(body: str) -> tuple:
    """Parse command from comment body."""
    body = body.strip()
    
    # /tip @user AMOUNT RTC [memo]
    tip_match = re.match(r"^\/tip\s+@(\w+)\s+(\d+(?:\.\d+)?)\s*RTC\s*(.*)?$", body, re.I)
    if tip_match:
        return ("tip", {
            "recipient": tip_match.group(1),
            "amount": float(tip_match.group(2)),
            "memo": tip_match.group(3) or ""
        })
    
    # /balance [wallet]
    if body.lower().startswith("/balance"):
        wallet = body.replace("/balance", "").strip()
        return ("balance", {"wallet": wallet})
    
    # /register WALLET_NAME
    reg_match = re.match(r"^\/register\s+(\w+)$", body, re.I)
    if reg_match:
        return ("register", {"wallet": reg_match.group(1)})
    
    # /leaderboard
    if body.lower() == "/leaderboard":
        return ("leaderboard", {})
    
    return (None, {})

def handle_comment(comment_data: dict) -> str:
    """Handle a comment and return response."""
    body = comment_data.get("body", "")
    user = comment_data.get("user", {}).get("login", "unknown")
    
    cmd, args = parse_command(body)
    
    if cmd == "tip":
        result = process_tip(user, args["recipient"], args["amount"], args["memo"])
        if result["status"] == "queued":
            return f"✅ Queued: {result['amount']} RTC → {result['to']}\nFrom: {user} | Memo: {result['memo']}\nStatus: Pending (confirms in 24h)"
        else:
            return f"❌ Error: {result.get('message', 'Unknown error')}"
    
    elif cmd == "balance":
        wallet = args.get("wallet") or user
        bal = check_balance(wallet)
        if "error" in bal:
            return f"❌ Error checking balance: {bal['error']}"
        return f"💰 Balance for {wallet}: {bal.get('amount_rtc', 0)} RTC"
    
    elif cmd == "register":
        register_wallet(user, args["wallet"])
        return f"✅ Wallet registered: {args['wallet']} for user {user}"
    
    elif cmd == "leaderboard":
        leaders = get_leaderboard()
        if not leaders:
            return "📊 No tips yet!"
        
        lines = ["🏆 Top Tipped Contributors:"]
        for i, (wallet, total) in enumerate(leaders, 1):
            lines.append(f"{i}. {wallet}: {total} RTC")
        return "\n".join(lines)
    
    return None  # Not a command we handle

# Example usage
if __name__ == "__main__":
    # Demo
    print("=== GitHub RTC Tip Bot ===")
    
    # Register some wallets
    register_wallet("Scottcjn", "scottcjn")
    register_wallet("testuser", "testwallet")
    
    # Process some tips
    print(process_tip("Scottcjn", "testwallet", 5.0, "Great PR!"))
    
    # Check balance
    print(check_balance("testwallet"))
    
    # Get leaderboard
    print(get_leaderboard())
