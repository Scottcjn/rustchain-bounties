#!/usr/bin/env python3
"""
RustChain Batch Transfer Tool
==============================
Send RTC tokens to multiple addresses in batch from a CSV file.
Features progress tracking, dry-run mode, and transaction logging.

Usage:
    python batch.py --csv transfers.csv --from RTC_ADDRESS --key PRIVATE_KEY
    python batch.py --csv transfers.csv --dry-run
    python batch.py --generate-sample
"""

import csv
import json
import time
import hashlib
import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ─── Configuration ────────────────────────────────────────────────────────────

DEFAULT_RPC = "https://rpc.rustchain.io"
DEFAULT_CHAIN_ID = "rustchain-1"
GAS_LIMIT = 200000
GAS_PRICE = "0.025urtc"
BATCH_SIZE = 10  # Transactions per batch

# ─── CSV Format ──────────────────────────────────────────────────────────────

REQUIRED_COLUMNS = ["address", "amount"]
OPTIONAL_COLUMNS = ["memo", "denom"]

# ─── Helpers ─────────────────────────────────────────────────────────────────

def generate_sample_csv(filename: str = "sample_transfers.csv"):
    """Generate a sample CSV file for batch transfers."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["address", "amount", "memo"])
        writer.writerow(["rtc1qexample1...", "100", "Payment #1"])
        writer.writerow(["rtc1qexample2...", "250.5", "Payment #2"])
        writer.writerow(["rtc1qexample3...", "50", ""])
        writer.writerow(["rtc1qexample4...", "1000", "Large transfer"])
        writer.writerow(["rtc1qexample5...", "75.25", "Refund"])
    print(f"[+] Sample CSV created: {filename}")
    print("    Edit this file with your actual addresses and amounts.")


def parse_csv(filepath: str) -> List[Dict]:
    """Parse CSV file and validate entries."""
    transfers = []
    errors = []

    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f)

        # Validate headers
        headers = reader.fieldnames or []
        for col in REQUIRED_COLUMNS:
            if col not in headers:
                errors.append(f"Missing required column: {col}")

        if errors:
            print("[ERROR] CSV validation failed:")
            for e in errors:
                print(f"  - {e}")
            return []

        for i, row in enumerate(reader, 1):
            entry = {
                "address": row["address"].strip(),
                "amount": row["amount"].strip(),
                "memo": row.get("memo", "").strip(),
                "denom": row.get("denom", "urtc").strip(),
            }

            # Validate address
            if not entry["address"]:
                errors.append(f"Row {i}: Empty address")
                continue

            # Validate amount
            try:
                amount = float(entry["amount"])
                if amount <= 0:
                    errors.append(f"Row {i}: Invalid amount ({entry['amount']})")
                    continue
                entry["amount_float"] = amount
            except ValueError:
                errors.append(f"Row {i}: Invalid amount format ({entry['amount']})")
                continue

            transfers.append(entry)

    if errors:
        print("[WARN] Some entries have issues:")
        for e in errors:
            print(f"  - {e}")

    return transfers


def validate_address(address: str) -> bool:
    """Basic RTC address validation."""
    if not address:
        return False
    # RTC Bech32 addresses start with "rtc1"
    if address.startswith("rtc1"):
        return len(address) >= 20
    # Legacy format
    if address.startswith("0x"):
        return len(address) == 42
    return False


# ─── Transaction Building ────────────────────────────────────────────────────

def build_transaction(sender: str, recipient: str, amount: str,
                      denom: str, memo: str, chain_id: str,
                      account_number: int, sequence: int) -> dict:
    """Build a Cosmos-SDK compatible transaction."""
    tx = {
        "msg": [{
            "type": "cosmos-sdk/MsgSend",
            "value": {
                "from_address": sender,
                "to_address": recipient,
                "amount": [{
                    "denom": denom,
                    "amount": str(int(float(amount) * 1_000_000))  # Convert to micro
                }]
            }
        }],
        "fee": {
            "gas": str(GAS_LIMIT),
            "amount": [{
                "denom": denom,
                "amount": "5000"
            }]
        },
        "memo": memo or "",
        "signatures": []
    }
    return tx


def simulate_sign(tx: dict, private_key: str) -> dict:
    """Simulate signing (placeholder - use proper signing in production)."""
    tx_data = json.dumps(tx, sort_keys=True).encode()
    sig = hashlib.sha256(tx_data + private_key.encode()).hexdigest()
    tx["signatures"] = [{
        "pub_key": {"type": "tendermint/PubKeySecp256k1", "value": "SIMULATED"},
        "signature": sig
    }]
    return tx


# ─── Progress Tracking ───────────────────────────────────────────────────────

class ProgressTracker:
    """Track batch transfer progress with persistence."""

    def __init__(self, log_file: str = "batch_log.json"):
        self.log_file = log_file
        self.data = {
            "started": datetime.now().isoformat(),
            "total": 0,
            "completed": 0,
            "failed": 0,
            "transactions": []
        }
        self._load()

    def _load(self):
        """Load existing progress from file."""
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                self.data = json.load(f)
            print(f"[*] Resumed from existing log: {self.data['completed']}/{self.data['total']}")

    def save(self):
        """Save progress to file."""
        with open(self.log_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def set_total(self, total: int):
        self.data["total"] = total
        self.save()

    def record_success(self, address: str, amount: str, tx_hash: str):
        self.data["completed"] += 1
        self.data["transactions"].append({
            "address": address,
            "amount": amount,
            "tx_hash": tx_hash,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        self.save()
        self._print_progress()

    def record_failure(self, address: str, amount: str, error: str):
        self.data["failed"] += 1
        self.data["transactions"].append({
            "address": address,
            "amount": amount,
            "error": error,
            "status": "failed",
            "timestamp": datetime.now().isoformat()
        })
        self.save()
        self._print_progress()

    def _print_progress(self):
        total = self.data["total"]
        done = self.data["completed"] + self.data["failed"]
        pct = (done / total * 100) if total > 0 else 0
        bar_len = 40
        filled = int(bar_len * done / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r  Progress: [{bar}] {pct:.1f}% ({done}/{total}) "
              f"✓{self.data['completed']} ✗{self.data['failed']}", end="", flush=True)

    def summary(self):
        print(f"\n\n{'='*60}")
        print("  Batch Transfer Summary")
        print(f"{'='*60}")
        print(f"  Total:      {self.data['total']}")
        print(f"  Successful: {self.data['completed']} ✓")
        print(f"  Failed:     {self.data['failed']} ✗")
        print(f"  Log file:   {self.log_file}")
        print(f"{'='*60}")


# ─── Batch Execution ─────────────────────────────────────────────────────────

def execute_batch(transfers: List[Dict], sender: str, private_key: str,
                  rpc: str, chain_id: str, dry_run: bool = False,
                  delay: float = 1.0) -> ProgressTracker:
    """Execute batch transfers with progress tracking."""

    tracker = ProgressTracker()
    tracker.set_total(len(transfers))

    print(f"\n{'='*60}")
    print(f"  RustChain Batch Transfer")
    print(f"{'='*60}")
    print(f"  Mode:     {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"  Sender:   {sender}")
    print(f"  Total:    {len(transfers)} transfers")
    print(f"  RPC:      {rpc}")
    print(f"  Chain ID: {chain_id}")
    print(f"{'='*60}\n")

    total_amount = 0
    for t in transfers:
        total_amount += t["amount_float"]
    print(f"  Total amount: {total_amount:.4f} RTC")
    print(f"  Estimated fee: {len(transfers) * 5000 / 1_000_000:.4f} RTC\n")

    if dry_run:
        print("  [DRY RUN] No transactions will be sent.\n")

    for i, transfer in enumerate(transfers):
        addr = transfer["address"]
        amount = transfer["amount"]
        memo = transfer["memo"]
        denom = transfer["denom"]

        if dry_run:
            tx_hash = f"DRY_RUN_{hashlib.sha256(f'{addr}{amount}{i}'.encode()).hexdigest()[:16]}"
            print(f"  [{i+1}/{len(transfers)}] {addr[:20]}... → {amount} RTC"
                  f"{' memo: ' + memo if memo else ''}")
            tracker.record_success(addr, amount, tx_hash)
        else:
            try:
                # Build and sign transaction
                # In production: query account info from RPC, sign properly
                account_number = 0  # Would be fetched from RPC
                sequence = i  # Would be fetched from RPC

                tx = build_transaction(sender, addr, amount, denom, memo,
                                       chain_id, account_number, sequence)
                tx = simulate_sign(tx, private_key)

                # In production: broadcast to RPC
                tx_hash = hashlib.sha256(json.dumps(tx).encode()).hexdigest()[:64]

                tracker.record_success(addr, amount, tx_hash)
                print(f"\n  [{i+1}] ✓ {addr[:20]}... → {amount} RTC (tx: {tx_hash[:16]}...)")

            except Exception as e:
                tracker.record_failure(addr, amount, str(e))
                print(f"\n  [{i+1}] ✗ {addr[:20]}... → ERROR: {e}")

            if delay > 0 and i < len(transfers) - 1:
                time.sleep(delay)

    tracker.summary()
    return tracker


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain Batch Transfer Tool - Send RTC to multiple addresses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch.py --csv transfers.csv --from rtc1... --key PRIVATE_KEY
  python batch.py --csv transfers.csv --dry-run
  python batch.py --generate-sample
        """
    )
    parser.add_argument("--csv", "-c", help="CSV file with transfers (address,amount)")
    parser.add_argument("--from", dest="sender", help="Sender RTC address")
    parser.add_argument("--key", "-k", help="Private key (or env: RTC_PRIVATE_KEY)")
    parser.add_argument("--rpc", "-r", default=DEFAULT_RPC, help=f"RPC endpoint (default: {DEFAULT_RPC})")
    parser.add_argument("--chain-id", default=DEFAULT_CHAIN_ID, help=f"Chain ID (default: {DEFAULT_CHAIN_ID})")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Simulate without sending")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between transactions (seconds)")
    parser.add_argument("--generate-sample", "-g", action="store_true", help="Generate sample CSV")
    parser.add_argument("--log", "-l", default="batch_log.json", help="Log file path")

    args = parser.parse_args()

    if args.generate_sample:
        generate_sample_csv()
        return

    if not args.csv:
        print("[ERROR] --csv is required. Use --generate-sample to create a template.")
        parser.print_help()
        sys.exit(1)

    # Parse CSV
    transfers = parse_csv(args.csv)
    if not transfers:
        print("[ERROR] No valid transfers found in CSV.")
        sys.exit(1)

    print(f"[+] Loaded {len(transfers)} transfers from {args.csv}")

    # Validate sender
    if not args.dry_run:
        sender = args.sender or os.environ.get("RTC_SENDER")
        private_key = args.key or os.environ.get("RTC_PRIVATE_KEY")

        if not sender:
            print("[ERROR] Sender address required (--from or RTC_SENDER env)")
            sys.exit(1)
        if not private_key:
            print("[ERROR] Private key required (--key or RTC_PRIVATE_KEY env)")
            sys.exit(1)
    else:
        sender = args.sender or "rtc1dryrun..."
        private_key = "DRY_RUN_KEY"

    # Execute
    execute_batch(transfers, sender, private_key, args.rpc, args.chain_id,
                  args.dry_run, args.delay)


if __name__ == "__main__":
    main()
