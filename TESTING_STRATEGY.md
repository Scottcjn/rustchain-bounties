# RustChain Testing Strategy Guide

> **Bounty:** #1683 - Create a RustChain testing strategy guide  
> **Reward:** 3 RTC  
> **Author:** AI Agent (牛)  
> **Date:** 2026-03-12

---

## Overview

This guide provides a comprehensive testing strategy for the RustChain blockchain project. RustChain is a Proof-of-Antiquity blockchain where vintage hardware earns higher mining rewards. The testing strategy covers three levels:

1. **Unit Testing** - Testing individual components in isolation
2. **Integration Testing** - Testing component interactions
3. **End-to-End (E2E) Testing** - Testing complete user workflows

---

## Project Structure

```
Rustchain/
├── node/
│   ├── rustchain_v2_integrated_v2.2.1_rip200.py  # Full node implementation
│   └── fingerprint_checks.py                      # Hardware verification
├── miners/
│   ├── linux/rustchain_linux_miner.py            # Linux miner
│   └── macos/rustchain_mac_miner_v2.4.py         # macOS miner
├── tools/
│   └── validator_core.py                         # Block validation
├── tests/                                        # Test suite
│   ├── test_*.py                                 # Test files
│   ├── conftest.py                               # Pytest configuration
│   └── requirements.txt                          # Test dependencies
└── docs/
    └── TESTING_STRATEGY.md                       # This document
```

---

## 1. Unit Testing

Unit tests verify individual functions, classes, and modules in isolation.

### 1.1 What to Test

| Component | Test Focus | Priority |
|-----------|-----------|----------|
| `fingerprint_checks.py` | Hardware fingerprinting algorithms | Critical |
| `validator_core.py` | Block validation logic | Critical |
| Miner scripts | Mining reward calculations | High |
| API handlers | Request/response validation | High |
| Crypto utilities | Signature verification | Critical |

### 1.2 Test Structure

```python
# tests/test_fingerprint.py
import pytest
from node.fingerprint_checks import validate_fingerprint_data

class TestFingerprintValidation:
    """Test hardware fingerprint validation logic."""
    
    def test_valid_fingerprint(self):
        """Test with valid fingerprint data."""
        data = {
            "cpu_id": "G4-12345",
            "cache_timing": {...},
            "simd_identity": "AltiVec"
        }
        result = validate_fingerprint_data(data)
        assert result["valid"] is True
    
    def test_missing_field(self):
        """Test with missing required field."""
        data = {"cpu_id": "G4-12345"}  # Missing cache_timing
        result = validate_fingerprint_data(data)
        assert result["valid"] is False
        assert "cache_timing" in result["errors"]
    
    def test_emulation_detection(self):
        """Test VM/emulator detection."""
        data = create_emulated_fingerprint()
        result = validate_fingerprint_data(data)
        assert result["valid"] is False
        assert "emulation_detected" in result["flags"]
```

### 1.3 Best Practices

- **Isolation**: Mock external dependencies (network, filesystem)
- **Coverage**: Aim for 80%+ code coverage on critical modules
- **Naming**: Use descriptive test names (`test_<scenario>_<expected_result>`)
- **Assertions**: One assertion per test concept (can have multiple related checks)

### 1.4 Running Unit Tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_fingerprint.py -v

# Run with coverage
pytest tests/ --cov=node --cov=miners --cov=tools --cov-report=html

# Run tests matching pattern
pytest tests/ -k "fingerprint" -v
```

---

## 2. Integration Testing

Integration tests verify that multiple components work together correctly.

### 2.1 What to Test

| Integration Point | Test Scenario | Priority |
|------------------|---------------|----------|
| Miner ↔ Node | Mining submission and reward | Critical |
| API ↔ Database | Data persistence and retrieval | High |
| Wallet ↔ Node | Balance queries and transfers | Critical |
| Governance ↔ Consensus | Proposal voting and execution | High |
| Bridge ↔ External Chain | Cross-chain operations | High |

### 2.2 Test Structure

```python
# tests/test_claims_integration.py
import pytest
import requests
from tests.conftest import get_test_node_url

