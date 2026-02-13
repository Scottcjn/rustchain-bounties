# RustChain Python SDK Tutorial

Getting started with the RustChain Python SDK for building applications on the RustChain network.

## Overview

The RustChain Python SDK provides a simple and powerful interface to interact with the RustChain network. Build miners, wallet tools, and automation scripts with ease.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-python-sdk.git
cd rustchain-python-sdk

# Install in development mode
pip install -e .

# Or install directly
pip install rustchain-sdk
```

### From PyPI (Coming Soon)

```bash
pip install rustchain-sdk
```

---

## Quick Start

### Basic Usage

```python
from rustchain import RustChain, Wallet

# Connect to node
node = RustChain(node_url="https://50.28.86.131")

# Check node health
health = node.health()
print(f"Node version: {health['version']}")
print(f"Uptime: {health['uptime_s']} seconds")

# Get current epoch
epoch = node.get_epoch()
print(f"Current epoch: {epoch['epoch']}")
```

### Wallet Operations

```python
from rustchain import Wallet

# Create a new wallet (generates random key)
wallet = Wallet()

# Or load from existing key
wallet = Wallet(private_key="your-hex-private-key")

# Get wallet ID (used for mining rewards)
miner_id = wallet.get_miner_id()
print(f"Wallet/Miner ID: {miner_id}")

# Check balance
balance = wallet.get_balance()
print(f"Balance: {balance['balance']} RTC")
print(f"Pending: {balance['pending_rewards']} RTC")
```

---

## Core Classes

### RustChain

Main class for interacting with the RustChain network.

```python
from rustchain import RustChain

node = RustChain(
    node_url="https://50.28.86.131",
    timeout=30,
    verify_ssl=False  # Set True in production
)
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `health()` | Check node health | dict |
| `get_epoch()` | Get current epoch info | dict |
| `get_miners()` | List active miners | list[dict] |
| `get_balance(miner_id)` | Get wallet balance | dict |
| `submit_attestation(miner_id, proof)` | Submit proof-of-work | dict |
| `get_block(height)` | Get block by height | dict |
| `get_transaction(tx_hash)` | Get transaction | dict |

#### Example: Monitor Network

```python
from rustchain import RustChain
import time

node = RustChain()

print("Monitoring RustChain network...")
print("-" * 40)

while True:
    # Check node health
    health = node.health()
    
    # Get epoch info
    epoch = node.get_epoch()
    
    # Get miner count
    miners = node.get_miners()
    
    print(f"Epoch: {epoch['epoch']} | "
          f"Miners: {len(miners)} | "
          f"Version: {health['version']}")
    
    time.sleep(60)  # Update every minute
```

---

### Wallet

Wallet class for managing keys and balances.

```python
from rustchain import Wallet

# Create new wallet
wallet = Wallet()

# Access properties
print(f"Miner ID: {wallet.miner_id}")
print(f"Public Key: {wallet.public_key}")
```

#### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_balance()` | Get current balance | dict |
| `generate_key()` | Generate new key pair | None (updates internally) |
| `sign(message)` | Sign a message | str (signature) |
| `verify(signature, message)` | Verify signature | bool |

#### Example: Automated Balance Checker

```python
from rustchain import Wallet
import time

# Load wallet (use environment variable in production)
wallet = Wallet(private_key="your-private-key")

wallets = [
    "wallet-1",
    "wallet-2", 
    "wallet-3"
]

print("Monitoring wallet balances...")
print("=" * 50)

while True:
    for wallet_id in wallets:
        try:
            balance = wallet.get_balance(miner_id=wallet_id)
            print(f"{wallet_id}: {balance['balance']} RTC "
                  f"(pending: {balance['pending_rewards']})")
        except Exception as e:
            print(f"{wallet_id}: Error - {e}")
    
    print("-" * 50)
    time.sleep(300)  # Check every 5 minutes
    print()
```

---

## Building a Miner Monitor

Create a comprehensive miner monitoring tool.

