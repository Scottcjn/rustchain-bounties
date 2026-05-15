#!/usr/bin/env python3
"""
RustChain Multi-Wallet Manager
Manage multiple RTC wallets, view balances, and use transfer templates.
"""

import json
import argparse
import os
import copy
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_WALLETS_FILE = "wallets.json"
DEFAULT_TEMPLATES_FILE = "transfer_templates.json"


class MultiWalletManager:
    """Manage multiple RustChain wallets."""

    def __init__(self, wallets_file: str = DEFAULT_WALLETS_FILE, templates_file: str = DEFAULT_TEMPLATES_FILE):
        self.wallets_file = Path(wallets_file)
        self.templates_file = Path(templates_file)
        self.wallets = self._load_json(self.wallets_file, {"wallets": {}})
        self.templates = self._load_json(self.templates_file, {"templates": {}})

    @staticmethod
    def _load_json(path: Path, default):
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return default

    def _save_wallets(self):
        with open(self.wallets_file, "w") as f:
            json.dump(self.wallets, f, indent=2)

    def _save_templates(self):
        with open(self.templates_file, "w") as f:
            json.dump(self.templates, f, indent=2)

    def add_wallet(self, name: str, address: str, group: str = "default", note: str = "") -> dict:
        """Add a new wallet."""
        if name in self.wallets["wallets"]:
            raise ValueError(f"Wallet '{name}' already exists")

        wallet = {
            "address": address,
            "group": group,
            "note": note,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "balance": 0.0,
            "last_checked": None,
        }
        self.wallets["wallets"][name] = wallet
        self._save_wallets()
        return wallet

    def remove_wallet(self, name: str) -> bool:
        """Remove a wallet by name."""
        if name not in self.wallets["wallets"]:
            return False
        del self.wallets["wallets"][name]
        self._save_wallets()
        return True

    def get_wallet(self, name: str) -> dict:
        """Get wallet details."""
        return self.wallets["wallets"].get(name)

    def list_wallets(self, group: str = None) -> dict:
        """List all wallets, optionally filtered by group."""
        wallets = self.wallets["wallets"]
        if group:
            return {k: v for k, v in wallets.items() if v.get("group") == group}
        return wallets

    def update_balance(self, name: str, balance: float) -> dict:
        """Update a wallet's balance."""
        if name not in self.wallets["wallets"]:
            raise ValueError(f"Wallet '{name}' not found")
        self.wallets["wallets"][name]["balance"] = balance
        self.wallets["wallets"][name]["last_checked"] = datetime.now(timezone.utc).isoformat()
        self._save_wallets()
        return self.wallets["wallets"][name]

    def balance_summary(self) -> dict:
        """Get a summary of all wallet balances."""
        wallets = self.wallets["wallets"]
        if not wallets:
            return {"total": 0.0, "wallet_count": 0, "groups": {}, "wallets": []}

        groups = {}
        total = 0.0
        wallet_list = []

        for name, w in wallets.items():
            bal = w.get("balance", 0.0)
            total += bal
            grp = w.get("group", "default")
            groups[grp] = groups.get(grp, 0.0) + bal
            wallet_list.append({"name": name, "balance": bal, "group": grp})

        return {
            "total": round(total, 6),
            "wallet_count": len(wallets),
            "groups": {k: round(v, 6) for k, v in groups.items()},
            "wallets": sorted(wallet_list, key=lambda x: x["balance"], reverse=True),
        }

    def add_template(self, name: str, from_wallet: str, to_address: str, amount: float, note: str = "") -> dict:
        """Create a transfer template."""
        if name in self.templates["templates"]:
            raise ValueError(f"Template '{name}' already exists")

        template = {
            "from_wallet": from_wallet,
            "to_address": to_address,
            "amount": amount,
            "note": note,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.templates["templates"][name] = template
        self._save_templates()
        return template

    def remove_template(self, name: str) -> bool:
        """Remove a transfer template."""
        if name not in self.templates["templates"]:
            return False
        del self.templates["templates"][name]
        self._save_templates()
        return True

    def list_templates(self) -> dict:
        """List all transfer templates."""
        return self.templates["templates"]

    def apply_template(self, name: str) -> dict:
        """Get template details for execution (does not execute transfer)."""
        template = self.templates["templates"].get(name)
        if not template:
            raise ValueError(f"Template '{name}' not found")

        # Resolve from_wallet to actual address
        from_w = self.wallets["wallets"].get(template["from_wallet"])
        if from_w:
            template = copy.deepcopy(template)
            template["from_address"] = from_w["address"]
            template["from_balance"] = from_w.get("balance", 0.0)

        return template

    def export_wallets(self, output: str = "wallets_export.json"):
        """Export wallet data (addresses only, no private keys)."""
        export_data = {"exported_at": datetime.now(timezone.utc).isoformat(), "wallets": {}}
        for name, w in self.wallets["wallets"].items():
            export_data["wallets"][name] = {
                "address": w["address"],
                "group": w.get("group", "default"),
                "balance": w.get("balance", 0.0),
            }
        with open(output, "w") as f:
            json.dump(export_data, f, indent=2)
        return output


def main():
    parser = argparse.ArgumentParser(description="RustChain Multi-Wallet Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Add wallet
    add = subparsers.add_parser("add", help="Add a wallet")
    add.add_argument("name", help="Wallet name/alias")
    add.add_argument("address", help="RTC wallet address")
    add.add_argument("-g", "--group", default="default", help="Wallet group")
    add.add_argument("-n", "--note", default="", help="Note")

    # Remove wallet
    rm = subparsers.add_parser("remove", help="Remove a wallet")
    rm.add_argument("name", help="Wallet name")

    # List wallets
    ls = subparsers.add_parser("list", help="List wallets")
    ls.add_argument("-g", "--group", help="Filter by group")

    # Show wallet
    show = subparsers.add_parser("show", help="Show wallet details")
    show.add_argument("name", help="Wallet name")

    # Update balance
    upd = subparsers.add_parser("update-balance", help="Update wallet balance")
    upd.add_argument("name", help="Wallet name")
    upd.add_argument("balance", type=float, help="New balance")

    # Balance summary
    subparsers.add_parser("summary", help="Balance summary across all wallets")

    # Add template
    tmpl_add = subparsers.add_parser("add-template", help="Add transfer template")
    tmpl_add.add_argument("name", help="Template name")
    tmpl_add.add_argument("-f", "--from", required=True, dest="from_wallet", help="From wallet name")
    tmpl_add.add_argument("-t", "--to", required=True, dest="to_address", help="To address")
    tmpl_add.add_argument("-a", "--amount", type=float, required=True, help="Amount in RTC")
    tmpl_add.add_argument("-n", "--note", default="", help="Note")

    # List templates
    subparsers.add_parser("list-templates", help="List transfer templates")

    # Apply template
    apply = subparsers.add_parser("apply-template", help="Apply (preview) a transfer template")
    apply.add_argument("name", help="Template name")

    # Remove template
    tmpl_rm = subparsers.add_parser("remove-template", help="Remove a transfer template")
    tmpl_rm.add_argument("name", help="Template name")

    # Export
    exp = subparsers.add_parser("export", help="Export wallet data")
    exp.add_argument("-o", "--output", default="wallets_export.json", help="Output file")

    args = parser.parse_args()
    mgr = MultiWalletManager()

    if args.command == "add":
        try:
            w = mgr.add_wallet(args.name, args.address, args.group, args.note)
            print(f"✅ Wallet '{args.name}' added: {args.address}")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.command == "remove":
        if mgr.remove_wallet(args.name):
            print(f"✅ Wallet '{args.name}' removed")
        else:
            print(f"❌ Wallet '{args.name}' not found")

    elif args.command == "list":
        wallets = mgr.list_wallets(args.group)
        if not wallets:
            print("No wallets found")
        for name, w in wallets.items():
            print(f"  {name} | {w['address']} | Bal: {w.get('balance', 0):.6f} RTC | Group: {w.get('group', 'default')}")

    elif args.command == "show":
        w = mgr.get_wallet(args.name)
        if not w:
            print(f"❌ Wallet '{args.name}' not found")
        else:
            print(f"  Name: {args.name}")
            print(f"  Address: {w['address']}")
            print(f"  Balance: {w.get('balance', 0):.6f} RTC")
            print(f"  Group: {w.get('group', 'default')}")
            print(f"  Note: {w.get('note', '')}")
            print(f"  Last Checked: {w.get('last_checked', 'Never')}")

    elif args.command == "update-balance":
        try:
            w = mgr.update_balance(args.name, args.balance)
            print(f"✅ Updated '{args.name}' balance: {args.balance:.6f} RTC")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.command == "summary":
        s = mgr.balance_summary()
        print(f"📊 Wallet Summary")
        print(f"  Total Balance: {s['total']:.6f} RTC")
        print(f"  Wallet Count:  {s['wallet_count']}")
        print(f"  Groups:")
        for g, bal in s["groups"].items():
            print(f"    {g}: {bal:.6f} RTC")
        print(f"  Top Wallets:")
        for w in s["wallets"][:10]:
            print(f"    {w['name']}: {w['balance']:.6f} RTC ({w['group']})")

    elif args.command == "add-template":
        try:
            t = mgr.add_template(args.name, args.from_wallet, args.to_address, args.amount, args.note)
            print(f"✅ Template '{args.name}' created")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.command == "list-templates":
        templates = mgr.list_templates()
        if not templates:
            print("No templates found")
        for name, t in templates.items():
            print(f"  {name} | {t['from_wallet']} → {t['to_address']} | {t['amount']} RTC")

    elif args.command == "apply-template":
        try:
            t = mgr.apply_template(args.name)
            from_addr = t.get("from_address", t["from_wallet"])
            from_bal = t.get("from_balance", "?")
            print(f"📋 Transfer Template: {args.name}")
            print(f"  From: {from_addr} (Balance: {from_bal} RTC)")
            print(f"  To:   {t['to_address']}")
            print(f"  Amount: {t['amount']} RTC")
            if t.get("note"):
                print(f"  Note: {t['note']}")
            sufficient = isinstance(from_bal, (int, float)) and from_bal >= t["amount"]
            print(f"  Sufficient balance: {'✅ Yes' if sufficient else '❌ No'}")
        except ValueError as e:
            print(f"❌ {e}")

    elif args.command == "remove-template":
        if mgr.remove_template(args.name):
            print(f"✅ Template '{args.name}' removed")
        else:
            print(f"❌ Template '{args.name}' not found")

    elif args.command == "export":
        out = mgr.export_wallets(args.output)
        print(f"✅ Exported to {out}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
