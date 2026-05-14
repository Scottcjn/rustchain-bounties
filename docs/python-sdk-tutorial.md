# RustChain Python SDK Tutorial

Quick guide to integrate with the RustChain node API using Python.

## Setup

```bash
pip install requests
```

## Connection

```python
import requests
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://50.28.86.131"

def api_get(path):
    """Make a GET request to the RustChain node."""
    resp = requests.get(f"{BASE_URL}{path}", verify=False)
    resp.raise_for_status()
    return resp.json()
```

## Health Check

```python
health = api_get("/health")
print(f"Node status: {'OK' if health['ok'] else 'DOWN'}")
print(f"Version: {health['version']}")
print(f"Uptime: {health['uptime_s']} seconds")
print(f"DB read/write: {health['db_rw']}")
```

## Network Statistics

```python
stats = api_get("/api/stats")
print(f"Current epoch: {stats['epoch']}")
print(f"Total miners: {stats['total_miners']}")
print(f"Block time: {stats['block_time']}s")
print(f"Chain ID: {stats['chain_id']}")
print(f"Active features: {', '.join(stats['features'])}")
```

## Epoch Information

```python
epoch = api_get("/epoch")
print(f"Epoch: {epoch['epoch']}")
print(f"Slot: {epoch['slot']}")
print(f"Blocks per epoch: {epoch['blocks_per_epoch']}")
print(f"Epoch reward pot: {epoch['epoch_pot']} RTC")
print(f"Enrolled miners: {epoch['enrolled_miners']}")
print(f"Total supply: {epoch['total_supply_rtc']} RTC")
```

## Check Balance

```python
MINER_ID = "your_miner_id"

balance = api_get(f"/balance/{MINER_ID}")
print(f"Balance for {MINER_ID}: {balance}")
```

## Complete Example: Dashboard Monitor

```python
import time

def show_dashboard():
    health = api_get("/health")
    stats = api_get("/api/stats")
    epoch = api_get("/epoch")

    print("=" * 50)
    print(f"  RustChain Dashboard")
    print("=" * 50)
    print(f"  Node: {'ONLINE' if health['ok'] else 'OFFLINE'}")
    print(f"  Version: {health['version']}")
    print(f"  Uptime: {health['uptime_s'] / 3600:.1f} hours")
    print(f"  Epoch: {epoch['epoch']}")
    print(f"  Slot: {epoch['slot']}")
    print(f"  Reward pot: {epoch['epoch_pot']} RTC")
    print(f"  Enrolled miners: {epoch['enrolled_miners']}")
    print(f"  Total miners: {stats['total_miners']}")
    print(f"  Total supply: {epoch['total_supply_rtc']} RTC")
    print("=" * 50)

if __name__ == "__main__":
    show_dashboard()
```

## API Field Reference

All field names below are verified against the live node (v2.2.1-rip200):

| Endpoint | Key Fields |
|----------|-----------|
| `/health` | `ok`, `uptime_s`, `version`, `db_rw`, `backup_age_hours`, `tip_age_slots` |
| `/api/stats` | `epoch`, `total_miners`, `block_time`, `chain_id`, `total_balance` |
| `/epoch` | `epoch`, `slot`, `blocks_per_epoch`, `epoch_pot`, `enrolled_miners`, `total_supply_rtc` |

For the full API including attestation and withdrawal endpoints, see [API_REFERENCE.md](./API_REFERENCE.md).
