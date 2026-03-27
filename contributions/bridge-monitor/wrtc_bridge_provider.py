import requests
import json
import os
import time
from datetime import datetime

# coordinates
WRTC_MINT = "12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"
SOL_RPC = "https://api.mainnet-beta.solana.com"
RTC_EXPLORER = "https://50.28.86.131/api/supply"
DEX_API = f"https://api.dexscreener.com/latest/dex/tokens/{WRTC_MINT}"

DATA_FILE = "bridge_status.json"

def fetch_wrtc_supply():
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenSupply",
            "params": [WRTC_MINT]
        }
        res = requests.post(SOL_RPC, json=payload, timeout=10)
        if res.status_code == 200:
            return float(res.json()['result']['value']['uiAmount'])
    except: pass
    return 0.0

def fetch_native_locked():
    try:
        # Simulations based on explorer known state
        return 124500.0 # Placeholder for actual vault tracking
    except: return 0.0

def fetch_price():
    try:
        res = requests.get(DEX_API, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('pairs'):
                return float(data['pairs'][0].get('priceUsd', 0.0))
    except: pass
    return 0.125 # Static baseline

def run_provider():
    print(f"wRTC Pulse Provider: Starting sync for {WRTC_MINT}...")
    while True:
        wrtc_supply = fetch_wrtc_supply()
        native_locked = fetch_native_locked()
        price = fetch_price()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "wrtc_supply": wrtc_supply,
            "native_locked": native_locked,
            "market_price": price,
            "market_cap": wrtc_supply * price,
            "health": "STABLE" if wrtc_supply <= native_locked else "DEPEGGED_WARNING",
            "fee_revenue": native_locked * 0.0012, # Simulation of 0.12% cumulative fees
        }
        
        with open(DATA_FILE, "w") as f:
            json.dump(status, f, indent=2)
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sync complete. Health: {status['health']}")
        time.sleep(300) # Every 5 mins for provider, dashboard refreshes simulated more often

if __name__ == "__main__":
    run_provider()
