"""
PR Submitter - Handles GitHub operations for submitting bounty solutions
"""

import os
import subprocess
from typing import Optional, Dict
from github import Github


class PRSubmitter:
    """Handles forking, branching, and submitting PRs"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN.")
        
        self.github = Github(self.token)
        self.wallet = os.getenv('RTC_WALLET', 'anonymous')
    
    def fork_repository(self, repo_name: str) -> Optional[str]:
        """Fork a repository to the user's account"""
        try:
            print(f"🍴 Forking {repo_name}...")
            repo = self.github.get_repo(repo_name)
            user = self.github.get_user()
            
            # Check if already forked
            forks = repo.get_forks()
            for fork in forks:
                if fork.owner.login == user.login:
                    print(f"✅ Already forked: {fork.full_name}")
                    return fork.full_name
            
            # Create fork
            fork = repo.create_fork()
            print(f"✅ Forked to: {fork.full_name}")
            return fork.full_name
            
        except Exception as e:
            print(f"❌ Fork failed: {e}")
            return None
    
    def create_branch(self, repo_name: str, branch_name: str, 
                      base_branch: str = "main") -> bool:
        """Create a new branch in the forked repo"""
        try:
            print(f"🌿 Creating branch: {branch_name}")
            repo = self.github.get_repo(repo_name)
            
            # Get base branch
            base = repo.get_branch(base_branch)
            
            # Create new branch
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base.commit.sha
            )
            print(f"✅ Branch created: {branch_name}")
            return True
            
        except Exception as e:
            print(f"❌ Branch creation failed: {e}")
            return False
    
    def submit_pr(self, original_repo: str, fork_repo: str, 
                  branch_name: str, title: str, body: str) -> Optional[str]:
        """Submit a pull request"""
        try:
            print(f"📤 Submitting PR...")
            
            # Get original repo
            repo = self.github.get_repo(original_repo)
            
            # Get user's login
            user = self.github.get_user()
            
            # Create PR
            pr = repo.create_pull(
                title=title,
                body=body + f"\n\n---\nWallet: {self.wallet}",
                head=f"{user.login}:{branch_name}",
                base="main"
            )
            
            print(f"✅ PR created: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            print(f"❌ PR submission failed: {e}")
            return None
    
    def build_pr_body(self, bounty_url: str, solution_summary: str,
                      changes: list) -> str:
        """Build a professional PR description"""
        body = f"""## Bounty Claim

**Bounty:** {bounty_url}

## Summary

{solution_summary}

## Changes

"""
        for change in changes:
            body += f"- {change}\n"
        
        body += f"\n## Testing

- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Follows repository coding standards
- [ ] Includes appropriate documentation
- [ ] No breaking changes (or documented)
"""
        return body


if __name__ == "__main__":
    # Example usage
    submitter = PRSubmitter()
    
    # Test forking
    repo = "Scottcjn/rustchain-bounties"
    fork = submitter.fork_repository(repo)
    print(f"Fork: {fork}")
