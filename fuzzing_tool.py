import requests
import json
import random
import string

# Configuration
BASE_URL = "https://api.rustchain.org"
ENDPOINT = "/attest/submit"
HEADERS = {"Content-Type": "application/json"}

# Payload generators
def generate_missing_field_payload():
    """Generate payload with missing required fields"""
    fields = ["attestation", "signature", "public_key"]
    missing_field = random.choice(fields)
    payload = {
        "attestation": "test_attestation",
        "signature": "test_signature",
        "public_key": "test_public_key"
    }
    del payload[missing_field]
    return payload

def generate_wrong_type_payload():
    """Generate payload with wrong data types"""
    payload = {
        "attestation": random.randint(1, 100),  # Should be string
        "signature": random.randint(1, 100),    # Should be string
        "public_key": random.randint(1, 100)   # Should be string
    }
    return payload

def generate_oversized_payload():
    """Generate payload with oversized inputs"""
    payload = {
        "attestation": "a" * 10000,  # Excessive length
        "signature": "b" * 10000,    # Excessive length
        "public_key": "c" * 10000    # Excessive length
    }
    return payload

def generate_injection_payload():
    """Generate payload with injection attempts"""
    injection_strings = [
        "<script>alert('xss')</script>",
        "' OR '1'='1",
        "DROP TABLE users;--",
        "UNION SELECT * FROM users"
    ]
    field = random.choice(["attestation", "signature", "public_key"])
    payload = {
        "attestation": "normal_attestation",
        "signature": "normal_signature",
        "public_key": "normal_public_key"
    }
    payload[field] = random.choice(injection_strings)
    return payload

# Fuzzing function
def fuzz_endpoint():
    """Fuzz the /attest/submit endpoint with malformed payloads"""
    payload_generators = [
        generate_missing_field_payload,
        generate_wrong_type_payload,
        generate_oversized_payload,
        generate_injection_payload
    ]

    results = []

    for _ in range(100):  # Send at least 100 payloads
        generator = random.choice(payload_generators)
        payload = generator()

        try:
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                headers=HEADERS,
                data=json.dumps(payload)
            )
            results.append({
                "payload": payload,
                "status_code": response.status_code,
                "response": response.text
            })
        except Exception as e:
            results.append({
                "payload": payload,
                "error": str(e)
            })

    return results

# Run fuzzing and save results
if __name__ == "__main__":
    fuzzing_results = fuzz_endpoint()

    # Save results to a file
    with open("fuzzing_results.json", "w") as f:
        json.dump(fuzzing_results, f, indent=2)

    print("Fuzzing complete. Results saved to fuzzing_results.json")