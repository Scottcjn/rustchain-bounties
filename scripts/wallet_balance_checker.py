#!/usr/bin/env python3
"""
RustChain Wallet Balance Checker
A simple script to check multiple wallet balances simultaneously.

Usage:
    python3 wallet_balance_checker.py <wallet_id_1> [wallet_id_2] ... [wallet_id_n]
    python3 wallet_balance_checker.py --file wallets.txt

Example:
    python3 wallet_balance_checker.py my_wallet_1 my_wallet_2
    python3 wallet_balance_checker.py --file my_wallets.txt

File format (one wallet ID per line):
    wallet_id_1
    wallet_id_2
    wallet_id_3
"""

import argparse
import json
import sys
import requests
from typing import List, Dict


def get_wallet_balance(wallet_id: str, node_url: str = "https://50.28.86.131") -> Dict:
    """
    Get balance for a single wallet from RustChain node.
    
    Args:
        wallet_id: The wallet ID to check
        node_url: The RustChain node URL
        
    Returns:
        Dictionary containing balance information
    """
    try:
        url = f"{node_url}/wallet/balance?miner_id={wallet_id}"
        # Disable SSL verification to handle certificate issues
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch balance for {wallet_id}: {str(e)}",
            "miner_id": wallet_id,
            "amount_rtc": 0.0
        }


def check_multiple_wallets(wallet_ids: List[str]) -> List[Dict]:
    """
    Check balances for multiple wallets.
    
    Args:
        wallet_ids: List of wallet IDs to check
        
    Returns:
        List of balance dictionaries
    """
    results = []
    for wallet_id in wallet_ids:
        balance_info = get_wallet_balance(wallet_id)
        results.append(balance_info)
    return results


def print_results(results: List[Dict]):
    """
    Print balance results in a formatted table.
    """
    print("\n" + "="*60)
    print("RUSTCHAIN WALLET BALANCE REPORT")
    print("="*60)
    
    total_rtc = 0.0
    successful_checks = 0
    
    for result in results:
        if "error" in result:
            print(f"❌ {result['miner_id']}: {result['error']}")
        else:
            rtc_amount = result.get("amount_rtc", 0.0)
            total_rtc += rtc_amount
            successful_checks += 1
            print(f"✅ {result['miner_id']}: {rtc_amount:.4f} RTC")
    
    print("-"*60)
    print(f"Total Balance: {total_rtc:.4f} RTC")
    print(f"Successful Checks: {successful_checks}/{len(results)}")
    print("="*60)


def read_wallets_from_file(file_path: str) -> List[str]:
    """
    Read wallet IDs from a file (one per line).
    """
    try:
        with open(file_path, 'r') as f:
            wallets = [line.strip() for line in f if line.strip()]
        return wallets
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Check RustChain wallet balances")
    parser.add_argument('wallets', nargs='*', help='Wallet IDs to check')
    parser.add_argument('--file', '-f', help='File containing wallet IDs (one per line)')
    parser.add_argument('--node', '-n', default='https://50.28.86.131', 
                       help='RustChain node URL (default: https://50.28.86.131)')
    
    args = parser.parse_args()
    
    # Determine wallet IDs to check
    if args.file:
        wallet_ids = read_wallets_from_file(args.file)
    elif args.wallets:
        wallet_ids = args.wallets
    else:
        print("Error: Please provide wallet IDs or a file containing wallet IDs.")
        print("Usage: python3 wallet_balance_checker.py <wallet_id_1> [wallet_id_2] ...")
        print("   or: python3 wallet_balance_checker.py --file wallets.txt")
        sys.exit(1)
    
    if not wallet_ids:
        print("Error: No wallet IDs provided.")
        sys.exit(1)
    
    print(f"Checking {len(wallet_ids)} wallet(s)...")
    results = check_multiple_wallets(wallet_ids)
    print_results(results)


if __name__ == "__main__":
    # Disable warnings for insecure SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()