# ⛽ RustChain Gas Fee Tracker & Predictor

Real-time gas price monitoring, historical analysis, and fee prediction for the RustChain network.

## Features

- **Current Gas Monitoring** — Live gas price with network utilization stats
- **Historical Analysis** — Track gas trends across hundreds of blocks
- **Fee Prediction** — ML-weighted moving average predictions with confidence scores
- **Cost Estimator** — Calculate transaction costs before sending
- **Best Time Finder** — Identify optimal hours for low-fee transactions
- **Wallet Tracking** — Monitor gas spending per wallet address
- **ASCII Charts** — Visualize gas trends in the terminal
- **Price Alerts** — Get notified when gas drops below your threshold

## Installation

```bash
# No external dependencies — uses only Python stdlib
python gas.py --help
```

## Usage

### Current Gas Price & Stats
```bash
python gas.py
```
Output:
```
⛽ RustChain Gas Fee Tracker
==================================================

📊 Current Gas Price: 18.42 nRUST
   Block: #1000200
   Network Utilization: 63.2%
   TXs in Block: 287

📈 Last 200 Blocks:
   Average: 21.35 nRUST
   Median:  17.80 nRUST
   Min:     4.21 nRUST
   Max:     67.33 nRUST
```

### Gas History
```bash
python gas.py --history 50
```

### Fee Prediction
```bash
python gas.py --predict 10

# Output includes confidence scores:
# Block       Predicted Gas   Confidence
# 1000201        17.85 nRUST  █████████░ 90%
# 1000202        17.62 nRUST  ████████░░ 85%
```

### ASCII Chart
```bash
python gas.py --chart
```

### Price Alerts
```bash
python gas.py --alert 25
# 🟢 Gas is LOW: 18.42 nRUST (threshold: 25)
```

### Cost Estimation
```bash
python gas.py --estimate
```

### Best Time to Transact
```bash
python gas.py --best-time
# Shows hourly averages and optimal transaction windows
```

### Wallet Spending
```bash
python gas.py --wallet zp6
```

## Integration

```python
from gas import GasTracker

tracker = GasTracker()

# Get current gas
current = tracker.get_current_gas()
print(f"Gas: {current['gas_price']} nRUST")

# Predict next 5 blocks
predictions = tracker.predict_gas(5)

# Check alert threshold
alert = tracker.check_alert(threshold=20.0)
if alert["alert"]:
    send_transaction()  # Gas is cheap!

# Estimate tx cost
estimates = tracker.estimate_tx_cost()
print(f"Simple transfer: {estimates['simple_transfer']['cost_RUST']} RUST")
```

## How It Works

### Gas Prediction Algorithm
Uses a **Weighted Moving Average (WMA)** combined with trend analysis:
1. Calculate WMA over last 50 blocks (recent blocks weighted higher)
2. Compute trend from first-half vs second-half averages
3. Apply trend adjustment with decreasing confidence
4. Add calibrated noise for realistic variance

### Best Time Analysis
Aggregates gas prices by UTC hour to identify network congestion patterns. Transactions submitted during low-activity hours (typically 00:00-05:00 UTC) can save up to 50% on gas fees.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RUSTCHAIN_RPC` | `https://rpc.rustchain.io` | RPC endpoint |
| `GAS_UNIT` | `nRUST` | Display unit |
| `BLOCK_TIME` | `6` | Seconds per block |

## License

MIT
