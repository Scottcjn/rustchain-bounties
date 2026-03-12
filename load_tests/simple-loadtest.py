"""
RustChain API Load Test Suite - Simple Version
===============================================
Simple load test script that properly handles self-signed certificates.
Run this for quick API performance testing.

Usage:
    python simple-loadtest.py
"""

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import ssl
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Configuration
BASE_URL = "https://50.28.86.131"
REQUESTS_PER_ENDPOINT = 10
CONCURRENT_USERS = 5

# Endpoints to test
ENDPOINTS = {
    'health': '/health',
    'epoch': '/epoch',
    'miners': '/api/miners',
    'wallet': '/wallet/balance?miner_id=test-miner',
    'attest': '/attest/challenge',
}


def make_request(endpoint_name, endpoint_path, session):
    """Make a single request and return timing info"""
    try:
        start_time = time.time()
        
        if endpoint_name == 'attest':
            response = session.post(
                f"{BASE_URL}{endpoint_path}",
                json={},
                verify=False,
                timeout=10
            )
        else:
            response = session.get(
                f"{BASE_URL}{endpoint_path}",
                verify=False,
                timeout=10
            )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return {
            'endpoint': endpoint_name,
            'success': response.status_code in [200, 404],
            'status_code': response.status_code,
            'response_time_ms': elapsed_ms,
            'error': None
        }
    except Exception as e:
        return {
            'endpoint': endpoint_name,
            'success': False,
            'status_code': 0,
            'response_time_ms': 0,
            'error': str(e)
        }


def test_endpoint(endpoint_name, endpoint_path, num_requests=REQUESTS_PER_ENDPOINT):
    """Test a single endpoint with multiple requests"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'RustChain-SimpleLoadTest/1.0'
    })
    
    results = []
    print(f"\nTesting {endpoint_name} ({endpoint_path})...")
    
    for i in range(num_requests):
        result = make_request(endpoint_name, endpoint_path, session)
        results.append(result)
        
        if result['success']:
            print(f"  [OK] Request {i+1}/{num_requests}: {result['response_time_ms']:.2f}ms (HTTP {result['status_code']})")
        else:
            print(f"  [FAIL] Request {i+1}/{num_requests}: {result['error'] or f'HTTP {result['status_code']}'}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    return results


def run_load_test():
    """Run the complete load test"""
    print("=" * 70)
    print("RustChain API Load Test")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Requests per endpoint: {REQUESTS_PER_ENDPOINT}")
    print(f"Concurrent users simulation: {CONCURRENT_USERS}")
    print("=" * 70)
    
    all_results = []
    
    # Test each endpoint
    for endpoint_name, endpoint_path in ENDPOINTS.items():
        results = test_endpoint(endpoint_name, endpoint_path)
        all_results.extend(results)
    
    # Calculate statistics
    print("\n" + "=" * 70)
    print("LOAD TEST RESULTS")
    print("=" * 70)
    
    total_requests = len(all_results)
    successful_requests = sum(1 for r in all_results if r['success'])
    failed_requests = total_requests - successful_requests
    
    response_times = [r['response_time_ms'] for r in all_results if r['success'] and r['response_time_ms'] > 0]
    
    print(f"\nTotal Requests: {total_requests}")
    print(f"Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
    print(f"Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
    
    if response_times:
        print(f"\nResponse Time Statistics:")
        print(f"  Min: {min(response_times):.2f}ms")
        print(f"  Max: {max(response_times):.2f}ms")
        print(f"  Average: {statistics.mean(response_times):.2f}ms")
        print(f"  Median: {statistics.median(response_times):.2f}ms")
        
        if len(response_times) >= 10:
            sorted_times = sorted(response_times)
            p90_idx = int(len(sorted_times) * 0.9)
            p95_idx = int(len(sorted_times) * 0.95)
            p99_idx = int(len(sorted_times) * 0.99)
            print(f"  P90: {sorted_times[p90_idx]:.2f}ms")
            print(f"  P95: {sorted_times[p95_idx]:.2f}ms")
            print(f"  P99: {sorted_times[p99_idx]:.2f}ms")
    
    # Per-endpoint breakdown
    print(f"\nPer-Endpoint Breakdown:")
    for endpoint_name in ENDPOINTS.keys():
        endpoint_results = [r for r in all_results if r['endpoint'] == endpoint_name]
        endpoint_success = sum(1 for r in endpoint_results if r['success'])
        endpoint_times = [r['response_time_ms'] for r in endpoint_results if r['success'] and r['response_time_ms'] > 0]
        
        if endpoint_times:
            avg_time = statistics.mean(endpoint_times)
            print(f"  {endpoint_name:15s}: {endpoint_success}/{len(endpoint_results)} success, avg {avg_time:6.2f}ms")
        else:
            print(f"  {endpoint_name:15s}: {endpoint_success}/{len(endpoint_results)} success")
    
    print("\n" + "=" * 70)
    print(f"End Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    return all_results


if __name__ == "__main__":
    results = run_load_test()