class TestMiningIntegration:
    """Test miner-to-node integration."""
    
    @pytest.fixture
    def node_url(self):
        return get_test_node_url()
    
    def test_miner_submission_flow(self, node_url):
        """Test complete mining submission flow."""
        # 1. Submit attestation
        attestation = create_valid_attestation()
        response = requests.post(
            f"{node_url}/attest/submit",
            json=attestation
        )
        assert response.status_code == 200
        miner_id = response.json()["miner_id"]
        
        # 2. Submit mining work
        work = create_mining_work(miner_id)
        response = requests.post(
            f"{node_url}/mining/submit",
            json=work
        )
        assert response.status_code == 200
        
        # 3. Verify reward credited
        balance = requests.get(
            f"{node_url}/wallet/balance",
            params={"miner_id": miner_id}
        )
        assert balance.json()["balance"] > 0
```

### 2.3 Test Fixtures

```python
# tests/conftest.py
import pytest
import subprocess
import time

@pytest.fixture(scope="session")
def test_node():
    """Start a test node for integration tests."""
    # Start node in test mode
    proc = subprocess.Popen([
        "python3", "node/rustchain_v2_integrated_v2.2.1_rip200.py",
        "--test-mode", "--port", "5001"
    ])
    
    # Wait for node to be ready
    time.sleep(3)
    
    yield "http://localhost:5001"
    
    # Cleanup
    proc.terminate()
    proc.wait()

@pytest.fixture
def test_wallet():
    """Create a test wallet."""
    wallet_id = f"test_wallet_{int(time.time())}"
    requests.post("http://localhost:5001/wallet/create", json={"id": wallet_id})
    yield wallet_id
    # Cleanup handled by test node shutdown
```

### 2.4 Running Integration Tests

```bash
# Run integration tests only
pytest tests/ -m integration -v

# Run with specific node version
RUSTCHAIN_VERSION=2.2.1 pytest tests/ -m integration -v

# Run with verbose logging
pytest tests/ -m integration -v -s --log-cli-level=INFO
```

---

## 3. End-to-End (E2E) Testing

E2E tests verify complete user workflows from start to finish.

### 3.1 What to Test

| Workflow | Steps | Priority |
|----------|-------|----------|
| New Miner Onboarding | Install → Attest → Mine → Receive Reward | Critical |
| Wallet Transfer | Create → Fund → Transfer → Verify Balance | Critical |
| Governance Proposal | Create → Vote → Execute → Verify State | High |
| Cross-Chain Bridge | Lock → Bridge → Verify on Target Chain | High |
| Bounty Claim | Find → Claim → Submit → Get Paid | Medium |

### 3.2 Test Structure

```python
# tests/test_e2e_miner_onboarding.py
import pytest
import requests
import time

class TestE2EMinerOnboarding:
    """End-to-end test for new miner onboarding."""
    
    def test_complete_onboarding_flow(self):
        """Test complete miner onboarding from install to first reward."""
        node_url = "http://localhost:5001"
        
        # Step 1: Create wallet
        wallet_response = requests.post(
            f"{node_url}/wallet/create",
            json={"name": "e2e_test_miner"}
        )
        assert wallet_response.status_code == 200
        
        # Step 2: Submit hardware attestation
        attestation = self.create_g4_attestation()
        attest_response = requests.post(
            f"{node_url}/attest/submit",
            json=attestation
        )
        assert attest_response.status_code == 200
        miner_id = attest_response.json()["miner_id"]
        
        # Step 3: Wait for epoch boundary
        epoch_info = requests.get(f"{node_url}/epoch")
        wait_time = epoch_info.json()["seconds_until_next_epoch"] + 5
        time.sleep(wait_time)
        
        # Step 4: Submit mining work
        mining_response = requests.post(
            f"{node_url}/mining/submit",
            json={"miner_id": miner_id, "work_proof": "valid_proof"}
        )
        assert mining_response.status_code == 200
        
        # Step 5: Verify reward received
        balance_response = requests.get(
            f"{node_url}/wallet/balance",
            params={"miner_id": miner_id}
        )
        balance = balance_response.json()["balance"]
        assert balance >= 0.12  # Minimum base reward
        
        # Step 6: Verify antiquity multiplier applied
        miner_info = requests.get(
            f"{node_url}/api/miners",
            params={"miner_id": miner_id}
        )
        multiplier = miner_info.json()["antiquity_multiplier"]
        assert multiplier >= 1.0  # G4 should have 2.5x
```

### 3.3 E2E Test Environment

```bash
# Start test environment
docker-compose -f tests/docker-compose.yml up -d

# Run E2E tests
pytest tests/ -m e2e -v

