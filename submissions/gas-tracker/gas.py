#!/usr/bin/env python3
"""
RustChain Gas Fee Tracker & Predictor
======================================
Track historical gas fees, analyze trends, and predict future costs.

Usage:
    python gas.py                  # Show current gas price
    python gas.py --history 50     # Show last 50 blocks gas history
    python gas.py --predict 10     # Predict gas for next 10 blocks
    python gas.py --chart          # Display ASCII chart of gas trends
    python gas.py --alert 25       # Alert when gas drops below 25 nRUST
    python gas.py --wallet zp6     # Track gas spent by wallet
"""

import argparse
import json
import math
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

# ─── Configuration ────────────────────────────────────────────────────────────

RUSTCHAIN_RPC = "https://rpc.rustchain.io"
GAS_UNIT = "nRUST"  # nano RUST
BLOCK_TIME = 6  # seconds per block

# ─── Simulated Data Layer ─────────────────────────────────────────────────────
# In production, replace with actual RPC calls to RustChain node.

def _generate_gas_history(num_blocks: int = 200) -> List[Dict]:
    """Generate realistic simulated gas price data."""
    base_price = 15.0
    data = []
    now = time.time()
    
    for i in range(num_blocks):
        block_num = 1000000 + num_blocks - i
        # Simulate realistic gas patterns: daily cycles + spikes
        hour = datetime.fromtimestamp(now - i * BLOCK_TIME).hour
        # Peak hours: 8-10 AM, 6-9 PM UTC
        peak_factor = 1.0
        if 8 <= hour <= 10:
            peak_factor = 1.8
        elif 18 <= hour <= 21:
            peak_factor = 2.2
        elif 0 <= hour <= 5:
            peak_factor = 0.6
        
        noise = random.gauss(0, 3)
        spike = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 15, 30])  # occasional spikes
        price = max(1.0, base_price * peak_factor + noise + spike)
        
        data.append({
            "block": block_num,
            "timestamp": now - i * BLOCK_TIME,
            "gas_price": round(price, 2),
            "gas_used": random.randint(8000000, 29000000),
            "gas_limit": 30000000,
            "tx_count": random.randint(50, 500),
        })
    
    return data


def _generate_wallet_gas_spent(wallet: str) -> List[Dict]:
    """Generate simulated gas spending data for a wallet."""
    data = []
    now = time.time()
    for i in range(30):  # Last 30 days
        data.append({
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "tx_count": random.randint(1, 15),
            "gas_spent": round(random.uniform(0.001, 0.5), 6),
            "avg_gas_price": round(random.uniform(10, 40), 2),
        })
    return data


# ─── Core Functions ────────────────────────────────────────────────────────────

