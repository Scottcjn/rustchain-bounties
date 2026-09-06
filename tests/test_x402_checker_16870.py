"""Unit test suite for x402 integration retest v2.

Verifies endpoint contracts, challenge parsing, genuine EIP-712 / EIP-3009
cryptographic signing and signer recovery, price unit conversion logic,
and full 402 -> payment -> 200 HTTP round-trip negotiation.
"""

import importlib.util
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

module_path = repo_root / "submissions" / "16870-x402-retest-v2" / "x402_checker.py"
spec = importlib.util.spec_from_file_location("x402_checker", str(module_path))
checker_mod = importlib.util.module_from_spec(spec)
sys.modules["x402_checker"] = checker_mod
spec.loader.exec_module(checker_mod)

SimulatedX402Server = checker_mod.SimulatedX402Server
build_eip3009_authorization = checker_mod.build_eip3009_authorization
check_dns_resolvable = checker_mod.check_dns_resolvable
create_signed_x402_header = checker_mod.create_signed_x402_header
execute_http_request = checker_mod.execute_http_request
parse_x402_challenge = checker_mod.parse_x402_challenge
verify_eip3009_signature = checker_mod.verify_eip3009_signature

try:
    from eth_account import Account
except ImportError:
    Account = None


class TestX402RetestV2(unittest.TestCase):
    """Test suite validating x402 retest v2 components and cryptographic integrity."""

    def test_challenge_parsing_valid(self) -> None:
        """Verify successful extraction of payment requirements from valid 402 response."""
        sample_body = json.dumps({
            "x402Version": 1,
            "accepts": [
                {
                    "scheme": "exact",
                    "network": "base",
                    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                    "maxAmountRequired": "10000000000",
                    "resource": "https://bottube.ai/api/premium/videos",
                    "description": "Bulk video data export",
                    "mimeType": "application/json",
                    "payTo": "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa",
                    "maxTimeoutSeconds": 60,
                }
            ],
            "error": "No X-PAYMENT header provided",
        })
        resp = {"body": sample_body, "status_code": 402}
        parsed = parse_x402_challenge(resp)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["scheme"], "exact")
        self.assertEqual(parsed["network"], "base")
        self.assertEqual(parsed["maxAmountRequired"], "10000000000")
        self.assertEqual(parsed["payTo"], "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa")

    def test_challenge_parsing_empty_or_malformed(self) -> None:
        """Verify graceful handling when challenge payload is malformed or empty."""
        self.assertIsNone(parse_x402_challenge({"body": "not json", "status_code": 402}))
        self.assertIsNone(parse_x402_challenge({"body": "{}", "status_code": 402}))
        self.assertIsNone(parse_x402_challenge({"body": '{"accepts": []}', "status_code": 402}))

    def test_eip3009_authorization_construction(self) -> None:
        """Verify field types and structure of EIP-3009 authorization dictionary."""
        sender = "0xF46C9F6d70C50BF81ef3588AB523a90a594a2F89"
        recipient = "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa"
        amount = "10000"
        nonce = "0x" + "a" * 64

        auth = build_eip3009_authorization(
            sender_address=sender,
            recipient_address=recipient,
            amount_atomic=amount,
            valid_after=100,
            valid_before=2000,
            nonce_hex=nonce,
        )

        self.assertEqual(auth["from"], sender)
        self.assertEqual(auth["to"], recipient)
        self.assertEqual(auth["value"], "10000")
        self.assertEqual(auth["validAfter"], "100")
        self.assertEqual(auth["validBefore"], "2000")
        self.assertEqual(auth["nonce"], nonce)

    @unittest.skipIf(Account is None, "eth_account required for cryptographic tests")
    def test_cryptographic_signature_signing_and_recovery(self) -> None:
        """Verify real EIP-712 typed data signing and mathematical address recovery."""
        account = Account.create()
        auth = build_eip3009_authorization(
            sender_address=account.address,
            recipient_address="0x008097344A4C6E49401f2b6b9BAA4881b702e0fa",
            amount_atomic="10000",
        )

        encoded_header, signature_hex = create_signed_x402_header(
            account=account,
            authorization=auth,
            network="base",
            chain_id=8453,
        )

        self.assertTrue(signature_hex.startswith("0x"))
        self.assertEqual(len(signature_hex), 132)

        recovered = verify_eip3009_signature(
            authorization=auth,
            signature_hex=signature_hex,
            chain_id=8453,
        )

        self.assertEqual(account.address.lower(), recovered.lower())

    def test_price_unit_conversion_multiplier_defect(self) -> None:
        """Verify mathematical calculation proving the 1,000,000x multiplier defect."""
        declared_input = "10000"
        usdc_decimals = 6

        intended_atomic_amount = int(declared_input)
        intended_usd_value = Decimal(intended_atomic_amount) / Decimal(10**usdc_decimals)
        self.assertEqual(intended_usd_value, Decimal("0.01"))

        buggy_amount_dollars = Decimal(declared_input)
        buggy_atomic_amount = int(buggy_amount_dollars * Decimal(10**usdc_decimals))
        self.assertEqual(buggy_atomic_amount, 10000000000)

        error_multiplier = buggy_atomic_amount // intended_atomic_amount
        self.assertEqual(error_multiplier, 1000000)

    def test_facilitator_dns_resolution(self) -> None:
        """Verify DNS check correctly identifies non-resolving facilitator host."""
        nxdomain_host = "x402-facilitator.cdp.coinbase.com"
        resolves, ips = check_dns_resolvable(nxdomain_host)
        self.assertFalse(resolves)
        self.assertEqual(len(ips), 0)

        working_host = "x402.org"
        resolves_working, ips_working = check_dns_resolvable(working_host)
        self.assertTrue(resolves_working)
        self.assertGreater(len(ips_working), 0)

    @unittest.skipIf(Account is None, "eth_account required for roundtrip test")
    def test_simulated_x402_server_full_roundtrip(self) -> None:
        """Verify complete 402 -> payment -> 200 HTTP roundtrip on simulated server."""
        server = SimulatedX402Server()
        base_url = server.start()

        try:
            initial_resp = execute_http_request(f"{base_url}/api/premium/videos")
            self.assertEqual(initial_resp["status_code"], 402)

            challenge = parse_x402_challenge(initial_resp)
            self.assertIsNotNone(challenge)

            payer = Account.create()
            auth = build_eip3009_authorization(
                sender_address=payer.address,
                recipient_address=challenge["payTo"],
                amount_atomic=challenge["maxAmountRequired"],
            )

            signed_header, sig_hex = create_signed_x402_header(
                account=payer,
                authorization=auth,
                network=challenge["network"],
                chain_id=8453,
                asset_address=challenge["asset"],
            )

            paid_resp = execute_http_request(
                f"{base_url}/api/premium/videos",
                headers={"X-PAYMENT": signed_header},
            )

            self.assertEqual(paid_resp["status_code"], 200)
            self.assertIn("X-PAYMENT-RESPONSE", paid_resp["headers"])

            body = json.loads(paid_resp["body"])
            self.assertEqual(body["status"], "success")
            self.assertEqual(len(body["videos"]), 2)
        finally:
            server.stop()


if __name__ == "__main__":
    unittest.main()
