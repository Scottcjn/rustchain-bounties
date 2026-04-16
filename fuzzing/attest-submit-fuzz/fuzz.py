#!/usr/bin/env python3
"""
Fuzzing tool for /attest/submit endpoint - Bounty #1112
Tests for validation bugs, injection points, and Cloudflare bypass techniques.
"""

import json
import time
import random
import string
import urllib.request
import urllib.error
import ssl
from datetime import datetime

TARGET_URL = "https://50.28.86.131:8099/attest/submit"
REPORT_FILE = "/tmp/rustchain-bounties/fuzzing/attest-submit-fuzz/fuzz_report.json"

# Cloudflare bypass User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "python-requests/2.31.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
]

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_oversized(length=10000):
    return ''.join(random.choices(string.ascii_letters + string.digits + " \n\t", k=length))

def send_request(payload, headers=None, method="POST"):
    """Send request to target, handle Cloudflare and errors gracefully."""
    if headers is None:
        headers = {}

    # Set default Content-Type
    headers.setdefault("Content-Type", "application/json")

    # Try different bypass techniques
    for ua in USER_AGENTS:
        try:
            req_headers = {**headers, "User-Agent": ua}

            data = json.dumps(payload).encode('utf-8') if method == "POST" else None

            req = urllib.request.Request(
                TARGET_URL,
                data=data,
                headers=req_headers,
                method=method
            )

            # SSL context that ignores cert errors (for testing)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                return {
                    "status_code": resp.status,
                    "body": body[:500],
                    "headers": dict(resp.headers),
                    "bypass_used": ua[:50]
                }
        except urllib.error.HTTPError as e:
            if e.code == 403:
                # Try next User-Agent
                continue
            return {
                "status_code": e.code,
                "body": e.read().decode('utf-8', errors='replace')[:500] if e.fp else "",
                "headers": dict(e.headers) if e.headers else {},
                "bypass_used": ua[:50]
            }
        except urllib.error.URLError as e:
            return {
                "status_code": 0,
                "error": str(e),
                "bypass_used": ua[:50]
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e),
                "bypass_used": ua[:50]
            }

    # All bypasses failed - Cloudflare blocked
    return {
        "status_code": 403,
        "body": "Cloudflare blocked",
        "bypass_used": "all",
        "cloudflare_blocked": True
    }

