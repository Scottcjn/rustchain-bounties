#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Mobile-friendly wallet API proxy for RustChain.

Wraps the RustChain node API and provides CORS-enabled, mobile-ready
endpoints for balance queries, transaction history, and network health.

The upstream node uses a self-signed certificate and has no CORS headers,
which makes it unreachable from mobile webviews and React Native fetch.
This lightweight proxy resolves both issues.

Endpoints:
    GET  /api/health            – node health passthrough
    GET  /api/balance/<wallet>  – RTC balance for *wallet*
    GET  /api/history/<wallet>  – recent payout/attestation log
    GET  /api/epoch             – current epoch / slot info
    GET  /api/miners            – active miners list

Usage:
    python scripts/wallet_api_server.py                 # default :8787
    python scripts/wallet_api_server.py --port 9090     # custom port
    python scripts/wallet_api_server.py --node https://custom-node:443

Bounty: #1616
"""

from __future__ import annotations

import argparse
import http.server
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_NODE = "https://50.28.86.131"
DEFAULT_PORT = 8787

# Wallet format: 38 hex chars followed by "RTC" (41 total)
WALLET_RE = re.compile(r"^[0-9a-fA-F]{38}RTC$")

# Path routing: (method, regex) -> handler name
ROUTE_TABLE: List[Tuple[str, re.Pattern[str], str]] = [
    ("GET", re.compile(r"^/api/health$"), "handle_health"),
    ("GET", re.compile(r"^/api/balance/(?P<wallet>[^/]+)$"), "handle_balance"),
    ("GET", re.compile(r"^/api/history/(?P<wallet>[^/]+)$"), "handle_history"),
    ("GET", re.compile(r"^/api/epoch$"), "handle_epoch"),
    ("GET", re.compile(r"^/api/miners$"), "handle_miners"),
]


# ---------------------------------------------------------------------------
# Upstream helpers
# ---------------------------------------------------------------------------


def _make_ssl_ctx() -> ssl.SSLContext:
    """Create an SSL context that tolerates self-signed certs."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def node_get(
    node_url: str,
    path: str,
    params: Optional[Dict[str, str]] = None,
    timeout: int = 10,
) -> Tuple[int, Any]:
    """GET from upstream node. Returns (status_code, parsed_json | None)."""
    url = f"{node_url}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "rustchain-wallet-proxy/1.0")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_make_ssl_ctx()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return resp.status, data
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {"error": str(exc)}
        return exc.code, body
    except Exception as exc:
        return 502, {"error": f"upstream: {exc}"}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wallet(wallet_id: str) -> Optional[str]:
    """Return an error message if *wallet_id* is invalid, else None."""
    if not wallet_id:
        return "wallet ID is required"
    if len(wallet_id) > 64:
        return "wallet ID too long"
    # Accept both strict 38-hex+RTC format and free-form miner IDs
    # (the upstream API accepts both)
    if not re.match(r"^[a-zA-Z0-9_\-]+$", wallet_id):
        return "wallet ID contains invalid characters"
    return None


# ---------------------------------------------------------------------------
# Request handlers
# ---------------------------------------------------------------------------


def handle_health(node_url: str, _match: re.Match) -> Tuple[int, dict]:
    """Proxy GET /health from the upstream node."""
    status, body = node_get(node_url, "/health")
    return status, body


def handle_balance(node_url: str, match: re.Match) -> Tuple[int, dict]:
    """Return RTC balance for a wallet."""
    wallet = match.group("wallet")
    err = validate_wallet(wallet)
    if err:
        return 400, {"error": err}
    status, body = node_get(node_url, "/wallet/balance", {"miner_id": wallet})
    if status == 200 and isinstance(body, dict):
        # Normalise the response for the mobile client
        return 200, {
            "wallet_id": wallet,
            "balance_rtc": body.get("amount_rtc", 0.0),
            "balance_raw": body.get("amount_i64", 0),
        }
    return status, body


def handle_history(node_url: str, match: re.Match) -> Tuple[int, dict]:
    """Return recent activity for a wallet.

    The upstream node does not currently expose a per-wallet transaction
    history endpoint, so we synthesise a stub from the wallet balance and
    epoch data.  This keeps the mobile client contract stable so a real
    history endpoint can be swapped in later without app changes.
    """
    wallet = match.group("wallet")
    err = validate_wallet(wallet)
    if err:
        return 400, {"error": err}

    bal_status, bal_body = node_get(node_url, "/wallet/balance", {"miner_id": wallet})
    epoch_status, epoch_body = node_get(node_url, "/epoch")

    transactions: List[Dict[str, Any]] = []

    if bal_status == 200 and isinstance(bal_body, dict):
        balance = bal_body.get("amount_rtc", 0.0)
        if balance > 0:
            transactions.append({
                "type": "mining_reward",
                "amount_rtc": balance,
                "description": "Cumulative mining rewards",
                "epoch": epoch_body.get("epoch") if epoch_status == 200 else None,
            })

    return 200, {
        "wallet_id": wallet,
        "transactions": transactions,
        "note": "Full history will be available when the node exposes /wallet/history.",
    }


def handle_epoch(node_url: str, _match: re.Match) -> Tuple[int, dict]:
    """Proxy GET /epoch from the upstream node."""
    status, body = node_get(node_url, "/epoch")
    return status, body


def handle_miners(node_url: str, _match: re.Match) -> Tuple[int, dict]:
    """Proxy GET /api/miners from the upstream node."""
    status, body = node_get(node_url, "/api/miners")
    if isinstance(body, list):
        return status, {"miners": body, "count": len(body)}
    return status, body


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

HANDLERS = {
    "handle_health": handle_health,
    "handle_balance": handle_balance,
    "handle_history": handle_history,
    "handle_epoch": handle_epoch,
    "handle_miners": handle_miners,
}


class WalletRequestHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP handler with CORS and JSON responses."""

    node_url: str = DEFAULT_NODE

    # Silence per-request logs in production
    def log_message(self, fmt: str, *args: Any) -> None:  # pragma: no cover
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    # -- CORS preflight -----------------------------------------------

    def do_OPTIONS(self) -> None:
        self._cors_headers()
        self.send_response(204)
        self.end_headers()

    # -- GET routing ---------------------------------------------------

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        for method, pattern, handler_name in ROUTE_TABLE:
            if method != "GET":
                continue
            m = pattern.match(path)
            if m:
                handler = HANDLERS[handler_name]
                status, body = handler(self.node_url, m)
                self._json_response(status, body)
                return
        self._json_response(404, {"error": "not found"})

    # -- response helpers ---------------------------------------------

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _json_response(self, status: int, body: Any) -> None:
        payload = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def run_server(port: int = DEFAULT_PORT, node_url: str = DEFAULT_NODE) -> None:
    """Start the wallet API proxy server."""
    WalletRequestHandler.node_url = node_url
    server = http.server.HTTPServer(("0.0.0.0", port), WalletRequestHandler)
    server.verbose = True  # type: ignore[attr-defined]
    print(f"Wallet API proxy listening on :{port}  (upstream: {node_url})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="RustChain mobile wallet API proxy")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Listen port (default: %(default)s)")
    parser.add_argument("--node", default=DEFAULT_NODE, help="Upstream node URL (default: %(default)s)")
    args = parser.parse_args()
    run_server(port=args.port, node_url=args.node)


if __name__ == "__main__":
    main()
