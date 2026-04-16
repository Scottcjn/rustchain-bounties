"""
Earnings Tracker Module for Autonomous Bounty Agent.
Tracks claimed bounties, submitted PRs, and estimated earnings in RTC.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RTC_NODE_URL = "https://50.28.86.131"


@dataclass
class ClaimedBounty:
    """Record of a claimed bounty."""
    bounty_number: int
    bounty_title: str
    claimed_at: str
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    status: str = "pending"
    estimated_reward: Optional[str] = None
    actual_reward: Optional[str] = None
    wallet_address: str = ""


@dataclass
class EarningsRecord:
    """Overall earnings record for an agent instance."""
    agent_id: str
    wallet_address: str
    created_at: str
    claimed_bounties: List[ClaimedBounty] = field(default_factory=list)
    total_pending: int = 0
    total_earned: int = 0
    total_merged: int = 0
    total_prs: int = 0


class EarningsTracker:
    """Tracks earnings and bounty claims for an autonomous agent."""

    def __init__(self, agent_id: str, wallet_address: str, data_dir: Optional[str] = None):
        self.agent_id = agent_id
        self.wallet_address = wallet_address
        self.data_dir = Path(data_dir) if data_dir else Path("./data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.record_file = self.data_dir / f"earnings_{agent_id}.json"
        self.record = self._load_record()
        logger.info(f"EarningsTracker initialized for agent {agent_id}")

    def _load_record(self) -> EarningsRecord:
        """Load existing record or create new one."""
        if self.record_file.exists():
            try:
                with open(self.record_file) as f:
                    data = json.load(f)
                    if "claimed_bounties" in data:
                        data["claimed_bounties"] = [ClaimedBounty(**b) for b in data["claimed_bounties"]]
                    return EarningsRecord(**data)
            except Exception as e:
                logger.warning(f"Could not load record: {e}. Creating new.")
        return EarningsRecord(agent_id=self.agent_id, wallet_address=self.wallet_address, created_at=datetime.utcnow().isoformat())

    def _save_record(self):
        """Persist record to disk."""
        try:
            with open(self.record_file, "w") as f:
                json.dump(asdict(self.record), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save record: {e}")

    def claim_bounty(self, bounty_number: int, bounty_title: str, estimated_reward: Optional[str] = None) -> ClaimedBounty:
        """Record a new bounty claim."""
        existing = self.get_bounty_claim(bounty_number)
        if existing:
            logger.info(f"Bounty #{bounty_number} already claimed")
            return existing
        claim = ClaimedBounty(bounty_number=bounty_number, bounty_title=bounty_title, claimed_at=datetime.utcnow().isoformat(), estimated_reward=estimated_reward, wallet_address=self.wallet_address)
        self.record.claimed_bounties.append(claim)
        self.record.total_pending += 1
        self._save_record()
        logger.info(f"Claimed bounty #{bounty_number}: {bounty_title}")
        return claim

    def record_pr_submission(self, bounty_number: int, pr_url: str, pr_number: int) -> bool:
        """Record PR submission for a claimed bounty."""
        claim = self.get_bounty_claim(bounty_number)
        if not claim:
            logger.error(f"No claim found for bounty #{bounty_number}")
            return False
        claim.pr_url = pr_url
        claim.pr_number = pr_number
        claim.status = "submitted"
        self.record.total_prs += 1
        self._save_record()
        logger.info(f"Recorded PR #{pr_number} for bounty #{bounty_number}")
        return True

    def mark_merged(self, bounty_number: int) -> bool:
        """Mark a bounty PR as merged."""
        claim = self.get_bounty_claim(bounty_number)
        if not claim:
            return False
        claim.status = "merged"
        self.record.total_merged += 1
        self.record.total_pending = max(0, self.record.total_pending - 1)
        self._save_record()
        return True

    def mark_paid(self, bounty_number: int, actual_reward: Optional[str] = None) -> bool:
        """Mark a bounty as paid out."""
        claim = self.get_bounty_claim(bounty_number)
        if not claim:
            return False
        claim.status = "paid"
        if actual_reward:
            claim.actual_reward = actual_reward
        self.record.total_earned += 1
        self._save_record()
        return True

    def get_bounty_claim(self, bounty_number: int) -> Optional[ClaimedBounty]:
        """Get claim record for a specific bounty."""
        for claim in self.record.claimed_bounties:
            if claim.bounty_number == bounty_number:
                return claim
        return None

    def get_summary(self) -> Dict:
        """Get earnings summary."""
        return {
            "agent_id": self.agent_id,
            "wallet": self.wallet_address,
            "total_prs": self.record.total_prs,
            "total_merged": self.record.total_merged,
            "total_paid": self.record.total_earned,
            "total_pending": self.record.total_pending,
            "bounties_claimed": len(self.record.claimed_bounties),
            "claims": [{"bounty": c.bounty_number, "title": c.bounty_title, "status": c.status, "pr": c.pr_url, "estimated": c.estimated_reward, "actual": c.actual_reward} for c in self.record.claimed_bounties],
        }

    def check_wallet_balance(self) -> Optional[Dict]:
        """Query the RustChain node for wallet balance."""
        if not requests:
            return None
        try:
            url = f"{RTC_NODE_URL}/wallet/{self.wallet_address}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            logger.warning(f"Could not query wallet: {e}")
            return None

    def export_summary(self, output_path: Optional[str] = None) -> str:
        """Export earnings summary to a JSON file."""
        path = output_path or f"earnings_summary_{self.agent_id}.json"
        summary = self.get_summary()
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Exported summary to {path}")
        return path


if __name__ == "__main__":
    tracker = EarningsTracker("test-agent-001", "RTC_test_wallet_address_123")
    tracker.claim_bounty(2861, "Test Bounty", "10 RTC")
    print(json.dumps(tracker.get_summary(), indent=2))
