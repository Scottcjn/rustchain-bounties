#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
React with thumbs-up, rocket, and heart to 3+ open issues.
Usage: python3 issue_reactor.py <github_token> <repo_owner> <repo_name>
Example: python3 issue_reactor.py ghp_abc123 octocat Hello-World
"""

import sys
import requests
import json
import time

# Configuration
EMOJIS = ["+1", "rocket", "heart"]
MIN_REACTIONS = 3
RATE_LIMIT_SLEEP = 2  # seconds between API calls

def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_open_issues(token, owner, repo):
    """Fetch open issues (excluding pull requests)"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = get_headers(token)
    params = {"state": "open", "per_page": 100, "page": 1}
    issues = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_issues = response.json()
        if not page_issues:
            break
        # Filter out pull requests (they have 'pull_request' key)
        for issue in page_issues:
            if 'pull_request' not in issue:
                issues.append(issue)
        params["page"] += 1
        time.sleep(RATE_LIMIT_SLEEP)
    
    return issues

def get_existing_reactions(token, owner, repo, issue_number):
    """Get existing reactions for an issue"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/reactions"
    headers = get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def add_reaction(token, owner, repo, issue_number, emoji):
    """Add a reaction to an issue"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/reactions"
    headers = get_headers(token)
    headers["Content-Type"] = "application/json"
    data = {"content": emoji}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return True
    elif response.status_code == 200:
        # Already reacted
        return True
    else:
        print(f"Failed to add {emoji} to issue #{issue_number}: {response.status_code}")
        return False

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 issue_reactor.py <github_token> <repo_owner> <repo_name>")
        sys.exit(1)
    
    token = sys.argv[1]
    owner = sys.argv[2]
    repo = sys.argv[3]
    
    print(f"Fetching open issues for {owner}/{repo}...")
    issues = get_open_issues(token, owner, repo)
    print(f"Found {len(issues)} open issues")
    
    reactions_added = 0
    reacted_issues = []
    
    for issue in issues:
        if reactions_added >= MIN_REACTIONS:
            break
        
        issue_number = issue["number"]
        issue_title = issue["title"]
        
        print(f"\nProcessing issue #{issue_number}: {issue_title}")
        
        # Get existing reactions
        existing = get_existing_reactions(token, owner, repo, issue_number)
        existing_emojis = [r["content"] for r in existing]
        
        # Add missing reactions
        for emoji in EMOJIS:
            if emoji not in existing_emojis:
                print(f"  Adding {emoji} reaction...")
                if add_reaction(token, owner, repo, issue_number, emoji):
                    reactions_added += 1
                    time.sleep(RATE_LIMIT_SLEEP)
            else:
                print(f"  {emoji} already exists")
        
        if reactions_added > 0:
            reacted_issues.append(issue_number)
    
    print(f"\n=== Summary ===")
    print(f"Total reactions added: {reactions_added}")
    print(f"Reacted to issues: {reacted_issues}")
    
    # Print comment with links
    if reacted_issues:
        print("\nComment to post on the bounty issue:")
        print("---")
        print(f"I've added emoji reactions (👍, 🚀, ❤️) to the following open issues:")
        for num in reacted_issues:
            print(f"- https://github.com/{owner}/{repo}/issues/{num}")
        print(f"\nWallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")
        print("---")

if __name__ == "__main__":
    main()