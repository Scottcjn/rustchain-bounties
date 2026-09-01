"""
RustChain ↔ BoTTube Cross-Bounty Escrow System
Milestone 4: Dual-currency bounty escrow, multi-party payout splits, and cross-platform reputation.
"""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from typing import Dict, Any, List, Optional

from ..wallet import RustChainWallet
from .models import BountyStatus, DualCurrencyBounty, BountyClaim
from .receipts import CryptographicReceiptManager


class CrossBountyEscrowManager:
    """
    Manages Dual-Currency Bounties (RTC + BoTTube tokens) in escrow.

    Features:
    - Creation & funding with both RTC and BoTTube token deposits
    - Claim submission with proof validation
    - Multi-party split settlements (claimant, reviewer, creator)
    - Cross-platform reputation tracking (RustChain + BoTTube)
    - Unclaimed refund & cancellation handling
    - Cryptographic receipts and audit trail for all disbursements
    """

    def __init__(self, receipt_manager: Optional[CryptographicReceiptManager] = None):
        self.receipt_manager = receipt_manager or CryptographicReceiptManager()
        self._bounties: Dict[str, DualCurrencyBounty] = {}
        self._escrow_rtc: float = 0.0
        self._escrow_bottube: float = 0.0
        self._reputation_scores: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_bounty(
        self,
        bounty_id: str,
        title: str,
        poster_rtc: str,
        poster_bottube: str,
        escrow_rtc: float,
        escrow_bottube: float,
        description: str = "",
        stipulations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new dual-currency bounty.
        """
        if not bounty_id or not title:
            raise ValueError("bounty_id and title are required")
        if escrow_rtc < 0 or escrow_bottube < 0:
            raise ValueError("Escrow deposit amounts cannot be negative")
        if escrow_rtc == 0 and escrow_bottube == 0:
            raise ValueError("At least one currency deposit must be greater than zero")

        with self._lock:
            if bounty_id in self._bounties:
                raise ValueError(f"Bounty ID {bounty_id} already exists")

            bounty = DualCurrencyBounty(
                bounty_id=bounty_id,
                title=title,
                description=description,
                poster_rtc=poster_rtc,
                poster_bottube=poster_bottube,
                escrow_rtc=escrow_rtc,
                escrow_bottube=escrow_bottube,
                status=BountyStatus.OPEN,
                stipulations=stipulations or [],
                created_at=time.time(),
            )

            self._escrow_rtc = round(self._escrow_rtc + escrow_rtc, 6)
            self._escrow_bottube = round(self._escrow_bottube + escrow_bottube, 6)
            self._bounties[bounty_id] = bounty

            receipt = self.receipt_manager.generate_receipt(
                operation_type="bounty_created",
                sender=poster_rtc,
                recipient=bounty_id,
                amount=escrow_rtc,
                currency="RTC",
                extra_data={
                    "escrow_bottube": escrow_bottube,
                    "title": title,
                    "poster_bottube": poster_bottube,
                },
            )

            return {
                "status": "success",
                "bounty": bounty.to_dict(),
                "receipt": receipt,
            }

    def submit_claim(
        self,
        bounty_id: str,
        claimant_rtc: str,
        claimant_bottube: str,
        proof_url: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Submit a solution claim for a dual-currency bounty.
        """
        if not claimant_rtc or not claimant_bottube or not proof_url:
            raise ValueError("claimant_rtc, claimant_bottube, and proof_url are required")

        with self._lock:
            bounty = self._bounties.get(bounty_id)
            if not bounty:
                raise ValueError(f"Bounty {bounty_id} not found")

            if bounty.status != BountyStatus.OPEN and bounty.status != BountyStatus.CLAIMED:
                raise ValueError(f"Cannot submit claim to bounty in status {bounty.status}")

            claim = BountyClaim(
                claimant_rtc=claimant_rtc,
                claimant_bottube=claimant_bottube,
                proof_url=proof_url,
                notes=notes,
                submitted_at=time.time(),
            )

            bounty.claims.append(claim)
            bounty.status = BountyStatus.UNDER_REVIEW

            receipt = self.receipt_manager.generate_receipt(
                operation_type="bounty_claim_submitted",
                sender=claimant_rtc,
                recipient=bounty_id,
                amount=0.0,
                currency="RTC",
                extra_data={
                    "claim_id": claim.claim_id,
                    "claimant_bottube": claimant_bottube,
                    "proof_url": proof_url,
                },
            )

            return {
                "status": "success",
                "claim": claim.to_dict(),
                "bounty_status": bounty.status.value,
                "receipt": receipt,
            }

    def settle_bounty(
        self,
        bounty_id: str,
        claim_id: Optional[str] = None,
        split_ratios: Optional[Dict[str, float]] = None,
        reviewer_rtc: Optional[str] = None,
        reviewer_bottube: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Settle and disburse funds for an approved bounty.

        Args:
            bounty_id: Target bounty ID.
            claim_id: Specific claim to approve (defaults to first claim).
            split_ratios: Payout ratio dict, e.g. {"claimant": 0.8, "reviewer": 0.2}.
            reviewer_rtc: Optional reviewer address if split includes reviewer.
            reviewer_bottube: Optional reviewer BoTTube username.

        Returns:
            Dict containing payout records, updated reputation scores, and receipts.
        """
        with self._lock:
            bounty = self._bounties.get(bounty_id)
            if not bounty:
                raise ValueError(f"Bounty {bounty_id} not found")

            if bounty.status == BountyStatus.SETTLED:
                raise ValueError(f"Bounty {bounty_id} is already settled")

            if not bounty.claims:
                raise ValueError(f"Cannot settle bounty without any claims")

            # Find matching claim
            target_claim = None
            if claim_id:
                for c in bounty.claims:
                    if c.claim_id == claim_id:
                        target_claim = c
                        break
            else:
                target_claim = bounty.claims[0]

            if not target_claim:
                raise ValueError(f"Claim {claim_id} not found")

            target_claim.approved = True

            # Calculate splits
            ratios = split_ratios or {"claimant": 1.0}
            claimant_ratio = ratios.get("claimant", 1.0)
            reviewer_ratio = ratios.get("reviewer", 0.0)

            if round(claimant_ratio + reviewer_ratio, 4) != 1.0:
                raise ValueError("Split ratios must sum to 1.0")

            disbursements = []

            # Claimant Payout
            c_rtc = round(bounty.escrow_rtc * claimant_ratio, 6)
            c_bt = round(bounty.escrow_bottube * claimant_ratio, 6)
            disbursements.append({
                "recipient_role": "claimant",
                "rtc_address": target_claim.claimant_rtc,
                "bottube_user": target_claim.claimant_bottube,
                "rtc_amount": c_rtc,
                "bottube_amount": c_bt,
            })

            # Reviewer Payout (if any)
            if reviewer_ratio > 0 and reviewer_rtc:
                r_rtc = round(bounty.escrow_rtc * reviewer_ratio, 6)
                r_bt = round(bounty.escrow_bottube * reviewer_ratio, 6)
                disbursements.append({
                    "recipient_role": "reviewer",
                    "rtc_address": reviewer_rtc,
                    "bottube_user": reviewer_bottube or "reviewer_agent",
                    "rtc_amount": r_rtc,
                    "bottube_amount": r_bt,
                })

            bounty.status = BountyStatus.SETTLED
            bounty.settled_at = time.time()
            bounty.payout_records = disbursements

            # Deduct from global escrow
            self._escrow_rtc = max(0.0, round(self._escrow_rtc - bounty.escrow_rtc, 6))
            self._escrow_bottube = max(0.0, round(self._escrow_bottube - bounty.escrow_bottube, 6))

            # Boost cross-platform reputation
            self._update_reputation(target_claim.claimant_rtc, target_claim.claimant_bottube, bounty.escrow_rtc, bounty.escrow_bottube)

            # Generate settlement receipt
            receipt = self.receipt_manager.generate_receipt(
                operation_type="bounty_settled",
                sender=bounty_id,
                recipient=target_claim.claimant_rtc,
                amount=bounty.escrow_rtc,
                currency="RTC",
                extra_data={
                    "escrow_bottube": bounty.escrow_bottube,
                    "disbursements": disbursements,
                    "claim_id": target_claim.claim_id,
                },
            )

            return {
                "status": "success",
                "bounty": bounty.to_dict(),
                "disbursements": disbursements,
                "receipt": receipt,
            }

    def cancel_and_refund(self, bounty_id: str, reason: str = "Bounty cancelled by poster") -> Dict[str, Any]:
        """
        Cancel an open/unclaimed bounty and refund deposits to poster.
        """
        with self._lock:
            bounty = self._bounties.get(bounty_id)
            if not bounty:
                raise ValueError(f"Bounty {bounty_id} not found")

            if bounty.status == BountyStatus.SETTLED:
                raise ValueError("Cannot cancel an already settled bounty")

            refund_rtc = bounty.escrow_rtc
            refund_bt = bounty.escrow_bottube

            self._escrow_rtc = max(0.0, round(self._escrow_rtc - refund_rtc, 6))
            self._escrow_bottube = max(0.0, round(self._escrow_bottube - refund_bt, 6))

            bounty.status = BountyStatus.REFUNDED
            bounty.settled_at = time.time()

            receipt = self.receipt_manager.generate_receipt(
                operation_type="bounty_refunded",
                sender=bounty_id,
                recipient=bounty.poster_rtc,
                amount=refund_rtc,
                currency="RTC",
                extra_data={"refund_bottube": refund_bt, "reason": reason},
            )

            return {
                "status": "success",
                "bounty": bounty.to_dict(),
                "refunded_rtc": refund_rtc,
                "refunded_bottube": refund_bt,
                "receipt": receipt,
            }

    def _update_reputation(self, rtc_addr: str, bt_user: str, earned_rtc: float, earned_bt: float) -> None:
        """Helper to increase cross-platform reputation score."""
        for key in (rtc_addr, bt_user):
            rep = self._reputation_scores.setdefault(key, {
                "score": 100,
                "bounties_completed": 0,
                "total_rtc_earned": 0.0,
                "total_bottube_earned": 0.0,
                "linked_identities": {"rtc": rtc_addr, "bottube": bt_user},
            })
            rep["bounties_completed"] += 1
            rep["total_rtc_earned"] = round(rep["total_rtc_earned"] + earned_rtc, 6)
            rep["total_bottube_earned"] = round(rep["total_bottube_earned"] + earned_bt, 6)
            rep["score"] += int(10 + earned_rtc * 2 + earned_bt * 0.1)

    def get_reputation(self, identity: str) -> Dict[str, Any]:
        """Fetch cross-platform reputation for an address or username."""
        with self._lock:
            return self._reputation_scores.get(identity, {
                "score": 100,
                "bounties_completed": 0,
                "total_rtc_earned": 0.0,
                "total_bottube_earned": 0.0,
                "linked_identities": {},
            })

    def get_bounty(self, bounty_id: str) -> Optional[Dict[str, Any]]:
        """Fetch bounty details by ID."""
        with self._lock:
            b = self._bounties.get(bounty_id)
            return b.to_dict() if b else None

    def list_bounties(self, status: Optional[BountyStatus] = None) -> List[Dict[str, Any]]:
        """List all bounties, optionally filtered by status."""
        with self._lock:
            bounties = list(self._bounties.values())
            if status is not None:
                bounties = [b for b in bounties if b.status == status]
            return [b.to_dict() for b in bounties]
