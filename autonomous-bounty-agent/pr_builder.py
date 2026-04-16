"""
PR Builder Module for Autonomous Bounty Agent.
Handles forking, branch creation, file commits, and PR submission.
"""

import os
import logging
from typing import Optional, Dict
from dataclasses import dataclass

try:
    from github import Github
except ImportError:
    raise ImportError("PyGithub not installed. Run: pip install PyGithub")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PRResult:
    """Result of a PR submission."""
    success: bool
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    message: str = ""


class PRBuilder:
    """Builds and submits pull requests to the RustChain Bounties repository."""

    TARGET_REPO = "Scottcjn/rustchain-bounties"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var or pass token.")
        self.client = Github(self.token)
        self.target_repo = self.client.get_repo(self.TARGET_REPO)
        self.forked_repo = None
        logger.info(f"Initialized PR builder for {self.TARGET_REPO}")

    def fork_repository(self) -> bool:
        """Fork the target repository to the authenticated user's account."""
        try:
            username = self.client.get_user().login
            try:
                self.forked_repo = self.client.get_repo(f"{username}/{self.TARGET_REPO.split('/')[1]}")
                logger.info(f"Using existing fork: {self.forked_repo.full_name}")
                return True
            except Exception:
                pass
            self.forked_repo = self.target_repo.create_fork()
            logger.info(f"Created fork: {self.forked_repo.full_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to fork repository: {e}")
            return False

    def create_branch(self, branch_name: str, base_branch: str = "main") -> bool:
        """Create a new branch in the forked repository."""
        if not self.forked_repo:
            logger.error("No forked repository. Call fork_repository() first.")
            return False
        try:
            base = self.forked_repo.get_branch(base_branch)
            self.forked_repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)
            logger.info(f"Created branch: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create branch '{branch_name}': {e}")
            return False

    def commit_files(self, branch_name: str, files: Dict[str, str], commit_message: str = "Autonomous agent commit") -> bool:
        """Commit multiple files to a branch."""
        if not self.forked_repo:
            logger.error("No forked repository. Call fork_repository() first.")
            return False
        try:
            for path, content in files.items():
                try:
                    contents = self.forked_repo.get_contents(path, ref=branch_name)
                    self.forked_repo.update_file(path=path, message=commit_message, content=content, sha=contents.sha, branch=branch_name)
                    logger.info(f"Updated file: {path}")
                except Exception:
                    self.forked_repo.create_file(path=path, message=commit_message, content=content, branch=branch_name)
                    logger.info(f"Created file: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to commit files: {e}")
            return False

    def create_pr(self, branch_name: str, title: str, body: str, target_branch: str = "main") -> PRResult:
        """Create a pull request from the forked branch to the target repo."""
        if not self.forked_repo:
            logger.error("No forked repository. Call fork_repository() first.")
            return PRResult(success=False, message="No fork available")
        try:
            username = self.client.get_user().login
            head = f"{username}:{branch_name}"
            pr = self.target_repo.create_pull(title=title, body=body, head=head, base=target_branch)
            logger.info(f"Created PR #{pr.number}: {pr.html_url}")
            return PRResult(success=True, pr_url=pr.html_url, pr_number=pr.number, message=f"PR created successfully at {pr.html_url}")
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return PRResult(success=False, message=str(e))

    def submit_bounty_pr(self, bounty_number: int, bounty_title: str, wallet_address: str, files: Dict[str, str], agent_id: str, target_branch: str = "main") -> PRResult:
        """Complete workflow: fork -> branch -> commit -> PR for a bounty."""
        sanitized = "".join(c if c.isalnum() or c in "-_" else "-" for c in bounty_title)[:50]
        branch_name = f"bounty-{bounty_number}-{agent_id[:8]}"
        logger.info(f"Starting PR submission workflow for bounty #{bounty_number}")
        if not self.fork_repository():
            return PRResult(success=False, message="Failed to fork repository")
        if not self.create_branch(branch_name, base_branch=target_branch):
            return PRResult(success=False, message="Failed to create branch")
        commit_msg = f"Complete bounty #{bounty_number}: {bounty_title}\n\nBounty: https://github.com/{self.TARGET_REPO}/issues/{bounty_number}\nWallet: {wallet_address}"
        if not self.commit_files(branch_name, files, commit_message=commit_msg):
            return PRResult(success=False, message="Failed to commit files")
        pr_body = (
            f"## Bounty #{bounty_number} Submission\n\n"
            f"**Bounty:** [{bounty_title}](https://github.com/{self.TARGET_REPO}/issues/{bounty_number})\n\n"
            f"**Wallet for payout:** `{wallet_address}`\n\n"
            f"**Agent ID:** `{agent_id}`\n\n"
            f"---\n\nSubmitted by autonomous bounty agent.\n"
        )
        pr_title = f"Bounty #{bounty_number}: {bounty_title[:80]}"
        return self.create_pr(branch_name, pr_title, pr_body, target_branch=target_branch)


if __name__ == "__main__":
    builder = PRBuilder()
    print("PRBuilder initialized. Call via agent.py for full workflow.")
