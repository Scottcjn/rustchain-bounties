#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Usage: python3 issue_reactor.py <github_token> <repo_owner/repo_name>
"""

import sys
import requests
import json
import time

# Emoji reaction types supported by GitHub API
REACTIONS = ["+1", "rocket", "heart"]

def get_open_issues(repo, token):
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.squirrel-girl-preview+json"
    }
    params = {"state": "open", "per_page": 100}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

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
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 issue_reactor.py <github_token> <repo_owner/repo_name>")
        print("Example: python3 issue_reactor.py ghp_xxxxx octocat/Hello-World")
        sys.exit(1)
    
    token = sys.argv[1]
    repo = sys.argv[2]
    
    try:
        print(f"Fetching open issues from {repo}...")
        issues = get_open_issues(repo, token)
        
        if not issues:
            print("No open issues found.")
            sys.exit(0)
        
        # Filter out pull requests (they appear in issues endpoint)
        actual_issues = [issue for issue in issues if 'pull_request' not in issue]
        
        if len(actual_issues) < 3:
            print(f"Only {len(actual_issues)} open issues found. Need at least 3.")
            sys.exit(1)
        
        print(f"Found {len(actual_issues)} open issues. Reacting to first 3...")
        
        reacted_issues = []
        for i, issue in enumerate(actual_issues[:3]):
            issue_number = issue['number']
            issue_title = issue['title']
            issue_url = issue['url']
            
            print(f"\nReacting to issue #{issue_number}: {issue_title}")
            
            for reaction in REACTIONS:
                try:
                    add_reaction(issue_url, reaction, token)
                    print(f"  Added {reaction} reaction")
                    time.sleep(0.5)  # Rate limiting precaution
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 422:
                        print(f"  {reaction} reaction already exists (skipping)")
                    else:
                        print(f"  Failed to add {reaction}: {e}")
            
            reacted_issues.append(issue)
        
        # Print summary with links
        print("\n" + "="*50)
        print("REACTION SUMMARY")
        print("="*50)
        for issue in reacted_issues:
            print(f"\nIssue #{issue['number']}: {issue['title']}")
            print(f"Link: {issue['html_url']}")
            print(f"Reactions added: {', '.join(REACTIONS)}")
        
        print("\n" + "="*50)
        print("Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")
        print("="*50)
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()