#!/usr/bin/env python3
"""
RustChain Bounty Hunter Agent
Autonomously finds, evaluates, and claims RustChain bounties.
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from typing import Optional

# Configuration
GITHUB_API = "https://api.github.com"
REPO_OWNER = "Scottcjn"
REPO_NAME = "rustchain-bounties"
NODE_URL = "https://50.28.86.131"

class BountyHunterAgent:
    def __init__(self, wallet_name: str):
        self.wallet_name = wallet_name
        self.session_token = os.environ.get("GITHUB_TOKEN", "")
        self.headers = {
            "Authorization": f"token {self.session_token}",
            "Accept": "application/vnd.github.v3+json"
        } if self.session_token else {}

    def fetch_open_bounties(self) -> list:
        """Fetch all open bounties from the RustChain bounties repo."""
        print("[*] Fetching open bounties...")
        url = f"{GITHUB_API}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
        params = {"state": "open", "per_page": 50}
        
        resp = requests.get(url, headers=self.headers, params=params)
        resp.raise_for_status()
        issues = resp.json()
        
        bounties = []
        for issue in issues:
            if "BOUNTY:" in issue.get("title", "").upper():
                bounties.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "body": issue.get("body", ""),
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "html_url": issue["html_url"]
                })
        
        print(f"[+] Found {len(bounties)} open bounties")
        return bounties

    def evaluate_bounty(self, bounty: dict) -> dict:
        """Evaluate if we can complete this bounty."""
        title = bounty["title"].lower()
        body = bounty["body"].lower()
        labels = bounty["labels"]
        
        # Extract RTC amount
        import re
        match = re.search(r'\[BOUNTY:\s*(\d+)\s*RTC\]', bounty["title"], re.IGNORECASE)
        rtc_amount = int(match.group(1)) if match else 0
        
        # Skill assessment
        can_do = {
            "docker": "docker" in title or "docker" in body,
            "github_action": "github action" in title or "action" in title,
            "vscode": "vs code" in title or "extension" in title,
            "script": "script" in title or "bot" in title,
            "docs": "docs" in title or "readme" in title or "document" in title,
        }
        
        difficulty = "easy" if any(l in labels for l in ["easy", "good-first-issue"]) else \
                     "medium" if any(l in labels for l in ["standard", "help-wanted"]) else \
                     "hard" if any(l in labels for l in ["critical", "major"]) else "unknown"
        
        score = rtc_amount * (1.5 if difficulty == "easy" else 1.0 if difficulty == "medium" else 0.8)
        
        return {
            **bounty,
            "rtc_amount": rtc_amount,
            "difficulty": difficulty,
            "can_partially_do": any(can_do.values()),
            "skills_needed": [k for k, v in can_do.items() if v],
            "score": score
        }

    def fork_repo(self, repo_full_name: str) -> Optional[str]:
        """Fork a repository to the authenticated user's account."""
        print(f"[*] Forking {repo_full_name}...")
        url = f"{GITHUB_API}/repos/{repo_full_name}/forks"
        resp = requests.post(url, headers=self.headers)
        
        if resp.status_code == 202:
            data = resp.json()
            print(f"[+] Forked to {data['full_name']}")
            return data['full_name']
        elif resp.status_code == 202:
            # Fork may already exist
            resp = requests.get(url, headers=self.headers)
            forks = resp.json()
            for fork in forks:
                if fork["owner"]["login"] == self.session_token.split("/")[0] if self.session_token else "":
                    return fork["full_name"]
        print(f"[!] Fork failed: {resp.status_code}")
        return None

    def create_pr(self, forked_repo: str, bounty: dict, changes: dict) -> Optional[str]:
        """Create a PR for the bounty."""
        print(f"[*] Creating PR for bounty #{bounty['number']}...")
        
        # Implementation would go here
        # For now, return placeholder
        return None

    def run(self):
        """Main agent loop."""
        print(f"""
========================================
  RustChain Bounty Hunter Agent
  Wallet: {self.wallet_name}
========================================
""")
        
        # Fetch and evaluate bounties
        bounties = self.fetch_open_bounties()
        evaluated = [self.evaluate_bounty(b) for b in bounties]
        
        # Sort by score
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        
        print("\n[*] Top bounties by score:")
        for i, b in enumerate(evaluated[:5]):
            print(f"  {i+1}. #{b['number']} [{b['rtc_amount']} RTC] {b['title'][:50]}")
            print(f"     Difficulty: {b['difficulty']} | Can do: {b['skills_needed']}")
        
        # TODO: Implement autonomous PR creation
        print("\n[!] Autonomous PR creation not yet implemented.")
        print("[*] This script demonstrates the evaluation logic.")
        
        return evaluated

if __name__ == "__main__":
    wallet = sys.argv[1] if len(sys.argv) > 1 else "shuziyoumin2_agent"
    agent = BountyHunterAgent(wallet)
    results = agent.run()
    
    # Save results
    with open("bounty_analysis.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n[+] Results saved to bounty_analysis.json")
