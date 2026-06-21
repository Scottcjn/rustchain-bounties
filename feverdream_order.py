#!/usr/bin/env python3
"""
feverdream-order: Commission RTC-paid videos from CLI

USAGE:
  feverdream-order --prompt "..." --seconds 6 --wallet mykey.json [--endpoint https://...]

EXAMPLE:
  feverdream-order --prompt "chrome whale over neon canyon" --seconds 6 --wallet ~/.rtc/keys.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import requests
from datetime import datetime

# Try to import rustchain_crypto, fallback to mock
try:
    from rustchain_crypto import sign_ed25519
except ImportError:
    def sign_ed25519(payload: str, private_key: str, domain: str) -> str:
        """Mock Ed25519 signature for testing"""
        import hashlib
        msg = f"{domain}:{payload}".encode()
        return hashlib.sha256(msg).hexdigest()


class FeverdreamError(Exception):
    """Base exception for Feverdream operations"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class WalletError(FeverdreamError):
    """Wallet-related errors"""
    pass


class QuoteError(FeverdreamError):
    """API quote request errors"""
    pass


class SignatureError(FeverdreamError):
    """Signature generation errors"""
    pass


class OrderError(FeverdreamError):
    """Order submission errors"""
    pass


class FeverdreamOrderHandler:
    """Handle video commissioning via Feverdream API"""

    def __init__(self, endpoint: str = "https://bottube.ai"):
        self.endpoint = endpoint.rstrip("/")
        self.session = requests.Session()
        self.timeout = 300  # 5 min total timeout
        self.poll_interval = 2  # seconds between polls
        self.max_retries = 3

    def commission_video(
        self,
        prompt: str,
        seconds: int,
        wallet: Dict[str, Any],
        dry_run: bool = False
    ) -> str:
        """End-to-end video commissioning workflow"""

        # Step 1: Get quote
        quote = self._get_quote(prompt, seconds)
        print(f"📹 Quote: {quote['cost_rtc']} RTC (animation_id: {quote['animation_id']})",
              file=sys.stderr)

        if dry_run:
            print(f"DRY RUN: Would charge {quote['cost_rtc']} RTC", file=sys.stderr)
            return ""

        # Step 2-4: Build & sign transfer
        payload = self._build_payload(wallet, quote)
        signature = self._sign_payload(wallet, payload)

        # Step 5: Post order
        order = self._post_order(payload, signature, quote['animation_id'])
        print(f"⏳ Order ID: {order['order_id']}", file=sys.stderr)

        # Step 6: Poll status
        video_id = self._wait_for_ready(order['order_id'])

        # Step 7: Return URL
        watch_url = f"{self.endpoint}/watch/{video_id}"
        print(f"✅ Ready! {watch_url}", file=sys.stderr)
        return watch_url

    def _get_quote(self, prompt: str, seconds: int) -> Dict[str, Any]:
        """GET /api/feverdream/info - Get pricing quote"""
        try:
            resp = self.session.get(
                f"{self.endpoint}/api/feverdream/info",
                params={"prompt": prompt, "seconds": seconds},
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise QuoteError(f"Failed to get quote: {str(e)}")

    def _build_payload(self, wallet: Dict[str, Any], quote: Dict[str, Any]) -> Dict[str, Any]:
        """Build transfer payload for signing"""
        return {
            "from": wallet.get("address", ""),
            "to": "feverdream_studio",
            "amount": quote["cost_rtc"],
            "nonce": int(time.time() * 1000),
            "domain": "bottube.feverdream.v1"
        }

    def _sign_payload(self, wallet: Dict[str, Any], payload: Dict[str, Any]) -> str:
        """Sign payload with Ed25519"""
        try:
            payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            signature = sign_ed25519(
                payload=payload_json,
                private_key=wallet.get("private_key", ""),
                domain="bottube.feverdream.v1"
            )
            return signature
        except Exception as e:
            raise SignatureError(f"Failed to sign payload: {str(e)}")

    def _post_order(
        self,
        payload: Dict[str, Any],
        signature: str,
        animation_id: str
    ) -> Dict[str, Any]:
        """POST /api/feverdream/order - Submit order"""
        try:
            resp = self.session.post(
                f"{self.endpoint}/api/feverdream/order",
                json={
                    "payload": payload,
                    "signature": signature,
                    "animation_id": animation_id
                },
                timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise OrderError(f"Failed to submit order: {str(e)}")

    def _wait_for_ready(self, order_id: str, verbose: bool = True) -> str:
        """Poll /api/feverdream/status until ready"""
        start = time.time()
        attempts = 0

        while time.time() - start < self.timeout:
            attempts += 1
            try:
                resp = self.session.get(
                    f"{self.endpoint}/api/feverdream/status",
                    params={"order_id": order_id},
                    timeout=10
                )
                resp.raise_for_status()
                status = resp.json()

                if verbose:
                    elapsed = int(time.time() - start)
                    print(f"  Attempt {attempts} ({elapsed}s): {status.get('status', 'unknown')}",
                          file=sys.stderr)

                if status.get("status") == "ready":
                    return status.get("video_id", "")
                elif status.get("status") == "error":
                    raise OrderError(status.get("error", "Unknown error"))

                time.sleep(self.poll_interval)

            except requests.RequestException as e:
                if attempts >= self.max_retries:
                    raise OrderError(f"Failed to check status after {attempts} attempts: {str(e)}")
                time.sleep(self.poll_interval)

        raise OrderError(f"Timeout waiting for video after {int(self.timeout)}s (order_id={order_id})")


def load_wallet(wallet_path: str) -> Dict[str, Any]:
    """Load Ed25519 wallet from JSON file"""
    path = Path(wallet_path).expanduser()

    if not path.exists():
        raise WalletError(f"Wallet not found: {path}")

    try:
        with open(path) as f:
            wallet = json.load(f)
    except json.JSONDecodeError:
        raise WalletError(f"Invalid JSON in wallet: {path}")

    # Validate required fields
    required = ["address", "private_key"]
    for field in required:
        if field not in wallet:
            raise WalletError(f"Missing field in wallet: {field}")

    return wallet


def main():
    parser = argparse.ArgumentParser(
        description="Commission RTC-paid videos via Feverdream",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--prompt", required=True, help="Video description/prompt")
    parser.add_argument("--seconds", type=int, default=6, help="Video duration (default: 6)")
    parser.add_argument("--wallet", required=True, help="Path to Ed25519 wallet JSON")
    parser.add_argument("--endpoint", default="https://bottube.ai", help="API endpoint")
    parser.add_argument("--dry-run", action="store_true", help="Show quote without ordering")

    args = parser.parse_args()

    # Validate inputs
    if not args.prompt.strip():
        print("ERROR: prompt cannot be empty", file=sys.stderr)
        sys.exit(1)

    if args.seconds < 1 or args.seconds > 300:
        print("ERROR: seconds must be 1-300", file=sys.stderr)
        sys.exit(1)

    try:
        # Load wallet
        wallet = load_wallet(args.wallet)

        # Commission video
        handler = FeverdreamOrderHandler(args.endpoint)
        watch_url = handler.commission_video(
            prompt=args.prompt,
            seconds=args.seconds,
            wallet=wallet,
            dry_run=args.dry_run
        )

        # Output
        print(watch_url)
        return 0

    except FeverdreamError as e:
        print(f"ERROR: {e.message}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
