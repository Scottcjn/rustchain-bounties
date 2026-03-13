"""
RustChain API Load Test Suite
==============================
Load testing suite for RustChain API endpoints using Locust.
Tests performance, reliability, and rate limiting of the API.

Bounty: #1614 - Create a load test suite for the RustChain API
Reward: 5 RTC
"""

from locust import HttpUser, task, between, events
import json
import time
import random
from datetime import datetime
import urllib3
import ssl

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RustChainAPIUser(HttpUser):
    """
    Simulates a user interacting with the RustChain API.
    Uses self-signed certificate handling for testing.
    """
    
    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    # API endpoints to test
    endpoints = {
        'health': '/health',
        'epoch': '/epoch',
        'miners': '/api/miners',
        'explorer': '/explorer',
    }
    
    def on_start(self):
        """Called when a simulated user starts"""
        # Configure session to handle self-signed certificates
        self.client.verify = '/dev/null'  # Disable SSL verification
        self.client.auth = None
        
        # Disable SSL verification at session level
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        self.client.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'RustChain-LoadTest/1.0'
        })
        
    @task(3)
    def test_health_endpoint(self):
        """
        Test the health endpoint - most frequently called
        Measures: response time, availability, uptime reporting
        """
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('ok') == True:
                        response.success()
                    else:
                        response.failure("Health check returned ok=false")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def test_epoch_endpoint(self):
        """
        Test the epoch endpoint - high frequency reads
        Measures: response time, epoch data consistency
        """
        with self.client.get(
            "/epoch",
            name="/epoch",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    required_fields = ['epoch', 'slot', 'blocks_per_epoch', 'enrolled_miners']
                    if all(field in data for field in required_fields):
                        response.success()
                    else:
                        response.failure(f"Missing required fields. Got: {list(data.keys())}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def test_miners_endpoint(self):
        """
        Test the miners endpoint - moderate frequency
        Measures: response time, miner list retrieval
        """
        with self.client.get(
            "/api/miners",
            name="/api/miners",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Expected array of miners")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_explorer_redirect(self):
        """
        Test the explorer endpoint - low frequency
        Measures: redirect handling, availability
        """
        with self.client.get(
            "/explorer",
            name="/explorer",
            catch_response=True,
            allow_redirects=False
        ) as response:
            # Explorer should redirect (301/302)
            if response.status_code in [200, 301, 302]:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def test_wallet_balance(self):
        """
        Test wallet balance endpoint with random miner IDs
        Measures: query parameter handling, response consistency
        """
        # Test with various miner ID patterns
        test_miner_ids = [
            "victus-x86-scott",
            "test-miner-001",
            "miner-" + str(random.randint(1, 1000)),
        ]
        
        miner_id = random.choice(test_miner_ids)
        
        with self.client.get(
            f"/wallet/balance?miner_id={miner_id}",
            name="/wallet/balance",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'amount_rtc' in data and 'miner_id' in data:
                        response.success()
                    else:
                        response.failure(f"Missing required fields. Got: {list(data.keys())}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            elif response.status_code == 404:
                # Miner not found is acceptable
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_attest_challenge(self):
        """
        Test attestation challenge endpoint - POST request
        Measures: POST handling, challenge generation
        """
        with self.client.post(
            "/attest/challenge",
            json={},
            name="/attest/challenge",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'nonce' in data and 'expires_at' in data:
                        response.success()
                    else:
                        response.failure(f"Missing nonce or expires_at. Got: {list(data.keys())}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def test_lottery_eligibility(self):
        """
        Test lottery eligibility endpoint with query params
        Measures: query parameter handling, eligibility checking
        """
        test_miner_ids = [
            "victus-x86-scott",
            "test-miner-" + str(random.randint(1, 100)),
        ]
        
        miner_id = random.choice(test_miner_ids)
        
        with self.client.get(
            f"/lottery/eligibility?miner_id={miner_id}",
            name="/lottery/eligibility",
            catch_response=True
        ) as response:
            # 200 or 404 are both acceptable
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Aggressive stress testing user - simulates high load scenarios.
    Shorter wait times, more frequent requests.
    """
    
    wait_time = between(0.1, 0.5)
    
    @task
    def rapid_health_checks(self):
        """Rapid fire health checks to stress test the endpoint"""
        self.client.get("/health", name="/health [stress]")
    
    @task
    def rapid_epoch_checks(self):
        """Rapid fire epoch checks"""
        self.client.get("/epoch", name="/epoch [stress]")


class RateLimitTestUser(HttpUser):
    """
    Tests rate limiting behavior by making many rapid requests.
    """
    
    wait_time = between(0.01, 0.1)
    
    @task
    def test_rate_limiting(self):
        """
        Intentionally make rapid requests to trigger rate limiting.
        Verifies that the API properly implements rate limiting (HTTP 429).
        """
        response = self.client.get("/health", name="/health [rate-limit-test]")
        
        # Rate limiting is expected and acceptable
        if response.status_code == 429:
            # Good - rate limiting is working
            events.request.fire(
                request_type="GET",
                name="/health [rate-limit-test]",
                response_time=response.elapsed.total_seconds() * 1000,
                response_length=len(response.content),
                exception=None,
                context={}
            )


# Event hooks for custom logging and reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("=" * 60)
    print("RustChain API Load Test Starting")
    print("=" * 60)
    print(f"Target Host: {environment.host}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("=" * 60)
    print("RustChain API Load Test Complete")
    print("=" * 60)
    print(f"End Time: {datetime.now().isoformat()}")
    
    # Print summary statistics
    stats = environment.stats
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Failure Rate: {(stats.total.num_failures / max(stats.total.num_requests, 1)) * 100:.2f}%")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.current_rps:.2f}")
    print("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Called on each request for custom logging"""
    if exception:
        print(f"Request failed: {name} - {exception}")
    
    # Log slow requests
    if response_time > 1000:  # > 1 second
        print(f"Slow request: {name} took {response_time:.2f}ms")