# Run with screenshot on failure (for UI tests)
pytest tests/ -m e2e --screenshot-on-failure

# Cleanup
docker-compose -f tests/docker-compose.yml down
```

---

## 4. Fuzz Testing

RustChain includes a comprehensive fuzz testing framework for security-critical endpoints.

### 4.1 Fuzz Testing Targets

| Target | Mutation Strategies | Purpose |
|--------|-------------------|---------|
| `/attest/submit` | 15 strategies | Find attestation validation bugs |
| `/mining/submit` | 10 strategies | Find mining logic vulnerabilities |
| `/wallet/transfer` | 12 strategies | Find financial security issues |
| `/governance/vote` | 8 strategies | Find governance manipulation vectors |

### 4.2 Running Fuzz Tests

```bash
# Basic fuzz run (1000 iterations)
python3 tests/fuzz_attestation_runner.py

# CI mode (exit non-zero on crash)
python3 tests/fuzz_attestation_runner.py --ci --count 5000

# Save interesting cases
python3 tests/fuzz_attestation_runner.py --save-corpus --verbose

# Replay saved corpus
python3 tests/fuzz_attestation_runner.py --replay

# View crash report
python3 tests/fuzz_attestation_runner.py --report
```

### 4.3 Mutation Strategies

```python
MUTATORS = [
    "missing_field",      # Remove required fields
    "wrong_type",         # Replace values with wrong types
    "unknown_field",      # Inject unexpected fields
    "nested_bomb",        # Deeply nested structures (JSON bomb)
    "array_overflow",     # Extremely large arrays
    "float_edge",         # Edge-case floats (inf, nan)
    "unicode_inject",     # Unicode edge cases
    "size_extremes",      # Empty/huge strings
    "sql_injection",      # SQL injection attempts
    "xss_attempt",        # XSS injection attempts
    # ... more strategies
]
```

---

## 5. Security Testing

### 5.1 Security Test Categories

| Category | Tests | Tools |
|----------|-------|-------|
| Input Validation | Malformed payloads, boundary tests | Fuzz testing |
| Authentication | Unauthorized access, token replay | Custom scripts |
| Cryptography | Signature forgery, replay attacks | Custom scripts |
| Consensus | Double-spend, 51% attack simulation | Network simulation |
| Economic | Reward manipulation, inflation attacks | Game theory analysis |

### 5.2 Running Security Tests

```bash
# Run all security tests
pytest tests/ -m security -v

# Run specific security category
pytest tests/ -m "security and cryptography" -v

# Run with detailed logging
pytest tests/ -m security -v -s --log-level=DEBUG
```

---

## 6. Performance Testing

### 6.1 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Attestation Latency | < 100ms | p95 response time |
| Mining Throughput | 1000 submissions/epoch | Submissions per epoch |
| API Response Time | < 50ms | p99 response time |
| Block Validation | < 10ms | Per-block validation time |

### 6.2 Running Performance Tests

```bash
# Run performance benchmarks
pytest tests/ -m performance -v

# Run with custom load
pytest tests/ -m performance --load=high -v

# Generate performance report
pytest tests/ -m performance --report=perf-report.json
```

---

## 7. Continuous Integration

### 7.1 CI Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      - name: Run unit tests
        run: pytest tests/ -m "not integration and not e2e" --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      - name: Start test node
        run: python3 node/rustchain_v2_integrated_v2.2.1_rip200.py --test-mode &
      - name: Run integration tests
        run: pytest tests/ -m integration -v

  fuzz-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install flask pytest
      - name: Run fuzz tests (CI mode)
        run: python3 tests/fuzz_attestation_runner.py --ci --count 1000
      - name: Upload crash report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: fuzz-crash-report
          path: tests/fuzz_crashes.json
```

### 7.2 Pre-commit Hooks

```bash
#!/bin/bash
# .git-hooks/pre-commit

# Run quick unit tests
pytest tests/ -m "not integration and not e2e" -q || exit 1

# Run quick fuzz test
python3 tests/fuzz_attestation_runner.py --count 100 --ci || exit 1

# Check code style
flake8 node/ miners/ tools/ --max-line-length=100 || exit 1

exit 0
```

---

## 8. Test Coverage Goals

