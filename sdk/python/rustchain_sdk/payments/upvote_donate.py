"""
RustChain Upvote + Donate System
Milestone 1: Free upvote signals, RTC micro-donations, content stats aggregation, and multiplier tracking.
"""

from __future__ import annotations

import hashlib
import threading
import time
from typing import Dict, Any, List, Optional, Union

from ..wallet import RustChainWallet
from .models import DonationTier, UpvoteRecord, ContentStats
from .rate_limiter import AntiSpamGuard
from .receipts import CryptographicReceiptManager


class UpvoteDonateService:
    """
    Core service managing Content Upvotes and RTC Micro-donations.

    Features:
    - Free upvotes (signal/reputation only, zero cost)
    - Upvote + Donate (attaches RTC micropayment to creator)
    - Standard tiers: 0.001, 0.01, 0.1, 1.0 RTC + custom amounts
    - Hardware multiplier integration (rewards vintage node participation)
    - Content stats aggregation & top donor analytics
    - Ed25519 signature verification on transfer payloads
    - Anti-spam & rate limiting protection
    - Receipt generation and tamper-evident audit log
    """

    def __init__(
        self,
        receipt_manager: Optional[CryptographicReceiptManager] = None,
        anti_spam_guard: Optional[AntiSpamGuard] = None,
    ):
        self.receipt_manager = receipt_manager or CryptographicReceiptManager()
        self.anti_spam = anti_spam_guard or AntiSpamGuard(cooldown_seconds=0.1, max_actions_per_min=300)
        self._content_stats: Dict[str, ContentStats] = {}
        self._upvote_records: List[UpvoteRecord] = []
        self._creator_balances: Dict[str, float] = {}
        self._voter_content_history: Dict[str, set] = {}  # voter -> set of content_ids
        self._lock = threading.Lock()

    def upvote(
        self,
        content_id: str,
        voter: str,
        platform: str = "bottube",
        hardware_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Record a free upvote signal for content.

        Args:
            content_id: ID of the post / video / submission.
            voter: Wallet address or username of the voting agent.
            platform: Platform name ("bottube", "discord", "rustchain").
            hardware_multiplier: Vintage multiplier (e.g. 2.5 for G4 Mac).

        Returns:
            Dict with upvote details and updated content statistics.
        """
        if not content_id or not voter:
            raise ValueError("content_id and voter must be provided")

        action_hash = hashlib.sha256(f"upvote:{content_id}:{voter}".encode()).hexdigest()
        is_valid, err = self.anti_spam.validate_action(voter, action_hash)
        if not is_valid:
            raise ValueError(f"Spam protection rejected upvote: {err}")

        with self._lock:
            # Initialize or fetch content stats
            stats = self._get_or_create_stats(content_id)

            record = UpvoteRecord(
                content_id=content_id,
                voter=voter,
                is_donation=False,
                amount=0.0,
                platform=platform,
                hardware_multiplier=hardware_multiplier,
                timestamp=time.time(),
            )

            stats.upvote_count += 1
            if voter not in stats.unique_voters:
                stats.unique_voters.append(voter)

            # Update rolling average multiplier
            total_votes = len(stats.unique_voters)
            stats.average_multiplier = round(
                ((stats.average_multiplier * (total_votes - 1)) + hardware_multiplier) / total_votes,
                3,
            )

            self._upvote_records.append(record)
            voter_history = self._voter_content_history.setdefault(voter, set())
            voter_history.add(content_id)

            receipt = self.receipt_manager.generate_receipt(
                operation_type="upvote_free",
                sender=voter,
                recipient=content_id,
                amount=0.0,
                currency="RTC",
                extra_data={"content_id": content_id, "multiplier": hardware_multiplier, "platform": platform},
            )

            return {
                "status": "success",
                "record": record.to_dict(),
                "content_stats": stats.to_dict(),
                "receipt": receipt,
            }

    def upvote_donate(
        self,
        content_id: str,
        voter: str,
        creator: str,
        amount: float,
        wallet: Optional[RustChainWallet] = None,
        signed_tx: Optional[Dict[str, Any]] = None,
        platform: str = "bottube",
        hardware_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Record an Upvote with an attached RTC micro-donation.

        Args:
            content_id: Target content identifier.
            voter: Voter wallet address.
            creator: Creator recipient wallet address.
            amount: RTC donation amount (e.g. 0.001, 0.01, 0.1, 1.0).
            wallet: Optional sender wallet instance to sign transfer automatically.
            signed_tx: Optional pre-signed transaction payload if wallet is not passed.
            platform: Host platform identifier.
            hardware_multiplier: Hardware multiplier of voter.

        Returns:
            Dict containing transaction record, updated stats, creator balance, and receipt.
        """
        if not content_id or not voter or not creator:
            raise ValueError("content_id, voter, and creator are required")

        if amount <= 0:
            raise ValueError("Donation amount must be strictly positive")

        # Handle Ed25519 signing & verification first
        tx_signature: Optional[str] = None
        tx_pubkey: Optional[str] = None
        tx_hash: Optional[str] = None

        if wallet is not None:
            tx_payload = wallet.sign_transfer(to_address=creator, amount=int(amount * 1_000_000))
            tx_signature = tx_payload.get("signature")
            tx_pubkey = tx_payload.get("public_key")
            tx_hash = hashlib.sha256(json_bytes(tx_payload)).hexdigest()
        elif signed_tx is not None:
            # Verify pre-signed transfer with real Ed25519 cryptography
            valid = RustChainWallet.verify_transfer(signed_tx)
            if not valid:
                raise ValueError("Invalid Ed25519 transaction signature in signed_tx")
            tx_signature = signed_tx.get("signature")
            tx_pubkey = signed_tx.get("public_key")
            tx_hash = hashlib.sha256(json_bytes(signed_tx)).hexdigest()
        else:
            # Simulated local signing hash for light testing when keypair not supplied
            payload_raw = f"{voter}:{creator}:{amount}:{time.time()}".encode()
            tx_hash = hashlib.sha256(payload_raw).hexdigest()

        # Anti-spam validation
        action_hash = hashlib.sha256(
            f"donate:{content_id}:{voter}:{amount}:{tx_signature or time.time()}".encode()
        ).hexdigest()
        is_valid, err = self.anti_spam.validate_action(voter, action_hash)
        if not is_valid:
            raise ValueError(f"Spam protection rejected donation: {err}")


        with self._lock:
            stats = self._get_or_create_stats(content_id)

            record = UpvoteRecord(
                content_id=content_id,
                voter=voter,
                creator=creator,
                is_donation=True,
                amount=amount,
                platform=platform,
                hardware_multiplier=hardware_multiplier,
                signature=tx_signature,
                public_key=tx_pubkey,
                tx_hash=tx_hash,
                timestamp=time.time(),
            )

            # Update stats
            stats.upvote_count += 1
            stats.donation_count += 1
            stats.total_donated_rtc = round(stats.total_donated_rtc + amount, 6)

            if voter not in stats.unique_voters:
                stats.unique_voters.append(voter)

            # Categorize tier
            tier_str = str(amount)
            if tier_str in stats.donations_by_tier:
                stats.donations_by_tier[tier_str] += 1
            else:
                stats.donations_by_tier["custom"] += 1

            # Update top donors
            stats.top_donors[voter] = round(stats.top_donors.get(voter, 0.0) + amount, 6)

            # Credit creator balance
            self._creator_balances[creator] = round(self._creator_balances.get(creator, 0.0) + amount, 6)

            self._upvote_records.append(record)

            receipt = self.receipt_manager.generate_receipt(
                operation_type="upvote_donate",
                sender=voter,
                recipient=creator,
                amount=amount,
                currency="RTC",
                extra_data={
                    "content_id": content_id,
                    "multiplier": hardware_multiplier,
                    "platform": platform,
                    "tx_hash": tx_hash,
                },
            )

            return {
                "status": "success",
                "record": record.to_dict(),
                "content_stats": stats.to_dict(),
                "creator_balance": self._creator_balances[creator],
                "receipt": receipt,
            }

    def _get_or_create_stats(self, content_id: str) -> ContentStats:
        """Helper to get or initialize stats for content."""
        if content_id not in self._content_stats:
            self._content_stats[content_id] = ContentStats(content_id=content_id)
        return self._content_stats[content_id]

    def get_content_stats(self, content_id: str) -> Dict[str, Any]:
        """Fetch aggregated stats for a content item."""
        with self._lock:
            stats = self._content_stats.get(content_id, ContentStats(content_id=content_id))
            return stats.to_dict()

    def get_creator_earnings(self, creator: str) -> Dict[str, Any]:
        """Fetch total earnings received by a creator across all contents."""
        with self._lock:
            total_earned = self._creator_balances.get(creator, 0.0)
            creator_records = [r.to_dict() for r in self._upvote_records if r.creator == creator]
            return {
                "creator": creator,
                "total_earned_rtc": total_earned,
                "total_donations_received": len(creator_records),
                "donations": creator_records,
            }

    def list_recent_donations(self, content_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent donations, optionally filtered by content_id."""
        with self._lock:
            filtered = [
                r.to_dict() for r in self._upvote_records
                if r.is_donation and (content_id is None or r.content_id == content_id)
            ]
            return filtered[-limit:]


def json_bytes(obj: Dict[str, Any]) -> bytes:
    import json
    return json.dumps(obj, sort_keys=True).encode("utf-8")
