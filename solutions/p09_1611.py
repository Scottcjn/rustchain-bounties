#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Usage: python3 issue_reactor.py <github_token> <repo_owner/repo_name>
"""

import sys
import requests
import random

# Emoji reactions mapping
EMOJIS = {
    "thumbs-up": "+1",
    "rocket": "rocket",
    "heart": "heart"
}

def get_open_issues(repo, token):
    """Fetch open issues from the repository."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    params = {"state": "open", "per_page": 100}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    issues = response.json()
    
    # Filter out pull requests (they have pull_request key)
    return [issue for issue in issues if "pull_request" not in issue]

def add_reaction(issue_url, reaction, token):
    """Add an emoji reaction to a specific issue."""
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
        sys.exit(1)
    
    token = sys.argv[1]
    repo = sys.argv[2]
    
    try:
        print(f"Fetching open issues from {repo}...")
        issues = get_open_issues(repo, token)
        
        if len(issues) < 3:
            print(f"Error: Need at least 3 open issues, found {len(issues)}")
            sys.exit(1)
        
        # Select 3 random issues
        selected_issues = random.sample(issues, 3)
        
        print(f"Selected {len(selected_issues)} issues for reactions:")
        for issue in selected_issues:
            print(f"  - #{issue['number']}: {issue['title']}")
        
        # Add reactions
        for i, issue in enumerate(selected_issues):
            # Choose a random emoji for each issue
            emoji_name = random.choice(list(EMOJIS.keys()))
            emoji_content = EMOJIS[emoji_name]
            
            print(f"Adding {emoji_name} reaction to issue #{issue['number']}...")
            add_reaction(issue["url"], emoji_content, token)
            print(f"  ✓ Reaction added: {issue['html_url']}")
        
        # Print summary with links
        print("\n" + "="*50)
        print("REACTION SUMMARY")
        print("="*50)
        for issue in selected_issues:
            print(f"Issue #{issue['number']}: {issue['html_url']}")
        
        # Wallet address for bounty
        print("\n" + "="*50)
        print("BOUNTY INFORMATION")
        print("="*50)
        print("Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu")
        print("Bounty: 1 RTC")
        
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()