| Component | Unit Coverage | Integration Coverage | E2E Coverage |
|-----------|--------------|---------------------|--------------|
| `fingerprint_checks.py` | 90% | 80% | 70% |
| `validator_core.py` | 90% | 80% | 70% |
| Miner scripts | 80% | 70% | 60% |
| API handlers | 85% | 75% | 65% |
| Crypto utilities | 95% | 85% | 50% |

### 8.1 Checking Coverage

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View coverage summary
coverage report --show-missing

# Fail if coverage below threshold
coverage report --fail-under=80
```

---

## 9. Test Data Management

### 9.1 Test Fixtures

```python
# tests/fixtures/hardware_profiles.py

HARDWARE_PROFILES = {
    "g4_mac": {
        "cpu_id": "PowerPC G4",
        "era": "1999-2005",
        "multiplier": 2.5,
        "fingerprint": {...}
    },
    "g5_mac": {
        "cpu_id": "PowerPC G5",
        "era": "2003-2006",
        "multiplier": 2.0,
        "fingerprint": {...}
    },
    "power8": {
        "cpu_id": "IBM POWER8",
        "era": "2014",
        "multiplier": 1.5,
        "fingerprint": {...}
    },
    "modern_x86": {
        "cpu_id": "Intel x86_64",
        "era": "Current",
        "multiplier": 1.0,
        "fingerprint": {...}
    }
}

def create_attestation(profile_name):
    """Create attestation for given hardware profile."""
    profile = HARDWARE_PROFILES[profile_name]
    return {
        "hardware_type": profile["cpu_id"],
        "fingerprint_data": profile["fingerprint"],
        "timestamp": int(time.time())
    }
```

### 9.2 Test Corpus

```
tests/
├── attestation_corpus/           # Fuzz test corpus
│   ├── valid_baseline.json
│   ├── malformed_*.json
│   ├── attack_*.json
│   └── edge_*.json
├── attestation_crash_corpus/     # Crash-inducing payloads
│   └── *.json
└── fixtures/                     # Test fixtures
    ├── hardware_profiles.py
    ├── wallet_addresses.json
    └── sample_blocks.json
```

---

## 10. Troubleshooting

### 10.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Tests fail with `Connection refused` | Test node not running | Start node with `--test-mode` |
| Fuzz tests too slow | Network latency | Use local server, adjust delay |
| Coverage too low | Missing test cases | Add tests for uncovered branches |
| Flaky integration tests | Timing issues | Add explicit waits, increase timeouts |

### 10.2 Debug Mode

```bash
# Run tests with debug output
pytest tests/ -v -s --log-cli-level=DEBUG

# Run specific test with pdb
pytest tests/test_fingerprint.py::test_valid_fingerprint --pdb

# Run fuzz test with verbose output
python3 tests/fuzz_attestation_runner.py --verbose --count 100
```

---

## 11. Contributing Tests

### 11.1 Adding New Tests

1. **Identify test target**: What function/workflow are you testing?
2. **Choose test level**: Unit, integration, or E2E?
3. **Write test**: Follow existing patterns in `tests/`
4. **Add fixtures**: Create reusable test data in `tests/fixtures/`
5. **Run tests**: Verify tests pass locally
6. **Update CI**: Add test to appropriate CI job if needed

### 11.2 Test Naming Convention

```python
# Unit tests
test_<function>_<scenario>_<expected_result>()

# Integration tests
test_<component_a>_to_<component_b>_<scenario>()

# E2E tests
test_e2e_<workflow_name>()

# Security tests
test_security_<attack_vector>()

# Fuzz tests
test_fuzz_<target>_<mutation_strategy>()
```

---

## 12. Resources

- **Existing Test Suite**: `tests/` directory
- **Fuzz Testing Guide**: `tests/ATTESTATION_FUZZ_README.md`
- **Pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **GitHub Actions**: https://docs.github.com/en/actions

---

## Summary

| Test Level | Purpose | When to Run | Tools |
|------------|---------|-------------|-------|
| **Unit** | Test individual components | Every commit | pytest, coverage |
| **Integration** | Test component interactions | PR checks | pytest, test node |
| **E2E** | Test complete workflows | Release candidates | pytest, docker |
| **Fuzz** | Find security vulnerabilities | CI/CD pipeline | Custom fuzz runner |
| **Security** | Verify security properties | Before releases | pytest, custom scripts |
| **Performance** | Measure performance metrics | Before releases | pytest, benchmarks |

This testing strategy ensures RustChain maintains high quality, security, and reliability as it grows.

---

**License:** Same as RustChain project license (MIT)
