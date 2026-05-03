#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Reacts with thumbs-up, rocket, and heart to 3+ open issues.
Usage: python3 react_to_issues.py <github_token> <repo_owner> <repo_name>
"""

import sys
import requests
import json

def get_open_issues(token, owner, repo):
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {"state": "open", "per_page": 100}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def react_to_issue(token, owner, repo, issue_number, reaction):
    """Add a reaction to a specific issue."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/reactions"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.squirrel-girl-preview+json"
    }
    data = {"content": reaction}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 react_to_issues.py <github_token> <repo_owner> <repo_name>")
        sys.exit(1)
    
    token = sys.argv[1]
    owner = sys.argv[2]
    repo = sys.argv[3]
    
    # Reactions to add
    reactions = ["+1", "rocket", "heart"]
    
    try:
        issues = get_open_issues(token, owner, repo)
        
        # Filter out pull requests (GitHub API includes PRs as issues)
        issues = [issue for issue in issues if 'pull_request' not in issue]
        
        if len(issues) < 3:
            print(f"Error: Need at least 3 open issues, found {len(issues)}")
            sys.exit(1)
        
        # React to first 3 issues
        for i, issue in enumerate(issues[:3]):
            print(f"Reacting to issue #{issue['number']}: {issue['title']}")
            for reaction in reactions:
                try:
                    react_to_issue(token, owner, repo, issue['number'], reaction)
                    print(f"  Added {reaction} reaction")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 410:
                        print(f"  Reaction {reaction} already exists or not available")
                    else:
                        print(f"  Failed to add {reaction}: {e}")
        
        # Output comment with links
        print("\nComment with links to reacted issues:")
        for issue in issues[:3]:
            print(f"- https://github.com/{owner}/{repo}/issues/{issue['number']}")
        
        print(f"\nWallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()