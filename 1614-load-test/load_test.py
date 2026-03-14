#!/usr/bin/env python3
"""
Load Test Suite for RustChain API
Tests API endpoints under various load conditions
"""

import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median, stdev

# Configuration
API_BASE_URL = "https://api.rustchain.com"
RPC_URL = "https://rpc.rustchain.com"

# Test addresses (example)
TEST_ADDRESSES = [
    "RTC1234567890abcdef1234567890abcdef12345678",
    "RTCabcdef1234567890abcdef1234567890abcdef12",
]

# Test transaction hashes
TEST_TX_HASHES = [
    "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
]


def rpc_call(method, params):
    """Make JSON-RPC call"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    start = time.time()
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        latency = time.time() - start
        return response.json().get("result"), latency
    except Exception as e:
        return None, time.time() - start


def test_get_balance():
    """Test eth_getBalance endpoint"""
    address = random.choice(TEST_ADDRESSES)
    result, latency = rpc_call("eth_getBalance", [address, "latest"])
    return "balance", latency, result is not None


def test_get_block_number():
    """Test eth_blockNumber endpoint"""
    result, latency = rpc_call("eth_blockNumber", [])
    return "block_number", latency, result is not None


def test_get_transaction():
    """Test eth_getTransactionByHash endpoint"""
    tx_hash = random.choice(TEST_TX_HASHES)
    result, latency = rpc_call("eth_getTransactionByHash", [tx_hash])
    return "transaction", latency, result is not None


def test_chain_id():
    """Test eth_chainId endpoint"""
    result, latency = rpc_call("eth_chainId", [])
    return "chain_id", latency, result is not None


def run_load_test(num_requests=100, concurrent_users=10):
    """Run load test with specified parameters"""
    tests = [
        test_get_balance,
        test_get_block_number,
        test_get_transaction,
        test_chain_id,
    ]
    
    results = {
        "balance": [],
        "block_number": [],
        "transaction": [],
        "chain_id": [],
    }
    
    def run_test(test_func):
        result = test_func()
        test_name, latency, success = result
        if success:
            results[test_name].append(latency)
        return success
    
    print(f"🚀 Starting load test: {num_requests} requests, {concurrent_users} concurrent users")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for i in range(num_requests):
            test_func = random.choice(tests)
            futures.append(executor.submit(run_test, test_func))
        
        completed = sum(1 for f in futures if f.result())
    
    total_time = time.time() - start_time
    
    # Calculate statistics
    all_latencies = []
    for latencies in results.values():
        all_latencies.extend(latencies)
    
    print(f"\n✅ Load Test Complete!")
    print(f"📊 Total requests: {num_requests}")
    print(f"✅ Successful: {completed}")
    print(f"❌ Failed: {num_requests - completed}")
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📈 Requests/sec: {num_requests / total_time:.2f}")
    
    if all_latencies:
        print(f"\n⏱️  Latency Statistics:")
        print(f"   Min: {min(all_latencies)*1000:.2f}ms")
        print(f"   Max: {max(all_latencies)*1000:.2f}ms")
        print(f"   Mean: {mean(all_latencies)*1000:.2f}ms")
        print(f"   Median: {median(all_latencies)*1000:.2f}ms")
        if len(all_latencies) > 1:
            print(f"   Std Dev: {stdev(all_latencies)*1000:.2f}ms")
    
    return {
        "total_requests": num_requests,
        "successful": completed,
        "failed": num_requests - completed,
        "total_time": total_time,
        "requests_per_second": num_requests / total_time,
        "latency_stats": {
            "min": min(all_latencies) if all_latencies else 0,
            "max": max(all_latencies) if all_latencies else 0,
            "mean": mean(all_latencies) if all_latencies else 0,
            "median": median(all_latencies) if all_latencies else 0,
        }
    }


if __name__ == "__main__":
    # Run load test
    results = run_load_test(num_requests=100, concurrent_users=10)
    
    # You can also run heavier tests:
    # run_load_test(num_requests=1000, concurrent_users=50)
    # run_load_test(num_requests=5000, concurrent_users=100)
