#!/usr/bin/env python3
"""
RustChain /attest/submit Endpoint Fuzzer
Bounty #1112 - Fuzz /attest/submit Endpoint (10 RTC)

This fuzzer tests the RustChain attestation submission endpoint
with various payloads to identify crashes, errors, and edge cases.
"""

import requests
import json
import random
import string
import sys
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Node endpoints
NODES = [
    "http://50.28.86.131:8099",  # Alpha
    "http://50.28.86.153:8099",  # Beta
    "http://76.8.228.245:8099",  # Gamma
]

ENDPOINT = "/attest/submit"

# Test results storage
results = []


def log(message: str):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def test_payload(node: str, payload: Any, description: str) -> Tuple[int, str]:
    """Send a test payload and return status code and response"""
    url = f"{node}{ENDPOINT}"
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code, response.text[:200]
    except requests.exceptions.Timeout:
        return -1, "TIMEOUT"
    except requests.exceptions.ConnectionError:
        return -2, "CONNECTION_ERROR"
    except Exception as e:
        return -3, str(e)[:200]


def fuzz_test_1_empty_object(nodes: List[str]):
    """Test 1: Empty JSON object"""
    log("Test 1: Empty JSON object {}")
    for node in nodes:
        status, resp = test_payload(node, {}, "empty_object")
        results.append({
            "test": "empty_object",
            "node": node,
            "status": status,
            "response": resp,
            "expected": "400 or validation error",
            "issue": status == 500
        })
        if status == 500:
            log(f"  ⚠️  BUG: {node} returned 500 for empty object")


