#!/usr/bin/env python3
"""
Fuzzing script for the /attest/submit endpoint
This script generates random attestations and submits them to the endpoint
"""

import requests
import random
import string
import json
import time
from datetime import datetime, timedelta
import argparse


def generate_random_attestation():
    """Generate a random attestation payload"""
    return {
        "miner_id": ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        "timestamp": int(time.time()),
        "data": {
            "type": random.choice(['performance', 'availability', 'integrity']),
            "value": random.uniform(0, 100),
            "metadata": {
                "random_field': ''.join(random.choices(string.ascii_letters, k=8)),
                "nested_data': {
                    "level1': random.randint(1, 100),
                    "level2': ''.join(random.choices(string.digits, k=4))
                }
            }
        },
        "signature': ''.join(random.choices(string.hexdigits, k=64)),
        "version": random.choice(['1.0', '2.0', '3.0'])
    }


def generate_malformed_attestation():
    """Generate a malformed attestation for edge case testing"""
    malformed_types = [
        # Missing required fields
        {"data": {"type": "test"}},
        # Invalid data types
        {"miner_id": 123, "timestamp": "not_a_timestamp", "data": "not_an_object"},
        # Empty data
        {"miner_id": "", "timestamp": 0, "data": {}},
        # Extremely large values
        {"miner_id": "a" * 10000, "timestamp": 999999999999, "data": {"type": "test", "value": 999999999999999}},
        # Invalid JSON structure
        {"miner_id": "test", "timestamp": 123, "data": ["invalid", "structure"]},
        # Missing data field entirely
        {"miner_id": "test", "timestamp": 123}
    ]
    return random.choice(malformed_types)


def submit_attestation(attestation, base_url="http://localhost:8000"):
    """Submit an attestation to the /attest/submit endpoint"""
    url = f"{base_url}/attest/submit"
    
    try:
        response = requests.post(
            url,
            json=attestation,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return -1, str(e)


def fuzz_endpoint(base_url="http://localhost:8000", num_requests=1000):
    """Main fuzzing function"""
    print(f"Starting fuzzing of {base_url}/attest/submit with {num_requests} requests")
    
    success_count = 0
    error_count = 0
    status_codes = {}
    
    for i in range(num_requests):
        # Alternate between valid and malformed attestations
        if i % 10 == 0:
            attestation = generate_malformed_attestation()
            print(f"Request {i+1}: Submitting malformed attestation")
        else:
            attestation = generate_random_attestation()
            print(f"Request {i+1}: Submitting valid attestation")
        
        status_code, response_text = submit_attestation(attestation, base_url)
        
        if status_code == -1:
            print(f"Request {i+1}: Failed - {response_text}")
            error_count += 1
        else:
            print(f"Request {i+1}: Status {status_code} - {response_text[:100]}...")
            
            if status_code not in status_codes:
                status_codes[status_code] = 0
            status_codes[status_code] += 1
            
            if 200 <= status_code < 300:
                success_count += 1
            else:
                error_count += 1
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    # Print summary
    print("\n=== FUZZING SUMMARY ===")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {success_count}")
    print(f"Failed requests: {error_count}")
    print("\nStatus code distribution:")
    for code, count in sorted(status_codes.items()):
        print(f"  {code}: {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fuzz the /attest/submit endpoint")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--requests", type=int, default=1000, help="Number of requests to send")
    
    args = parser.parse_args()
    
    fuzz_endpoint(args.url, args.requests)