```python
#!/usr/bin/env python3
"""
RustChain Miner Monitor
Real-time monitoring of miner performance and rewards.
"""

from rustchain import RustChain
import time
import json
from datetime import datetime

class MinerMonitor:
    def __init__(self, node_url="https://50.28.86.131"):
        self.node = RustChain(node_url=node_url)
        self.miners = {}
    
    def fetch_all_miners(self):
        """Get list of all active miners."""
        return self.node.get_miners()
    
    def get_miner_stats(self, miner_id):
        """Get detailed stats for a specific miner."""
        balance = self.node.get_balance(miner_id)
        miners = self.fetch_all_miners()
        
        miner_data = next(
            (m for m in miners if m['miner'] == miner_id),
            None
        )
        
        return {
            'miner_id': miner_id,
            'balance': balance['balance'],
            'pending': balance['pending_rewards'],
            'hardware': miner_data['hardware_type'] if miner_data else 'Unknown',
            'multiplier': miner_data['antiquity_multiplier'] if miner_data else 1.0,
            'last_attest': miner_data['last_attest'] if miner_data else None
        }
    
    def print_leaderboard(self, limit=10):
        """Print top miners by balance."""
        miners = self.fetch_all_miners()
        
        # Get balances for top miners
        miner_balances = []
        for m in miners[:limit]:
            stats = self.get_miner_stats(m['miner'])
            miner_balances.append(stats)
        
        # Sort by balance
        miner_balances.sort(key=lambda x: float(x['balance']), reverse=True)
        
        print(f"\n{'='*60}")
        print(f"Top {limit} Miners by Balance")
        print(f"{'='*60}")
        print(f"{'Rank':<6}{'Miner ID':<35}{'Balance':<12}{'Hardware':<15}")
        print("-" * 60)
        
        for i, m in enumerate(miner_balances, 1):
            print(f"{i:<6}{m['miner_id'][:33]:<35}{m['balance']:<12}"
                  f"{m['hardware'][:13]:<15}")
        print()
    
    def monitor(self, interval=60):
        """Continuous monitoring loop."""
        print("Starting RustChain Miner Monitor...")
        print(f"Node: {self.node.node_url}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Updating...")
                
                self.print_leaderboard(limit=20)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")

if __name__ == "__main__":
    monitor = MinerMonitor()
    monitor.monitor(interval=120)
```

---

## Building an Automated Miner

Create an automated miner script.

```python
#!/usr/bin/env python3
"""
RustChain Automated Miner
Automates the mining process with health checks and auto-restart.
"""

import time
import logging
import sys
from datetime import datetime
from rustchain import RustChain, Wallet

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AutoMiner:
    def __init__(self, wallet_id, node_url="https://50.28.86.131"):
        self.wallet_id = wallet_id
        self.node = RustChain(node_url=node_url)
        self.running = True
        self.attestations = 0
        self.start_time = None
        
    def check_node_health(self):
        """Check if node is responsive."""
        try:
            health = self.node.health()
            return health.get('ok', False)
        except Exception as e:
            logger.error(f"Node health check failed: {e}")
            return False
    
    def submit_attestation(self):
        """Submit proof of work attestation."""
        try:
            # Generate proof (simplified - real implementation needed)
            proof = self.generate_proof()
            
            result = self.node.submit_attestation(
                miner_id=self.wallet_id,
                proof=proof
            )
            
            if result.get('success'):
                self.attestations += 1
                logger.info(f"Attestation submitted! Total: {self.attestations}")
                return True
            else:
                logger.warning(f"Attestation failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Attestation error: {e}")
            return False
    
    def generate_proof(self):
        """Generate proof-of-work (placeholder - implement actual POW)."""
        import hashlib
        import time as time_module
        
        timestamp = str(time_module.time())
        data = f"{self.wallet_id}{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:64]
    
    def check_balance(self):
        """Check current balance."""
        try:
            balance = self.node.get_balance(self.wallet_id)
            logger.info(f"Balance: {balance['balance']} RTC")
            return balance
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return None
    
    def run(self):
        """Main mining loop."""
        self.start_time = datetime.now()
        logger.info(f"Starting miner: {self.wallet_id}")
        logger.info(f"Node: {self.node.node_url}")
        
        while self.running:
            # Check node health
            if not self.check_node_health():
                logger.warning("Node unhealthy, waiting 30s...")
                time.sleep(30)
                continue
            
            # Submit attestation
            self.submit_attestation()
            
            # Check balance periodically
            if self.attestations % 10 == 0:
                self.check_balance()
            
            # Update stats
            elapsed = (datetime.now() - self.start_time).total_seconds()
            rate = self.attestations / (elapsed / 3600) if elapsed > 0 else 0
            logger.info(f"Rate: {rate:.2f} attestations/hour")
            
            # Wait before next attestation
            time.sleep(60)  # Adjust based on network difficulty
    
    def stop(self):
        """Stop the miner."""
        self.running = False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"Miner stopped. Total attestations: {self.attestations}")
        logger.info(f"Uptime: {elapsed:.0f} seconds")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RustChain Auto Miner')
    parser.add_argument('--wallet', required=True, help='Your wallet/miner ID')
    parser.add_argument('--node', default='https://50.28.86.131',
                        help='RustChain node URL')
    args = parser.parse_args()
    
    miner = AutoMiner(wallet_id=args.wallet, node_url=args.node)
    
    try:
        miner.run()
    except KeyboardInterrupt:
        miner.stop()
```

---

## Building Wallet Tools

Create useful wallet management tools.

