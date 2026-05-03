#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Requires: pip install requests
Usage: python3 reactor.py <github_token> <repo_owner/repo_name>
"""

import sys
import requests
import time

# Emojis to react with
EMOJIS = ["+1", "rocket", "heart"]

def get_open_issues(repo, token):
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": "open", "per_page": 100}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        issues = response.json()
        # Filter out pull requests (GitHub API includes PRs as issues)
        return [issue for issue in issues if "pull_request" not in issue]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues: {e}")
        sys.exit(1)

def add_reaction(issue_url, emoji, token):
    """Add an emoji reaction to an issue."""
    url = f"{issue_url}/reactions"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.squirrel-girl-preview+json",
        "Content-Type": "application/json"
    }
    data = {"content": emoji}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error adding reaction: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 reactor.py <github_token> <repo_owner/repo_name>")
        print("Example: python3 reactor.py ghp_xxxxx octocat/Hello-World")
        sys.exit(1)
    
    token = sys.argv[1]
    repo = sys.argv[2]
    
    print(f"Fetching open issues from {repo}...")
    issues = get_open_issues(repo, token)
    
    if not issues:
        print("No open issues found.")
        sys.exit(0)
    
    print(f"Found {len(issues)} open issue(s).")
    
    # React to at least 3 issues
    issues_to_react = min(3, len(issues))
    reacted_issues = []
    
    for i in range(issues_to_react):
        issue = issues[i]
        issue_number = issue["number"]
        issue_title = issue["title"]
        issue_url = issue["url"]
        
        print(f"\nReacting to issue #{issue_number}: {issue_title}")
        
        for emoji in EMOJIS:
            print(f"  Adding {emoji} reaction...")
            if add_reaction(issue_url, emoji, token):
                print(f"    ✓ {emoji} added")
            else:
                print(f"    ✗ Failed to add {emoji}")
            time.sleep(0.5)  # Rate limiting precaution
        
        reacted_issues.append(f"https://github.com/{repo}/issues/{issue_number}")
    
    # Output results
    print("\n" + "="*50)
    print("REACTION SUMMARY")
    print("="*50)
    print(f"Reacted to {len(reacted_issues)} issue(s):")
    for link in reacted_issues:
        print(f"  • {link}")
    print(f"\nWallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")

if __name__ == "__main__":
    main()