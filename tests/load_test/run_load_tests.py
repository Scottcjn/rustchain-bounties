#!/usr/bin/env python3
"""
Script to run RustChain API load tests

Usage:
    python run_load_tests.py                    # Run basic load tests
    python run_load_tests.py --stress            # Run stress test on all endpoints
    python run_load_tests.py --endpoint blocks   # Test specific endpoint
    python run_load_tests.py --help              # Show help
"""

import argparse
import sys
import os
from test_rustchain_api import TestRustChainAPI


def main():
    parser = argparse.ArgumentParser(description="Run RustChain API load tests")
    parser.add_argument("--stress", action="store_true", help="Run stress test on all endpoints")
    parser.add_argument("--endpoint", type=str, help="Test specific endpoint")
    parser.add_argument("--requests", type=int, default=50, help="Number of requests to send (default: 50)")
    parser.add_argument("--workers", type=int, default=10, help="Number of concurrent workers (default: 10)")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    # Add the tests directory to the path so we can import the test module
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    test_instance = TestRustChainAPI()
    
    if args.endpoint:
        print(f"Testing endpoint: {args.endpoint}")
        result = test_instance.test_endpoint_concurrent_requests(
            args.endpoint, 
            num_requests=args.requests, 
            max_workers=args.workers
        )
        
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
    
    elif args.stress:
        print("Running stress test on all endpoints...")
        results = test_instance.test_stress_test_all_endpoints()
        
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print("\nStress Test Results:")
            for endpoint, result in results.items():
                print(f"{endpoint}: {result}")
    
    else:
        print("Running basic load tests...")
        
        # Run individual tests
        test_instance.test_get_blocks_endpoint()
        test_instance.test_get_block_by_hash_endpoint()
        test_instance.test_get_transactions_endpoint()
        test_instance.test_get_transaction_by_hash_endpoint()
        test_instance.test_get_miners_endpoint()
        test_instance.test_get_stats_endpoint()
        
        print("\nAll tests completed!")


if __name__ == "__main__":
    main()