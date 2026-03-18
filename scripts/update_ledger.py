#!/usr/bin/env python3
"""
Script to update the bounty payout ledger with new entries and status changes.
Usage: python scripts/update_ledger.py [options]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

LEDGER_FILE = project_root / "LEDGER.md"
DATA_DIR = project_root / "data"
BOUNTIES_FILE = DATA_DIR / "bounties.json"
PAYMENTS_FILE = DATA_DIR / "payments.json"

class LedgerUpdater:
    def __init__(self):
        self.bounties = self.load_bounties()
        self.payments = self.load_payments()
        
    def load_bounties(self) -> Dict[str, Any]:
        """Load bounty data from JSON file."""
        if not BOUNTIES_FILE.exists():
            return {}
        try:
            with open(BOUNTIES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading bounties: {e}")
            return {}
    
    def load_payments(self) -> Dict[str, Any]:
        """Load payment data from JSON file."""
        if not PAYMENTS_FILE.exists():
            return {}
        try:
            with open(PAYMENTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading payments: {e}")
            return {}
    
    def save_payments(self):
        """Save payment data to JSON file."""
        DATA_DIR.mkdir(exist_ok=True)
        with open(PAYMENTS_FILE, 'w') as f:
            json.dump(self.payments, f, indent=2)
    
    def add_entry(self, bounty_id: str, hunter: str, amount: float, 
                  description: str, status: str = "QUEUED", 
                  wallet: Optional[str] = None, tx_hash: Optional[str] = None) -> bool:
        """Add a new payout entry."""
        entry_id = f"{bounty_id}_{len(self.payments.get(bounty_id, {}))}"
        
        if bounty_id not in self.payments:
            self.payments[bounty_id] = {}
        
        entry = {
            "hunter": hunter,
            "amount": amount,
            "description": description,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if wallet:
            entry["wallet"] = wallet
        if tx_hash:
            entry["tx_hash"] = tx_hash
            
        self.payments[bounty_id][entry_id] = entry
        self.save_payments()
        
        print(f"Added entry {entry_id}: {hunter} - ${amount} ({status})")
        return True
    
    def update_status(self, bounty_id: str, entry_id: str, status: str, 
                     tx_hash: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """Update the status of an existing entry."""
        if bounty_id not in self.payments:
            print(f"Bounty {bounty_id} not found")
            return False
        
        if entry_id not in self.payments[bounty_id]:
            print(f"Entry {entry_id} not found in bounty {bounty_id}")
            return False
        
        entry = self.payments[bounty_id][entry_id]
        old_status = entry["status"]
        entry["status"] = status
        entry["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        if tx_hash:
            entry["tx_hash"] = tx_hash
        if notes:
            entry["notes"] = notes
            
        self.save_payments()
        
        print(f"Updated {entry_id}: {old_status} -> {status}")
        return True
    
    def bulk_update_status(self, bounty_id: str, old_status: str, new_status: str) -> int:
        """Update all entries with a specific status to a new status."""
        if bounty_id not in self.payments:
            print(f"Bounty {bounty_id} not found")
            return 0
        
        updated_count = 0
        for entry_id, entry in self.payments[bounty_id].items():
            if entry["status"] == old_status:
                entry["status"] = new_status
                entry["updated_at"] = datetime.now(timezone.utc).isoformat()
                updated_count += 1
        
        if updated_count > 0:
            self.save_payments()
            print(f"Updated {updated_count} entries from {old_status} to {new_status}")
        
        return updated_count
    
    def generate_ledger_md(self) -> str:
        """Generate the markdown content for the ledger."""
        content = []
        content.append("# Bounty Payout Ledger")
        content.append("")
        content.append("This ledger tracks all bounty payouts and their current status.")
        content.append("")
        content.append("## Status Definitions")
        content.append("- **QUEUED**: Payment approved, waiting to be processed")
        content.append("- **PENDING**: Payment initiated, transaction in progress")
        content.append("- **CONFIRMED**: Payment completed and confirmed on-chain")
        content.append("- **FAILED**: Payment failed and needs attention")
        content.append("")
        
        total_queued = 0
        total_pending = 0
        total_confirmed = 0
        total_failed = 0
        
        for bounty_id, entries in self.payments.items():
            if not entries:
                continue
                
            content.append(f"## Bounty: {bounty_id}")
            content.append("")
            content.append("| Entry ID | Hunter | Amount | Description | Status | Updated | TX Hash |")
            content.append("|----------|--------|--------|-------------|--------|---------|---------|")
            
            for entry_id, entry in entries.items():
                hunter = entry.get("hunter", "Unknown")
                amount = entry.get("amount", 0)
                description = entry.get("description", "")
                status = entry.get("status", "UNKNOWN")
                updated = entry.get("updated_at", "")
                tx_hash = entry.get("tx_hash", "")
                
                # Format date
                if updated:
                    try:
                        dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        updated_str = dt.strftime('%Y-%m-%d')
                    except:
                        updated_str = updated[:10] if len(updated) >= 10 else updated
                else:
                    updated_str = ""
                
                # Format TX hash
                tx_display = f"`{tx_hash[:8]}...`" if tx_hash and len(tx_hash) > 8 else tx_hash
                
                content.append(f"| {entry_id} | {hunter} | ${amount:.2f} | {description} | **{status}** | {updated_str} | {tx_display} |")
                
                # Count totals
                if status == "QUEUED":
                    total_queued += amount
                elif status == "PENDING":
                    total_pending += amount
                elif status == "CONFIRMED":
                    total_confirmed += amount
                elif status == "FAILED":
                    total_failed += amount
            
            content.append("")
        
        # Add summary
        content.append("## Summary")
        content.append("")
        content.append("| Status | Count | Total Amount |")
        content.append("|--------|-------|--------------|")
        
        for status, total in [("QUEUED", total_queued), ("PENDING", total_pending), 
                             ("CONFIRMED", total_confirmed), ("FAILED", total_failed)]:
            count = sum(1 for entries in self.payments.values() 
                       for entry in entries.values() if entry.get("status") == status)
            content.append(f"| {status} | {count} | ${total:.2f} |")
        
        content.append("")
        content.append(f"*Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
        content.append("")
        
        return "\n".join(content)
    
    def update_ledger_file(self):
        """Update the LEDGER.md file with current data."""
        content = self.generate_ledger_md()
        with open(LEDGER_FILE, 'w') as f:
            f.write(content)
        print(f"Updated {LEDGER_FILE}")
    
    def list_entries(self, bounty_id: Optional[str] = None, status: Optional[str] = None):
        """List entries with optional filtering."""
        bounties_to_check = [bounty_id] if bounty_id else list(self.payments.keys())
        
        for bid in bounties_to_check:
            if bid not in self.payments:
                continue
                
            entries = self.payments[bid]
            if status:
                entries = {k: v for k, v in entries.items() if v.get("status") == status}
            
            if entries:
                print(f"\nBounty: {bid}")
                for entry_id, entry in entries.items():
                    print(f"  {entry_id}: {entry['hunter']} - ${entry['amount']} ({entry['status']})")

def main():
    parser = argparse.ArgumentParser(description="Update bounty payout ledger")
    parser.add_argument("--action", choices=["add", "update", "bulk-update", "list", "generate"], 
                       required=True, help="Action to perform")
    
    # Add entry arguments
    parser.add_argument("--bounty-id", help="Bounty ID")
    parser.add_argument("--hunter", help="Hunter username/address")
    parser.add_argument("--amount", type=float, help="Payout amount")
    parser.add_argument("--description", help="Payment description")
    parser.add_argument("--wallet", help="Hunter wallet address")
    
    # Update entry arguments
    parser.add_argument("--entry-id", help="Entry ID to update")
    parser.add_argument("--status", help="New status")
    parser.add_argument("--old-status", help="Old status for bulk update")
    parser.add_argument("--tx-hash", help="Transaction hash")
    parser.add_argument("--notes", help="Additional notes")
    
    # List arguments
    parser.add_argument("--filter-status", help="Filter by status")
    
    args = parser.parse_args()
    
    updater = LedgerUpdater()
    
    if args.action == "add":
        if not all([args.bounty_id, args.hunter, args.amount, args.description]):
            print("Error: --bounty-id, --hunter, --amount, and --description are required for add action")
            return 1
        
        status = args.status or "QUEUED"
        success = updater.add_entry(args.bounty_id, args.hunter, args.amount, 
                                  args.description, status, args.wallet, args.tx_hash)
        if success:
            updater.update_ledger_file()
    
    elif args.action == "update":
        if not all([args.bounty_id, args.entry_id, args.status]):
            print("Error: --bounty-id, --entry-id, and --status are required for update action")
            return 1
        
        success = updater.update_status(args.bounty_id, args.entry_id, args.status, 
                                       args.tx_hash, args.notes)
        if success:
            updater.update_ledger_file()
    
    elif args.action == "bulk-update":
        if not all([args.bounty_id, args.old_status, args.status]):
            print("Error: --bounty-id, --old-status, and --status are required for bulk-update action")
            return 1
        
        count = updater.bulk_update_status(args.bounty_id, args.old_status, args.status)
        if count > 0:
            updater.update_ledger_file()
    
    elif args.action == "list":
        updater.list_entries(args.bounty_id, args.filter_status)
    
    elif args.action == "generate":
        updater.update_ledger_file()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())