class GasTracker:
    """RustChain gas fee tracker and predictor."""
    
    def __init__(self):
        self.history = _generate_gas_history()
    
    def get_current_gas(self) -> Dict:
        """Get current gas price and network stats."""
        if not self.history:
            return {}
        latest = self.history[0]
        recent = [h["gas_price"] for h in self.history[:10]]
        return {
            "block": latest["block"],
            "gas_price": latest["gas_price"],
            "unit": GAS_UNIT,
            "avg_10_blocks": round(sum(recent) / len(recent), 2),
            "min_10_blocks": round(min(recent), 2),
            "max_10_blocks": round(max(recent), 2),
            "network_utilization": round(latest["gas_used"] / latest["gas_limit"] * 100, 1),
            "tx_count": latest["tx_count"],
        }
    
    def get_history(self, count: int = 20) -> List[Dict]:
        """Get gas price history for the last N blocks."""
        return self.history[:count]
    
    def predict_gas(self, blocks_ahead: int = 10) -> List[Dict]:
        """Predict gas prices for upcoming blocks using weighted moving average."""
        if len(self.history) < 20:
            return []
        
        recent_prices = [h["gas_price"] for h in self.history[:50]]
        predictions = []
        
        # Weighted Moving Average + trend
        weights = list(range(1, len(recent_prices) + 1))
        wma = sum(p * w for p, w in zip(recent_prices, weights)) / sum(weights)
        
        # Calculate trend
        first_half = recent_prices[:len(recent_prices)//2]
        second_half = recent_prices[len(recent_prices)//2:]
        trend = (sum(first_half) / len(first_half) - sum(second_half) / len(second_half)) / len(first_half)
        
        last_block = self.history[0]["block"]
        last_ts = self.history[0]["timestamp"]
        
        for i in range(1, blocks_ahead + 1):
            predicted = wma + trend * i + random.gauss(0, 1)
            predicted = max(1.0, predicted)
            predictions.append({
                "block": last_block + i,
                "timestamp": last_ts + i * BLOCK_TIME,
                "predicted_gas": round(predicted, 2),
                "confidence": round(max(0.3, 0.95 - i * 0.05), 2),
                "unit": GAS_UNIT,
            })
        
        return predictions
    
    def get_best_time_window(self) -> Dict:
        """Find the best time to submit transactions (lowest gas)."""
        hourly_avg = {}
        for h in self.history:
            hour = datetime.fromtimestamp(h["timestamp"]).hour
            if hour not in hourly_avg:
                hourly_avg[hour] = []
            hourly_avg[hour].append(h["gas_price"])
        
        hourly_means = {h: round(sum(p)/len(p), 2) for h, p in hourly_avg.items()}
        best_hour = min(hourly_means, key=hourly_means.get)
        worst_hour = max(hourly_means, key=hourly_means.get)
        
        return {
            "best_hour_utc": f"{best_hour:02d}:00",
            "best_avg_gas": hourly_means[best_hour],
            "worst_hour_utc": f"{worst_hour:02d}:00",
            "worst_avg_gas": hourly_means[worst_hour],
            "hourly_averages": dict(sorted(hourly_means.items())),
        }
    
    def get_gas_stats(self) -> Dict:
        """Get comprehensive gas statistics."""
        prices = [h["gas_price"] for h in self.history]
        utils = [h["gas_used"] / h["gas_limit"] * 100 for h in self.history]
        
        return {
            "period_blocks": len(self.history),
            "avg_gas": round(sum(prices) / len(prices), 2),
            "median_gas": round(sorted(prices)[len(prices)//2], 2),
            "min_gas": round(min(prices), 2),
            "max_gas": round(max(prices), 2),
            "std_dev": round(math.sqrt(sum((p - sum(prices)/len(prices))**2 for p in prices) / len(prices)), 2),
            "avg_utilization": round(sum(utils) / len(utils), 1),
            "total_tx": sum(h["tx_count"] for h in self.history),
        }
    
    def check_alert(self, threshold: float) -> Optional[Dict]:
        """Check if current gas is below alert threshold."""
        current = self.get_current_gas()
        if current["gas_price"] <= threshold:
            return {
                "alert": True,
                "message": f"🟢 Gas is LOW: {current['gas_price']} {GAS_UNIT} (threshold: {threshold})",
                "current_gas": current["gas_price"],
                "threshold": threshold,
            }
        else:
            return {
                "alert": False,
                "message": f"🔴 Gas is HIGH: {current['gas_price']} {GAS_UNIT} (threshold: {threshold})",
                "current_gas": current["gas_price"],
                "threshold": threshold,
            }
    
    def estimate_tx_cost(self, gas_limit: int = 21000) -> Dict:
        """Estimate transaction cost at current gas prices."""
        current = self.get_current_gas()
        gas_price = current["gas_price"]
        
        # Standard transfer, contract interaction, complex contract
        estimates = {
            "simple_transfer": {
                "gas_limit": 21000,
                "cost_nRUST": round(21000 * gas_price, 2),
                "cost_RUST": round(21000 * gas_price / 1e9, 9),
            },
            "token_transfer": {
                "gas_limit": 65000,
                "cost_nRUST": round(65000 * gas_price, 2),
                "cost_RUST": round(65000 * gas_price / 1e9, 9),
            },
            "swap": {
                "gas_limit": 200000,
                "cost_nRUST": round(200000 * gas_price, 2),
                "cost_RUST": round(200000 * gas_price / 1e9, 9),
            },
            "contract_deploy": {
                "gas_limit": 1500000,
                "cost_nRUST": round(1500000 * gas_price, 2),
                "cost_RUST": round(1500000 * gas_price / 1e9, 9),
            },
        }
        return estimates


def render_ascii_chart(data: List[Dict], width: int = 60, height: int = 15) -> str:
    """Render an ASCII chart of gas prices."""
    prices = [d["gas_price"] for d in data]
    if not prices:
        return "No data"
    
    min_p = min(prices)
    max_p = max(prices)
    range_p = max_p - min_p or 1
    
    # Reverse so oldest is on the left
    prices = list(reversed(prices))
    
    lines = []
    for row in range(height, 0, -1):
        threshold = min_p + (range_p * row / height)
        line = f"{threshold:6.1f} │"
        for p in prices:
            normalized = (p - min_p) / range_p * height
            if normalized >= row - 0.5 and normalized < row + 0.5:
                line += "█"
            elif normalized >= row:
                line += "│"
            else:
                line += " "
        lines.append(line)
    
    # X-axis
    lines.append(f"       └{'─' * len(prices)}")
    lines.append(f"        {'↑ oldest':<{len(prices)//2}}{'newest →':>{len(prices)//2}}")
    
    lines.insert(0, f"  Gas Price Chart ({data[-1]['gas_price']:.1f} ← most recent)")
    lines.insert(1, f"  Range: {min_p:.1f} - {max_p:.1f} {GAS_UNIT}")
    lines.insert(2, "")
    
    return "\n".join(lines)


def format_gas_table(data: List[Dict]) -> str:
    """Format gas history as a table."""
    lines = []
    lines.append(f"{'Block':<12} {'Gas Price':>10} {'Utilization':>12} {'TXs':>6} {'Time':>20}")
    lines.append("─" * 62)
    for d in data:
        ts = datetime.fromtimestamp(d["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        util = round(d["gas_used"] / d["gas_limit"] * 100, 1)
        lines.append(f"{d['block']:<12} {d['gas_price']:>8.2f} {GAS_UNIT:>0} {util:>10.1f}% {d['tx_count']:>6} {ts:>20}")
    return "\n".join(lines)


def format_predictions(predictions: List[Dict]) -> str:
    """Format gas predictions."""
    lines = []
    lines.append(f"{'Block':<12} {'Predicted Gas':>14} {'Confidence':>12} {'Time':>20}")
    lines.append("─" * 60)
    for p in predictions:
        ts = datetime.fromtimestamp(p["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        conf_bar = "█" * int(p["confidence"] * 10) + "░" * (10 - int(p["confidence"] * 10))
        lines.append(f"{p['block']:<12} {p['predicted_gas']:>10.2f} {GAS_UNIT:>0} {conf_bar} {p['confidence']:>5.0%} {ts:>20}")
    return "\n".join(lines)


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain Gas Fee Tracker & Predictor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gas.py                     Show current gas price
  python gas.py --history 50        Show last 50 blocks
  python gas.py --predict 10        Predict next 10 blocks
  python gas.py --chart             ASCII gas chart
  python gas.py --alert 25          Alert when gas < 25 nRUST
  python gas.py --wallet zp6        Wallet gas spending
  python gas.py --stats             Gas statistics
  python gas.py --estimate          Estimate tx costs
        """
    )
    parser.add_argument("--history", type=int, metavar="N", help="Show gas history for N blocks")
    parser.add_argument("--predict", type=int, metavar="N", help="Predict gas for N blocks")
    parser.add_argument("--chart", action="store_true", help="Display ASCII gas chart")
    parser.add_argument("--alert", type=float, metavar="PRICE", help="Alert when gas drops below threshold")
    parser.add_argument("--wallet", type=str, metavar="ADDR", help="Show gas spending for wallet")
    parser.add_argument("--stats", action="store_true", help="Show gas statistics")
    parser.add_argument("--estimate", action="store_true", help="Estimate transaction costs")
    parser.add_argument("--best-time", action="store_true", help="Find best time to transact")
    
    args = parser.parse_args()
    tracker = GasTracker()
    
    # If no args, show current gas
    if not any(vars(args).values()):
        args.stats = True
    
    print()
    print("⛽ RustChain Gas Fee Tracker")
    print("=" * 50)
    
    if args.stats:
        current = tracker.get_current_gas()
        stats = tracker.get_gas_stats()
        
        print(f"\n📊 Current Gas Price: {current['gas_price']:.2f} {GAS_UNIT}")
        print(f"   Block: #{current['block']}")
        print(f"   Network Utilization: {current['network_utilization']:.1f}%")
        print(f"   TXs in Block: {current['tx_count']}")
        print(f"\n📈 Last {stats['period_blocks']} Blocks:")
        print(f"   Average: {stats['avg_gas']:.2f} {GAS_UNIT}")
        print(f"   Median:  {stats['median_gas']:.2f} {GAS_UNIT}")
        print(f"   Min:     {stats['min_gas']:.2f} {GAS_UNIT}")
        print(f"   Max:     {stats['max_gas']:.2f} {GAS_UNIT}")
        print(f"   Std Dev: {stats['std_dev']:.2f}")
        print(f"   Avg Utilization: {stats['avg_utilization']:.1f}%")
        print(f"   Total TXs: {stats['total_tx']}")
    
    if args.history:
        data = tracker.get_history(args.history)
        print(f"\n📜 Gas History (last {args.history} blocks):")
        print(format_gas_table(data))
    
    if args.predict:
        preds = tracker.predict_gas(args.predict)
        print(f"\n🔮 Gas Predictions (next {args.predict} blocks):")
        print(format_predictions(preds))
        
        avg_pred = sum(p["predicted_gas"] for p in preds) / len(preds)
        current = tracker.get_current_gas()
        if avg_pred < current["gas_price"]:
            print(f"\n💡 Gas is trending DOWN. Consider waiting for lower fees.")
        else:
            print(f"\n⚠️  Gas is trending UP. Consider transacting now.")
    
    if args.chart:
        data = tracker.get_history(60)
        print(f"\n{render_ascii_chart(data)}")
    
    if args.alert:
        alert = tracker.check_alert(args.alert)
        print(f"\n🔔 Alert Check (threshold: {args.alert} {GAS_UNIT}):")
        print(f"   {alert['message']}")
        if alert["alert"]:
            print(f"   ✅ Good time to submit transactions!")
        else:
            print(f"   ⏳ Consider waiting for gas to drop.")
    
    if args.wallet:
        spending = _generate_wallet_gas_spent(args.wallet)
        print(f"\n💼 Gas Spending for Wallet: {args.wallet}")
        print(f"{'Date':<12} {'TXs':>5} {'Gas Spent (RUST)':>18} {'Avg Gas Price':>14}")
        print("─" * 52)
        total_spent = 0
        for s in spending:
            total_spent += s["gas_spent"]
            print(f"{s['date']:<12} {s['tx_count']:>5} {s['gas_spent']:>18.6f} {s['avg_gas_price']:>12.2f} {GAS_UNIT}")
        print("─" * 52)
        print(f"{'Total':.<12} {sum(s['tx_count'] for s in spending):>5} {total_spent:>18.6f}")
    
    if args.estimate:
        estimates = tracker.estimate_tx_cost()
        current = tracker.get_current_gas()
        print(f"\n💰 Estimated TX Costs (gas price: {current['gas_price']:.2f} {GAS_UNIT}):")
        print(f"{'TX Type':<20} {'Gas Limit':>10} {'Cost (nRUST)':>15} {'Cost (RUST)':>15}")
        print("─" * 62)
        for name, est in estimates.items():
            print(f"{name:<20} {est['gas_limit']:>10,} {est['cost_nRUST']:>15,.2f} {est['cost_RUST']:>15.9f}")
    
    if args.best_time:
        window = tracker.get_best_time_window()
        print(f"\n🕐 Best Time to Transact:")
        print(f"   Best hour (UTC):  {window['best_hour_utc']} — avg {window['best_avg_gas']:.2f} {GAS_UNIT}")
        print(f"   Worst hour (UTC): {window['worst_hour_utc']} — avg {window['worst_avg_gas']:.2f} {GAS_UNIT}")
        savings = (1 - window['best_avg_gas'] / window['worst_avg_gas']) * 100
        print(f"   Potential savings: {savings:.1f}%")
        print(f"\n   Hourly Averages:")
        for hour, avg in window['hourly_averages'].items():
            bar = "█" * int(avg / 2)
            print(f"   {hour:02d}:00  {avg:>6.2f}  {bar}")
    
    print()


if __name__ == "__main__":
    main()