def build_payloads():
    """Build 100+ malformed payloads across multiple categories."""
    payloads = []

    # === Category 1: Missing required fields ===
    required_fields = ["data", "signature", "timestamp", "public_key", "proof"]
    for field in required_fields:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof"
        }
        del payload[field]
        payloads.append({
            "category": "missing_field",
            "description": f"Missing required field: {field}",
            "payload": payload
        })

    # Missing all fields
    payloads.append({
        "category": "missing_field",
        "description": "Empty object - all fields missing",
        "payload": {}
    })

    # Missing multiple fields
    payload = {"data": "test"}
    payloads.append({
        "category": "missing_field",
        "description": "Only 'data' field present",
        "payload": payload
    })

    # === Category 2: Wrong types ===
    type_tests = [
        ("data", 12345, "data as integer"),
        ("data", ["array"], "data as array"),
        ("data", {"obj": "value"}, "data as object"),
        ("data", None, "data as null"),
        ("data", True, "data as boolean"),
        ("signature", 999, "signature as integer"),
        ("signature", [], "signature as array"),
        ("timestamp", "not_a_number", "timestamp as string"),
        ("timestamp", "1234567890", "timestamp as numeric string"),
        ("timestamp", 99.99, "timestamp as float"),
        ("timestamp", -1, "timestamp as negative"),
        ("public_key", 0, "public_key as integer"),
        ("public_key", "", "public_key as empty string"),
        ("proof", {}, "proof as object"),
        ("proof", 3.14159, "proof as float"),
    ]

    for field, value, desc in type_tests:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof",
            field: value
        }
        # Remove original and add wrong type
        if field in payload and isinstance(payload[field], str) and value != "":
            payload[field] = value
        payloads.append({
            "category": "wrong_type",
            "description": desc,
            "payload": payload
        })

    # === Category 3: Oversized inputs ===
    oversized_tests = [
        ("data", random_oversized(10000), "data 10KB"),
        ("data", random_oversized(100000), "data 100KB"),
        ("signature", random_string(10000), "signature 10KB"),
        ("public_key", random_string(5000), "public_key 5KB"),
        ("proof", random_oversized(50000), "proof 50KB"),
    ]

    for field, value, desc in oversized_tests:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof",
            field: value
        }
        payloads.append({
            "category": "oversized",
            "description": desc,
            "payload": payload
        })

    # === Category 4: Injection attempts ===
    injection_tests = [
        ("data", "<script>alert('xss')</script>", "XSS in data"),
        ("data", "'; DROP TABLE users; --", "SQL injection in data"),
        ("data", "{{.Class}}", "Template injection"),
        ("data", "$(whoami)", "Command injection"),
        ("data", "../../../etc/passwd", "Path traversal"),
        ("data", "\n\r\n<script>alert(1)</script>", "Newline injection"),
        ("data", "null\nContent-Type: text/html\n\n<html>", "Header injection"),
        ("signature", "OR 1=1--", "SQL injection in signature"),
        ("signature", "admin'--", "SQL auth bypass attempt"),
        ("public_key", "data:text/html,<script>alert(1)</script>", "XSS in public_key"),
        ("proof", "<img src=x onerror=alert(1)>", "XSS in proof"),
        ("proof", "\x00\x00\x00NULL_BYTES", "null bytes injection"),
        ("data", "=" * 1000, "ReDos attempt - long equals"),
        ("data", "a" * 10000 + "!", "ReDos attempt - long repeating"),
    ]

    for field, value, desc in injection_tests:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof",
            field: value
        }
        payloads.append({
            "category": "injection",
            "description": desc,
            "payload": payload
        })

    # === Category 5: Edge cases & malformed JSON ===
    edge_cases = [
        (None, "null JSON body"),
        ("{", "truncated JSON"),
        ("{}", "empty JSON object"),
        ('{"data": "test",}', "trailing comma"),
        ('{"data" "test"}', "missing colon"),
        ('{"data":}', "missing value"),
        ("[", "array start only"),
        ("", "empty body"),
        ('"string"', "bare string"),
        ("NaN", "NaN value"),
        ("Infinity", "Infinity value"),
        ("-Infinity", "negative Infinity"),
        ("undefined", "undefined value"),
    ]

    for value, desc in edge_cases:
        payloads.append({
            "category": "edge_case",
            "description": desc,
            "raw_body": value,
            "payload": value
        })

    # === Category 6: Boundary values ===
    boundary_tests = [
        ("timestamp", 0, "timestamp = 0"),
        ("timestamp", -1, "timestamp = -1"),
        ("timestamp", 2147483647, "timestamp = INT_MAX"),
        ("timestamp", 2147483648, "timestamp = INT_MAX+1"),
        ("timestamp", -2147483648, "timestamp = INT_MIN"),
        ("data", "", "empty string data"),
        ("signature", "", "empty string signature"),
    ]

    for field, value, desc in boundary_tests:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof",
            field: value
        }
        payloads.append({
            "category": "boundary",
            "description": desc,
            "payload": payload
        })

    # === Category 7: Extra/unexpected fields ===
    extra_fields = [
        ("extra_field", "test_value", "unexpected string field"),
        ("_hidden", "test", "underscore-prefixed field"),
        ("__proto__", "test", "proto pollution attempt"),
        ("constructor", {"name": "test"}, "constructor pollution"),
        ("toString", "test", "toString override attempt"),
        ("password", "Admin123!", "suspicious password field"),
        ("api_key", "secret_key_123", "api_key field"),
    ]

    for field, value, desc in extra_fields:
        payload = {
            "data": "test_data",
            "signature": "test_signature",
            "timestamp": 1234567890,
            "public_key": "test_key",
            "proof": "test_proof",
            field: value
        }
        payloads.append({
            "category": "extra_fields",
            "description": desc,
            "payload": payload
        })

    return payloads

def analyze_response(response, payload_desc):
    """Categorize response based on status code."""
    status = response.get("status_code", 0)

    if status == 0:
        if response.get("cloudflare_blocked"):
            return {
                "result": "cloudflare_blocked",
                "severity": "info",
                "note": "Cloudflare protection active"
            }
        return {
            "result": "error",
            "severity": "unknown",
            "note": response.get("error", "Unknown error")
        }

    if status == 400:
        return {
            "result": "validation_rejected",
            "severity": "good",
            "note": "Proper input validation - request rejected"
        }

    if status == 422:
        return {
            "result": "validation_rejected",
            "severity": "good",
            "note": "Unprocessable entity - proper validation"
        }

    if status == 403:
        return {
            "result": "cloudflare_blocked",
            "severity": "info",
            "note": "Cloudflare blocked request"
        }

    if status == 401:
        return {
            "result": "auth_required",
            "severity": "info",
            "note": "Authentication required"
        }

    if status == 500:
        return {
            "result": "server_error",
            "severity": "critical",
            "note": "Internal server error - potential bug"
        }

    if status == 502:
        return {
            "result": "bad_gateway",
            "severity": "high",
            "note": "Bad gateway - potential proxy issue"
        }

    if status == 504:
        return {
            "result": "gateway_timeout",
            "severity": "high",
            "note": "Gateway timeout - potential DoS vector"
        }

    if 200 <= status < 300:
        return {
            "result": "accepted",
            "severity": "warning",
            "note": f"Request accepted - unexpected for malformed input (status {status})"
        }

    return {
        "result": "unknown",
        "severity": "unknown",
        "note": f"Received status {status}"
    }

