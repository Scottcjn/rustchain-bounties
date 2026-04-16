"""
GitHub Scanner Module for Autonomous Bounty Agent.
Scans the RustChain Bounties repository for open bounty issues matching criteria.
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    from github import Github
    from github.Issue import Issue
except ImportError:
    raise ImportError("PyGithub not installed. Run: pip install PyGithub")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Bounty:
    """Represents a bounty issue."""
    number: int
    title: str
    body: str
    labels: List[str]
    reward: Optional[str] = None
    difficulty: Optional[str] = None
    url: str = ""


class GitHubScanner:
    """Scans GitHub for open bounties matching agent capabilities."""

    REPO_NAME = "Scottcjn/rustchain-bounties"

    # Labels that indicate suitable bounties for an autonomous agent
    AGENT_FRIENDLY_LABELS = [
        "good first issue",
        "beginner",
        "standard",
        "propagation",
        "content",
        "documentation",
    ]

    # Labels to skip (require hardware, manual testing, etc.)
    SKIP_LABELS = [
        "hardware",
        "red-team",
        "critical",
        "audit required",
    ]

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var or pass token.")
        self.client = Github(self.token)
        self.repo = self.client.get_repo(self.REPO_NAME)
        logger.info(f"Initialized scanner for {self.REPO_NAME}")

    def get_open_bounties(self, limit: int = 50) -> List[Bounty]:
        """Fetch all open bounty issues."""
        bounties = []
        issues = self.repo.get_issues(state="open", sort="created", direction="desc")

        for issue in issues:
            if len(bounties) >= limit:
                break
            if issue.pull_request:
                continue
            bounty = self._parse_bounty(issue)
            if bounty:
                bounties.append(bounty)
        logger.info(f"Found {len(bounties)} open bounties")
        return bounties

    def _parse_bounty(self, issue: Issue) -> Optional[Bounty]:
        """Parse a GitHub issue into a Bounty object."""
        label_names = [label.name.lower() for label in issue.labels]
        for skip_label in self.SKIP_LABELS:
            if skip_label in label_names:
                return None
        reward = self._extract_reward(issue.body or "")
        difficulty = self._extract_difficulty(label_names)
        return Bounty(
            number=issue.number,
            title=issue.title,
            body=issue.body or "",
            labels=label_names,
            reward=reward,
            difficulty=difficulty,
            url=issue.html_url,
        )

    def _extract_reward(self, body: str) -> Optional[str]:
        """Extract reward amount from issue body."""
        import re
        patterns = [
            r'(\d+(?:\.\d+)?\s*(?:RTC|rtc))',
            r'Reward:?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*RTC',
        ]
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_difficulty(self, labels: List[str]) -> Optional[str]:
        """Determine difficulty from labels."""
        difficulty_map = {
            "good first issue": "beginner",
            "beginner": "beginner",
            "standard": "standard",
            "major": "major",
            "critical": "critical",
        }
        for label in labels:
            if label in difficulty_map:
                return difficulty_map[label]
        return "unknown"

    def get_agent_suitable_bounties(self, limit: int = 20) -> List[Bounty]:
        """Get bounties suitable for an autonomous agent."""
        all_bounties = self.get_open_bounties(limit=limit)
        suitable = []
        for bounty in all_bounties:
            has_friendly = any(label in bounty.labels for label in self.AGENT_FRIENDLY_LABELS)
            needs_human = any(kw in bounty.body.lower() for kw in ["hardware", "physical", "deploy to", "set up server"])
            if has_friendly and not needs_human:
                suitable.append(bounty)
        logger.info(f"Found {len(suitable)} agent-suitable bounties")
        return suitable

    def claim_bounty(self, bounty: Bounty, wallet_address: str) -> bool:
        """Post a comment claiming the bounty."""
        try:
            issue = self.repo.get_issue(bounty.number)
            comment = (
                f"**Claiming this bounty with autonomous agent.**\n\n"
                f"Wallet: `{wallet_address}`\n\n"
                f"Agent will submit a PR with the implementation."
            )
            issue.create_comment(comment)
            logger.info(f"Claimed bounty #{bounty.number}: {bounty.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to claim bounty #{bounty.number}: {e}")
            return False

    def check_already_claimed(self, bounty: Bounty, agent_identifier: str) -> bool:
        """Check if this agent has already claimed this bounty."""
        try:
            issue = self.repo.get_issue(bounty.number)
            for comment in issue.get_comments():
                if agent_identifier in comment.body:
                    return True
        except Exception as e:
            logger.error(f"Error checking existing claims: {e}")
        return False


if __name__ == "__main__":
    scanner = GitHubScanner()
    bounties = scanner.get_agent_suitable_bounties(limit=10)
    for b in bounties:
        print(f"#{b.number} [{b.difficulty}] {b.title} - Reward: {b.reward or 'TBD'}")
