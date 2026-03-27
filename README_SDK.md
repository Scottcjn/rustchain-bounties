# RustChain Python SDK

Professional Python SDK for interacting with RustChain's Proof of Antiquity protocol.

## Installation

```bash
pip install rustchain-sdk
```

## Usage

```python
from rustchain import Miner

miner = Miner(wallet="YOUR_RTC_WALLET")
status = miner.get_status()
print(f"Miner status: {status}")
```
