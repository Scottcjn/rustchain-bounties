#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Requires: pip install requests
"""

import requests
import json
import sys
import time

# Configuration
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"  # Replace with your token
REPO_OWNER = "YOUR_REPO_OWNER"  # e.g., "octocat"
REPO_NAME = "YOUR_REPO_NAME"    # e.g., "Hello-World"
WALLET_ADDRESS = "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Emoji content types
EMOJIS = ["+1", "rocket", "heart"]  # thumbs-up, rocket, heart

def get_open_issues():
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": "open", "per_page": 10}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching issues: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    issues = response.json()
    # Filter out pull requests (they are also issues in GitHub API)
    return [issue for issue in issues if 'pull_request' not in issue]

def add_reaction(issue_number, emoji):
    """Add an emoji reaction to a specific issue."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}/reactions"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.squirrel-girl-preview+json",
        "Content-Type": "application/json"
    }
    data = {"content": emoji}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ Added {emoji} reaction to issue #{issue_number}")
        return True
    elif response.status_code == 200:
        print(f"⚠️ Already reacted with {emoji} to issue #{issue_number}")
        return True
    else:
        print(f"❌ Failed to add {emoji} to issue #{issue_number}: {response.status_code}")
        print(response.text)
        return False

def main():
    print(f"🚀 Starting emoji reaction bounty for {REPO_OWNER}/{REPO_NAME}")
    print(f"Wallet: {WALLET_ADDRESS}")
    print("=" * 50)
    
    # Get open issues
    issues = get_open_issues()
    if not issues:
        print("No open issues found!")
        sys.exit(1)
    
    print(f"Found {len(issues)} open issues")
    
    # React to at least 3 issues with all 3 emojis
    reacted_issues = []
    for i, issue in enumerate(issues[:5]):  # Process up to 5 issues
        issue_number = issue['number']
        issue_title = issue['title']
        print(f"\n📌 Issue #{issue_number}: {issue_title}")
        
        # Add all 3 emojis to each issue
        for emoji in EMOJIS:
            success = add_reaction(issue_number, emoji)
            if success:
                reacted_issues.append(issue_number)
            time.sleep(0.5)  # Rate limiting
        
        # Stop after reacting to 3+ issues
        if len(set(reacted_issues)) >= 3:
            break
    
    # Summary
    unique_issues = set(reacted_issues)
    print("\n" + "=" * 50)
    print(f"📊 Summary: Reacted to {len(unique_issues)} issues")
    print(f"💰 Bounty claimed: 1 RTC")
    print(f"💳 Wallet: {WALLET_ADDRESS}")
    
    # Generate comment with links
    print("\n📝 Comment to post on bounty issue:")
    print("-" * 50)
    print(f"Completed emoji reactions for {REPO_OWNER}/{REPO_NAME}")
    print(f"Reacted with 👍🚀❤️ to issues: #{', #'.join(map(str, unique_issues))}")
    print(f"Wallet: {WALLET_ADDRESS}")
    print("-" * 50)

if __name__ == "__main__":
    main()