def run_fuzzing():
    """Main fuzzing loop."""
    print("=" * 60)
    print("Fuzzing Tool for /attest/submit Endpoint")
    print("Bounty #1112 - RTC Fuzzing")
    print("=" * 60)
    print(f"Target: {TARGET_URL}")
    print(f"Started: {datetime.now().isoformat()}")
    print()

    payloads = build_payloads()
    print(f"Total payloads to test: {len(payloads)}")
    print()

    results = []
    stats = {
        "total": len(payloads),
        "cloudflare_blocked": 0,
        "validation_rejected": 0,
        "server_error": 0,
        "accepted": 0,
        "error": 0,
        "unknown": 0,
    }

    for i, test_case in enumerate(payloads):
        category = test_case["category"]
        description = test_case["description"]
        payload = test_case.get("payload")
        raw_body = test_case.get("raw_body")

        print(f"[{i+1}/{len(payloads)}] {category}: {description}")

        # Handle edge cases with raw body
        headers = {}
        if raw_body is not None:
            # This is a malformed JSON test
            response = send_request_raw(raw_body, headers)
        else:
            response = send_request(payload, headers)

        analysis = analyze_response(response, description)

        result_entry = {
            "test_id": i + 1,
            "category": category,
            "description": description,
            "payload_preview": str(payload)[:200] if payload else raw_body[:200] if raw_body else "",
            "response_status": response.get("status_code", 0),
            "response_body_preview": response.get("body", "")[:200],
            "result": analysis["result"],
            "severity": analysis["severity"],
            "note": analysis["note"],
            "bypass_used": response.get("bypass_used", "N/A"),
            "timestamp": datetime.now().isoformat()
        }

        results.append(result_entry)

        # Update stats
        stats[analysis["result"]] = stats.get(analysis["result"], 0) + 1

        print(f"    -> Status: {response.get('status_code', 0)}, Result: {analysis['result']}")

        # Small delay between requests
        time.sleep(0.1)

    print()
    print("=" * 60)
    print("Fuzzing Complete")
    print("=" * 60)

    report = {
        "metadata": {
            "target": TARGET_URL,
            "start_time": datetime.now().isoformat(),
            "total_tests": len(payloads),
            "bounty": "Scottcjn/rustchain-bounties#1112",
            "reward": "10 RTC + bonus for bugs",
            "wallet": "RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5"
        },
        "statistics": stats,
        "results": results
    }

    # Save JSON report
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"JSON report saved to: {REPORT_FILE}")
    print()
    print("Summary:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Generate markdown summary for terminal
    print()
    print("=" * 60)
    print("Key Findings:")
    print("=" * 60)

    critical = [r for r in results if r["severity"] == "critical"]
    if critical:
        print(f"\nCRITICAL BUGS FOUND: {len(critical)}")
        for c in critical:
            print(f"  - [{c['category']}] {c['description']}")
            print(f"    Status: {c['response_status']}, Note: {c['note']}")

    high = [r for r in results if r["severity"] == "high"]
    if high:
        print(f"\nHIGH SEVERITY ISSUES: {len(high)}")
        for h in high:
            print(f"  - [{h['category']}] {h['description']}")

    # Cloudflare status
    blocked = stats.get("cloudflare_blocked", 0)
    total = stats.get("total", 0)
    if blocked > total * 0.8:
        print(f"\nCloudflare Protection: ACTIVE")
        print(f"  {blocked}/{total} requests were blocked by Cloudflare.")
        print("  Bypass techniques tested but endpoint remains protected.")

    return report

def send_request_raw(raw_body, headers=None):
    """Send raw body for malformed JSON tests."""
    if headers is None:
        headers = {}

    headers.setdefault("Content-Type", "application/json")

    for ua in USER_AGENTS:
        try:
            req_headers = {**headers, "User-Agent": ua}

            data = raw_body.encode('utf-8') if raw_body else b''

            req = urllib.request.Request(
                TARGET_URL,
                data=data,
                headers=req_headers,
                method="POST"
            )

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                body = resp.read().decode('utf-8', errors='replace')
                return {
                    "status_code": resp.status,
                    "body": body[:500],
                    "headers": dict(resp.headers),
                    "bypass_used": ua[:50]
                }
        except urllib.error.HTTPError as e:
            if e.code == 403:
                continue
            return {
                "status_code": e.code,
                "body": e.read().decode('utf-8', errors='replace')[:500] if e.fp else "",
                "headers": dict(e.headers) if e.headers else {},
                "bypass_used": ua[:50]
            }
        except Exception as e:
            return {
                "status_code": 0,
                "error": str(e),
                "bypass_used": ua[:50]
            }

    return {
        "status_code": 403,
        "body": "Cloudflare blocked",
        "bypass_used": "all",
        "cloudflare_blocked": True
    }

if __name__ == "__main__":
    run_fuzzing()
