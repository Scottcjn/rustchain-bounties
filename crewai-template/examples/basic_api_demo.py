#!/usr/bin/env python3
"""
Basic API Demo - Demonstrates RustChain and BoTTube API usage
"""

import sys
sys.path.insert(0, '.')

from rustchain_client import RustChainClient, BoTTubeClient


def main():
    print("=" * 60)
    print("RustChain API Demo")
    print("=" * 60)
    
    # Initialize clients
    rc = RustChainClient()
    bt = BoTTubeClient()
    
    # 1. Health Check
    print("\n1. Checking node health...")
    health = rc.health()
    print(f"   OK: {health.get('ok')}")
    print(f"   Version: {health.get('version')}")
    print(f"   Uptime: {health.get('uptime_s', 0) / 3600:.1f} hours")
    
    # 2. Epoch Info
    print("\n2. Getting epoch info...")
    epoch = rc.get_epoch()
    print(f"   Epoch: {epoch.get('epoch')}")
    print(f"   Slot: {epoch.get('slot')}")
    print(f"   Blocks/Epoch: {epoch.get('blocks_per_epoch')}")
    print(f"   Total Supply: {epoch.get('total_supply_rtc'):,} RTC")
    print(f"   Epoch POT: {epoch.get('epoch_pot')} RTC")
    
    # 3. Miners
    print("\n3. Listing active miners...")
    miners = rc.get_miners()
    print(f"   Active miners: {len(miners)}")
    for m in miners[:3]:
        print(f"   - {m.get('miner')}: {m.get('hardware_type')} ({m.get('device_arch')})")
    
    # 4. Balance (example wallet)
    print("\n4. Checking balance...")
    balance = rc.get_balance("aric-saxp-alpha")
    print(f"   Wallet: aric-saxp-alpha")
    print(f"   Balance: {balance}")
    
    # 5. BoTTube Stats
    print("\n5. Getting BoTTube stats...")
    try:
        stats = bt.get_stats()
        print(f"   Stats: {stats}")
    except Exception as e:
        print(f"   (BoTTube API not available: {e})")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
