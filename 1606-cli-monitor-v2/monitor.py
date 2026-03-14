#!/usr/bin/env python3
"""RustChain Node Health Monitor CLI"""
import argparse, requests, sys
from datetime import datetime

DEFAULT_RPC_URL = "https://rpc.rustchain.com"

def rpc_call(rpc_url, method, params=None):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("result")
    except Exception as e:
        return {"error": str(e)}

def check_node_health(rpc_url):
    print(f"\n🔍 Checking node health at {rpc_url}...\n")
    block_num = rpc_call(rpc_url, "eth_blockNumber")
    if not block_num or "error" in str(block_num):
        print("❌ Node is not responding!")
        return False
    block_int = int(block_num, 16)
    print(f"✅ Node Status: ONLINE")
    print(f"📦 Latest Block: #{block_int:,}")
    chain_id = rpc_call(rpc_url, "eth_chainId")
    if chain_id:
        print(f"🔗 Chain ID: {int(chain_id, 16)}")
    gas_price = rpc_call(rpc_url, "eth_gasPrice")
    if gas_price:
        gas_gwei = int(gas_price, 16) / 1e9
        print(f"⛽ Gas Price: {gas_gwei:.2f} Gwei")
    peer_count = rpc_call(rpc_url, "net_peerCount")
    if peer_count:
        peers = int(peer_count, 16)
        status = "✅ Good" if peers >= 5 else "⚠️ Low"
        print(f"👥 Peer Count: {peers} {status}")
    syncing = rpc_call(rpc_url, "eth_syncing")
    if syncing and syncing != False:
        print(f"🔄 Sync Status: SYNCING")
    else:
        print(f"✅ Sync Status: SYNCED")
    print(f"\n⏰ Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return True

def main():
    parser = argparse.ArgumentParser(description="RustChain Node Health Monitor")
    parser.add_argument("--rpc", default=DEFAULT_RPC_URL, help="RPC URL")
    parser.add_argument("--balance", metavar="ADDRESS", help="Check balance for address")
    parser.add_argument("--block", type=int, metavar="NUM", help="Get block details")
    args = parser.parse_args()
    check_node_health(args.rpc)

if __name__ == "__main__":
    main()
