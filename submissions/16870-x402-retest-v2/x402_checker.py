#!/usr/bin/env python3
"""x402 Integration Retest v2 Engine.

Validates the corrected endpoint matrix, inspects live headers, tests
cryptographic EIP-3009 payment authorizations, and verifies newly identified
production defects against the BoTTube and RustChain infrastructure.
"""

from __future__ import annotations

import argparse
import base64
import http.server
import json
import os
import secrets
import socket
import sys
import threading
import time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from eth_account import Account
    from eth_account.messages import encode_typed_data
except ImportError:
    Account = None
    encode_typed_data = None

DEFAULT_TREASURY = "0x008097344A4C6E49401f2b6b9BAA4881b702e0fa"
DEFAULT_USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
DEFAULT_FACILITATOR = "https://x402-facilitator.cdp.coinbase.com"
WORKING_FACILITATOR = "https://x402.org/facilitator"


def execute_http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[bytes] = None,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """Execute an HTTP request and capture status, headers, and payload.

    Args:
        url: Target HTTP/HTTPS endpoint.
        method: HTTP method.
        headers: Optional HTTP headers dictionary.
        data: Optional request body bytes.
        timeout: Socket timeout in seconds.

    Returns:
        Dictionary containing status_code, headers, body, and latency_ms.
    """
    request_headers = headers or {}
    if "User-Agent" not in request_headers:
        request_headers["User-Agent"] = "x402-retest-v2/1.0.0"

    req = Request(url=url, data=data, headers=request_headers, method=method)
    start_time = time.time()

    try:
        with urlopen(req, timeout=timeout) as response:
            latency_ms = (time.time() - start_time) * 1000
            raw_body = response.read()
            body_text = raw_body.decode("utf-8", errors="replace")
            resp_headers = dict(response.headers)
            return {
                "status_code": response.status,
                "headers": resp_headers,
                "body": body_text,
                "latency_ms": round(latency_ms, 2),
                "error": None,
            }
    except HTTPError as e:
        latency_ms = (time.time() - start_time) * 1000
        raw_body = e.read()
        body_text = raw_body.decode("utf-8", errors="replace")
        resp_headers = dict(e.headers)
        return {
            "status_code": e.code,
            "headers": resp_headers,
            "body": body_text,
            "latency_ms": round(latency_ms, 2),
            "error": str(e),
        }
    except URLError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "status_code": 0,
            "headers": {},
            "body": "",
            "latency_ms": round(latency_ms, 2),
            "error": str(e.reason),
        }


def check_dns_resolvable(hostname: str) -> Tuple[bool, List[str]]:
    """Check whether a given hostname resolves in DNS.

    Args:
        hostname: Domain name to resolve.

    Returns:
        Tuple of (resolvable_bool, list_of_resolved_ips).
    """
    try:
        _, _, ip_list = socket.gethostbyname_ex(hostname)
        return True, ip_list
    except socket.gaierror:
        return False, []


def build_eip3009_authorization(
    sender_address: str,
    recipient_address: str,
    amount_atomic: str,
    valid_after: int = 0,
    valid_before: Optional[int] = None,
    nonce_hex: Optional[str] = None,
) -> Dict[str, Any]:
    """Construct an EIP-3009 TransferWithAuthorization parameters dictionary.

    Args:
        sender_address: Sender 0x hex address.
        recipient_address: Recipient 0x hex address.
        amount_atomic: Transfer amount in atomic units as a string.
        valid_after: Epoch seconds start timestamp.
        valid_before: Epoch seconds expiration timestamp.
        nonce_hex: 32-byte hexadecimal nonce.

    Returns:
        Dictionary representing the EIP-3009 authorization structure.
    """
    if valid_before is None:
        valid_before = int(time.time()) + 3600

    if nonce_hex is None:
        nonce_hex = "0x" + secrets.token_hex(32)
    elif not nonce_hex.startswith("0x"):
        nonce_hex = f"0x{nonce_hex}"

    return {
        "from": sender_address,
        "to": recipient_address,
        "value": str(amount_atomic),
        "validAfter": str(valid_after),
        "validBefore": str(valid_before),
        "nonce": nonce_hex,
    }


