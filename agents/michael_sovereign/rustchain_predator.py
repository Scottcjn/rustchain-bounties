import os
import json
import requests
import argparse
from datetime import datetime

class RustChainBountyHunter:
    """
    Michael Sovereign's RustChain Autonomous Bounty Hunter V1.0
    Specially tuned for the RustChain ecosystem.
    """
    def __init__(self, node_url="https://50.28.86.131", github_token=None):
        self.node_url = node_url
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
        self.target_repo = "Scottcjn/rustchain-bounties"

    def fetch_open_bounties(self):
        """Scans the rustchain-bounties repo for open issues with the 'bounty' label."""
        url = f"https://api.github.com/repos/{self.target_repo}/issues?labels=bounty&state=open"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return []

    def evaluate_feasibility(self, issue):
        """Determines if the agent can solve the bounty based on keywords and reward."""
        title = issue.get("title", "").lower()
        body = issue.get("body", "").lower()
        reward_text = title + body
        
        # Scoring logic
        score = 0
        if "rtc" in reward_text: score += 20
        if "python" in reward_text: score += 30
        if "script" in reward_text: score += 10
        if "mcp" in reward_text: score += 40
        
        return score

    def run_cycle(self):
        print(f"[{datetime.now()}] Initializing RustChain Predator Scan...")
        bounties = self.fetch_open_bounties()
        print(f"Found {len(bounties)} open bounties.")
        
        for b in bounties:
            score = self.evaluate_feasibility(b)
            status = "ACQUIRED" if score > 50 else "IGNORE"
            print(f"[{status}] Score: {score} | {b['title']} | {b['html_url']}")

if __name__ == "__main__":
    hunter = RustChainBountyHunter()
    hunter.run_cycle()
