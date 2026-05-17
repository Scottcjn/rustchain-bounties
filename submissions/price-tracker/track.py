#!/usr/bin/env python3
"""
RustChain RTC Price Tracker
Track RTC price changes, record history, and set price alerts.
"""

import json
import time
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HISTORY_FILE = "price_history.json"
DEFAULT_ALERTS_FILE = "price_alerts.json"


class PriceTracker:
    """Track and manage RTC price data."""

    def __init__(self, history_file: str = DEFAULT_HISTORY_FILE, alerts_file: str = DEFAULT_ALERTS_FILE):
        self.history_file = Path(history_file)
        self.alerts_file = Path(alerts_file)
        self.history = self._load_json(self.history_file, [])
        self.alerts = self._load_json(self.alerts_file, [])

    @staticmethod
    def _load_json(path: Path, default):
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return default

    def _save_json(self, path: Path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def record_price(self, price: float, source: str = "manual", volume_24h: float = None):
        """Record a new price entry."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "price_usd": price,
            "source": source,
        }
        if volume_24h is not None:
            entry["volume_24h"] = volume_24h

        self.history.append(entry)
        self._save_json(self.history_file, self.history)

        # Check alerts
        triggered = self._check_alerts(price)
        return entry, triggered

    def _check_alerts(self, current_price: float) -> list:
        """Check if any price alerts are triggered."""
        triggered = []
        remaining = []

        for alert in self.alerts:
            alert_type = alert.get("type", "above")
            target = alert.get("target_price", 0)
            triggered_flag = False

            if alert_type == "above" and current_price >= target:
                triggered_flag = True
            elif alert_type == "below" and current_price <= target:
                triggered_flag = True
            elif alert_type == "change_percent":
                # Check percent change from last recorded price
                if len(self.history) >= 2:
                    prev_price = self.history[-2]["price_usd"]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    threshold = alert.get("percent", 5.0)
                    if abs(change_pct) >= threshold:
                        triggered_flag = True

            if triggered_flag:
                triggered.append(alert)
            else:
                remaining.append(alert)

        # Remove triggered alerts
        if triggered:
            self.alerts = remaining
            self._save_json(self.alerts_file, self.alerts)

        return triggered

    def add_alert(self, alert_type: str, target_price: float = None, percent: float = None, note: str = None) -> dict:
        """Add a price alert."""
        alert = {
            "id": int(time.time() * 1000),
            "type": alert_type,  # "above", "below", "change_percent"
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if target_price is not None:
            alert["target_price"] = target_price
        if percent is not None:
            alert["percent"] = percent
        if note:
            alert["note"] = note

        self.alerts.append(alert)
        self._save_json(self.alerts_file, self.alerts)
        return alert

    def remove_alert(self, alert_id: int) -> bool:
        """Remove an alert by ID."""
        original_len = len(self.alerts)
        self.alerts = [a for a in self.alerts if a["id"] != alert_id]
        self._save_json(self.alerts_file, self.alerts)
        return len(self.alerts) < original_len

    def list_alerts(self) -> list:
        """List all active alerts."""
        return self.alerts

    def get_history(self, limit: int = 20, sort: str = "desc") -> list:
        """Get price history."""
        data = self.history.copy()
        if sort == "desc":
            data.reverse()
        return data[:limit]

    def get_stats(self) -> dict:
        """Get price statistics."""
        if not self.history:
            return {"error": "No price data available"}

        prices = [e["price_usd"] for e in self.history]
        return {
            "current": prices[-1],
            "high": max(prices),
            "low": min(prices),
            "average": round(sum(prices) / len(prices), 6),
            "count": len(prices),
            "first_recorded": self.history[0]["timestamp"],
            "last_recorded": self.history[-1]["timestamp"],
            "change": round(prices[-1] - prices[0], 6),
            "change_percent": round(((prices[-1] - prices[0]) / prices[0]) * 100, 2) if prices[0] != 0 else 0,
        }

    def import_prices(self, data: list):
        """Import price data from a list of entries."""
        for entry in data:
            if "price_usd" in entry:
                self.history.append(entry)
        self._save_json(self.history_file, self.history)

    def export_csv(self, output: str = "price_history.csv"):
        """Export price history to CSV."""
        import csv
        if not self.history:
            print("No data to export")
            return

        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "price_usd", "source", "volume_24h"])
            writer.writeheader()
            for entry in self.history:
                writer.writerow({k: entry.get(k, "") for k in ["timestamp", "price_usd", "source", "volume_24h"]})
        print(f"[OK] Exported {len(self.history)} records to {output}")


def main():
    parser = argparse.ArgumentParser(description="RustChain RTC Price Tracker")
    subparsers = parser.add_subparsers(dest="command")

    # Record price
    rec = subparsers.add_parser("record", help="Record a new price")
    rec.add_argument("price", type=float, help="Price in USD")
    rec.add_argument("-s", "--source", default="manual", help="Price source")
    rec.add_argument("-v", "--volume", type=float, help="24h volume")

    # History
    hist = subparsers.add_parser("history", help="View price history")
    hist.add_argument("-n", "--limit", type=int, default=20, help="Number of records")
    hist.add_argument("--asc", action="store_true", help="Sort ascending")

    # Stats
    subparsers.add_parser("stats", help="Show price statistics")

    # Add alert
    alert_add = subparsers.add_parser("add-alert", help="Add a price alert")
    alert_add.add_argument("type", choices=["above", "below", "change_percent"], help="Alert type")
    alert_add.add_argument("-t", "--target", type=float, help="Target price")
    alert_add.add_argument("-p", "--percent", type=float, help="Percent change threshold")
    alert_add.add_argument("-n", "--note", help="Note for the alert")

    # List alerts
    subparsers.add_parser("list-alerts", help="List active alerts")

    # Remove alert
    alert_rm = subparsers.add_parser("remove-alert", help="Remove an alert")
    alert_rm.add_argument("id", type=int, help="Alert ID to remove")

    # Export CSV
    exp = subparsers.add_parser("export", help="Export history to CSV")
    exp.add_argument("-o", "--output", default="price_history.csv", help="Output file")

    args = parser.parse_args()
    tracker = PriceTracker()

    if args.command == "record":
        entry, triggered = tracker.record_price(args.price, args.source, args.volume)
        print(f"[OK] Recorded: ${args.price} at {entry['timestamp']}")
        for a in triggered:
            print(f"[ALERT] ALERT TRIGGERED: {a['type']} @ ${a.get('target_price', 'N/A')}")

    elif args.command == "history":
        data = tracker.get_history(limit=args.limit, sort="asc" if args.asc else "desc")
        if not data:
            print("No price history found")
        for e in data:
            vol = f" | Vol: ${e.get('volume_24h', 'N/A')}" if "volume_24h" in e else ""
            print(f"  {e['timestamp']} | ${e['price_usd']:.6f} | {e['source']}{vol}")

    elif args.command == "stats":
        stats = tracker.get_stats()
        if "error" in stats:
            print(stats["error"])
        else:
            print(f"[STATS] RTC Price Statistics")
            print(f"  Current:      ${stats['current']:.6f}")
            print(f"  High:         ${stats['high']:.6f}")
            print(f"  Low:          ${stats['low']:.6f}")
            print(f"  Average:      ${stats['average']:.6f}")
            print(f"  Change:       ${stats['change']:+.6f} ({stats['change_percent']:+.2f}%)")
            print(f"  Data points:  {stats['count']}")

    elif args.command == "add-alert":
        alert = tracker.add_alert(args.type, args.target, args.percent, args.note)
        print(f"[OK] Alert added: {alert['type']} (ID: {alert['id']})")

    elif args.command == "list-alerts":
        alerts = tracker.list_alerts()
        if not alerts:
            print("No active alerts")
        for a in alerts:
            target = f"${a.get('target_price', 'N/A')}" if "target_price" in a else f"{a.get('percent', 'N/A')}%"
            print(f"  ID: {a['id']} | {a['type']} | Target: {target} | {a.get('note', '')}")

    elif args.command == "remove-alert":
        if tracker.remove_alert(args.id):
            print(f"[OK] Alert {args.id} removed")
        else:
            print(f"[FAIL] Alert {args.id} not found")

    elif args.command == "export":
        tracker.export_csv(args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
