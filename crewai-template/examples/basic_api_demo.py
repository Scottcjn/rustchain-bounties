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
    
    # 5. BoTTube API Usage
    print("\n5. Testing BoTTube API...")
    try:
        # Developer Links
        print("   Developer Docs: https://bottube.ai/docs")
        print("   Setup: Get API key at https://bottube.ai/settings/api")
        
        # Health Check
        bt_health = bt.health()
        print(f"   Health: {bt_health}")
        
        # Stats
        stats = bt.get_stats()
        print(f"   Stats: {stats}")
        
        # Videos
        videos = bt.videos(limit=2)
        print(f"   Videos (latest {len(videos)}):")
        for v in videos:
            print(f"     - {v.get('title', 'Untitled')} ({v.get('id')})")
            
        # Feed
        feed = bt.feed(limit=2)
        print(f"   Feed (latest {len(feed)}):")
        for f in feed:
            print(f"     - {f.get('title', 'Untitled')} ({f.get('id')})")
            
    except Exception as e:
        print(f"   (BoTTube API not available: {e})")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
