# RustChain Python SDK Tutorial

Learn to interact with RustChain programmatically using Python.

## Installation

The RustChain Python SDK is a lightweight wrapper around the REST API.

```bash
pip install requests
```

## Quick Start

```python
import requests
import json

class RustChainClient:
    def __init__(self, node_url="https://50.28.86.131"):
        self.node_url = node_url
        self.session = requests.Session()
        self.session.verify = False  # Self-signed cert
    
    def get_balance(self, wallet_id):
        url = f"{self.node_url}/wallet/balance"
        params = {"miner_id": wallet_id}
        response = self.session.get(url, params=params)
        return response.json()
    
    def get_epoch(self):
        url = f"{self.node_url}/epoch"
        response = self.session.get(url)
        return response.json()
    
    def get_health(self):
        url = f"{self.node_url}/health"
        response = self.session.get(url)
        return response.json()

client = RustChainClient()
balance = client.get_balance("my-wallet-id")
print(f"Balance: {balance['balance']} RTC")
```

## API Methods

### Check Wallet Balance

```python
def get_balance(wallet_id):
    client = RustChainClient()
    result = client.get_balance(wallet_id)
    return result['balance']

balance = get_balance("my-wallet-id")
print(f"You have {balance} RTC")
```

### Transfer RTC

```python
import hashlib
import time

def transfer_rtc(from_wallet, to_wallet, amount, private_key):
    client = RustChainClient()
    
    timestamp = int(time.time())
    payload = f"{from_wallet}:{to_wallet}:{amount}:{timestamp}"
    signature = hashlib.sha256(f"{payload}:{private_key}".encode()).hexdigest()
    
    url = f"{client.node_url}/wallet/transfer"
    data = {
        "from_wallet": from_wallet,
        "to_wallet": to_wallet,
        "amount": amount,
        "signature": signature
    }
    
    response = client.session.post(url, json=data)
    return response.json()

result = transfer_rtc(
    from_wallet="alice",
    to_wallet="bob",
    amount=10.0,
    private_key="your_private_key"
)
print(f"Transfer status: {result['status']}")
```

### Get Active Miners

```python
def get_active_miners():
    client = RustChainClient()
    url = f"{client.node_url}/api/miners"
    response = client.session.get(url)
    return response.json()

miners = get_active_miners()
print(f"Total miners: {miners['total_miners']}")

for miner in miners['miners'][:5]:
    print(f"Wallet: {miner['wallet_id']}, Hardware: {miner['hardware']}, Multiplier: {miner['multiplier']}x")
```

### Monitor Epoch Changes

```python
import time

def wait_for_next_epoch():
    client = RustChainClient()
    current_epoch = client.get_epoch()['epoch']
    
    print(f"Current epoch: {current_epoch}")
    print("Waiting for next epoch...")
    
    while True:
        time.sleep(30)
        epoch_data = client.get_epoch()
        if epoch_data['epoch'] > current_epoch:
            print(f"New epoch: {epoch_data['epoch']}")
            return epoch_data

next_epoch = wait_for_next_epoch()
print(f"Reward per epoch: {next_epoch['reward_per_epoch']} RTC")
```

## Advanced Usage

### Async Support

```python
import asyncio
import aiohttp

class AsyncRustChainClient:
    def __init__(self, node_url="https://50.28.86.131"):
        self.node_url = node_url
    
    async def get_balance(self, wallet_id):
        url = f"{self.node_url}/wallet/balance"
        params = {"miner_id": wallet_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, ssl=False) as response:
                return await response.json()
    
    async def get_multiple_balances(self, wallet_ids):
        tasks = [self.get_balance(wid) for wid in wallet_ids]
        return await asyncio.gather(*tasks)

async def main():
    client = AsyncRustChainClient()
    wallet_ids = ["alice", "bob", "charlie"]
    balances = await client.get_multiple_balances(wallet_ids)
    
    for wid, balance in zip(wallet_ids, balances):
        print(f"{wid}: {balance['balance']} RTC")

asyncio.run(main())
```

### WebSocket Client

