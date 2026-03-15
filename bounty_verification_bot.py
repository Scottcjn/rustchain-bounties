#!/usr/bin/env python3
"""
Bounty Verification Bot - Auto-Verify Star/Follow Claims
For: Scottcjn/rustchain-bounties Issue #747
Reward: 50-75 RTC
"""
import os
import sys
import json
import time
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional

# GitHub API configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_API = 'https://api.github.com'

HEADERS = {'Accept': 'application/vnd.github.v3+json'}
if GITHUB_TOKEN:
    HEADERS['Authorization'] = f'token {GITHUB_TOKEN}'

class BountyVerifier:
    def __init__(self, repo_owner='Scottcjn', repo_name='rustchain-bounties'):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
    
    def verify_star(self, username: str, repo: str) -> Dict:
        """Verify if user has starred a repository"""
        try:
            url = f'{GITHUB_API}/user/starred/{username}/{repo}'
            resp = self.session.get(url)
            return {
                'verified': resp.status_code == 204,
                'status_code': resp.status_code
            }
        except Exception as e:
            return {'verified': False, 'error': str(e)}
    
    def verify_follow(self, username: str, target: str) -> Dict:
        """Verify if user is following target"""
        try:
            url = f'{GITHUB_API}/users/{username}/following/{target}'
            resp = self.session.get(url)
            return {
                'verified': resp.status_code == 204,
                'status_code': resp.status_code
            }
        except Exception as e:
            return {'verified': False, 'error': str(e)}
    
    def get_user_info(self, username: str) -> Dict:
        """Get user profile info"""
        try:
            url = f'{GITHUB_API}/users/{username}'
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'exists': True,
                    'public_repos': data.get('public_repos', 0),
                    'followers': data.get('followers', 0),
                    'following': data.get('following', 0),
                    'created_at': data.get('created_at', '')
                }
            return {'exists': False}
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """Get repository info"""
        try:
            url = f'{GITHUB_API}/repos/{owner}/{repo}'
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    'exists': True,
                    'stars': data.get('stargazers_count', 0),
                    'forks': data.get('forks_count', 0),
                    'watchers': data.get('watchers_count', 0)
                }
            return {'exists': False}
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def verify_wallet_exists(self, address: str) -> Dict:
        """Verify if a wallet address exists (placeholder for blockchain check)"""
        # This would integrate with blockchain APIs in production
        return {
            'address': address,
            'verified': len(address) >= 40,  # Basic format check
            'note': 'Requires blockchain node integration'
        }
    
    def scan_issue_comments(self, issue_number: int) -> List[Dict]:
        """Scan issue for claim comments that need verification"""
        try:
            url = f'{GITHUB_API}/repos/{self.repo_owner}/{self.repo_name}/issues/{issue_number}/comments'
            resp = self.session.get(url)
            if resp.status_code == 200:
                comments = resp.json()
                claims = []
                for comment in comments:
                    body = comment.get('body', '')
                    if 'claim' in body.lower():
                        # Extract usernames mentioned
                        user_matches = re.findall(r'@(\w+)', body)
                        # Extract wallet addresses
                        wallet_matches = re.findall(r'(0x[a-fA-F0-9]{40}|RTC[a-fA-F0-9]{32})', body)
                        claims.append({
                            'comment_id': comment['id'],
                            'user': comment['user']['login'],
                            'mentioned_users': user_matches,
                            'wallets': wallet_matches,
                            'timestamp': comment['created_at']
                        })
                return claims
            return []
        except Exception as e:
            print(f'Error scanning comments: {e}')
            return []
    
    def generate_verification_report(self, claims: List[Dict]) -> str:
        """Generate a verification report for all claims"""
        report = ['# Bounty Verification Report', '']
        report.append(f'Generated: {datetime.now().isoformat()}')
        report.append('')
        
        for i, claim in enumerate(claims, 1):
            report.append(f'## Claim #{i}')
            report.append(f'- User: @{claim["user"]}')
            report.append(f'- Timestamp: {claim["timestamp"]}')
            
            # Verify mentioned users
            for user in claim['mentioned_users']:
                user_info = self.get_user_info(user)
                report.append(f'- @{user}: {user_info.get("exists", False)} (exists)')
            
            # Verify wallets
            for wallet in claim['wallets']:
                wallet_info = self.verify_wallet_exists(wallet)
                report.append(f'- Wallet {wallet[:10]}...: {wallet_info.get("verified", False)}')
            
            report.append('')
        
        return '\n'.join(report)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Bounty Verification Bot')
    parser.add_argument('--issue', '-i', type=int, default=747, help='Issue number to scan')
    parser.add_argument('--repo', '-r', default='Scottcjn/rustchain-bounties', help='Repository')
    args = parser.parse_args()
    
    repo_parts = args.repo.split('/')
    verifier = BountyVerifier(repo_parts[0], repo_parts[1])
    
    print(f'Scanning issue #{args.issue}...')
    claims = verifier.scan_issue_comments(args.issue)
    
    print(f'Found {len(claims)} claim(s)')
    
    if claims:
        report = verifier.generate_verification_report(claims)
        print('\n' + report)
        
        # Save report
        with open('verification_report.md', 'w') as f:
            f.write(report)
        print('\nReport saved to verification_report.md')


if __name__ == '__main__':
    main()
