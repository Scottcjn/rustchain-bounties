#!/usr/bin/env python3
"""
RustChain RTC Token Distribution Analysis
Bounty #1113 - 8 RTC

Analyzes wallet distribution using the RustChain explorer API.
Calculates Gini coefficient, shows top holders, and generates visualizations.
"""

import requests
import json
import sys
from typing import List, Dict, Tuple
from dataclasses import dataclass
import urllib3

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://50.28.86.131"

@dataclass
class Wallet:
    miner_id: str
    balance_rtc: float
    balance_i64: int


def get_all_miners() -> List[Dict]:
    """Fetch all miners from the API."""
    try:
        resp = requests.get(f"{BASE_URL}/api/miners", verify=False, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching miners: {e}")
        return []


def get_wallet_balance(miner_id: str) -> Wallet:
    """Fetch balance for a specific miner."""
    try:
        resp = requests.get(
            f"{BASE_URL}/wallet/balance",
            params={"miner_id": miner_id},
            verify=False,
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        return Wallet(
            miner_id=data["miner_id"],
            balance_rtc=data["amount_rtc"],
            balance_i64=data["amount_i64"]
        )
    except Exception as e:
        print(f"Error fetching balance for {miner_id}: {e}")
        return Wallet(miner_id=miner_id, balance_rtc=0.0, balance_i64=0)


def calculate_gini(balances: List[float]) -> float:
    """
    Calculate Gini coefficient.
    0 = perfect equality, 1 = perfect inequality
    """
    if not balances or sum(balances) == 0:
        return 0.0
    
    n = len(balances)
    sorted_balances = sorted(balances)
    cumsum = 0
    for i, bal in enumerate(sorted_balances, 1):
        cumsum += (2 * i - n - 1) * bal
    
    return cumsum / (n * sum(sorted_balances))


def analyze_distribution(wallets: List[Wallet]) -> Dict:
    """Analyze token distribution statistics."""
    balances = [w.balance_rtc for w in wallets]
    total_supply = sum(balances)
    
    # Sort by balance descending
    sorted_wallets = sorted(wallets, key=lambda x: x.balance_rtc, reverse=True)
    
    # Calculate statistics
    non_zero_wallets = [w for w in wallets if w.balance_rtc > 0]
    
    stats = {
        "total_wallets": len(wallets),
        "non_zero_wallets": len(non_zero_wallets),
        "zero_balance_wallets": len(wallets) - len(non_zero_wallets),
        "total_supply_rtc": total_supply,
        "gini_coefficient": calculate_gini(balances),
        "mean_balance": total_supply / len(wallets) if wallets else 0,
        "median_balance": sorted(balances)[len(balances)//2] if balances else 0,
        "max_balance": max(balances) if balances else 0,
        "min_balance": min(b for b in balances if b > 0) if any(b > 0 for b in balances) else 0,
        "top_10_holders": sorted_wallets[:10],
        "top_10_percent": sum(w.balance_rtc for w in sorted_wallets[:10]) / total_supply * 100 if total_supply else 0,
        "top_50_percent": sum(w.balance_rtc for w in sorted_wallets[:len(sorted_wallets)//2]) / total_supply * 100 if total_supply else 0,
    }
    
    return stats


def print_text_histogram(balances: List[float], bins: int = 10, width: int = 50):
    """Print an ASCII histogram of balance distribution."""
    if not balances:
        return
    
    max_bal = max(balances)
    if max_bal == 0:
        return
    
    # Create bins (logarithmic for better visualization)
    non_zero = [b for b in balances if b > 0]
    if not non_zero:
        print("  No non-zero balances")
        return
    
    # Linear bins
    bin_size = max_bal / bins
    counts = [0] * bins
    
    for bal in balances:
        if bal > 0:
            bin_idx = min(int(bal / bin_size), bins - 1)
            counts[bin_idx] += 1
    
    max_count = max(counts) if counts else 1
    
    print("\n" + "="*60)
    print("BALANCE DISTRIBUTION HISTOGRAM")
    print("="*60)
    
    for i in range(bins):
        lower = i * bin_size
        upper = (i + 1) * bin_size if i < bins - 1 else max_bal
        count = counts[i]
        bar = "█" * int(count / max_count * width) if max_count > 0 else ""
        print(f"{lower:8.2f} - {upper:8.2f} RTC | {bar} {count}")


def print_lorenz_curve(wallets: List[Wallet], width: int = 50, height: int = 20):
    """Print an ASCII Lorenz curve."""
    if not wallets:
        return
    
    sorted_wallets = sorted(wallets, key=lambda x: x.balance_rtc)
    balances = [w.balance_rtc for w in sorted_wallets]
    total = sum(balances)
    
    if total == 0:
        print("\nNo balance to visualize")
        return
    
    n = len(balances)
    cumsum = 0
    points = []
    
    for i, bal in enumerate(balances):
        cumsum += bal
        pop_pct = (i + 1) / n * 100
        wealth_pct = cumsum / total * 100
        points.append((pop_pct, wealth_pct))
    
    print("\n" + "="*60)
    print("LORENZ CURVE (Wealth Distribution)")
    print("="*60)
    print("Population % → | Perfect Equality | Actual Distribution")
    print("-"*60)
    
    # Print key percentiles
    percentiles = [10, 25, 50, 75, 90, 99]
    for pct in percentiles:
        idx = int(n * pct / 100) - 1
        if 0 <= idx < len(points):
            pop, wealth = points[idx]
            bar_len = int(wealth / 100 * 30)
            bar = "█" * bar_len
            print(f"  Bottom {pct:2d}%     | {pct:5.1f}%          | {bar} {wealth:.1f}%")
    
    print("-"*60)


def main():
    print("="*60)
    print("RUSTCHAIN RTC TOKEN DISTRIBUTION ANALYSIS")
    print("="*60)
    print(f"API Endpoint: {BASE_URL}")
    print()
    
    # Fetch all miners
    print("Fetching miner list...")
    miners = get_all_miners()
    print(f"Found {len(miners)} miners")
    print()
    
    # Fetch balances for all miners
    print("Fetching wallet balances...")
    wallets = []
    for miner in miners:
        miner_id = miner.get("miner", "")
        if miner_id:
            wallet = get_wallet_balance(miner_id)
            wallets.append(wallet)
            print(f"  {miner_id[:40]:40s} {wallet.balance_rtc:12.6f} RTC")
    
    print()
    
    # Analyze distribution
    stats = analyze_distribution(wallets)
    
    # Print statistics
    print("="*60)
    print("DISTRIBUTION STATISTICS")
    print("="*60)
    print(f"Total Wallets:           {stats['total_wallets']}")
    print(f"Non-Zero Wallets:        {stats['non_zero_wallets']}")
    print(f"Zero Balance Wallets:    {stats['zero_balance_wallets']}")
    print(f"Total Supply:            {stats['total_supply_rtc']:,.6f} RTC")
    print()
    print(f"Gini Coefficient:        {stats['gini_coefficient']:.4f}")
    print(f"  (0 = perfect equality, 1 = perfect inequality)")
    print()
    print(f"Mean Balance:            {stats['mean_balance']:,.6f} RTC")
    print(f"Median Balance:          {stats['median_balance']:,.6f} RTC")
    print(f"Max Balance:             {stats['max_balance']:,.6f} RTC")
    print(f"Min Non-Zero Balance:    {stats['min_balance']:,.6f} RTC")
    print()
    print(f"Top 10 Holders Control:  {stats['top_10_percent']:.2f}% of supply")
    print(f"Bottom 50% Control:      {100 - stats['top_50_percent']:.2f}% of supply")
    
    # Print top 10 holders
    print("\n" + "="*60)
    print("TOP 10 HOLDERS (Excluding Founders)")
    print("="*60)
    
    # Filter out likely founder wallets (RTC prefix and high balances)
    founder_prefixes = ["RTC", "rustchain", "founder", "dev", "team"]
    non_founder_wallets = [
        w for w in stats['top_10_holders'] 
        if not any(w.miner_id.lower().startswith(p) for p in founder_prefixes)
    ]
    
    for i, wallet in enumerate(non_founder_wallets[:10], 1):
        pct = wallet.balance_rtc / stats['total_supply_rtc'] * 100 if stats['total_supply_rtc'] else 0
        print(f"{i:2d}. {wallet.miner_id[:45]:45s} {wallet.balance_rtc:12.6f} RTC ({pct:5.2f}%)")
    
    # Print histogram
    balances = [w.balance_rtc for w in wallets]
    print_text_histogram(balances)
    
    # Print Lorenz curve
    print_lorenz_curve(wallets)
    
    # Comparison to other cryptos
    print("\n" + "="*60)
    print("COMPARISON TO OTHER CRYPTOCURRENCIES")
    print("="*60)
    print("Typical Gini Coefficients:")
    print("  Bitcoin:        ~0.65 - 0.85 (highly concentrated)")
    print("  Ethereum:       ~0.70 - 0.90 (very concentrated)")
    print("  Small-cap alts: ~0.40 - 0.80 (variable)")
    print(f"  RustChain:      {stats['gini_coefficient']:.4f}")
    print()
    
    if stats['gini_coefficient'] < 0.4:
        print("  → MORE EQUAL than typical cryptocurrencies")
    elif stats['gini_coefficient'] < 0.6:
        print("  → MODERATELY CONCENTRATED (typical for new projects)")
    else:
        print("  → HIGHLY CONCENTRATED (common in early-stage projects)")
    
    # Save detailed report
    report = {
        "analysis_timestamp": str(__import__('datetime').datetime.now()),
        "statistics": {
            "total_wallets": stats['total_wallets'],
            "non_zero_wallets": stats['non_zero_wallets'],
            "total_supply_rtc": stats['total_supply_rtc'],
            "gini_coefficient": stats['gini_coefficient'],
            "mean_balance": stats['mean_balance'],
            "median_balance": stats['median_balance'],
        },
        "all_wallets": [
            {"miner_id": w.miner_id, "balance_rtc": w.balance_rtc}
            for w in sorted(wallets, key=lambda x: x.balance_rtc, reverse=True)
        ]
    }
    
    with open("token_distribution_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "="*60)
    print("Full report saved to: token_distribution_report.json")
    print("="*60)


if __name__ == "__main__":
    main()
