"""
RustChain API Load Test Suite
Uses Locust for load testing with comprehensive scenarios.

Usage:
    locust -f locustfile.py --host=http://localhost:8545
    locust -f locustfile.py --host=http://localhost:8545 --headless -u 100 -r 10 -t 300s
"""

import random
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner


class RustChainUser(HttpUser):
    """Simulated RustChain API user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts."""
        self.wallets = [
            f"wallet_{i}" for i in range(10)
        ]
        self.current_wallet = random.choice(self.wallets)
    
    @task(3)
    def get_balance(self):
        """Test balance endpoint - high frequency."""
        wallet = random.choice(self.wallets)
        with self.client.get(f"/api/v1/balance/{wallet}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # Wallet might not exist yet
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_epoch_info(self):
        """Test epoch info endpoint - medium frequency."""
        with self.client.get("/api/v1/epoch/current", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "epoch" in data:
                    response.success()
                else:
                    response.failure("Missing epoch field")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(2)
    def get_miner_stats(self):
        """Test miner stats endpoint - medium frequency."""
        with self.client.get("/api/v1/miners/stats", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def submit_attestation(self):
        """Test attestation submission - low frequency (expensive operation)."""
        payload = {
            "wallet": self.current_wallet,
            "epoch": random.randint(1000, 2000),
            "proof": f"proof_{random.randint(10000, 99999)}",
            "timestamp": int(time.time())
        }
        with self.client.post("/api/v1/attest/submit", json=payload, catch_response=True) as response:
            if response.status_code in [200, 201, 400]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def get_network_status(self):
        """Test network status endpoint - low frequency."""
        with self.client.get("/api/v1/network/status", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test health check endpoint - low frequency."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class HeavyLoadUser(HttpUser):
    """Heavy load user for stress testing."""
    
    wait_time = between(0.1, 0.5)  # Very short wait for stress testing
    
    @task
    def rapid_balance_check(self):
        """Rapid balance checks."""
        wallet = f"stress_test_{random.randint(1, 1000)}"
        self.client.get(f"/api/v1/balance/{wallet}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("🚀 RustChain Load Test Starting...")
    print(f"Target: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    print("✅ RustChain Load Test Completed!")
    if environment.stats.total.num_requests > 0:
        print(f"Total Requests: {environment.stats.total.num_requests}")
        print(f"Failed Requests: {environment.stats.total.num_failures}")
        print(f"Average Response Time: {environment.stats.total.avg_response_time:.2f}ms")


# Configuration for running without web UI
if __name__ == "__main__":
    import os
    os.system("locust -f locustfile.py --headless -u 100 -r 10 -t 300s")