# RustChain Load Test Suite

Load testing suite for the RustChain JSON-RPC API using Locust.

## Requirements

- Python 3.8+
- locust

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run with default settings (10 users, 1 spawn rate):
```bash
locust -f 1614-load-test/load_test.py --host https://rpc.rustchain.com
```

Run with custom settings:
```bash
locust -f 1614-load-test/load_test.py --host https://rpc.rustchain.com -u 100 -r 10
```

Run in headless mode:
```bash
locust -f 1614-load-test/load_test.py --host https://rpc.rustchain.com -u 50 -r 5 --headless --html report.html
```

## Test Endpoints

- `eth_blockNumber` - Get current block number
- `eth_getBlockByNumber` - Get block by number
- `eth_getBalance` - Get account balance
- `eth_gasPrice` - Get current gas price
- `eth_chainId` - Get chain ID
- `eth_getTransactionByHash` - Get transaction by hash

## Configuration

Set custom RPC URL:
```bash
export RUSTCHAIN_RPC_URL="https://rpc.rustchain.com"
locust -f 1614-load-test/load_test.py
```

## Output

Generate HTML report:
```bash
locust -f 1614-load-test/load_test.py --host https://rpc.rustchain.com --headless --html report.html
```

Generate CSV statistics:
```bash
locust -f 1614-load-test/load_test.py --host https://rpc.rustchain.com --headless --csv report
```

---

Fixes #1614
