#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Usage: python3 react_to_issues.py <github_token> <repo_owner/repo_name>
"""

import sys
import requests
import json
import time

# Emoji reactions mapping
REACTIONS = ["+1", "rocket", "heart"]

def get_open_issues(repo, token):
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": "open", "per_page": 10}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    issues = response.json()
    # Filter out pull requests (GitHub API includes PRs as issues)
    return [issue for issue in issues if "pull_request" not in issue]

def add_reaction(issue_url, reaction, token):
    """Add a reaction to a specific issue."""
    url = f"{issue_url}/reactions"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.squirrel-girl-preview+json",
        "Content-Type": "application/json"
    }
    data = {"content": reaction}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✓ Added {reaction} reaction to {issue_url}")
        return True
    else:
        print(f"✗ Failed to add {reaction} to {issue_url}: {response.status_code}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 react_to_issues.py <github_token> <repo_owner/repo_name>")
        sys.exit(1)
    
    token = sys.argv[1]
    repo = sys.argv[2]
    
    print(f"Fetching open issues from {repo}...")
    issues = get_open_issues(repo, token)
    
    if not issues:
        print("No open issues found.")
        sys.exit(0)
    
    print(f"Found {len(issues)} open issues.")
    
    # React to at least 3 issues with different reactions
    reactions_added = 0
    reaction_links = []
    
    for i, issue in enumerate(issues[:5]):  # Process up to 5 issues
        if reactions_added >= 3:
            break
            
        # Cycle through reactions
        reaction = REACTIONS[i % len(REACTIONS)]
        
        print(f"\nReacting to issue #{issue['number']}: {issue['title']}")
        success = add_reaction(issue["url"], reaction, token)
        
        if success:
            reactions_added += 1
            reaction_links.append(f"- {reaction} on #{issue['number']}: {issue['html_url']}")
        
        # Rate limiting: be nice to GitHub API
        time.sleep(0.5)
    
    print(f"\n{'='*50}")
    print(f"Total reactions added: {reactions_added}")
    print(f"\nReaction links for comment:")
    for link in reaction_links:
        print(link)
    
    # Wallet address for bounty
    print(f"\nWallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")

if __name__ == "__main__":
    main()