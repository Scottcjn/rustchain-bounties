#!/usr/bin/env python3
"""Query and verify a live RustChain wallet balance response."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from typing import Any


DEFAULT_ENDPOINT = "https://rustchain.org/wallet/balance"
RTC_SCALE = Decimal("100000000")


def fetch_balance(endpoint: str, miner_id: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"miner_id": miner_id})
    url = f"{endpoint}?{query}"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "rustchain-balance-verifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("endpoint did not return a JSON object")
    return data


def verify_balance(data: dict[str, Any], expected_miner_id: str) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if data.get("miner_id") != expected_miner_id:
        errors.append("returned miner_id does not match requested miner_id")

    try:
        amount_i64 = Decimal(str(data["amount_i64"]))
        amount_rtc = Decimal(str(data["amount_rtc"]))
    except KeyError as exc:
        errors.append(f"missing field: {exc.args[0]}")
        return False, errors
    except (InvalidOperation, TypeError):
        errors.append("amount_i64 and amount_rtc must be numeric")
        return False, errors

    if amount_i64 != amount_i64.to_integral_value():
        errors.append("amount_i64 must be an integer value")

    expected_rtc = amount_i64 / RTC_SCALE
    if amount_rtc != expected_rtc:
        errors.append(f"amount_rtc should equal amount_i64 / 100000000 ({expected_rtc})")

    return not errors, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a live RustChain wallet balance.")
    parser.add_argument("miner_id", help="Native RTC wallet/miner ID to verify")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="RustChain balance endpoint")
    args = parser.parse_args()

    data = fetch_balance(args.endpoint, args.miner_id)
    ok, errors = verify_balance(data, args.miner_id)

    print(f"endpoint: {args.endpoint}")
    print(f"miner_id: {data.get('miner_id')}")
    print(f"amount_i64: {data.get('amount_i64')}")
    print(f"amount_rtc: {data.get('amount_rtc')}")
    print(f"verification: {'PASS' if ok else 'FAIL'}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

