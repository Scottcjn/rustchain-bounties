# RustChain Python SDK

Python client for interacting with the RustChain network.

## Installation

```bash
pip install rustchain
```

## Usage

Here is a quick example of how to use the RustChain SDK:

```python
from rustchain import RustChainClient

# Initialize the client
client = RustChainClient("https://api.rustchain.dev")

# Check node status
status = client.get_status()
print(f"Network Status: {status}")

# Send a transaction (example)
# tx_id = client.send_transaction("0xABC123...", amount=100)
# print(f"Transaction ID: {tx_id}")
```

For more details, see the documentation or the `tests/` directory.
