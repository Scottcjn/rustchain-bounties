# RustChain API Load Test Suite

Load testing suite for RustChain API endpoints.

## Features

- **Concurrent request testing** - Test API under load
- **Multiple endpoints** - Balance, block, transaction, chain ID
- **Statistics** - Latency min/max/mean/median
- **Configurable** - Adjust request count and concurrent users

## Usage

### Quick Test

```bash
pip install -r requirements.txt
python load_test.py
```

### Custom Load

```python
from load_test import run_load_test

# Light load
run_load_test(num_requests=100, concurrent_users=10)

# Medium load
run_load_test(num_requests=1000, concurrent_users=50)

# Heavy load
run_load_test(num_requests=5000, concurrent_users=100)
```

## Endpoints Tested

1. `eth_getBalance` - Account balance query
2. `eth_blockNumber` - Latest block number
3. `eth_getTransactionByHash` - Transaction lookup
4. `eth_chainId` - Chain ID

## Metrics

- Requests per second
- Latency (min, max, mean, median, std dev)
- Success rate
- Error rate

---

Fixes #1614
