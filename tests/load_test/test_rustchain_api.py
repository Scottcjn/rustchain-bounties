import pytest
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string


class TestRustChainAPI:
    """Load test suite for RustChain API endpoints"""
    
    BASE_URL = "http://localhost:8000"  # Adjust if your API runs on a different port
    
    def generate_random_data(self, length=10):
        """Generate random string for testing"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def test_endpoint_concurrent_requests(self, endpoint, num_requests=100, max_workers=10):
        """Test endpoint with concurrent requests"""
        url = f"{self.BASE_URL}/{endpoint}"
        response_times = []
        success_count = 0
        error_count = 0
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(url)
                end_time = time.time()
                return response.status_code, end_time - start_time
            except Exception as e:
                end_time = time.time()
                return 500, end_time - start_time
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                status_code, response_time = future.result()
                response_times.append(response_time)
                
                if status_code < 500:
                    success_count += 1
                else:
                    error_count += 1
        
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        print(f"\nEndpoint: {endpoint}")
        print(f"Total requests: {num_requests}")
        print(f"Successful requests: {success_count}")
        print(f"Failed requests: {error_count}")
        print(f"Average response time: {avg_response_time:.4f}s")
        print(f"Min response time: {min_response_time:.4f}s")
        print(f"Max response time: {max_response_time:.4f}s")
        
        # Assertions
        assert error_count < num_requests * 0.05, f"Too many errors: {error_count}/{num_requests}"
        assert avg_response_time < 1.0, f"Average response time too high: {avg_response_time}s"
        
        return {
            "endpoint": endpoint,
            "total_requests": num_requests,
            "success_count": success_count,
            "error_count": error_count,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time
        }
    
    def test_get_blocks_endpoint(self):
        """Test GET /blocks endpoint under load"""
        return self.test_endpoint_concurrent_requests("blocks", num_requests=50)
    
    def test_get_block_by_hash_endpoint(self):
        """Test GET /blocks/{hash} endpoint under load"""
        # First get a valid block hash
        response = requests.get(f"{self.BASE_URL}/blocks")
        if response.status_code == 200 and len(response.json()) > 0:
            block_hash = response.json()[0].get("hash", "")
            if block_hash:
                return self.test_endpoint_concurrent_requests(f"blocks/{block_hash}", num_requests=50)
        
        # Fallback test with random hash if no blocks exist
        random_hash = self.generate_random_data(64)
        return self.test_endpoint_concurrent_requests(f"blocks/{random_hash}", num_requests=50)
    
    def test_get_transactions_endpoint(self):
        """Test GET /transactions endpoint under load"""
        return self.test_endpoint_concurrent_requests("transactions", num_requests=50)
    
    def test_get_transaction_by_hash_endpoint(self):
        """Test GET /transactions/{hash} endpoint under load"""
        # First get a valid transaction hash
        response = requests.get(f"{self.BASE_URL}/transactions")
        if response.status_code == 200 and len(response.json()) > 0:
            tx_hash = response.json()[0].get("hash", "")
            if tx_hash:
                return self.test_endpoint_concurrent_requests(f"transactions/{tx_hash}", num_requests=50)
        
        # Fallback test with random hash if no transactions exist
        random_hash = self.generate_random_data(64)
        return self.test_endpoint_concurrent_requests(f"transactions/{random_hash}", num_requests=50)
    
    def test_get_miners_endpoint(self):
        """Test GET /miners endpoint under load"""
        return self.test_endpoint_concurrent_requests("miners", num_requests=50)
    
    def test_get_stats_endpoint(self):
        """Test GET /stats endpoint under load"""
        return self.test_endpoint_concurrent_requests("stats", num_requests=100)
    
    def test_stress_test_all_endpoints(self):
        """Run stress test on all endpoints simultaneously"""
        endpoints = [
            "blocks",
            "transactions",
            "miners",
            "stats"
        ]
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.test_endpoint_concurrent_requests, endpoint, 20): endpoint for endpoint in endpoints}
            
            for future in as_completed(futures):
                endpoint = futures[future]
                try:
                    results[endpoint] = future.result()
                except Exception as e:
                    print(f"Error testing {endpoint}: {str(e)}")
                    results[endpoint] = {"error": str(e)}
        
        return results
    
    def test_endpoint_with_different_payload_sizes(self, endpoint, payload_sizes=[1, 10, 100, 1000]):
        """Test endpoint with different payload sizes"""
        results = {}
        
        for size in payload_sizes:
            # This is a placeholder - adjust based on your actual API
            # For example, if you have a POST endpoint that accepts data
            try:
                if endpoint == "submit":
                    payload = {"data": self.generate_random_data(size)}
                    response = requests.post(f"{self.BASE_URL}/{endpoint}", json=payload)
                    results[size] = response.status_code
                else:
                    # For GET requests, we'll just test with different query parameters
                    response = requests.get(f"{self.BASE_URL}/{endpoint}?size={size}")
                    results[size] = response.status_code
            except Exception as e:
                results[size] = f"Error: {str(e)}"
        
        return results


# Standalone script to run load tests
if __name__ == "__main__":
    import sys
    
    test_instance = TestRustChainAPI()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--stress":
        print("Running stress test on all endpoints...")
        results = test_instance.test_stress_test_all_endpoints()
        print("\nStress Test Results:")
        for endpoint, result in results.items():
            print(f"{endpoint}: {result}")
    else:
        print("Running individual endpoint tests...")
        
        # Run individual tests
        test_instance.test_get_blocks_endpoint()
        test_instance.test_get_block_by_hash_endpoint()
        test_instance.test_get_transactions_endpoint()
        test_instance.test_get_transaction_by_hash_endpoint()
        test_instance.test_get_miners_endpoint()
        test_instance.test_get_stats_endpoint()
        
        print("\nAll tests completed!")