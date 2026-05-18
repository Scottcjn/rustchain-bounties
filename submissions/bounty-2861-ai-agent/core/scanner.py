"""
RustChain Bounty Agent - Core Scanner Module
Discovers and monitors bounty opportunities on GitHub
"""

import os
import re
from typing import List, Dict, Optional
from github import Github
from datetime import datetime


class Bounty:
    """Represents a single bounty task"""
    
    def __init__(self, issue_data: Dict):
        self.title = issue_data.get('title', '')
        self.url = issue_data.get('html_url', '')
        self.number = issue_data.get('number', 0)
        self.body = issue_data.get('body', '')
        self.repo = issue_data.get('repository', {}).get('full_name', '')
        self.amount = self._parse_amount()
        self.difficulty = self._estimate_difficulty()
        self.created_at = issue_data.get('created_at', '')
        
    def _parse_amount(self) -> int:
        """Extract bounty amount from title/body"""
        # Look for patterns like "[BOUNTY: 50 RTC]" or "$50"
        patterns = [
            r'\[BOUNTY:\s*(\d+)\s*RTC\]',
            r'BOUNTY.*?(\d+)\s*RTC',
            r'\$(\d+)',
        ]
        text = f"{self.title} {self.body}"
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    def _estimate_difficulty(self) -> str:
        """Estimate task difficulty based on description"""
        text = f"{self.title} {self.body}".lower()
        
        if any(word in text for word in ['simple', 'easy', 'beginner', 'starter']):
            return 'easy'
        elif any(word in text for word in ['complex', 'advanced', 'expert', 'hard']):
            return 'hard'
        else:
            return 'medium'
    
    def __repr__(self):
        return f"Bounty(${self.amount} - {self.difficulty}): {self.title[:50]}..."


class BountyScanner:
    """Scans GitHub repositories for bounty issues"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN environment variable.")
        self.github = Github(self.token)
        self.results = []
        
    def scan_repository(self, repo_name: str, label: str = "bounty") -> List[Bounty]:
        """Scan a specific repository for bounty issues"""
        print(f"🔍 Scanning {repo_name} for bounties...")
        
        try:
            repo = self.github.get_repo(repo_name)
            issues = repo.get_issues(state='open', labels=[label])
            
            bounties = []
            for issue in issues:
                issue_data = {
                    'title': issue.title,
                    'html_url': issue.html_url,
                    'number': issue.number,
                    'body': issue.body or '',
                    'repository': {'full_name': repo_name},
                    'created_at': issue.created_at.isoformat() if issue.created_at else '',
                }
                bounty = Bounty(issue_data)
                if bounty.amount > 0:
                    bounties.append(bounty)
            
            print(f"✅ Found {len(bounties)} bounties in {repo_name}")
            return bounties
            
        except Exception as e:
            print(f"❌ Error scanning {repo_name}: {e}")
            return []
    
    def scan_multiple(self, repos: List[str], label: str = "bounty") -> List[Bounty]:
        """Scan multiple repositories"""
        all_bounties = []
        for repo in repos:
            bounties = self.scan_repository(repo, label)
            all_bounties.extend(bounties)
        
        # Sort by amount (highest first)
        all_bounties.sort(key=lambda x: x.amount, reverse=True)
        self.results = all_bounties
        return all_bounties
    
    def get_high_value(self, min_amount: int = 50) -> List[Bounty]:
        """Get high-value bounties above threshold"""
        return [b for b in self.results if b.amount >= min_amount]
    
    def print_summary(self):
        """Print scan summary"""
        print("\n" + "="*60)
        print("📊 BOUNTY SCAN SUMMARY")
        print("="*60)
        
        if not self.results:
            print("No bounties found.")
            return
        
        total_value = sum(b.amount for b in self.results)
        print(f"Total bounties: {len(self.results)}")
        print(f"Total value: ${total_value}")
        print(f"\nTop 5 bounties:")
        
        for i, bounty in enumerate(self.results[:5], 1):
            print(f"  {i}. ${bounty.amount} - {bounty.title[:60]}")
            print(f"     🔗 {bounty.url}")


if __name__ == "__main__":
    # Example usage
    scanner = BountyScanner()
    
    # Target repositories
    repos = [
        "Scottcjn/rustchain-bounties",
        "Scottcjn/Rustchain",
    ]
    
    bounties = scanner.scan_multiple(repos)
    scanner.print_summary()
    
    # Show high-value targets
    high_value = scanner.get_high_value(min_amount=50)
    if high_value:
        print(f"\n🎯 High-value targets (>=$50): {len(high_value)}")
        for bounty in high_value:
            print(f"   💰 ${bounty.amount} - {bounty.title[:50]}")
