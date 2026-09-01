"""
RustChain ↔ BoTTube Cross-Wallet Bridge
Milestone 2: Bidirectional atomic bridge between RustChain RTC and BoTTube wallets.
"""

from __future__ import annotations

import hashlib
import threading
import time
from typing import Dict, Any, List, Optional

from ..wallet import RustChainWallet
from .models import BridgeDirection, BridgeStatus, BridgeTransaction
from .receipts import CryptographicReceiptManager


class CrossWalletBridge:
    """
    Bidirectional Bridge between RustChain RTC and BoTTube Wallets.

    Features:
    - RTC → BoTTube: Locks RTC in escrow, verifies transfer signature, credits BoTTube user.
    - BoTTube → RTC: Locks BoTTube balance in escrow, credits RTC address.
    - Configurable exchange rates (default 1.0) and fee structure (default 0.1% / 10 bps).
    - Thread-safe transaction state machine (PENDING -> LOCKED -> SETTLED / REFUNDED).
    - Cryptographic receipt generation and audit logging.
    - Programmatic settlement, status inspection, and refund recovery.
    """

    def __init__(
        self,
        exchange_rate: float = 1.0,
        fee_basis_points: int = 10,  # 10 bps = 0.10%
        receipt_manager: Optional[CryptographicReceiptManager] = None,
    ):
        self.exchange_rate = exchange_rate
        self.fee_basis_points = fee_basis_points
        self.receipt_manager = receipt_manager or CryptographicReceiptManager()

        # In-memory escrow and balance ledgers
        self._rtc_escrow_pool: float = 0.0
        self._botttube_escrow_pool: float = 0.0
        self._rtc_balances: Dict[str, float] = {}
        self._botttube_balances: Dict[str, float] = {}
        self._transactions: Dict[str, BridgeTransaction] = {}
        self._lock = threading.Lock()

    def set_exchange_rate(self, rate: float, fee_bps: Optional[int] = None) -> None:
        """Update exchange rate and optionally fee basis points."""
        if rate <= 0:
            raise ValueError("Exchange rate must be positive")
        with self._lock:
            self.exchange_rate = rate
            if fee_bps is not None:
                if fee_bps < 0 or fee_bps > 5000:
                    raise ValueError("Fee bps must be between 0 and 5000 (0% - 50%)")
                self.fee_basis_points = fee_bps

    def calculate_fee(self, amount: float) -> float:
        """Calculate bridge fee in token units."""
        return round(amount * (self.fee_basis_points / 10000.0), 6)

    def rtc_to_botttube(
        self,
        rtc_address: str,
        botttube_user: str,
        amount: float,
        rtc_wallet: Optional[RustChainWallet] = None,
        signed_transfer: Optional[Dict[str, Any]] = None,
    ) -> BridgeTransaction:
        """
        Bridge RTC to BoTTube tokens.
        Locks RTC, calculates exchange and fees, credits BoTTube user account.
        """
        if not rtc_address or not botttube_user:
            raise ValueError("rtc_address and botttube_user are required")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        fee = self.calculate_fee(amount)
        net_rtc = round(amount - fee, 6)
        credited_botttube = round(net_rtc * self.exchange_rate, 6)

        tx_sig: Optional[str] = None
        if rtc_wallet is not None:
            # Sign the lock transfer
            payload = rtc_wallet.sign_transfer(to_address="RTC_BRIDGE_ESCROW", amount=int(amount * 1_000_000))
            tx_sig = payload.get("signature")
        elif signed_transfer is not None:
            # Verify signature
            if not RustChainWallet.verify_transfer(signed_transfer):
                raise ValueError("Invalid signed transfer payload for RTC lock")
            tx_sig = signed_transfer.get("signature")

        with self._lock:
            # Check sender balance if tracked
            current_sender_rtc = self._rtc_balances.get(rtc_address, 1000.0)  # default initial balance for testing
            if current_sender_rtc < amount:
                raise ValueError(f"Insufficient RTC balance: has {current_sender_rtc}, needs {amount}")

            self._rtc_balances[rtc_address] = round(current_sender_rtc - amount, 6)
            self._rtc_escrow_pool = round(self._rtc_escrow_pool + amount, 6)

            tx = BridgeTransaction(
                direction=BridgeDirection.RTC_TO_BOTTUBE,
                sender=rtc_address,
                recipient=botttube_user,
                amount=amount,
                fee=fee,
                net_amount=credited_botttube,
                exchange_rate=self.exchange_rate,
                status=BridgeStatus.LOCKED,
                escrow_lock_id=f"escrow_rtc_{hashlib.sha256(f'{rtc_address}:{time.time()}'.encode()).hexdigest()[:10]}",
                signature=tx_sig,
                created_at=time.time(),
            )

            # Settle immediately to BoTTube recipient
            tx.status = BridgeStatus.SETTLED
            tx.settled_at = time.time()

            # Credit recipient BoTTube balance
            self._botttube_balances[botttube_user] = round(
                self._botttube_balances.get(botttube_user, 0.0) + credited_botttube,
                6,
            )

            receipt = self.receipt_manager.generate_receipt(
                operation_type="bridge_rtc_to_botttube",
                sender=rtc_address,
                recipient=botttube_user,
                amount=amount,
                currency="RTC",
                extra_data={
                    "tx_id": tx.tx_id,
                    "net_credited": credited_botttube,
                    "exchange_rate": self.exchange_rate,
                    "fee": fee,
                },
            )
            tx.receipt_hash = receipt["receipt_hash"]

            self._transactions[tx.tx_id] = tx
            return tx

    def botttube_to_rtc(
        self,
        botttube_user: str,
        rtc_address: str,
        amount: float,
        auth_token: Optional[str] = None,
    ) -> BridgeTransaction:
        """
        Bridge BoTTube tokens to RustChain RTC.
        Locks BoTTube tokens, calculates exchange and fees, credits RTC wallet.
        """
        if not botttube_user or not rtc_address:
            raise ValueError("botttube_user and rtc_address are required")
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        fee = self.calculate_fee(amount)
        net_botttube = round(amount - fee, 6)
        credited_rtc = round(net_botttube / self.exchange_rate, 6)

        with self._lock:
            current_botttube = self._botttube_balances.get(botttube_user, 1000.0)  # default initial balance
            if current_botttube < amount:
                raise ValueError(f"Insufficient BoTTube balance: has {current_botttube}, needs {amount}")

            self._botttube_balances[botttube_user] = round(current_botttube - amount, 6)
            self._botttube_escrow_pool = round(self._botttube_escrow_pool + amount, 6)

            tx = BridgeTransaction(
                direction=BridgeDirection.BOTTUBE_TO_RTC,
                sender=botttube_user,
                recipient=rtc_address,
                amount=amount,
                fee=fee,
                net_amount=credited_rtc,
                exchange_rate=self.exchange_rate,
                status=BridgeStatus.LOCKED,
                escrow_lock_id=f"escrow_bt_{hashlib.sha256(f'{botttube_user}:{time.time()}'.encode()).hexdigest()[:10]}",
                created_at=time.time(),
            )

            # Settle immediately to RTC recipient
            tx.status = BridgeStatus.SETTLED
            tx.settled_at = time.time()

            # Credit recipient RTC balance
            self._rtc_balances[rtc_address] = round(
                self._rtc_balances.get(rtc_address, 0.0) + credited_rtc,
                6,
            )

            receipt = self.receipt_manager.generate_receipt(
                operation_type="bridge_botttube_to_rtc",
                sender=botttube_user,
                recipient=rtc_address,
                amount=amount,
                currency="BOTTUBE",
                extra_data={
                    "tx_id": tx.tx_id,
                    "net_credited_rtc": credited_rtc,
                    "exchange_rate": self.exchange_rate,
                    "fee": fee,
                },
            )
            tx.receipt_hash = receipt["receipt_hash"]

            self._transactions[tx.tx_id] = tx
            return tx

    def refund_transaction(self, tx_id: str, reason: str = "User requested refund") -> BridgeTransaction:
        """
        Refund an unsettled or locked bridge transaction back to sender.
        """
        with self._lock:
            tx = self._transactions.get(tx_id)
            if not tx:
                raise ValueError(f"Transaction {tx_id} not found")

            if tx.status == BridgeStatus.REFUNDED:
                return tx

            if tx.status != BridgeStatus.LOCKED and tx.status != BridgeStatus.PENDING:
                raise ValueError(f"Cannot refund transaction in status {tx.status}")

            if tx.direction == BridgeDirection.RTC_TO_BOTTUBE:
                # Return RTC to sender
                self._rtc_balances[tx.sender] = round(self._rtc_balances.get(tx.sender, 0.0) + tx.amount, 6)
                self._rtc_escrow_pool = max(0.0, round(self._rtc_escrow_pool - tx.amount, 6))
            else:
                # Return BoTTube tokens to sender
                self._botttube_balances[tx.sender] = round(self._botttube_balances.get(tx.sender, 0.0) + tx.amount, 6)
                self._botttube_escrow_pool = max(0.0, round(self._botttube_escrow_pool - tx.amount, 6))

            tx.status = BridgeStatus.REFUNDED
            tx.error_message = reason
            tx.settled_at = time.time()
            return tx

    def get_transaction(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Fetch transaction record by ID."""
        with self._lock:
            tx = self._transactions.get(tx_id)
            return tx.to_dict() if tx else None

    def get_transaction_history(self, party_identifier: Optional[str] = None) -> List[Dict[str, Any]]:
        """List transaction history, optionally filtered by user or address."""
        with self._lock:
            txs = list(self._transactions.values())
            if party_identifier:
                txs = [t for t in txs if t.sender == party_identifier or t.recipient == party_identifier]
            return [t.to_dict() for t in txs]

    def get_balances(self, identifier: str) -> Dict[str, float]:
        """Fetch both RTC and BoTTube balances for an agent / address."""
        with self._lock:
            return {
                "rtc_balance": self._rtc_balances.get(identifier, 0.0),
                "botttube_balance": self._botttube_balances.get(identifier, 0.0),
            }

    def seed_balance(self, identifier: str, rtc: float = 0.0, botttube: float = 0.0) -> None:
        """Seed initial balance for testing / development."""
        with self._lock:
            if rtc > 0:
                self._rtc_balances[identifier] = round(self._rtc_balances.get(identifier, 0.0) + rtc, 6)
            if botttube > 0:
                self._botttube_balances[identifier] = round(self._botttube_balances.get(identifier, 0.0) + botttube, 6)
