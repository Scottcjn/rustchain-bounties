# Load Test Suite for RustChain API

## Summary

This PR implements a comprehensive load testing suite for the RustChain API as specified in issue #1614.

## Changes

### New Files

1. **load_tests/locustfile.py** - Locust-based load testing with multiple user classes:
   - `RustChainAPIUser`: Normal API usage patterns
   - `StressTestUser`: Aggressive stress testing
   - `RateLimitTestUser`: Rate limiting behavior testing

2. **load_tests/k6-loadtest.js** - k6-based load testing with:
   - Built-in performance thresholds
   - Multiple test scenarios (normal, stress, spike)
   - Custom metrics and detailed reporting

3. **load_tests/artillery-loadtest.yml** - Artillery-based load testing with:
   - YAML configuration for quick setup
   - Built-in reporting
   - Phase-based load patterns

4. **load_tests/simple-loadtest.py** - Simple Python script for quick API testing:
   - No external dependencies beyond requests
   - Clear console output
   - Response time statistics

5. **load_tests/requirements-loadtest.txt** - Python dependencies

6. **load_tests/README.md** - Comprehensive documentation

## Test Coverage

All major API endpoints are tested:

| Endpoint | Method | Test Coverage |
|----------|--------|---------------|
| `/health` | GET | ✓ |
| `/epoch` | GET | ✓ |
| `/api/miners` | GET | ✓ |
| `/wallet/balance` | GET | ✓ |
| `/attest/challenge` | POST | ✓ |
| `/lottery/eligibility` | GET | ✓ |
| `/explorer` | GET | ✓ |

## Test Results

Initial load test results (50 requests, 10 per endpoint):

- **Success Rate**: 100%
- **Average Response Time**: 689ms
- **Median Response Time**: 282ms
- **P90 Response Time**: 1863ms
- **P95 Response Time**: 2560ms

### Per-Endpoint Performance

- `/health`: avg 2062ms (first request slower due to connection setup)
- `/epoch`: avg 341ms
- `/api/miners`: avg 346ms
- `/wallet/balance`: avg 342ms
- `/attest/challenge`: avg 356ms

## Usage

### Locust
```bash
cd load_tests
pip install -r requirements-loadtest.txt
locust -f locustfile.py --host https://50.28.86.131
```

### k6
```bash
k6 run k6-loadtest.js
```

### Artillery
```bash
artillery run artillery-loadtest.yml
```

### Simple Test
```bash
python simple-loadtest.py
```

## Bounty

Closes #1614

## Checklist

- [x] Locust test suite
- [x] k6 test suite
- [x] Artillery test suite
- [x] Simple Python test script
- [x] Documentation (README.md)
- [x] Requirements files
- [x] Tested against live API
- [x] Performance benchmarks captured