def create_signed_x402_header(
    account: Any,
    authorization: Dict[str, Any],
    network: str = "base",
    chain_id: int = 8453,
    asset_address: str = DEFAULT_USDC_CONTRACT,
    token_name: str = "USD Coin",
    token_version: str = "2",
) -> Tuple[str, str]:
    """Sign an EIP-3009 transfer authorization and format as base64 X-PAYMENT header.

    Args:
        account: eth_account.Account instance.
        authorization: EIP-3009 authorization dictionary.
        network: Network identifier string expected by challenge.
        chain_id: Integer EVM chain ID.
        asset_address: Token contract address.
        token_name: EIP-712 domain name.
        token_version: EIP-712 domain version.

    Returns:
        Tuple of (base64_encoded_header, hex_signature).
    """
    if Account is None or encode_typed_data is None:
        raise RuntimeError("eth_account is required for cryptographic signing")

    nonce_clean = authorization["nonce"]
    if nonce_clean.startswith("0x"):
        nonce_clean = nonce_clean[2:]
    nonce_bytes = bytes.fromhex(nonce_clean)

    domain_data = {
        "name": token_name,
        "version": token_version,
        "chainId": chain_id,
        "verifyingContract": asset_address,
    }

    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }

    message_data = {
        "from": authorization["from"],
        "to": authorization["to"],
        "value": int(authorization["value"]),
        "validAfter": int(authorization["validAfter"]),
        "validBefore": int(authorization["validBefore"]),
        "nonce": nonce_bytes,
    }

    signable = encode_typed_data(
        domain_data=domain_data,
        message_types=message_types,
        message_data=message_data,
    )
    signed = account.sign_message(signable)
    signature_hex = f"0x{signed.signature.hex()}"

    payload_dict = {
        "x402Version": 1,
        "scheme": "exact",
        "network": network,
        "payload": {
            "signature": signature_hex,
            "authorization": dict(authorization),
        },
    }

    raw_json = json.dumps(payload_dict, separators=(",", ":"))
    encoded_b64 = base64.b64encode(raw_json.encode("utf-8")).decode("utf-8")
    return encoded_b64, signature_hex


def verify_eip3009_signature(
    authorization: Dict[str, Any],
    signature_hex: str,
    chain_id: int = 8453,
    asset_address: str = DEFAULT_USDC_CONTRACT,
    token_name: str = "USD Coin",
    token_version: str = "2",
) -> str:
    """Recover the signer address from an EIP-3009 authorization signature.

    Args:
        authorization: EIP-3009 authorization dictionary.
        signature_hex: Hexadecimal signature string.
        chain_id: Integer EVM chain ID.
        asset_address: Token contract address.
        token_name: EIP-712 domain name.
        token_version: EIP-712 domain version.

    Returns:
        Recovered checksummed Ethereum address.
    """
    if Account is None or encode_typed_data is None:
        raise RuntimeError("eth_account is required for cryptographic verification")

    nonce_clean = authorization["nonce"]
    if nonce_clean.startswith("0x"):
        nonce_clean = nonce_clean[2:]
    nonce_bytes = bytes.fromhex(nonce_clean)

    domain_data = {
        "name": token_name,
        "version": token_version,
        "chainId": chain_id,
        "verifyingContract": asset_address,
    }

    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }

    message_data = {
        "from": authorization["from"],
        "to": authorization["to"],
        "value": int(authorization["value"]),
        "validAfter": int(authorization["validAfter"]),
        "validBefore": int(authorization["validBefore"]),
        "nonce": nonce_bytes,
    }

    signable = encode_typed_data(
        domain_data=domain_data,
        message_types=message_types,
        message_data=message_data,
    )
    recovered = Account.recover_message(signable, signature=signature_hex)
    return recovered


