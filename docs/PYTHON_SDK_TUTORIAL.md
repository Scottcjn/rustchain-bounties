# RustChain Python SDK Tutorial

Complete tutorial for building applications with the RustChain Python SDK.

**Build RTC-powered applications** with simple Python code. Perfect for AI agents, bots, and automated systems.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [SDK Reference](#sdk-reference)
- [Code Examples](#code-examples)
- [Advanced Usage](#advanced-usage)
- [Best Practices](#best-practices)

---

## Installation

### Method 1: pip install (Recommended)

```bash
pip install rustchain-sdk
```

### Method 2: From Source

```bash
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/sdk
pip install -e .
```

### Method 3: Standalone (No Installation)

```python
# Download the SDK module
import urllib.request
urllib.request.urlretrieve(
    'https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/sdk/rustchain.py',
    'rustchain.py'
)

# Import and use
from rustchain import RustChainAPI
```

---

## Quick Start

### Basic Usage

```python
from rustchain import RustChainAPI

# Initialize the SDK
api = RustChainAPI()

# Check wallet balance
balance = api.get_balance("your-wallet-id")
print(f"Balance: {balance['amount_rtc']} RTC")

# Get network info
epoch = api.get_epoch()
print(f"Current epoch: {epoch['epoch']}")

# List active miners
miners = api.get_miners()
print(f"Active miners: {len(miners)}")
```

### AI Agent Example

```python
#!/usr/bin/env python3
"""
RustChain AI Agent - Automated bounty hunter
Monitors bounties, claims them, and tracks earnings
"""

from rustchain import RustChainAPI
import time
import requests

class RustChainAgent:
    def __init__(self, wallet_id, github_token=None):
        self.api = RustChainAPI()
        self.wallet_id = wallet_id
        self.github_token = github_token
        
    def check_balance(self):
        """Check current RTC balance"""
        balance = self.api.get_balance(self.wallet_id)
        return balance['amount_rtc']
    
    def monitor_bounties(self):
        """Monitor GitHub issues for new bounties"""
        url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
        params = {"labels": "bounty", "state": "open"}
        
        response = requests.get(url, params=params)
        bounties = response.json()
        
        return [b for b in bounties if "claim" not in b['body'].lower()]
    
    def claim_bounty(self, issue_number, approach):
        """Claim a bounty by commenting on the issue"""
        if not self.github_token:
            print("GitHub token required to claim bounties")
            return False
            
        comment = f"""**Claim**
- Wallet: {self.wallet_id}
- Agent/Handle: RustChain AI Agent
- Approach: {approach}
"""
        
        url = f"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues/{issue_number}/comments"
        headers = {"Authorization": f"token {self.github_token}"}
        
        response = requests.post(url, json={"body": comment}, headers=headers)
        return response.status_code == 201
    
    def run(self):
        """Main agent loop"""
        print(f"🤖 RustChain Agent starting (wallet: {self.wallet_id})")
        
        while True:
            try:
                # Check balance
                balance = self.check_balance()
                print(f"💰 Current balance: {balance} RTC")
                
                # Monitor bounties
                bounties = self.monitor_bounties()
                print(f"🎯 Found {len(bounties)} unclaimed bounties")
                
                # Auto-claim simple bounties
                for bounty in bounties:
                    if "documentation" in bounty['title'].lower():
                        print(f"📝 Claiming documentation bounty: {bounty['title']}")
                        self.claim_bounty(bounty['number'], "AI-generated documentation with examples")
                        break
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)

# Usage
if __name__ == "__main__":
    agent = RustChainAgent("ai-agent-wallet", github_token="your_github_token")
    agent.run()
```

---

## SDK Reference

### RustChainAPI Class

```python
class RustChainAPI:
    def __init__(self, base_url="https://50.28.86.131", verify_ssl=False):
        """
        Initialize RustChain API client
        
        Args:
            base_url (str): RustChain node URL
            verify_ssl (bool): Verify SSL certificates
        """
```

### Wallet Operations

#### get_balance(wallet_id)

```python
def get_balance(self, wallet_id):
    """
    Get wallet balance
    
    Args:
        wallet_id (str): Wallet identifier
        
    Returns:
        dict: {
            'amount_i64': int,
            'amount_rtc': float,
            'miner_id': str
        }
    """
    
# Example
balance = api.get_balance("my-wallet")
print(f"Balance: {balance['amount_rtc']} RTC")
```

#### transfer(from_wallet, to_wallet, amount, private_key)

```python
def transfer(self, from_wallet, to_wallet, amount, private_key):
    """
    Transfer RTC between wallets
    
    Args:
        from_wallet (str): Sender wallet ID
        to_wallet (str): Recipient wallet ID
        amount (float): Amount to transfer
        private_key (str): Sender's private key for signing
        
    Returns:
        dict: Transfer result
    """
    
# Example
result = api.transfer("sender-wallet", "recipient-wallet", 10.5, "private_key")
if result['success']:
    print(f"Transfer successful: {result['tx_hash']}")
```

### Network Information

#### get_epoch()

```python
def get_epoch(self):
    """
    Get current epoch information
    
    Returns:
        dict: {
            'blocks_per_epoch': int,
            'enrolled_miners': int,
            'epoch': int,
            'epoch_pot': float,
            'slot': int
        }
    """
    
# Example
epoch = api.get_epoch()
print(f"Epoch {epoch['epoch']}: {epoch['enrolled_miners']} miners, {epoch['epoch_pot']} RTC pot")
```

#### get_miners()

```python
def get_miners(self):
    """
    Get list of active miners
    
    Returns:
        list: List of miner objects with hardware info
    """
    
# Example
miners = api.get_miners()
for miner in miners:
    print(f"Miner: {miner['miner']}")
    print(f"Hardware: {miner['hardware_type']}")
    print(f"Multiplier: {miner['antiquity_multiplier']}x")
```

#### get_health()

```python
def get_health(self):
    """
    Check node health status
    
    Returns:
        dict: Node health information
    """
    
# Example
health = api.get_health()
if health['ok']:
    print(f"Node healthy, uptime: {health['uptime_s']}s")
```

---

## Code Examples

### Example 1: Balance Monitor

```python
#!/usr/bin/env python3
"""
Balance Monitor - Track RTC earnings over time
"""

from rustchain import RustChainAPI
import time
import json
from datetime import datetime

class BalanceMonitor:
    def __init__(self, wallet_id, log_file="balance_log.json"):
        self.api = RustChainAPI()
        self.wallet_id = wallet_id
        self.log_file = log_file
        self.history = self.load_history()
    
    def load_history(self):
        """Load balance history from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_history(self):
        """Save balance history to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def check_and_log(self):
        """Check balance and log to history"""
        try:
            balance_data = self.api.get_balance(self.wallet_id)
            balance = balance_data['amount_rtc']
            
            entry = {
                'timestamp': datetime.now().isoformat(),
                'balance': balance,
                'wallet_id': self.wallet_id
            }
            
            # Calculate earnings since last check
            if self.history:
                last_balance = self.history[-1]['balance']
                earnings = balance - last_balance
                entry['earnings'] = earnings
                
                if earnings > 0:
                    print(f"💰 Earned {earnings:.6f} RTC! New balance: {balance:.6f} RTC")
                else:
                    print(f"📊 Balance unchanged: {balance:.6f} RTC")
            else:
                print(f"📊 Initial balance: {balance:.6f} RTC")
            
            self.history.append(entry)
            self.save_history()
            
        except Exception as e:
            print(f"❌ Error checking balance: {e}")
    
    def show_stats(self):
        """Show earnings statistics"""
        if len(self.history) < 2:
            print("Not enough data for statistics")
            return
        
        total_earnings = sum(entry.get('earnings', 0) for entry in self.history)
        avg_earnings = total_earnings / (len(self.history) - 1)
        
        print(f"\n📈 Earnings Statistics:")
        print(f"Total earned: {total_earnings:.6f} RTC")
        print(f"Average per check: {avg_earnings:.6f} RTC")
        print(f"Checks logged: {len(self.history)}")
    
    def run(self, interval=300):
        """Run monitoring loop"""
        print(f"🔍 Starting balance monitor for {self.wallet_id}")
        
        while True:
            self.check_and_log()
            self.show_stats()
            print(f"⏰ Next check in {interval} seconds...\n")
            time.sleep(interval)

# Usage
if __name__ == "__main__":
    monitor = BalanceMonitor("your-wallet-id")
    monitor.run(interval=600)  # Check every 10 minutes
```

### Example 2: Mining Pool Manager

```python
#!/usr/bin/env python3
"""
Mining Pool Manager - Manage multiple miners and distribute rewards
"""

from rustchain import RustChainAPI
import time
import json

class MiningPool:
    def __init__(self, pool_wallet, miners_config):
        self.api = RustChainAPI()
        self.pool_wallet = pool_wallet
        self.miners = miners_config  # {wallet_id: share_percentage}
        
    def get_pool_balance(self):
        """Get total pool balance"""
        balance = self.api.get_balance(self.pool_wallet)
        return balance['amount_rtc']
    
    def distribute_rewards(self, amount_to_distribute):
        """Distribute rewards to pool members"""
        print(f"💰 Distributing {amount_to_distribute} RTC to pool members")
        
        for miner_wallet, share in self.miners.items():
            reward = amount_to_distribute * (share / 100)
            
            if reward > 0.001:  # Minimum distribution threshold
                try:
                    result = self.api.transfer(
                        self.pool_wallet, 
                        miner_wallet, 
                        reward,
                        "pool_private_key"  # Replace with actual key
                    )
                    
                    if result['success']:
                        print(f"✅ Sent {reward:.6f} RTC to {miner_wallet}")
                    else:
                        print(f"❌ Failed to send to {miner_wallet}")
                        
                except Exception as e:
                    print(f"❌ Error sending to {miner_wallet}: {e}")
    
    def check_miners_status(self):
        """Check which pool miners are active"""
        active_miners = self.api.get_miners()
        active_wallets = [m['miner'] for m in active_miners]
        
        print("👥 Pool Miner Status:")
        for wallet in self.miners:
            status = "🟢 Active" if wallet in active_wallets else "🔴 Inactive"
            print(f"  {wallet}: {status}")
    
    def run_pool(self):
        """Main pool management loop"""
        print(f"🏊 Starting mining pool: {self.pool_wallet}")
        last_balance = self.get_pool_balance()
        
        while True:
            try:
                current_balance = self.get_pool_balance()
                new_earnings = current_balance - last_balance
                
                if new_earnings > 0:
                    print(f"📈 Pool earned {new_earnings:.6f} RTC")
                    
                    # Keep 10% for pool operations, distribute 90%
                    distribute_amount = new_earnings * 0.9
                    self.distribute_rewards(distribute_amount)
                    
                    last_balance = current_balance - distribute_amount
                
                self.check_miners_status()
                print(f"💼 Pool balance: {current_balance:.6f} RTC\n")
                
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                print(f"❌ Pool error: {e}")
                time.sleep(300)

# Usage
pool_config = {
    "miner-1": 30,  # 30% share
    "miner-2": 25,  # 25% share
    "miner-3": 20,  # 20% share
    "miner-4": 25   # 25% share
}

pool = MiningPool("pool-wallet-id", pool_config)
pool.run_pool()
```

### Example 3: Bounty Hunter Bot

```python
#!/usr/bin/env python3
"""
Bounty Hunter Bot - Automatically find and claim bounties
"""

from rustchain import RustChainAPI
import requests
import time
import re

class BountyHunter:
    def __init__(self, wallet_id, github_token, skills=None):
        self.api = RustChainAPI()
        self.wallet_id = wallet_id
        self.github_token = github_token
        self.skills = skills or ["documentation", "python", "api"]
        self.claimed_bounties = set()
    
    def get_open_bounties(self):
        """Fetch open bounties from GitHub"""
        url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
        params = {"labels": "bounty", "state": "open"}
        
        response = requests.get(url, params=params)
        return response.json()
    
    def extract_bounty_value(self, issue_body):
        """Extract RTC value from bounty description"""
        match = re.search(r'(\d+)\s*RTC', issue_body, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def can_handle_bounty(self, issue):
        """Check if bot can handle this bounty"""
        title = issue['title'].lower()
        body = issue['body'].lower()
        
        # Check if it matches our skills
        for skill in self.skills:
            if skill in title or skill in body:
                return True
        return False
    
    def is_already_claimed(self, issue):
        """Check if bounty is already claimed"""
        comments_url = issue['comments_url']
        response = requests.get(comments_url)
        comments = response.json()
        
        for comment in comments:
            if "claim" in comment['body'].lower():
                return True
        return False
    
    def claim_bounty(self, issue):
        """Claim a bounty"""
        if issue['number'] in self.claimed_bounties:
            return False
        
        bounty_value = self.extract_bounty_value(issue['body'])
        
        comment = f"""**Claim**
- Wallet: {self.wallet_id}
- Agent/Handle: RustChain Bounty Hunter Bot
- Approach: Automated solution using Python SDK and best practices
- Estimated completion: 24-48 hours

🤖 This bounty will be completed by an AI agent specialized in {', '.join(self.skills)}.
Expected value: {bounty_value} RTC
"""
        
        url = f"https://api.github.com/repos/Scottcjn/rustchain-bounties/issues/{issue['number']}/comments"
        headers = {"Authorization": f"token {self.github_token}"}
        
        response = requests.post(url, json={"body": comment}, headers=headers)
        
        if response.status_code == 201:
            self.claimed_bounties.add(issue['number'])
            print(f"✅ Claimed bounty #{issue['number']}: {issue['title']} ({bounty_value} RTC)")
            return True
        else:
            print(f"❌ Failed to claim bounty #{issue['number']}")
            return False
    
    def hunt_bounties(self):
        """Main bounty hunting logic"""
        bounties = self.get_open_bounties()
        print(f"🎯 Found {len(bounties)} open bounties")
        
        for bounty in bounties:
            if self.can_handle_bounty(bounty) and not self.is_already_claimed(bounty):
                bounty_value = self.extract_bounty_value(bounty['body'])
                
                # Only claim bounties worth 5+ RTC
                if bounty_value >= 5:
                    print(f"🎯 Targeting bounty: {bounty['title']} ({bounty_value} RTC)")
                    self.claim_bounty(bounty)
                    time.sleep(5)  # Rate limiting
    
    def check_earnings(self):
        """Check current earnings"""
        balance = self.api.get_balance(self.wallet_id)
        print(f"💰 Current balance: {balance['amount_rtc']} RTC")
    
    def run(self):
        """Main bot loop"""
        print(f"🤖 Bounty Hunter Bot starting (wallet: {self.wallet_id})")
        print(f"🎯 Skills: {', '.join(self.skills)}")
        
        while True:
            try:
                self.check_earnings()
                self.hunt_bounties()
                print("⏰ Next hunt in 30 minutes...\n")
                time.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(300)

# Usage
bot = BountyHunter(
    wallet_id="bounty-hunter-bot",
    github_token="your_github_token",
    skills=["documentation", "python", "api", "tutorial", "guide"]
)
bot.run()
```

### Example 4: RTC Price Tracker

```python
#!/usr/bin/env python3
"""
RTC Price Tracker - Monitor RTC/wRTC price and portfolio value
"""

from rustchain import RustChainAPI
import requests
import time
import json

class RTCPriceTracker:
    def __init__(self, wallet_ids):
        self.api = RustChainAPI()
        self.wallet_ids = wallet_ids if isinstance(wallet_ids, list) else [wallet_ids]
        
    def get_wrtc_price(self):
        """Get wRTC price from DexScreener"""
        try:
            url = "https://api.dexscreener.com/latest/dex/tokens/12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"
            response = requests.get(url)
            data = response.json()
            
            if data['pairs']:
                price_usd = float(data['pairs'][0]['priceUsd'])
                return price_usd
            return 0.10  # Fallback reference price
            
        except Exception as e:
            print(f"❌ Error fetching price: {e}")
            return 0.10  # Fallback reference price
    
    def get_portfolio_value(self):
        """Calculate total portfolio value"""
        total_rtc = 0
        
        for wallet_id in self.wallet_ids:
            balance = self.api.get_balance(wallet_id)
            total_rtc += balance['amount_rtc']
        
        return total_rtc
    
    def track_prices(self):
        """Track and display price information"""
        wrtc_price = self.get_wrtc_price()
        total_rtc = self.get_portfolio_value()
        portfolio_usd = total_rtc * wrtc_price
        
        print(f"📊 RTC Price Tracker")
        print(f"💰 wRTC Price: ${wrtc_price:.6f}")
        print(f"🏦 Total RTC: {total_rtc:.6f}")
        print(f"💵 Portfolio Value: ${portfolio_usd:.2f}")
        
        # Individual wallet breakdown
        print(f"\n📋 Wallet Breakdown:")
        for wallet_id in self.wallet_ids:
            balance = self.api.get_balance(wallet_id)
            rtc_amount = balance['amount_rtc']
            usd_value = rtc_amount * wrtc_price
            print(f"  {wallet_id}: {rtc_amount:.6f} RTC (${usd_value:.2f})")
        
        return {
            'wrtc_price': wrtc_price,
            'total_rtc': total_rtc,
            'portfolio_usd': portfolio_usd
        }
    
    def run_tracker(self, interval=300):
        """Run price tracking loop"""
        print(f"📈 Starting RTC price tracker for {len(self.wallet_ids)} wallets")
        
        while True:
            try:
                self.track_prices()
                print(f"\n⏰ Next update in {interval} seconds...\n")
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Tracker error: {e}")
                time.sleep(60)

# Usage
tracker = RTCPriceTracker([
    "main-wallet",
    "mining-wallet", 
    "bounty-wallet"
])
tracker.run_tracker(interval=600)  # Update every 10 minutes
```

---

## Advanced Usage

### Custom API Client

```python
import requests
import hashlib
import time
from typing import Optional, Dict, Any

class AdvancedRustChainAPI:
    def __init__(self, base_url="https://50.28.86.131", timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False  # For self-signed certs
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def get_balance_with_history(self, wallet_id: str) -> Dict[str, Any]:
        """Get balance with transaction history"""
        balance = self._make_request('GET', '/wallet/balance', params={'miner_id': wallet_id})
        
        # Add mock transaction history (would be real API endpoint)
        balance['history'] = []
        return balance
    
    def create_signed_transfer(self, from_wallet: str, to_wallet: str, 
                            amount: float, private_key: str) -> Dict[str, Any]:
        """Create a cryptographically signed transfer"""
        timestamp = int(time.time())
        
        # Create transfer payload
        transfer_data = {
            'from': from_wallet,
            'to': to_wallet,
            'amount': amount,
            'timestamp': timestamp
        }
        
        # Sign the transfer (simplified - use proper crypto in production)
        message = f"{from_wallet}:{to_wallet}:{amount}:{timestamp}"
        signature = hashlib.sha256(f"{message}:{private_key}".encode()).hexdigest()
        
        transfer_data['signature'] = signature
        
        return self._make_request('POST', '/transfer', json=transfer_data)
    
    def batch_balance_check(self, wallet_ids: list) -> Dict[str, Dict]:
        """Check multiple wallet balances efficiently"""
        results = {}
        
        for wallet_id in wallet_ids:
            try:
                balance = self.get_balance(wallet_id)
                results[wallet_id] = balance
            except Exception as e:
                results[wallet_id] = {'error': str(e)}
        
        return results
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        health = self._make_request('GET', '/health')
        epoch = self._make_request('GET', '/epoch')
        miners = self._make_request('GET', '/api/miners')
        
        # Calculate additional stats
        total_multiplier = sum(m.get('antiquity_multiplier', 1.0) for m in miners)
        avg_multiplier = total_multiplier / len(miners) if miners else 1.0
        
        return {
            'health': health,
            'epoch': epoch,
            'miners': {
                'count': len(miners),
                'total_multiplier': total_multiplier,
                'avg_multiplier': avg_multiplier,
                'hardware_types': list(set(m.get('hardware_type', 'Unknown') for m in miners))
            }
        }
```

### Async API Client

```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class AsyncRustChainAPI:
    def __init__(self, base_url="https://50.28.86.131"):
        self.base_url = base_url.rstrip('/')
        
    async def _make_request(self, session: aiohttp.ClientSession, 
                          method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        async with session.request(method, url, ssl=False, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Get wallet balance asynchronously"""
        async with aiohttp.ClientSession() as session:
            return await self._make_request(
                session, 'GET', '/wallet/balance', 
                params={'miner_id': wallet_id}
            )
    
    async def get_multiple_balances(self, wallet_ids: List[str]) -> Dict[str, Dict]:
        """Get multiple wallet balances concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for wallet_id in wallet_ids:
                task = self._make_request(
                    session, 'GET', '/wallet/balance',
                    params={'miner_id': wallet_id}
                )
                tasks.append((wallet_id, task))
            
            results = {}
            for wallet_id, task in tasks:
                try:
                    balance = await task
                    results[wallet_id] = balance
                except Exception as e:
                    results[wallet_id] = {'error': str(e)}
            
            return results
    
    async def monitor_network(self, callback, interval=60):
        """Monitor network changes asynchronously"""
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    health = await self._make_request(session, 'GET', '/health')
                    epoch = await self._make_request(session, 'GET', '/epoch')
                    miners = await self._make_request(session, 'GET', '/api/miners')
                    
                    await callback({
                        'health': health,
                        'epoch': epoch,
                        'miners': miners,
                        'timestamp': time.time()
                    })
                    
            except Exception as e:
                print(f"❌ Monitor error: {e}")
            
            await asyncio.sleep(interval)

# Usage example
async def network_callback(data):
    print(f"📊 Epoch {data['epoch']['epoch']}: {len(data['miners'])} miners active")

async def main():
    api = AsyncRustChainAPI()
    
    # Check multiple balances concurrently
    wallets = ["wallet-1", "wallet-2", "wallet-3"]
    balances = await api.get_multiple_balances(wallets)
    
    for wallet, balance in balances.items():
        if 'error' not in balance:
            print(f"{wallet}: {balance['amount_rtc']} RTC")
    
    # Start network monitoring
    await api.monitor_network(network_callback, interval=300)

# Run async example
# asyncio.run(main())
```

---

## Best Practices

### Error Handling

```python
from rustchain import RustChainAPI
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustRustChainClient:
    def __init__(self, wallet_id, max_retries=3):
        self.api = RustChainAPI()
        self.wallet_id = wallet_id
        self.max_retries = max_retries
    
    def safe_api_call(self, func, *args, **kwargs):
        """Make API call with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"API call failed after {self.max_retries} attempts")
                    raise
    
    def get_balance_safely(self):
        """Get balance with error handling"""
        return self.safe_api_call(self.api.get_balance, self.wallet_id)
```

### Rate Limiting

```python
import time
from functools import wraps

class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove calls older than 1 minute
            self.calls = [call_time for call_time in self.calls if now - call_time < 60]
            
            # Check if we're at the limit
            if len(self.calls) >= self.calls_per_minute:
                sleep_time = 60 - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
            
            # Record this call
            self.calls.append(now)
            
            return func(*args, **kwargs)
        return wrapper

# Usage
@RateLimiter(calls_per_minute=30)
def get_balance(wallet_id):
    api = RustChainAPI()
    return api.get_balance(wallet_id)
```

### Configuration Management

```python
import json
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class RustChainConfig:
    wallet_id: str
    node_url: str = "https://50.28.86.131"
    github_token: Optional[str] = None
    check_interval: int = 300
    log_level: str = "INFO"
    
    @classmethod
    def from_file(cls, config_path: str):
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            wallet_id=os.getenv('RUSTCHAIN_WALLET_ID'),
            node_url=os.getenv('RUSTCHAIN_NODE_URL', "https://50.28.86.131"),
            github_token=os.getenv('GITHUB_TOKEN'),
            check_interval=int(os.getenv('CHECK_INTERVAL', '300')),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        with open(config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)

# Usage
config = RustChainConfig.from_env()
api = RustChainAPI(base_url=config.node_url)
```

### Testing

```python
import unittest
from unittest.mock import Mock, patch
from rustchain import RustChainAPI

class TestRustChainAPI(unittest.TestCase):
    def setUp(self):
        self.api = RustChainAPI()
        self.test_wallet = "test-wallet-id"
    
    @patch('requests.get')
    def test_get_balance(self, mock_get):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'amount_i64': 1000000,
            'amount_rtc': 1.0,
            'miner_id': self.test_wallet
        }
        mock_get.return_value = mock_response
        
        # Test the method
        balance = self.api.get_balance(self.test_wallet)
        
        # Assertions
        self.assertEqual(balance['amount_rtc'], 1.0)
        self.assertEqual(balance['miner_id'], self.test_wallet)
    
    @patch('requests.get')
    def test_get_miners(self, mock_get):
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                'miner': 'test-miner',
                'hardware_type': 'PowerPC G4',
                'antiquity_multiplier': 2.5
            }
        ]
        mock_get.return_value = mock_response
        
        # Test the method
        miners = self.api.get_miners()
        
        # Assertions
        self.assertEqual(len(miners), 1)
        self.assertEqual(miners[0]['antiquity_multiplier'], 2.5)

if __name__ == '__main__':
    unittest.main()
```

---

## Troubleshooting

### Common Issues

**SSL Certificate Errors:**
```python
# Disable SSL verification (development only)
api = RustChainAPI(verify_ssl=False)

# Or use custom certificate
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

**Connection Timeouts:**
```python
# Increase timeout
api = RustChainAPI(timeout=60)

# Add retry logic
def robust_api_call(func, *args, **kwargs):
    for i in range(3):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i == 2:
                raise
            time.sleep(2 ** i)
```

**Rate Limiting:**
```python
# Add delays between requests
import time

def rate_limited_requests():
    for wallet in wallet_list:
        balance = api.get_balance(wallet)
        print(f"{wallet}: {balance['amount_rtc']} RTC")
        time.sleep(1)  # 1 second delay
```

---

## Support & Resources

- **GitHub**: [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties)
- **API Docs**: [API_REFERENCE.md](./API_REFERENCE.md)
- **Examples**: [examples/](../examples/)
- **Issues**: [GitHub Issues](https://github.com/Scottcjn/rustchain-bounties/issues)

---

**Happy Coding! 🚀**

*Build the future of decentralized applications with RustChain.*

---

*Last updated: February 2026*  
*SDK Version: 1.0*