```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

def on_open(ws):
    subscribe_msg = {
        "action": "subscribe",
        "channel": "balance",
        "wallet_id": "my-wallet-id"
    }
    ws.send(json.dumps(subscribe_msg))

ws = websocket.WebSocketApp(
    "wss://50.28.86.131/ws",
    on_message=on_message,
    on_open=on_open
)

ws.run_forever(sslopt={"cert_reqs": 0})
```

### Balance Monitor Bot

```python
import time
import smtplib
from email.mime.text import MIMEText

class BalanceMonitor:
    def __init__(self, wallet_id, threshold=100.0, check_interval=300):
        self.wallet_id = wallet_id
        self.threshold = threshold
        self.check_interval = check_interval
        self.client = RustChainClient()
    
    def check_balance(self):
        balance_data = self.client.get_balance(self.wallet_id)
        return balance_data['balance']
    
    def send_alert(self, balance):
        msg = MIMEText(f"RustChain balance alert: {balance} RTC reached threshold {self.threshold}")
        msg['Subject'] = 'RustChain Balance Alert'
        msg['From'] = 'bot@rustchain.org'
        msg['To'] = 'your@email.com'
        
        with smtplib.SMTP('localhost') as s:
            s.send_message(msg)
    
    def run(self):
        print(f"Monitoring wallet {self.wallet_id} for threshold {self.threshold} RTC")
        
        while True:
            try:
                balance = self.check_balance()
                print(f"Current balance: {balance} RTC")
                
                if balance >= self.threshold:
                    self.send_alert(balance)
                    print(f"Alert sent! Threshold reached.")
                    break
                
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

monitor = BalanceMonitor(
    wallet_id="my-wallet-id",
    threshold=100.0,
    check_interval=300
)
monitor.run()
```

## Mining Integration

### Automated Miner Manager

```python
import subprocess
import time

class MinerManager:
    def __init__(self, wallet_id, node_url="https://50.28.86.131"):
        self.wallet_id = wallet_id
        self.node_url = node_url
        self.process = None
        self.client = RustChainClient(node_url)
    
    def start_miner(self):
        cmd = [
            "python3", "rustchain_miner.py",
            "--wallet", self.wallet_id,
            "--node", self.node_url
        ]
        self.process = subprocess.Popen(cmd)
        print(f"Miner started with PID {self.process.pid}")
    
    def stop_miner(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("Miner stopped")
    
    def get_earnings(self):
        balance_data = self.client.get_balance(self.wallet_id)
        return balance_data['balance']
    
    def run_for_duration(self, hours):
        self.start_miner()
        start_balance = self.get_earnings()
        
        time.sleep(hours * 3600)
        
        self.stop_miner()
        end_balance = self.get_earnings()
        
        earnings = end_balance - start_balance
        print(f"Earned {earnings} RTC in {hours} hours")
        return earnings

manager = MinerManager(wallet_id="my-wallet-id")
earnings = manager.run_for_duration(hours=1)
```

## Error Handling

```python
import requests
from requests.exceptions import RequestException, Timeout

def safe_api_call(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
        except RequestException as e:
            print(f"Request error: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

client = RustChainClient()
balance = safe_api_call(client.get_balance, "my-wallet-id")
```

## Testing

```python
import unittest
from unittest.mock import patch, Mock

class TestRustChainClient(unittest.TestCase):
    def setUp(self):
        self.client = RustChainClient()
    
    @patch('requests.Session.get')
    def test_get_balance(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "wallet_id": "test",
            "balance": 50.0,
            "pending": 0.0
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_balance("test")
        self.assertEqual(result['balance'], 50.0)
    
    @patch('requests.Session.get')
    def test_get_epoch(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "epoch": 12345,
            "reward_per_epoch": 1.5
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_epoch()
        self.assertEqual(result['epoch'], 12345)

if __name__ == '__main__':
    unittest.main()
```

## Next Steps

- [API Reference](api-reference.md) - Complete API documentation
- [Miner Setup Guide](miner-setup-guide.md) - Set up mining
- [Node Operator Guide](node-operator-guide.md) - Run your own node
