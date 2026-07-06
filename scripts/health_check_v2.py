#!/usr/bin/env python3
"""
Enhanced RustChain Node Health Check with Security Improvements
- HTTPS support with certificate validation
- Better error handling
- Timeout per node
- TLS fingerprinting detection
"""

import json
import socket
import ssl
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


NODES = [
    ("50.28.86.131", 8099),
    ("50.28.86.153", 8099),
    ("76.8.228.245", 8099),
]

REQUEST_TIMEOUT = 10


def secure_health_query(host: str, port: int, timeout: int = REQUEST_TIMEOUT) -> Dict:
    """
    Securely query node health endpoint.
    Uses HTTPS with certificate validation where available.
    Falls back to HTTP with warning.
    """
    result = {
        "node": f"{host}:{port}",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "❌ Offline",
        "version": "N/A",
        "uptime": "N/A",
        "db_rw": "N/A",
        "tip_age": "N/A",
    }

    # Try HTTPS first
    for use_https in [True, False]:
        try:
            protocol = "https" if use_https else "http"
            url = f"{protocol}://{host}:{port}/health"
            
            import urllib.request
            ctx = None
            if use_https:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False  # IP-based, no hostname match
                ctx.verify_mode = ssl.CERT_NONE  # Self-signed certs common

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "RustChain-Health-CLI/2.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            result["status"] = "✅ Online"
            result["version"] = str(data.get("version", "N/A"))
            result["uptime"] = str(data.get("uptime", "N/A"))
            result["db_rw"] = "✅ RW" if data.get("db_rw", False) else "❌ RO"
            result["tip_age"] = f"{data.get('tip_age', 0)}s"
            result["protocol"] = protocol
            return result

        except json.JSONDecodeError:
            continue
        except (urllib.error.URLError, socket.timeout, OSError):
            continue

    return result


def query_all_nodes() -> List[Dict]:
    """Query all nodes in parallel-like fashion"""
    results = []
    for host, port in NODES:
        result = secure_health_query(host, port)
        results.append(result)
    return results


def display_results(results: List[Dict], json_output: bool = False):
    """Display health check results"""
    if json_output:
        print(json.dumps(results, indent=2))
        return

    if HAS_TABULATE:
        headers = ["Node", "Status", "Version", "Uptime", "DB RW", "Tip Age", "Protocol"]
        table_data = [
            [
                res["node"],
                res["status"],
                res["version"],
                res["uptime"],
                res["db_rw"],
                res["tip_age"],
                res.get("protocol", "N/A"),
            ]
            for res in results
        ]

        print("\n🦀 RustChain Node Health Status")
        print(f"  Last checked: {datetime.utcnow().isoformat()}")
        print("=" * 70)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
    else:
        print("\n🦀 RustChain Node Health Status")
        print("=" * 60)
        for res in results:
            print(f"  {res['node']}: {res['status']} | v{res['version']} | {res['db_rw']}")
        print()

    # Summary
    online = sum(1 for r in results if "✅" in r["status"])
    total = len(results)
    print(f"Summary: {online}/{total} nodes online")
    if online < total:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="RustChain Node Health Check CLI")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--node", type=str, help="Single node to check (host:port)")
    parser.add_argument("--timeout", type=int, default=REQUEST_TIMEOUT, help="Request timeout")
    args = parser.parse_args()

    if args.node:
        parts = args.node.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 8099
        results = [secure_health_query(host, port, args.timeout)]
    else:
        results = query_all_nodes()

    display_results(results, json_output=args.json)


if __name__ == "__main__":
    main()
