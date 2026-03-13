#!/usr/bin/env python3
"""
Automated submission tool for adding RustChain to awesome lists.
This script helps identify suitable awesome lists and prepares PR submissions.
"""
import requests
import json
import time
from typing import List, Dict, Optional
import re


class AwesomeListSubmitter:
    def __init__(self):
        self.github_token = None
        self.session = requests.Session()
        
    def search_awesome_lists(self, query: str = "awesome-rust") -> List[Dict]:
        """Search GitHub for awesome lists matching the query."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RustChain-Bounty-Tool'
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            
        url = f'https://api.github.com/search/repositories'
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"Error searching awesome lists: {e}")
            return []
    
    def find_readme_content(self, owner: str, repo: str) -> Optional[str]:
        """Fetch README content from repository."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'RustChain-Bounty-Tool'
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            
        url = f'https://api.github.com/repos/{owner}/{repo}/contents/README.md'
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            content_data = response.json()
            import base64
            content = base64.b64decode(content_data['content']).decode('utf-8')
            return content
        except Exception as e:
            print(f"Error fetching README for {owner}/{repo}: {e}")
            return None
    
    def check_if_suitable(self, readme_content: str) -> bool:
        """Check if the README has a section for blockchain/cryptocurrency projects."""
        # Look for keywords indicating this might be a suitable list
        keywords = [
            r'blockchain', r'cryptocurrency', r'crypto', r'bitcoin', r'ethereum',
            r'developer tools', r'libraries', r'frameworks', r'projects',
            r'rust', r'web3', r'de-fi', r'distributed systems'
        ]
        
        content_lower = readme_content.lower()
        matches = 0
        for keyword in keywords:
            if re.search(keyword, content_lower):
                matches += 1
        
        # Consider suitable if it has at least 2 relevant keywords
        return matches >= 2
    
    def generate_pr_content(self, repo_name: str) -> Dict[str, str]:
        """Generate PR title and body for submission."""
        title = f"Add RustChain - A blockchain framework written in Rust"
        body = f"""## RustChain

**RustChain** is a blockchain framework written in Rust that enables developers to build secure, scalable decentralized applications.

- **GitHub**: https://github.com/Scottcjn/rustchain-bounties
- **Language**: Rust
- **License**: MIT/Apache-2.0
- **Features**: Secure consensus, smart contracts, decentralized governance

RustChain provides a robust foundation for building blockchain applications with the safety and performance benefits of Rust.

> This PR adds RustChain to the list of awesome Rust blockchain projects.
"""
        return {'title': title, 'body': body}
    
    def find_suitable_lists(self, search_query: str = "awesome-rust") -> List[Dict]:
        """Find awesome lists that might be suitable for RustChain submission."""
        print(f"Searching for awesome lists with query: {search_query}")
        repos = self.search_awesome_lists(search_query)
        suitable_repos = []
        
        for repo in repos:
            print(f"Checking {repo['full_name']}...")
            readme_content = self.find_readme_content(repo['owner']['login'], repo['name'])
            
            if readme_content and self.check_if_suitable(readme_content):
                suitable_repos.append({
                    'repo': repo,
                    'readme_preview': readme_content[:500] + "..." if len(readme_content) > 500 else readme_content
                })
                print(f"  ✓ Suitable: {repo['full_name']}")
            else:
                print(f"  ✗ Not suitable: {repo['full_name']}")
            
            # Be respectful to API limits
            time.sleep(1)
        
        return suitable_repos
    
    def prepare_submission_materials(self, suitable_repos: List[Dict]):
        """Prepare materials for submission to suitable repositories."""
        print("\nPreparing submission materials...")
        
        for item in suitable_repos:
            repo = item['repo']
            pr_content = self.generate_pr_content(repo['full_name'])
            
            print(f"\nRepository: {repo['html_url']}")
            print(f"Stars: {repo['stargazers_count']}")
            print(f"Description: {repo['description']}")
            print(f"PR Title: {pr_content['title']}")
            print(f"PR Body Preview:\n{pr_content['body'][:200]}...")
            print("-" * 50)


def main():
    submitter = AwesomeListSubmitter()
    
    print("RustChain Awesome List Submission Tool")
    print("=====================================")
    
    # First try searching for awesome-rust
    suitable_repos = submitter.find_suitable_lists("awesome-rust")
    
    # If none found, try broader searches
    if not suitable_repos:
        print("\nNo suitable Rust-specific lists found. Trying broader searches...")
        suitable_repos = submitter.find_suitable_lists("awesome blockchain")
    
    if not suitable_repos:
        suitable_repos = submitter.find_suitable_lists("awesome cryptocurrency")
    
    if not suitable_repos:
        suitable_repos = submitter.find_suitable_lists("awesome web3")
    
    if suitable_repos:
        submitter.prepare_submission_materials(suitable_repos)
        print(f"\nFound {len(suitable_repos)} suitable awesome lists for RustChain submission.")
        print("Follow the generated PR templates to submit your pull requests manually.")
    else:
        print("\nNo suitable awesome lists found. Consider creating an issue in popular lists instead.")

if __name__ == "__main__":
    main()