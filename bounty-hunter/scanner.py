#!/usr/bin/env python3
"""Bounty Scanner - GitHub API integration"""

import os
import asyncio
from github import Github
from typing import List, Dict


class BountyScanner:
    def __init__(self, config: dict):
        self.github = Github(config['github_token'])
        self.repo_owner = config['repo_owner']
        self.repo_name = config['repo_name']
        
    async def scan_bounties(self) -> List[Dict]:
        """Scan for open bounty issues"""
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        issues = repo.get_issues(labels=['bounty'], state='open')
        
        bounties = []
        for issue in issues:
            bounties.append({
                'id': issue.number,
                'title': issue.title,
                'body': issue.body,
                'labels': [l.name for l in issue.labels],
                'comments': issue.comments,
                'url': issue.html_url,
                'created_at': issue.created_at,
            })
        
        return bounties
    
    async def fork_repo(self, bounty: Dict) -> str:
        """Fork the repository for a bounty"""
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        return f"https://github.com/{os.getenv('GITHUB_USER')}/{self.repo_name}"
    
    async def get_issue_details(self, issue_number: int) -> Dict:
        """Get detailed info about a specific issue"""
        repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
        issue = repo.get_issue(issue_number)

        return {
            'id': issue.number,
            'title': issue.title,
            'body': issue.body,
            'comments': issue.get_comments(),
            'labels': [l.name for l in issue.labels],
        }

    async def add_reaction(self, issue_number: int, reaction: str = "+1") -> bool:
        """Add an emoji reaction to an issue"""
        try:
            repo = self.github.get_repo(f"{self.repo_owner}/{self.repo_name}")
            issue = repo.get_issue(issue_number)
            issue.create_reaction(reaction)
            return True
        except Exception:
            return False

    async def add_reactions_to_issues(self, issue_numbers: List[int], reaction: str = "+1") -> Dict[int, bool]:
        """Add an emoji reaction to multiple issues; returns a map of issue number to success"""
        results = {}
        for number in issue_numbers:
            results[number] = await self.add_reaction(number, reaction)
        return results