```python
#!/usr/bin/env python3
"""
RustChain Wallet Manager
Manage multiple wallets and track balances.
"""

import json
from rustchain import Wallet

class WalletManager:
    def __init__(self):
        self.wallets = {}
    
    def create_wallet(self, name):
        """Create a new wallet."""
        wallet = Wallet()
        self.wallets[name] = {
            'wallet': wallet,
            'miner_id': wallet.miner_id,
            'private_key': wallet.private_key  # Store securely!
        }
        return wallet
    
    def load_wallet(self, name, private_key):
        """Load existing wallet."""
        wallet = Wallet(private_key=private_key)
        self.wallets[name] = {
            'wallet': wallet,
            'miner_id': wallet.miner_id,
            'private_key': private_key
        }
        return wallet
    
    def get_balance(self, name):
        """Get balance for a named wallet."""
        if name not in self.wallets:
            raise ValueError(f"Wallet '{name}' not found")
        return self.wallets[name]['wallet'].get_balance()
    
    def get_all_balances(self):
        """Get balances for all wallets."""
        balances = {}
        for name, data in self.wallets.items():
            try:
                balance = data['wallet'].get_balance()
                balances[name] = balance
            except Exception as e:
                balances[name] = {'error': str(e)}
        return balances
    
    def export_config(self, filepath='wallets.json'):
        """Export wallet configuration (excluding private keys!)."""
        export = {}
        for name, data in self.wallets.items():
            export[name] = {
                'miner_id': data['miner_id']
                # Never export private_key!
            }
        
        with open(filepath, 'w') as f:
            json.dump(export, f, indent=2)
        print(f"Config exported to {filepath}")

# Example usage
if __name__ == "__main__":
    manager = WalletManager()
    
    # Create a new wallet
    manager.create_wallet('main')
    
    # Load existing wallet
    # manager.load_wallet('backup', 'your-private-key-here')
    
    # Get all balances
    balances = manager.get_all_balances()
    
    for name, data in balances.items():
        print(f"{name}: {data['balance']} RTC")
```

---

## Error Handling

### Common Errors

```python
from rustchain import RustChain
from rustchain.exceptions import (
    NodeConnectionError,
    WalletError,
    AttestationError
)

node = RustChain()

try:
    balance = node.get_balance('my-wallet')
except NodeConnectionError as e:
    print(f"Cannot connect to node: {e}")
    # Retry or switch node
except WalletError as e:
    print(f"Wallet error: {e}")
except AttestationError as e:
    print(f"Attestation failed: {e}")
```

### Retry Logic

```python
from rustchain import RustChain
import time

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
            time.sleep(delay)

# Usage
node = RustChain()
balance = retry_with_backoff(
    lambda: node.get_balance('my-wallet')
)
```

---

## Best Practices

### 1. Secure Your Keys

```python
# ❌ Bad - Hardcoded keys
wallet = Wallet(private_key="abc123...")

# ✅ Good - Environment variables
import os
wallet = Wallet(private_key=os.environ['RUSTCHAIN_PRIVATE_KEY'])

# ✅ Better - Use a secrets manager
from keyring import get_password
private_key = get_password('rustchain', 'my-wallet')
wallet = Wallet(private_key=private_key)
```

### 2. Handle Rate Limits

```python
import time
from rustchain import RustChain

node = RustChain()

def rate_limited_request():
    """Make request with rate limiting."""
    response = node.health()
    
    # Check rate limit headers (if available)
    remaining = response.headers.get('X-RateLimit-Remaining')
    if remaining == '0':
        reset_time = response.headers.get('X-RateLimit-Reset')
        sleep_time = int(reset_time) - int(time.time())
        print(f"Rate limited. Sleeping {sleep_time}s...")
        time.sleep(sleep_time + 1)
```

### 3. Monitor Health

```python
from rustchain import RustChain
import logging

logger = logging.getLogger(__name__)

class MonitoredNode(RustChain):
    def health(self):
        start = time.time()
        result = super().health()
        duration = time.time() - start
        
        if duration > 5:
            logger.warning(f"Slow health check: {duration:.2f}s")
        elif result.get('ok') is False:
            logger.error("Node reported unhealthy!")
        
        return result
```

---

## Examples Repository

More examples available at:
- https://github.com/Scottcjn/rustchain-python-sdk/tree/main/examples

### Available Examples

| Example | Description |
|---------|-------------|
| `basic_usage.py` | Basic node and wallet operations |
| `miner_monitor.py` | Real-time miner monitoring |
| `auto_miner.py` | Automated mining script |
| `wallet_manager.py` | Multi-wallet management |
| `balance_tracker.py` | Historical balance tracking |
| `alert_system.py` | Custom alerting system |

---

## API Reference

See [API_REFERENCE.md](./API_REFERENCE.md) for complete API documentation.

---

## Support

- **Issues:** https://github.com/Scottcjn/rustchain-python-sdk/issues
- **Examples:** https://github.com/Scottcjn/rustchain-python-sdk/tree/main/examples
- **Docs:** https://docs.rustchain.io/python-sdk

---

*Last updated: 2026-02-12*
*SDK Version: 1.0.0*
