"""
RustChain 8004 / x402 HTTP Payment Protocol
Milestone 3: Agent-to-Agent Machine-to-Machine micropayments over HTTP 402.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import json
import time
import uuid
from typing import Dict, Any, Optional, Callable, Tuple, Union

from ..wallet import RustChainWallet
from .models import X402Challenge, X402PaymentProof
from .receipts import CryptographicReceiptManager


class X402ServerManager:
    """
    Manages x402 payment challenges, verification, and replay protection on the server side.
    """

    def __init__(
        self,
        receipt_manager: Optional[CryptographicReceiptManager] = None,
        challenge_ttl_seconds: float = 300.0,
    ):
        self.receipt_manager = receipt_manager or CryptographicReceiptManager()
        self.challenge_ttl_seconds = challenge_ttl_seconds
        self._active_quotes: Dict[str, X402Challenge] = {}
        self._settled_payments: Dict[str, Dict[str, Any]] = {}
        self._used_nonces: set = set()

    def create_challenge(
        self,
        price_rtc: float,
        recipient: str,
        realm: str = "rustchain",
        service_name: str = "Agent Service",
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Generate a 402 challenge response payload and HTTP headers.
        """
        challenge = X402Challenge(
            price_rtc=price_rtc,
            recipient=recipient,
            realm=realm,
            currency="RTC",
            service_name=service_name,
            expires_at=time.time() + self.challenge_ttl_seconds,
        )
        self._active_quotes[challenge.quote_id] = challenge

        headers = {
            "WWW-Authenticate": f'x402 realm="{realm}", price="{price_rtc}", recipient="{recipient}", currency="RTC", quote_id="{challenge.quote_id}"',
            "X-Payment-Required": json.dumps(challenge.to_dict()),
        }

        body = {
            "error": "Payment Required",
            "status_code": 402,
            "challenge": challenge.to_dict(),
            "instructions": "Attach signed X-Payment header or Authorization: x402 <token> to complete request.",
        }
        return body, headers

    def verify_payment(
        self,
        payment_header_str: str,
        expected_price: Optional[float] = None,
        expected_recipient: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Verify incoming X-Payment header against active quote and Ed25519 signature.

        Returns:
            (is_valid: bool, error_message: Optional[str], receipt: Optional[Dict[str, Any]])
        """
        try:
            # Parse header (can be raw JSON or Base64 encoded JSON)
            raw = payment_header_str.strip()
            if raw.startswith("x402 "):
                raw = raw[5:].strip()

            if raw.startswith("{"):
                payload = json.loads(raw)
            else:
                decoded = base64.b64decode(raw).decode("utf-8")
                payload = json.loads(decoded)
        except Exception as e:
            return False, f"Malformed X-Payment header: {e}", None

        payer = payload.get("payer") or payload.get("from")
        recipient = payload.get("recipient") or payload.get("to")
        amount = payload.get("amount") or payload.get("amount_rtc")
        quote_id = payload.get("quote_id", "")
        nonce = payload.get("nonce", "")
        timestamp = payload.get("timestamp")
        signature = payload.get("signature")
        public_key = payload.get("public_key")

        if not all([payer, recipient, amount is not None, timestamp, signature]):
            return False, "Missing required payment fields in header", None

        amount = float(amount)

        # Nonce and Replay Protection
        nonce_key = f"{payer}:{nonce}:{signature[:16]}"
        if nonce_key in self._used_nonces:
            return False, "Replay attack detected: nonce/signature already used", None

        # Check freshness window (must be within 5 minutes)
        now = time.time()
        if abs(now - float(timestamp)) > 300.0:
            return False, "Payment signature expired or clock skew too large (>300s)", None

        # Check against quote if provided
        if quote_id and quote_id in self._active_quotes:
            quote = self._active_quotes[quote_id]
            if now > quote.expires_at:
                return False, f"Quote {quote_id} has expired", None
            if expected_price is None:
                expected_price = quote.price_rtc
            if expected_recipient is None:
                expected_recipient = quote.recipient

        # Validate amount
        if expected_price is not None and amount < expected_price:
            return False, f"Insufficient payment: sent {amount} RTC, requires {expected_price} RTC", None

        # Validate recipient
        if expected_recipient is not None and recipient != expected_recipient:
            return False, f"Payment recipient mismatch: sent to {recipient}, expected {expected_recipient}", None

        # Verify cryptographic Ed25519 signature
        message_to_verify = f"x402:{payer}:{recipient}:{amount}:{quote_id}:{nonce}:{int(timestamp)}".encode()

        if public_key:
            sig_valid = RustChainWallet.verify_signature(public_key, message_to_verify, signature)
        else:
            # Check if signature matches standard wallet transfer signature format
            transfer_msg = f"{payer}:{recipient}:{int(amount * 1_000_000)}:0:{int(timestamp)}".encode()
            sig_valid = RustChainWallet.verify_signature(payer, transfer_msg, signature) or RustChainWallet.verify_signature(payer, message_to_verify, signature)

        if not sig_valid:
            return False, "Invalid cryptographic Ed25519 payment signature", None

        # Mark nonce as spent
        self._used_nonces.add(nonce_key)

        # Generate receipt
        receipt = self.receipt_manager.generate_receipt(
            operation_type="x402_payment",
            sender=payer,
            recipient=recipient,
            amount=amount,
            currency="RTC",
            extra_data={"quote_id": quote_id, "nonce": nonce, "signature": signature},
        )

        self._settled_payments[receipt["receipt_id"]] = {
            "payer": payer,
            "recipient": recipient,
            "amount": amount,
            "timestamp": now,
            "receipt": receipt,
        }

        return True, None, receipt


# Global default server manager for decorator convenience
_default_server_manager = X402ServerManager()


def require_rtc_payment(
    price: float,
    recipient: str,
    realm: str = "rustchain",
    service_name: str = "Agent Service",
    server_manager: Optional[X402ServerManager] = None,
):
    """
    Flask route decorator enforcing x402 payment requirements.
    
    Usage:
        @app.route("/api/inference", methods=["POST"])
        @require_rtc_payment(price=0.001, recipient="RTC_AGENT_B_WALLET")
        def inference():
            return jsonify({"output": "Model response"})
    """
    mgr = server_manager or _default_server_manager

    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                from flask import request, jsonify, make_response, g
            except ImportError:
                # Fallback for non-flask environments
                return f(*args, **kwargs)

            # Check for payment header
            payment_header = request.headers.get("X-Payment") or request.headers.get("Authorization")

            if not payment_header:
                body, headers = mgr.create_challenge(
                    price_rtc=price,
                    recipient=recipient,
                    realm=realm,
                    service_name=service_name,
                )
                resp = make_response(jsonify(body), 402)
                for k, v in headers.items():
                    resp.headers[k] = v
                return resp

            # Verify payment
            is_valid, err_msg, receipt = mgr.verify_payment(
                payment_header,
                expected_price=price,
                expected_recipient=recipient,
            )

            if not is_valid:
                body = {
                    "error": "Payment Verification Failed",
                    "status_code": 402,
                    "reason": err_msg,
                }
                resp = make_response(jsonify(body), 402)
                resp.headers["X-Payment-Error"] = err_msg or "Verification failed"
                return resp

            # Attach receipt to request context
            g.payment_receipt = receipt
            result = f(*args, **kwargs)

            # Inject payment receipt header into successful response
            if hasattr(result, "headers") and receipt:
                result.headers["X-Payment-Receipt"] = receipt["receipt_id"]
            return result

        return wrapper

    return decorator


class AutoPayClient:
    """
    Intelligent Agent-to-Agent HTTP client with automated x402 payment handling.

    When an endpoint returns HTTP 402:
    1. Intercepts and parses the challenge headers (quote_id, price, recipient).
    2. Constructs and signs the Ed25519 payment proof using the agent's wallet.
    3. Encodes proof into `X-Payment` header.
    4. Automatically resubmits the request and returns the resulting 200 OK response.
    """

    def __init__(self, wallet: RustChainWallet, max_auto_spend_rtc: float = 10.0):
        self.wallet = wallet
        self.max_auto_spend_rtc = max_auto_spend_rtc
        self.total_spent_rtc: float = 0.0

    def create_payment_proof(
        self,
        recipient: str,
        amount: float,
        quote_id: str = "",
        nonce: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a cryptographically signed x402 payment proof.
        """
        nonce = nonce or uuid.uuid4().hex
        timestamp = int(time.time())
        message = f"x402:{self.wallet.address}:{recipient}:{amount}:{quote_id}:{nonce}:{timestamp}".encode()
        signature = self.wallet.sign(message).hex()

        return {
            "payer": self.wallet.address,
            "recipient": recipient,
            "amount": amount,
            "quote_id": quote_id,
            "nonce": nonce,
            "timestamp": timestamp,
            "signature": signature,
            "public_key": self.wallet.public_key_hex,
        }

    def execute_with_auto_pay(
        self,
        request_func: Callable[[Dict[str, str]], Any],
        max_price: Optional[float] = None,
    ) -> Any:
        """
        Execute an HTTP request callback, automatically handling 402 payment if challenged.

        Args:
            request_func: A callable that takes headers Dict and returns a response object
                          (supporting status_code, headers, and json()/text).
            max_price: Safety ceiling for auto-payment.
        """
        # Step 1: Initial request without payment headers
        headers: Dict[str, str] = {}
        response = request_func(headers)

        status_code = getattr(response, "status_code", 200)
        if status_code != 402:
            return response

        # Step 2: Parse challenge from 402 response
        resp_headers = getattr(response, "headers", {})
        payment_req_str = resp_headers.get("X-Payment-Required")
        if not payment_req_str and hasattr(response, "json"):
            try:
                body = response.json()
                challenge = body.get("challenge", {})
            except Exception:
                challenge = {}
        else:
            challenge = json.loads(payment_req_str) if payment_req_str else {}

        price = float(challenge.get("price_rtc") or challenge.get("price", 0.001))
        recipient = challenge.get("recipient")
        quote_id = challenge.get("quote_id", "")
        nonce = challenge.get("nonce", uuid.uuid4().hex)

        if not recipient:
            raise ValueError("402 Response did not specify payment recipient")

        # Budget safety checks
        if max_price is not None and price > max_price:
            raise ValueError(f"Required price {price} RTC exceeds maximum allowed {max_price} RTC")
        if self.total_spent_rtc + price > self.max_auto_spend_rtc:
            raise ValueError(f"Spending limit reached: tried to spend {price} RTC with total {self.total_spent_rtc}")

        # Step 3: Create cryptographic payment proof
        proof = self.create_payment_proof(
            recipient=recipient,
            amount=price,
            quote_id=quote_id,
            nonce=nonce,
        )

        # Step 4: Resubmit request with X-Payment header
        headers["X-Payment"] = json.dumps(proof)
        headers["Authorization"] = f"x402 {base64.b64encode(json.dumps(proof).encode()).decode()}"

        final_response = request_func(headers)
        self.total_spent_rtc = round(self.total_spent_rtc + price, 6)
        return final_response

    # Convenience agent helpers
    def pay_for_inference(self, prompt: str, invoke_fn: Callable[[Dict[str, str]], Any], max_price: float = 0.001) -> Any:
        """Call AI inference service with automated micropayment."""
        return self.execute_with_auto_pay(invoke_fn, max_price=max_price)

    def pay_for_review(self, pr_url: str, invoke_fn: Callable[[Dict[str, str]], Any], max_price: float = 0.01) -> Any:
        """Pay reviewer agent for reviewing a pull request."""
        return self.execute_with_auto_pay(invoke_fn, max_price=max_price)

    def pay_for_data_feed(self, query: str, invoke_fn: Callable[[Dict[str, str]], Any], max_price: float = 0.005) -> Any:
        """Query an analytics or scraper agent for real-time data."""
        return self.execute_with_auto_pay(invoke_fn, max_price=max_price)

    def pay_cross_platform_tip(self, target_agent: str, invoke_fn: Callable[[Dict[str, str]], Any], amount: float = 0.1) -> Any:
        """Send cross-platform tip to agent."""
        return self.execute_with_auto_pay(invoke_fn, max_price=amount)
