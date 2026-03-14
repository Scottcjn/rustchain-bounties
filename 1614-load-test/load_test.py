#!/usr/bin/env python3
"""
RustChain API Load Test Suite
Tests the RustChain JSON-RPC API endpoints under load using Locust.
"""

import os
import random
from locust import HttpUser, task, between, events

RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.com")

TEST_ADDRESSES = [
    "0x0000000000000000000000000000000000000001",
    "0x0000000000000000000000000000000000000002",
    "0x742d35Cc6634C0532925a3b844Bc9e7595f0eB1",
    "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
    "0xdD870fA1b7C4700F2BD7f44238821C26f7392148",
]

SAMPLE_TX_HASH = "0x0000000000000000000000000000000000000000000000000000000000000000"


def make_jsonrpc_request(method, params):
    return {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(1, 1000000),
    }


class RustChainUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.client.headers.update({"Content-Type": "application/json"})

    @task(5)
    def eth_block_number(self):
        payload = make_jsonrpc_request("eth_blockNumber", [])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(4)
    def eth_get_block_by_number(self):
        payload = make_jsonrpc_request("eth_blockNumber", [])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
                return

            try:
                data = response.json()
                block_num = data.get("result")
                if not block_num:
                    response.failure("No block number in response")
                    return
            except Exception as e:
                response.failure(f"Failed to parse block number: {e}")
                return

        payload = make_jsonrpc_request("eth_getBlockByNumber", [block_num, False])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(3)
    def eth_get_balance(self):
        address = random.choice(TEST_ADDRESSES)
        payload = make_jsonrpc_request("eth_getBalance", [address, "latest"])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def eth_gas_price(self):
        payload = make_jsonrpc_request("eth_gasPrice", [])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def eth_chain_id(self):
        payload = make_jsonrpc_request("eth_chainId", [])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def eth_get_transaction_by_hash(self):
        payload = make_jsonrpc_request("eth_getTransactionByHash", [SAMPLE_TX_HASH])
        with self.client.post(RPC_URL, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "result" in data:
                        response.success()
                    else:
                        response.failure(f"No result in response: {data}")
                except Exception as e:
                    response.failure(f"Invalid JSON: {e}")
            else:
                response.failure(f"HTTP {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print(f"Load test starting against {RPC_URL}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test completed")
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