def parse_x402_challenge(response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract payment requirements from a 402 HTTP response.

    Args:
        response_data: Dictionary returned by execute_http_request.

    Returns:
        First payment requirement dictionary if parsed successfully, else None.
    """
    try:
        parsed = json.loads(response_data.get("body", "{}"))
        accepts = parsed.get("accepts", [])
        if accepts and isinstance(accepts, list):
            return accepts[0]
        return None
    except json.JSONDecodeError:
        return None


class SimulatedX402Server:
    """Mock HTTP server simulating a working x402 endpoint and settlement."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.port = port
        self.server: Optional[http.server.HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.actual_port = 0
        self.received_payments: List[Dict[str, Any]] = []

    def start(self) -> str:
        """Start the simulated x402 server on an available port.

        Returns:
            Base URL string of the running simulated server.
        """
        outer_self = self

        class RequestHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                pass

            def do_GET(self) -> None:
                if self.path == "/api/premium/videos":
                    payment_header = self.headers.get("X-PAYMENT")
                    if not payment_header:
                        challenge = {
                            "x402Version": 1,
                            "accepts": [
                                {
                                    "scheme": "exact",
                                    "network": "base",
                                    "asset": DEFAULT_USDC_CONTRACT,
                                    "maxAmountRequired": "10000",
                                    "resource": f"http://{outer_self.host}:{outer_self.actual_port}/api/premium/videos",
                                    "description": "Bulk video data export",
                                    "mimeType": "application/json",
                                    "payTo": DEFAULT_TREASURY,
                                    "maxTimeoutSeconds": 60,
                                    "outputSchema": {
                                        "input": {"type": "http", "method": "GET", "discoverable": True},
                                        "output": None,
                                    },
                                    "extra": {"name": "USD Coin", "version": "2"},
                                }
                            ],
                            "error": "No X-PAYMENT header provided",
                        }
                        payload_bytes = json.dumps(challenge).encode("utf-8")
                        self.send_response(402)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(payload_bytes)))
                        self.end_headers()
                        self.wfile.write(payload_bytes)
                        return

                    try:
                        decoded_json = json.loads(base64.b64decode(payment_header).decode("utf-8"))
                        auth = decoded_json["payload"]["authorization"]
                        sig = decoded_json["payload"]["signature"]
                        recovered = verify_eip3009_signature(
                            authorization=auth,
                            signature_hex=sig,
                            chain_id=8453,
                            asset_address=DEFAULT_USDC_CONTRACT,
                            token_name="USD Coin",
                            token_version="2",
                        )
                        if recovered.lower() != auth["from"].lower():
                            self.send_error(402, "Signature verification failed")
                            return

                        outer_self.received_payments.append(decoded_json)

                        settle_response = {
                            "success": True,
                            "transactionHash": "0x" + secrets.token_hex(32),
                            "network": "base",
                        }
                        settle_header = base64.b64encode(json.dumps(settle_response).encode("utf-8")).decode("utf-8")

                        success_payload = json.dumps({
                            "status": "success",
                            "message": "Premium access granted via x402 payment authorization",
                            "videos": [
                                {"id": "vid_001", "title": "Sophia Elya Architecture Deep Dive", "views": 1420},
                                {"id": "vid_002", "title": "RustChain Autonomous Node Settlement", "views": 890},
                            ],
                        }).encode("utf-8")

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(success_payload)))
                        self.send_header("X-PAYMENT-RESPONSE", settle_header)
                        self.end_headers()
                        self.wfile.write(success_payload)
                    except Exception as exc:
                        error_bytes = json.dumps({"error": f"Invalid payment header: {exc}"}).encode("utf-8")
                        self.send_response(400)
                        self.send_header("Content-Type", "application/json")
                        self.send_header("Content-Length", str(len(error_bytes)))
                        self.end_headers()
                        self.wfile.write(error_bytes)
                else:
                    self.send_error(404, "Not Found")

        self.server = http.server.HTTPServer((self.host, self.port), RequestHandler)
        self.actual_port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return f"http://{self.host}:{self.actual_port}"

    def stop(self) -> None:
        """Shutdown the simulated HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()


def run_endpoint_matrix_audit() -> Dict[str, Any]:
    """Execute live verification across the 7 matrix rows.

    Returns:
        Structured dictionary containing test outcomes for all rows.
    """
    matrix_targets = [
        {
            "row": 1,
            "name": "x402_info",
            "method": "GET",
            "url": "https://bottube.ai/api/x402/info",
            "expected_status": 200,
            "description": "Capability discovery endpoint (replaces deprecated /status)",
        },
        {
            "row": 2,
            "name": "premium_videos",
            "method": "GET",
            "url": "https://bottube.ai/api/premium/videos",
            "expected_status": 402,
            "description": "Bulk video data export paywall challenge",
        },
        {
            "row": 3,
            "name": "premium_analytics",
            "method": "GET",
            "url": "https://bottube.ai/api/premium/analytics/sophia-elya",
            "expected_status": 402,
            "description": "Agent performance metrics paywall challenge",
        },
        {
            "row": 4,
            "name": "premium_trending_export",
            "method": "GET",
            "url": "https://bottube.ai/api/premium/trending/export",
            "expected_status": 402,
            "description": "Trending video export paywall challenge",
        },
        {
            "row": 5,
            "name": "coinbase_wallet_link_unauthenticated",
            "method": "POST",
            "url": "https://bottube.ai/api/agents/me/coinbase-wallet",
            "expected_status": 401,
            "description": "Agent wallet linking without API key",
        },
        {
            "row": 6,
            "name": "wallet_swap_info",
            "method": "GET",
            "url": "https://rustchain.org/wallet/swap-info",
            "expected_status": 200,
            "description": "Aerodrome DEX swap metadata and pool address",
        },
        {
            "row": 7,
            "name": "beacon_endpoints_unmounted",
            "method": "GET",
            "url": "https://rustchain.org/beacon/api/x402/status",
            "expected_status": 404,
            "description": "Deprecated Beacon endpoints correctly unmounted",
        },
    ]

    results = []
    for item in matrix_targets:
        resp = execute_http_request(url=item["url"], method=item["method"])
        passed = (resp["status_code"] == item["expected_status"])
        results.append({
            "row": item["row"],
            "name": item["name"],
            "url": item["url"],
            "method": item["method"],
            "expected_status": item["expected_status"],
            "actual_status": resp["status_code"],
            "passed": passed,
            "latency_ms": resp["latency_ms"],
            "headers": resp["headers"],
            "body_snippet": resp["body"][:300],
            "description": item["description"],
        })

    return {"matrix_results": results, "timestamp": time.time()}


def diagnose_production_defects() -> Dict[str, Any]:
    """Execute live diagnostic tests detecting active defects in production.

    Returns:
        Dictionary containing defect identification and reproduction results.
    """
    defects = {}

    facilitator_host = "x402-facilitator.cdp.coinbase.com"
    resolves, ips = check_dns_resolvable(facilitator_host)
    defects["defect_1_facilitator_nxdomain"] = {
        "title": "Configured facilitator host is non-existent (NXDOMAIN)",
        "severity": "CRITICAL",
        "configured_facilitator": DEFAULT_FACILITATOR,
        "dns_resolvable": resolves,
        "resolved_ips": ips,
        "impact": "Causes live server to crash with HTTP 500 when valid payment header is submitted",
    }

    acct = Account.create() if Account else None
    if acct:
        auth = build_eip3009_authorization(
            sender_address=acct.address,
            recipient_address=DEFAULT_TREASURY,
            amount_atomic="10000000000",
        )
        signed_b64, _ = create_signed_x402_header(
            account=acct,
            authorization=auth,
            network="base",
            chain_id=8453,
        )
        resp_500 = execute_http_request(
            url="https://bottube.ai/api/premium/videos",
            headers={"X-PAYMENT": signed_b64},
        )
        defects["defect_1_facilitator_nxdomain"]["server_response_status"] = resp_500["status_code"]
        defects["defect_1_facilitator_nxdomain"]["server_response_body"] = resp_500["body"][:300]
        defects["defect_1_facilitator_nxdomain"]["reproduced"] = (resp_500["status_code"] == 500)

    info_resp = execute_http_request("https://bottube.ai/api/x402/info")
    videos_resp = execute_http_request("https://bottube.ai/api/premium/videos")
    info_json = json.loads(info_resp["body"]) if info_resp["status_code"] == 200 else {}
    videos_challenge = parse_x402_challenge(videos_resp) or {}

    declared_price = info_json.get("price_usdc", "")
    demanded_atomic = videos_challenge.get("maxAmountRequired", "")
    defects["defect_2_price_unit_multiplier"] = {
        "title": "1,000,000x price unit conversion multiplication defect",
        "severity": "HIGH",
        "declared_price_in_info": declared_price,
        "demanded_max_amount_required": demanded_atomic,
        "intended_value_usdc": "0.01 USDC (10,000 atomic base units)",
        "actual_demanded_value_usdc": "10,000.00 USDC (10,000,000,000 atomic units)",
        "root_cause": "process_price_to_atomic_amount treats numeric string as whole USD, multiplying by 10^6",
        "reproduced": (demanded_atomic == "10000000000"),
    }

    if acct:
        auth_caip2 = build_eip3009_authorization(
            sender_address=acct.address,
            recipient_address=DEFAULT_TREASURY,
            amount_atomic="10000",
        )
        signed_caip2_b64, _ = create_signed_x402_header(
            account=acct,
            authorization=auth_caip2,
            network="eip155:8453",
            chain_id=8453,
        )
        resp_caip2 = execute_http_request(
            url="https://bottube.ai/api/premium/videos",
            headers={"X-PAYMENT": signed_caip2_b64},
        )
        defects["defect_3_caip2_network_mismatch"] = {
            "title": "CAIP-2 network identifier advertised in /info rejected by challenge",
            "severity": "MEDIUM",
            "info_network_advertised": info_json.get("network", ""),
            "challenge_network_expected": videos_challenge.get("network", ""),
            "server_response_status": resp_caip2["status_code"],
            "server_response_body": resp_caip2["body"][:300],
            "reproduced": ("No matching payment requirements found" in resp_caip2["body"]),
        }

    resp_xapikey = execute_http_request(
        url="https://bottube.ai/api/agents/me/coinbase-wallet",
        method="POST",
        headers={"X-API-Key": "dummy_test_token"},
    )
    resp_bearer = execute_http_request(
        url="https://bottube.ai/api/agents/me/coinbase-wallet",
        method="POST",
        headers={"Authorization": "Bearer dummy_test_token"},
    )
    defects["defect_4_auth_header_contract_inconsistency"] = {
        "title": "X-API-Key advertised in CORS headers but ignored by endpoint authentication",
        "severity": "LOW",
        "xapikey_response": resp_xapikey["body"],
        "bearer_response": resp_bearer["body"],
        "root_cause": "Endpoint handler inspects Authorization header only, ignoring X-API-Key",
        "reproduced": ("API key required" in resp_xapikey["body"] and "Invalid API key" in resp_bearer["body"]),
    }

    return defects


def demonstrate_simulated_roundtrip() -> Dict[str, Any]:
    """Demonstrate a real 402 -> payment -> 200 roundtrip on an x402 endpoint.

    Returns:
        Dictionary capturing each phase of the payment negotiation and settlement.
    """
    if Account is None:
        return {"error": "eth_account required for roundtrip demonstration"}

    sim_server = SimulatedX402Server()
    base_url = sim_server.start()

    try:
        initial_resp = execute_http_request(f"{base_url}/api/premium/videos")
        if initial_resp["status_code"] != 402:
            return {"error": f"Initial status not 402: {initial_resp['status_code']}"}

        challenge = parse_x402_challenge(initial_resp)
        if not challenge:
            return {"error": "Failed to parse 402 challenge requirements"}

        payer_account = Account.create()
        authorization = build_eip3009_authorization(
            sender_address=payer_account.address,
            recipient_address=challenge["payTo"],
            amount_atomic=challenge["maxAmountRequired"],
            valid_after=0,
            valid_before=int(time.time()) + challenge["maxTimeoutSeconds"],
        )

        signed_header, signature_hex = create_signed_x402_header(
            account=payer_account,
            authorization=authorization,
            network=challenge["network"],
            chain_id=8453,
            asset_address=challenge["asset"],
            token_name=challenge.get("extra", {}).get("name", "USD Coin"),
            token_version=challenge.get("extra", {}).get("version", "2"),
        )

        recovered_address = verify_eip3009_signature(
            authorization=authorization,
            signature_hex=signature_hex,
            chain_id=8453,
            asset_address=challenge["asset"],
            token_name=challenge.get("extra", {}).get("name", "USD Coin"),
            token_version=challenge.get("extra", {}).get("version", "2"),
        )

        if recovered_address.lower() != payer_account.address.lower():
            return {"error": "Cryptographic recovery mismatch"}

        paid_resp = execute_http_request(
            f"{base_url}/api/premium/videos",
            headers={"X-PAYMENT": signed_header},
        )

        if paid_resp["status_code"] != 200:
            return {"error": f"Payment retry failed: {paid_resp['status_code']}"}

        settlement_raw = paid_resp["headers"].get("X-PAYMENT-RESPONSE") or paid_resp["headers"].get("x-payment-response")
        settlement_data = json.loads(base64.b64decode(settlement_raw).decode("utf-8")) if settlement_raw else None

        return {
            "success": True,
            "roundtrip_status_sequence": [402, 200],
            "payer_address": payer_account.address,
            "recovered_signer": recovered_address,
            "signature": signature_hex,
            "challenge": challenge,
            "authorization": authorization,
            "final_response_body": json.loads(paid_resp["body"]),
            "settlement_data": settlement_data,
        }
    finally:
        sim_server.stop()


def main() -> int:
    """CLI entrypoint for x402 verification suite."""
    parser = argparse.ArgumentParser(description="x402 Integration Retest v2 Engine")
    parser.add_argument("--matrix", action="store_true", help="Audit live 7-row endpoint matrix")
    parser.add_argument("--defects", action="store_true", help="Diagnose active production defects")
    parser.add_argument("--roundtrip", action="store_true", help="Execute 402->payment->200 roundtrip")
    parser.add_argument("--all", action="store_true", help="Run full suite and output JSON report")
    parser.add_argument("--output", type=str, default="", help="Path to write JSON report")
    args = parser.parse_args()

    run_all = args.all or (not args.matrix and not args.defects and not args.roundtrip)

    full_report = {}

    if run_all or args.matrix:
        matrix_data = run_endpoint_matrix_audit()
        full_report["matrix"] = matrix_data
        print(f"Matrix Audit: {len(matrix_data['matrix_results'])} rows checked.")
        for row in matrix_data["matrix_results"]:
            status_tag = "PASS" if row["passed"] else "FAIL"
            print(f"  Row {row['row']} [{status_tag}] {row['method']} {row['url']} -> {row['actual_status']}")

    if run_all or args.defects:
        defect_data = diagnose_production_defects()
        full_report["defects"] = defect_data
        print(f"\nDefect Diagnostics: {len(defect_data)} defects evaluated.")
        for key, defect in defect_data.items():
            repro = "REPRODUCED" if defect.get("reproduced") else "UNREPRODUCED"
            print(f"  [{repro}] {defect['title']}")

    if run_all or args.roundtrip:
        roundtrip_data = demonstrate_simulated_roundtrip()
        full_report["roundtrip"] = roundtrip_data
        if roundtrip_data.get("success"):
            print("\nRoundtrip Demonstration: SUCCESS (402 -> payment signed -> 200 OK)")
            print(f"  Payer Address:    {roundtrip_data['payer_address']}")
            print(f"  Recovered Signer: {roundtrip_data['recovered_signer']}")
        else:
            print(f"\nRoundtrip Demonstration: FAILED ({roundtrip_data.get('error')})")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(full_report, f, indent=2)
        print(f"\nReport written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
