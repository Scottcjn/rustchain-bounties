#!/usr/bin/env python3
"""
GitHub Issue Emoji Reactor
Adds emoji reactions (thumbs-up, rocket, heart) to 3+ open issues.
Usage: python3 reactor.py <github_token> [--dry-run]
"""

import os
import sys
import json
import requests
import random
from typing import List, Dict, Optional

# Configuration
REPO_OWNER = "your-org-or-username"  # Replace with actual repo owner
REPO_NAME = "your-repo-name"         # Replace with actual repo name
EMOJIS = ["+1", "rocket", "heart"]   # thumbs-up, rocket, heart
MIN_ISSUES = 3
WALLET = "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

class GitHubReactor:
    def __init__(self, token: str, dry_run: bool = False):
        self.token = token
        self.dry_run = dry_run
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.squirrel-girl-preview+json",
            "User-Agent": "EmojiReactor/1.0"
        }
        self.reacted_issues = []

    def get_open_issues(self) -> List[Dict]:
        """Fetch open issues from the repository."""
        url = f"{self.base_url}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
        params = {"state": "open", "per_page": 100, "page": 1}
        issues = []
        
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            page_issues = response.json()
            if not page_issues:
                break
            # Filter out pull requests (GitHub API includes PRs as issues)
            issues.extend([i for i in page_issues if 'pull_request' not in i])
            params["page"] += 1
        
        return issues

    def add_reaction(self, issue_number: int, emoji: str) -> bool:
        """Add an emoji reaction to a specific issue."""
        url = f"{self.base_url}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}/reactions"
        payload = {"content": emoji}
        
        if self.dry_run:
            print(f"[DRY RUN] Would add {emoji} reaction to issue #{issue_number}")
            return True
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 201:
                print(f"✓ Added {emoji} reaction to issue #{issue_number}")
                return True
            elif response.status_code == 200:
                print(f"✓ Already reacted with {emoji} to issue #{issue_number}")
                return True
            else:
                print(f"✗ Failed to add {emoji} to issue #{issue_number}: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Error adding reaction: {e}")
            return False

    def react_to_issues(self, issues: List[Dict]) -> List[int]:
        """Add reactions to multiple issues."""
        if len(issues) < MIN_ISSUES:
            print(f"Warning: Only {len(issues)} open issues found, need at least {MIN_ISSUES}")
            return []
        
        # Select random issues to react to (at least MIN_ISSUES)
        selected_issues = random.sample(issues, min(MIN_ISSUES, len(issues)))
        reacted = []
        
        for issue in selected_issues:
            issue_number = issue["number"]
            # Add all three emojis to each selected issue
            for emoji in EMOJIS:
                success = self.add_reaction(issue_number, emoji)
                if success:
                    reacted.append(issue_number)
        
        return list(set(reacted))  # Deduplicate

    def generate_comment(self, issue_numbers: List[int]) -> str:
        """Generate a comment with links to reacted issues."""
        links = []
        for num in issue_numbers:
            links.append(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/issues/{num}")
        
        comment = (
            f"## Emoji Reactions Added\n\n"
            f"I've added thumbs-up, rocket, and heart reactions to the following issues:\n\n"
        )
        for link in links:
            comment += f"- {link}\n"
        comment += f"\nWallet: {WALLET}\n"
        return comment

    def run(self):
        """Main execution flow."""
        print(f"Fetching open issues from {REPO_OWNER}/{REPO_NAME}...")
        issues = self.get_open_issues()
        print(f"Found {len(issues)} open issues (excluding PRs)")
        
        if not issues:
            print("No open issues found. Exiting.")
            return
        
        reacted_issue_numbers = self.react_to_issues(issues)
        
        if reacted_issue_numbers:
            comment = self.generate_comment(reacted_issue_numbers)
            print("\n" + "="*50)
            print("Generated Comment:")
            print(comment)
            print("="*50)
        else:
            print("No reactions were added.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 reactor.py <github_token> [--dry-run]")
        print("Example: python3 reactor.py ghp_xxxxxxxxxxxx --dry-run")
        sys.exit(1)
    
    token = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    reactor = GitHubReactor(token, dry_run)
    reactor.run()

if __name__ == "__main__":
    main()