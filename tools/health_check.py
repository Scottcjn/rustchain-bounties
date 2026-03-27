#!/usr/bin/env python3
"""
RustChain Health Check CLI Tool

Queries RustChain attestation nodes and displays health status in a formatted table.

Nodes:
- 50.28.86.131
- 50.28.86.153  
- 76.8.228.245:8099

Displays: version, uptime, db_rw status, tip age
"""

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_NODES = [
    "http://50.28.86.131:8099",
    "http://50.28.86.153:8099",
    "http://76.8.228.245:8099",
]


def create_ssl_context(insecure: bool = False) -> Optional[ssl.SSLContext]:
    if not insecure:
        return None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_get(url: str, timeout: int = 10, insecure: bool = False) -> Tuple[bool, Any, str]:
    """Make HTTP GET request and return (success, data, error)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rustchain-health-check/1.0"})
        ctx = create_ssl_context(insecure)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return True, json.loads(body), ""
            except json.JSONDecodeError:
                return False, None, "invalid_json"
    except urllib.error.HTTPError as e:
        return False, None, f"http_{e.code}"
    except urllib.error.URLError as e:
        return False, None, f"url_error"
    except Exception as e:
        return False, None, str(type(e).__name__)


def check_node(base_url: str, insecure: bool = False) -> Dict[str, Any]:
    """Check a single node's health."""
    health_url = f"{base_url}/health"
    
    ok, data, err = http_get(health_url, insecure=insecure)
    
    if not ok:
        return {
            "url": base_url,
            "status": "DOWN",
            "error": err,
            "version": "-",
            "uptime": "-",
            "db_rw": "-",
            "tip_age": "-",
        }
    
    # Parse health response
    # Fields: version, uptime_s, db_rw, tip_age_slots, ok, backup_age_hours
    return {
        "url": base_url,
        "status": "UP" if data.get("ok", True) else "DEGRADED",
        "error": "",
        "version": data.get("version") or "-",
        "uptime": data.get("uptime_s") or data.get("uptime_seconds") or "-",
        "db_rw": "✓" if data.get("db_rw") else "✗" if data.get("db_rw") is not None else "-",
        "tip_age": str(data.get("tip_age_slots", "-")) if data.get("tip_age_slots") is not None else "-",
        "raw": data,
    }


def format_uptime(seconds: Any) -> str:
    """Format uptime seconds to human readable string."""
    try:
        secs = int(seconds)
        if secs < 60:
            return f"{secs}s"
        elif secs < 3600:
            return f"{secs // 60}m"
        elif secs < 86400:
            return f"{secs // 3600}h"
        else:
            days = secs // 86400
            return f"{days}d"
    except (TypeError, ValueError):
        return str(seconds)


def format_tip_age(seconds: Any) -> str:
    """Format tip age seconds to human readable string."""
    try:
        secs = int(seconds)
        if secs < 60:
            return f"{secs}s"
        elif secs < 3600:
            return f"{secs // 60}m"
        elif secs < 86400:
            return f"{secs // 3600}h"
        else:
            return f"{secs // 86400}d"
    except (TypeError, ValueError):
        return str(seconds)


def print_table(results: List[Dict[str, Any]]) -> None:
    """Print health status in a formatted table."""
    # Calculate column widths
    node_width = max(len(r["url"].replace("http://", "").replace("https://", "")) for r in results)
    node_width = max(node_width, 15)
    
    version_width = max(len(str(r["version"])) for r in results)
    version_width = max(version_width, 8)
    
    uptime_width = max(len(str(r["uptime"])) for r in results)
    uptime_width = max(uptime_width, 8)
    
    # Header
    print(f"{'NODE'.ljust(node_width)} {'STATUS':^10} {'VERSION'.ljust(version_width)} {'UPTIME'.ljust(uptime_width)} {'DB_RW':^8} {'TIP_AGE':^8}")
    print("-" * (node_width + 10 + version_width + uptime_width + 8 + 8 + 5))
    
    # Rows
    for r in results:
        node = r["url"].replace("http://", "").replace("https://", "")
        status = r["status"]
        status_emoji = "✅" if status == "UP" else "⚠️" if status == "DEGRADED" else "❌"
        
        version = str(r["version"])[:version_width]
        uptime = format_uptime(r["uptime"])[:uptime_width]
        db_rw = str(r["db_rw"])[:8]
        tip_age = format_tip_age(r["tip_age"])[:8]
        
        print(f"{node.ljust(node_width)} {status_emoji} {status:^8} {version.ljust(version_width)} {uptime.ljust(uptime_width)} {db_rw:^8} {tip_age:^8}")


def main():
    parser = argparse.ArgumentParser(description="RustChain Health Check CLI")
    parser.add_argument("-n", "--nodes", nargs="+", default=DEFAULT_NODES, help="Node URLs to check")
    parser.add_argument("-i", "--insecure", action="store_true", help="Allow insecure SSL connections")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("-j", "--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()
    
    print(f"🔍 Checking {len(args.nodes)} RustChain nodes...")
    print()
    
    results = []
    for node in args.nodes:
        result = check_node(node, insecure=args.insecure)
        results.append(result)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_table(results)
    
    # Summary
    up_count = sum(1 for r in results if r["status"] == "UP")
    print()
    print(f"📊 Summary: {up_count}/{len(results)} nodes online")
    
    # Exit code
    if up_count == 0:
        sys.exit(2)
    elif up_count < len(results):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
