"""
RustChain Cryptographic Receipts & Audit Trail
Generates tamper-evident, SHA256 hashed and Ed25519 signed transaction receipts.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Dict, Any, List, Optional
from ..wallet import RustChainWallet


class CryptographicReceiptManager:
    """
    Manages generation, signing, and verification of tamper-evident receipts
    for agent-to-agent transfers, upvote donations, bridge ops, and bounty escrows.
    """

    def __init__(self, system_wallet: Optional[RustChainWallet] = None):
        self.system_wallet = system_wallet or RustChainWallet.create()
        self._receipt_chain: List[Dict[str, Any]] = []
        self._prev_hash: str = "0" * 64

    @property
    def system_address(self) -> str:
        return self.system_wallet.address

    def generate_receipt(
        self,
        operation_type: str,
        sender: str,
        recipient: str,
        amount: float,
        currency: str = "RTC",
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate and cryptographically sign a receipt.
        Chains to previous receipt hash for audit trail integrity.
        """
        timestamp = time.time()
        receipt_data = {
            "operation": operation_type,
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "currency": currency,
            "timestamp": timestamp,
            "prev_hash": self._prev_hash,
            "extra": extra_data or {},
        }

        # Compute deterministic payload
        payload_bytes = json.dumps(receipt_data, sort_keys=True).encode("utf-8")
        receipt_hash = hashlib.sha256(payload_bytes).hexdigest()

        # Sign receipt hash with system wallet
        signature = self.system_wallet.sign(receipt_hash.encode("utf-8")).hex()

        full_receipt = {
            "receipt_id": f"rcpt_{receipt_hash[:16]}",
            "receipt_hash": receipt_hash,
            "signer": self.system_wallet.address,
            "signer_pubkey": self.system_wallet.public_key_hex,
            "signature": signature,
            "data": receipt_data,
        }

        self._prev_hash = receipt_hash
        self._receipt_chain.append(full_receipt)
        return full_receipt

    @classmethod
    def verify_receipt(cls, receipt: Dict[str, Any]) -> bool:
        """
        Verify the integrity and Ed25519 signature of a receipt.
        """
        try:
            receipt_hash = receipt.get("receipt_hash")
            signer_pubkey = receipt.get("signer_pubkey")
            signature = receipt.get("signature")
            data = receipt.get("data")

            if not all([receipt_hash, signer_pubkey, signature, data]):
                return False

            # Recompute hash of data
            payload_bytes = json.dumps(data, sort_keys=True).encode("utf-8")
            computed_hash = hashlib.sha256(payload_bytes).hexdigest()

            if computed_hash != receipt_hash:
                return False

            # Verify signature over receipt_hash
            return RustChainWallet.verify_signature(
                signer_pubkey,
                receipt_hash.encode("utf-8"),
                signature,
            )
        except Exception:
            return False

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent audit chain receipts."""
        return self._receipt_chain[-limit:]
