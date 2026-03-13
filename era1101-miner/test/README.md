# ERA 1101 Miner - Test Suite

Test suite for the ERA 1101 RustChain miner implementation.

## Running Tests

```bash
# Run all tests
python -m pytest test/ -v

# Run specific test
python test/test_simulator.py
python test/test_sha256.py
python test/test_miner.py

# Run with coverage
python -m pytest test/ --cov=. --cov-report=html
```

## Test Files

- `test_simulator.py` - ERA 1101 CPU simulator tests
- `test_sha256.py` - SHA256 implementation tests
- `test_miner.py` - Mining core tests
- `test_network.py` - Network bridge tests
