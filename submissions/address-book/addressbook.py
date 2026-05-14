#!/usr/bin/env python3
"""
RustChain Address Book Manager
================================
Manage frequently-used cryptocurrency addresses with groups, tags, and search.
Supports import/export (JSON, CSV) and address validation.

Usage:
    python addressbook.py add "My Wallet" rtc1q... --group personal --tags main,backup
    python addressbook.py list
    python addressbook.py list --group personal
    python addressbook.py search "wallet"
    python addressbook.py export --format json --output addresses.json
    python addressbook.py import --file addresses.json
"""

import json
import csv
import argparse
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# ─── Storage ──────────────────────────────────────────────────────────────────

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "addressbook.json")

class AddressBook:
    """Manage a local address book with groups, tags, and search."""

    def __init__(self, db_path: str = DEFAULT_DB):
        self.db_path = db_path
        self.data = {
            "version": "1.0",
            "addresses": [],
            "groups": ["personal", "exchange", "friend", "contract", "other"],
            "created": datetime.now().isoformat()
        }
        self._load()

    def _load(self):
        """Load address book from file."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self.data.update(loaded)
            print(f"[*] Loaded {len(self.data['addresses'])} addresses from {self.db_path}")

    def save(self):
        """Save address book to file."""
        self.data["updated"] = datetime.now().isoformat()
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ─── CRUD Operations ──────────────────────────────────────────────────

    def add(self, name: str, address: str, group: str = "other",
            tags: List[str] = None, memo: str = "") -> Dict:
        """Add a new address entry."""
        # Check duplicate
        for entry in self.data["addresses"]:
            if entry["address"] == address:
                print(f"[WARN] Address already exists as '{entry['name']}'. Use 'update' to modify.")
                return entry

        # Validate address
        if not self._validate_address(address):
            print(f"[ERROR] Invalid address format: {address}")
            return {}

        # Auto-detect chain from address prefix
        chain = self._detect_chain(address)

        # Create group if new
        if group not in self.data["groups"]:
            self.data["groups"].append(group)
            print(f"[+] Created new group: {group}")

        entry = {
            "id": self._next_id(),
            "name": name,
            "address": address,
            "chain": chain,
            "group": group,
            "tags": tags or [],
            "memo": memo,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }

        self.data["addresses"].append(entry)
        self.save()
        print(f"[+] Added: {name} ({chain}) → {address[:24]}...")
        return entry

    def update(self, entry_id: int, **kwargs) -> Optional[Dict]:
        """Update an existing address entry."""
        entry = self._find_by_id(entry_id)
        if not entry:
            print(f"[ERROR] Entry #{entry_id} not found.")
            return None

        for key in ["name", "address", "group", "memo"]:
            if key in kwargs and kwargs[key]:
                entry[key] = kwargs[key]

        if "tags" in kwargs and kwargs["tags"]:
            entry["tags"] = kwargs["tags"]

        if "group" in kwargs:
            if kwargs["group"] not in self.data["groups"]:
                self.data["groups"].append(kwargs["group"])

        entry["updated"] = datetime.now().isoformat()
        self.save()
        print(f"[+] Updated: #{entry_id} {entry['name']}")
        return entry

    def delete(self, entry_id: int) -> bool:
        """Delete an address entry."""
        entry = self._find_by_id(entry_id)
        if not entry:
            print(f"[ERROR] Entry #{entry_id} not found.")
            return False

        self.data["addresses"] = [e for e in self.data["addresses"] if e["id"] != entry_id]
        self.save()
        print(f"[-] Deleted: #{entry_id} {entry['name']}")
        return True

    # ─── Query Operations ─────────────────────────────────────────────────

    def list_all(self, group: str = None, chain: str = None,
                 tag: str = None, sort_by: str = "name") -> List[Dict]:
        """List addresses with optional filtering."""
        results = self.data["addresses"]

        if group:
            results = [e for e in results if e["group"] == group]
        if chain:
            results = [e for e in results if e["chain"] == chain.lower()]
        if tag:
            results = [e for e in results if tag in e.get("tags", [])]

        # Sort
        reverse = sort_by.startswith("-")
        key = sort_by.lstrip("-")
        results.sort(key=lambda x: x.get(key, ""), reverse=reverse)

        if not results:
            print("[*] No addresses found.")
            return []

        print(f"\n{'='*70}")
        print(f"  Address Book ({len(results)} entries)")
        print(f"{'='*70}")

        for e in results:
            tags_str = f" [{', '.join(e['tags'])}]" if e.get("tags") else ""
            print(f"  #{e['id']:3d}  {e['name']:<25s}  {e['chain'].upper():<6s}  "
                  f"{e['address'][:30]}...  {e['group']}{tags_str}")

        print(f"{'='*70}")
        return results

    def search(self, query: str) -> List[Dict]:
        """Search addresses by name, address, memo, or tags."""
        query_lower = query.lower()
        results = []
        for e in self.data["addresses"]:
            searchable = " ".join([
                e.get("name", ""),
                e.get("address", ""),
                e.get("memo", ""),
                " ".join(e.get("tags", []))
            ]).lower()
            if query_lower in searchable:
                results.append(e)

        if not results:
            print(f"[*] No results for '{query}'")
            return []

        print(f"\n  Search: '{query}' → {len(results)} result(s)\n")
        for e in results:
            print(f"  #{e['id']:3d}  {e['name']:<25s}  {e['address'][:40]}...")
        return results

    def groups(self) -> List[str]:
        """List all groups."""
        print(f"\n  Groups ({len(self.data['groups'])}):")
        for g in self.data["groups"]:
            count = len([e for e in self.data["addresses"] if e["group"] == g])
            print(f"    - {g} ({count} addresses)")
        return self.data["groups"]

    # ─── Import/Export ─────────────────────────────────────────────────────

    def export_json(self, filepath: str):
        """Export address book to JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"[+] Exported to {filepath}")

    def export_csv(self, filepath: str):
        """Export addresses to CSV."""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "address", "chain", "group", "tags", "memo"])
            for e in self.data["addresses"]:
                writer.writerow([
                    e["id"], e["name"], e["address"], e["chain"],
                    e["group"], ";".join(e.get("tags", [])), e.get("memo", "")
                ])
        print(f"[+] Exported {len(self.data['addresses'])} addresses to {filepath}")

    def import_json(self, filepath: str):
        """Import addresses from JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            imported = json.load(f)

        addresses = imported.get("addresses", [])
        added = 0
        skipped = 0
        for entry in addresses:
            # Check for duplicates
            existing = [e for e in self.data["addresses"] if e["address"] == entry.get("address")]
            if existing:
                skipped += 1
                continue
            entry["id"] = self._next_id()
            self.data["addresses"].append(entry)
            added += 1

        self.save()
        print(f"[+] Imported: {added} added, {skipped} duplicates skipped")

    def import_csv(self, filepath: str):
        """Import addresses from CSV."""
        added = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "Unnamed")
                address = row.get("address", "")
                group = row.get("group", "other")
                tags = row.get("tags", "").split(";") if row.get("tags") else []
                memo = row.get("memo", "")

                if address:
                    result = self.add(name, address, group, tags, memo)
                    if result:
                        added += 1

        print(f"[+] Imported {added} addresses from CSV")

    # ─── Helpers ───────────────────────────────────────────────────────────

    def _next_id(self) -> int:
        if not self.data["addresses"]:
            return 1
        return max(e["id"] for e in self.data["addresses"]) + 1

    def _find_by_id(self, entry_id: int) -> Optional[Dict]:
        for e in self.data["addresses"]:
            if e["id"] == entry_id:
                return e
        return None

    @staticmethod
    def _validate_address(address: str) -> bool:
        if not address or len(address) < 10:
            return False
        return True

    @staticmethod
    def _detect_chain(address: str) -> str:
        if address.startswith("rtc1"):
            return "rtc"
        elif address.startswith("0x"):
            return "eth"
        elif address.startswith("1") or address.startswith("3"):
            return "btc"
        elif address.startswith("bc1"):
            return "btc"
        elif address.startswith("cosmos1"):
            return "atom"
        elif address.startswith("sol1") or len(address) in (32, 44):
            return "sol"
        return "unknown"


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain Address Book Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  addressbook.py add "My Wallet" rtc1q... --group personal --tags main
  addressbook.py list
  addressbook.py list --group personal
  addressbook.py search "wallet"
  addressbook.py export --format json --output addresses.json
  addressbook.py import --file addresses.json
        """
    )
    sub = parser.add_subparsers(dest="command")

    # Add
    p_add = sub.add_parser("add", help="Add address")
    p_add.add_argument("name", help="Entry name")
    p_add.add_argument("address", help="Address")
    p_add.add_argument("--group", "-g", default="other", help="Group")
    p_add.add_argument("--tags", "-t", default="", help="Comma-separated tags")
    p_add.add_argument("--memo", "-m", default="", help="Memo")

    # List
    p_list = sub.add_parser("list", help="List addresses")
    p_list.add_argument("--group", "-g", help="Filter by group")
    p_list.add_argument("--chain", "-c", help="Filter by chain")
    p_list.add_argument("--tag", "-t", help="Filter by tag")
    p_list.add_argument("--sort", "-s", default="name", help="Sort by field")

    # Search
    p_search = sub.add_parser("search", help="Search addresses")
    p_search.add_argument("query", help="Search query")

    # Update
    p_update = sub.add_parser("update", help="Update entry")
    p_update.add_argument("id", type=int, help="Entry ID")
    p_update.add_argument("--name", help="New name")
    p_update.add_argument("--address", help="New address")
    p_update.add_argument("--group", help="New group")
    p_update.add_argument("--tags", help="New tags (comma-separated)")
    p_update.add_argument("--memo", help="New memo")

    # Delete
    p_delete = sub.add_parser("delete", help="Delete entry")
    p_delete.add_argument("id", type=int, help="Entry ID")

    # Groups
    sub.add_parser("groups", help="List groups")

    # Export
    p_export = sub.add_parser("export", help="Export addresses")
    p_export.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    p_export.add_argument("--output", "-o", default="addressbook_export")

    # Import
    p_import = sub.add_parser("import", help="Import addresses")
    p_import.add_argument("--file", "-f", required=True, help="File to import")
    p_import.add_argument("--format", choices=["json", "csv"], default=None,
                          help="Force format (auto-detected if omitted)")

    args = parser.parse_args()
    book = AddressBook()

    if args.command == "add":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        book.add(args.name, args.address, args.group, tags, args.memo)

    elif args.command == "list":
        book.list_all(args.group, args.chain, args.tag, args.sort)

    elif args.command == "search":
        book.search(args.query)

    elif args.command == "update":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        book.update(args.id, name=args.name, address=args.address,
                    group=args.group, tags=tags, memo=args.memo)

    elif args.command == "delete":
        book.delete(args.id)

    elif args.command == "groups":
        book.groups()

    elif args.command == "export":
        fmt = args.format
        filepath = args.output
        if not filepath.endswith(f".{fmt}"):
            filepath += f".{fmt}"
        if fmt == "json":
            book.export_json(filepath)
        else:
            book.export_csv(filepath)

    elif args.command == "import":
        fmt = args.format
        if not fmt:
            fmt = "json" if args.file.endswith(".json") else "csv"
        if fmt == "json":
            book.import_json(args.file)
        else:
            book.import_csv(args.file)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