def fuzz_test_2_null_values(nodes: List[str]):
    """Test 2: Null values in various fields"""
    log("Test 2: Null values")
    payloads = [
        {"value": None},
        {"wallet": None, "amount": 100},
        {"data": None, "nested": {"key": None}},
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "null_values")
            results.append({
                "test": "null_values",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on null value")


def fuzz_test_3_type_confusion(nodes: List[str]):
    """Test 3: Type confusion - wrong types for expected fields"""
    log("Test 3: Type confusion")
    payloads = [
        {"amount": "not_a_number"},
        {"amount": True},
        {"amount": []},
        {"amount": {}},
        {"wallet": 12345},
        {"wallet": True},
        {"active": "true_string"},
        {"count": "123"},
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "type_confusion")
            results.append({
                "test": "type_confusion",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on type confusion: {payload}")


def fuzz_test_4_boundary_values(nodes: List[str]):
    """Test 4: Boundary and extreme numeric values"""
    log("Test 4: Boundary values")
    payloads = [
        {"amount": 0},
        {"amount": -1},
        {"amount": -999999999},
        {"amount": 999999999999999},
        {"amount": 1.7976931348623157e+308},  # Max float64
        {"amount": float('inf')},
        {"amount": float('-inf')},
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "boundary_values")
            results.append({
                "test": "boundary_values",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on boundary value: {payload}")


def fuzz_test_5_deep_nesting(nodes: List[str]):
    """Test 5: Deeply nested objects"""
    log("Test 5: Deep nesting")
    
    def create_nested(depth: int) -> dict:
        if depth == 0:
            return {"value": "test"}
        return {"level": create_nested(depth - 1)}
    
    for depth in [5, 10, 20, 50, 100]:
        payload = create_nested(depth)
        for node in nodes:
            status, resp = test_payload(node, payload, f"deep_nesting_{depth}")
            results.append({
                "test": f"deep_nesting_{depth}",
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on depth {depth}")


def fuzz_test_6_large_strings(nodes: List[str]):
    """Test 6: Very large string values"""
    log("Test 6: Large strings")
    sizes = [100, 1000, 10000, 100000]
    for size in sizes:
        payload = {"data": "A" * size}
        for node in nodes:
            status, resp = test_payload(node, payload, f"large_string_{size}")
            results.append({
                "test": f"large_string_{size}",
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on {size} char string")


def fuzz_test_7_special_characters(nodes: List[str]):
    """Test 7: Special and unicode characters"""
    log("Test 7: Special characters")
    payloads = [
        {"text": "🦀🚀💎"},  # Emoji
        {"text": "<script>alert(1)</script>"},  # XSS attempt
        {"text": "';--"},  # SQL injection attempt
        {"text": "\\x00\\x01\\x02"},  # Control characters
        {"text": "日本語テスト"},  # Japanese
        {"text": "العربية"},  # Arabic
        {"text": "🅁🅄🅂🅃"},  # Unicode blocks
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "special_chars")
            results.append({
                "test": "special_chars",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on special chars")


def fuzz_test_8_array_instead_of_object(nodes: List[str]):
    """Test 8: Arrays instead of objects"""
    log("Test 8: Arrays instead of objects")
    payloads = [
        [],
        [1, 2, 3],
        ["a", "b", "c"],
        [{"key": "value"}],
        [[1, 2], [3, 4]],
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "array_instead_object")
            results.append({
                "test": "array_instead_object",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on array input")


def fuzz_test_9_many_keys(nodes: List[str]):
    """Test 9: Objects with many keys"""
    log("Test 9: Many keys")
    for num_keys in [10, 50, 100, 500]:
        payload = {f"key_{i}": f"value_{i}" for i in range(num_keys)}
        for node in nodes:
            status, resp = test_payload(node, payload, f"many_keys_{num_keys}")
            results.append({
                "test": f"many_keys_{num_keys}",
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on {num_keys} keys")


def fuzz_test_10_long_key_names(nodes: List[str]):
    """Test 10: Very long key names"""
    log("Test 10: Long key names")
    for length in [100, 500, 1000, 5000]:
        key = "k" * length
        payload = {key: "value"}
        for node in nodes:
            status, resp = test_payload(node, payload, f"long_key_{length}")
            results.append({
                "test": f"long_key_{length}",
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on {length} char key name")


def fuzz_test_11_boolean_values(nodes: List[str]):
    """Test 11: Boolean values in various contexts"""
    log("Test 11: Boolean values")
    payloads = [
        {"active": True},
        {"active": False},
        {"count": True},
        {"amount": False},
        {"wallet": True},
        {"true": True, "false": False},
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "boolean_values")
            results.append({
                "test": "boolean_values",
                "payload": str(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on boolean: {payload}")


def fuzz_test_12_malformed_but_valid_json(nodes: List[str]):
    """Test 12: Edge case JSON structures"""
    log("Test 12: Edge case JSON structures")
    payloads = [
        {"": "empty_key"},
        {" ": "space_key"},
        {"\t": "tab_key"},
        {"\n": "newline_key"},
        {"key": ""},
        {"key": " "},
        {"key": "\n\n\n"},
    ]
    for payload in payloads:
        for node in nodes:
            status, resp = test_payload(node, payload, "edge_case_json")
            results.append({
                "test": "edge_case_json",
                "payload": repr(payload)[:50],
                "node": node,
                "status": status,
                "issue": status == 500
            })
            if status == 500:
                log(f"  ⚠️  BUG: {node} crashed on edge case JSON")


def run_all_tests():
    """Run all fuzz tests"""
    log("=" * 60)
    log("RUSTCHAIN ATTEST/SUBMIT ENDPOINT FUZZER")
    log("=" * 60)
    
    # Check which nodes are online
    log("\nChecking node availability...")
    available_nodes = []
    for node in NODES:
        try:
            resp = requests.get(f"{node}/health", timeout=5)
            log(f"  ✅ {node} - ONLINE")
            available_nodes.append(node)
        except:
            log(f"  ❌ {node} - OFFLINE")
    
    if not available_nodes:
        log("No nodes available for testing!")
        return
    
    log(f"\nRunning fuzz tests against {len(available_nodes)} node(s)...")
    log("-" * 60)
    
    # Run all test suites
    fuzz_test_1_empty_object(available_nodes)
    fuzz_test_2_null_values(available_nodes)
    fuzz_test_3_type_confusion(available_nodes)
    fuzz_test_4_boundary_values(available_nodes)
    fuzz_test_5_deep_nesting(available_nodes)
    fuzz_test_6_large_strings(available_nodes)
    fuzz_test_7_special_characters(available_nodes)
    fuzz_test_8_array_instead_of_object(available_nodes)
    fuzz_test_9_many_keys(available_nodes)
    fuzz_test_10_long_key_names(available_nodes)
    fuzz_test_11_boolean_values(available_nodes)
    fuzz_test_12_malformed_but_valid_json(available_nodes)
    
    # Generate report
    log("\n" + "=" * 60)
    log("FUZZ TEST SUMMARY")
    log("=" * 60)
    
    bugs_found = [r for r in results if r.get("issue")]
    
    print(f"\nTotal tests run: {len(results)}")
    print(f"Bugs found (500 errors): {len(bugs_found)}")
    
    if bugs_found:
        print("\n🐛 BUGS DISCOVERED:")
        print("-" * 60)
        
        # Group by test type
        by_test = {}
        for bug in bugs_found:
            test = bug["test"]
            if test not in by_test:
                by_test[test] = []
            by_test[test].append(bug)
        
        for test_name, bugs in by_test.items():
            print(f"\n{test_name}:")
            for bug in bugs:
                node_short = bug["node"].split("//")[1]
                print(f"  - {node_short}: HTTP {bug['status']}")
    
    # Save detailed report
    report_file = "fuzzer_report.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "nodes_tested": available_nodes,
            "total_tests": len(results),
            "bugs_found": len(bugs_found),
            "results": results
        }, f, indent=2)
    
    log(f"\nDetailed report saved to: {report_file}")
    log("\nFuzz testing complete!")


if __name__ == "__main__":
    run_all_tests()
