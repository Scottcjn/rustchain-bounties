# RustChain Integration Guide

**Version:** RIP-200 PoA (v2.2.1)  
**Audience:** Developers integrating RustChain into AI agents, applications, or services

This guide covers how to integrate with RustChain from various environments: direct REST API calls, the MCP server, Python code, Claude Code, and CrewAI. Choose the section most relevant to your use case.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [MCP Server Installation](#mcp-server-installation)
3. [Using from Python](#using-from-python)
4. [Using from Claude Code](#using-from-claude-code)
5. [Using from CrewAI](#using-from-crewai)
6. [Direct REST API Integration](#direct-rest-api-integration)
7. [Webhook Callbacks](#webhook-callbacks)
8. [Rate Limits and Best Practices](#rate-limits-and-best-practices)
9. [Testing with Dry Run](#testing-with-dry-run)

---

## Quick Start

If you just want to query RustChain data right now:

```bash
# Health check
curl -sk https://50.28.86.131/health | python3 -m json.tool

# List active miners
curl -sk https://50.28.86.131/api/miners | python3 -m json.tool

# Get epoch info
curl -sk https://50.28.86.131/epoch | python3 -m json.tool

# Check balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID" | python3 -m json.tool
```

> ⚠️ The node uses a self-signed certificate. Always use `-k` with curl or `verify=False` with Python requests in development.

---

## MCP Server Installation

The MCP server is the recommended integration path for AI agents. It exposes all RustChain tools via the [Model Context Protocol](https://modelcontextprotocol.io/).

### Prerequisites

- Python 3.8 or higher
- `uv` or `pip` package manager
- A RustChain node URL (default: `https://50.28.86.131`)

### Installation Steps

```bash
# 1. Navigate to the MCP server directory
cd integrations/rustchain-mcp

# 2. Create a Python virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test the server runs
python -m rustchain_mcp.server
# You should see: "MCP Server running on stdio"
```

### Configuration

Create a `.env` file or set environment variables:

```bash
# Primary node URL (default: https://50.28.86.131)
export RUSTCHAIN_PRIMARY_URL=https://50.28.86.131

# Comma-separated fallback node URLs
export RUSTCHAIN_FALLBACK_URLS=https://backup1.rustchain.io,https://backup2.rustchain.io

# Log level
export RUSTCHAIN_LOG_LEVEL=INFO
```

### Architecture

The MCP server uses a two-layer architecture:

```
┌─────────────────────────────────────────┐
│  MCP Client (Claude Code, CrewAI, etc)  │
└──────────────┬──────────────────────────┘
               │  JSON-RPC over stdio
┌──────────────▼──────────────────────────┐
│  rustchain_mcp/server.py (FastMCP)       │
│  - Tool definitions (@mcp.tool)          │
│  - Async request dispatching             │
└──────────────┬──────────────────────────┘
               │  httpx async HTTP calls
┌──────────────▼──────────────────────────┐
│  rustchain_mcp/client.py (RustChainClient)
│  - Node failover                         │
│  - SSL verification control              │
│  - Error translation                     │
└──────────────┬──────────────────────────┘
               │  HTTPS
┌──────────────▼──────────────────────────┐
│  RustChain Node (https://50.28.86.131)  │
└─────────────────────────────────────────┘
```

---

## Using from Python

For Python applications that aren't using an MCP-compatible agent framework, use the `RustChainClient` directly.

### Direct Client Usage

```python
import asyncio
import httpx
from integrations.rustchain_mcp.rustchain_mcp.client import RustChainClient


async def main():
    # Initialize client (reads RUSTCHAIN_PRIMARY_URL from env)
    client = RustChainClient.from_env()

    # Query health
    health = await client.health()
    print(f"Node healthy: {health['ok']}")
    print(f"Version: {health['version']}")

    # Get current epoch
    epoch = await client.epoch()
    print(f"Epoch {epoch['epoch']}: {epoch['enrolled_miners']} miners")

    # List miners
    miners = await client.miners()
    for miner in miners:
        print(f"  {miner['miner']}: {miner['hardware_type']} × {miner['antiquity_multiplier']}")

    # Check balance
    balance = await client.balance("victus-x86-scott")
    print(f"Balance: {balance['amount_rtc']} RTC")


asyncio.run(main())
```

### Using `httpx` Directly (No Client Wrapper)

```python
import httpx
import json

BASE_URL = "https://50.28.86.131"
VERIFY = False  # Self-signed cert

def get_epoch():
    with httpx.Client(verify=VERIFY) as client:
        r = client.get(f"{BASE_URL}/epoch")
        r.raise_for_status()
        return r.json()

def get_miners():
    with httpx.Client(verify=VERIFY) as client:
        r = client.get(f"{BASE_URL}/api/miners")
        r.raise_for_status()
        return r.json()

def get_balance(miner_id: str):
    with httpx.Client(verify=VERIFY) as client:
        r = client.get(f"{BASE_URL}/wallet/balance", params={"miner_id": miner_id})
        r.raise_for_status()
        return r.json()

# Example usage
epoch = get_epoch()
print(f"Current epoch: {epoch['epoch']}")
print(f"Reward pot: {epoch['epoch_pot']} RTC")

miners = get_miners()
print(f"Active miners: {len(miners)}")
```

### Using `requests` (Synchronous)

```python
import requests

BASE_URL = "https://50.28.86.131"

def health_check():
    r = requests.get(f"{BASE_URL}/health", verify=False)
    r.raise_for_status()
    return r.json()

def get_balance(miner_id):
    r = requests.get(
        f"{BASE_URL}/wallet/balance",
        params={"miner_id": miner_id},
        verify=False
    )
    r.raise_for_status()
    return r.json()

# Check eligibility
def check_eligibility(miner_id):
    r = requests.get(
        f"{BASE_URL}/lottery/eligibility",
        params={"miner_id": miner_id},
        verify=False
    )
    r.raise_for_status()
    return r.json()
```

### Handling the Self-Signed Certificate

**Development only** — in production, install the node's CA certificate:

```python
import httpx

# Option 1: Disable verification (INSECURE — development only)
client = httpx.Client(verify=False)

# Option 2: Provide a custom CA bundle
client = httpx.Client(verify="/path/to/rustchain-ca.crt")

# Option 3: Configure system CA bundle
# On Ubuntu/Debian:
#   sudo cp rustchain-ca.crt /usr/local/share/ca-certificates/
#   sudo update-ca-certificates
```

---

## Using from Claude Code

Claude Code natively supports the MCP protocol. Once the RustChain MCP server is registered, all 34 tools are available as natural-language commands.

### Register the MCP Server

```bash
# From the rustchain-bounties repo root
cd integrations/rustchain-mcp
claude mcp add rustchain "$(pwd)/run.sh"
```

The `run.sh` script activates the venv and runs the server:
```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -f .venv/bin/activate ] && source .venv/bin/activate
python -m rustchain_mcp.server
```

### Example Claude Code Sessions

**Check node health:**
```
Is the RustChain node healthy?
```
→ Calls `rustchain_health()`

**Query a miner's balance:**
```
What's the RTC balance for miner "victus-x86-scott"?
```
→ Calls `rustchain_balance(miner_id="victus-x86-scott")`

**List all miners:**
```
Show me all active RustChain miners with their multipliers
```
→ Calls `rustchain_miners()` and formats the table

**Check lottery eligibility:**
```
Am I eligible for the epoch 73 lottery?
```
→ Calls `rustchain_lottery_eligibility(miner_id="YOUR_MINER_ID")`

**Check BoTTube trending:**
```
What's trending on BoTTube right now?
```
→ Calls `bottube_trending()`

**Discover other agents on Beacon:**
```
Who else is online on the Beacon network?
```
→ Calls `beacon_discover()`

### Using MCP Tools Directly in Claude Code

You can also invoke tools explicitly:

```
/mcp rustchain_health
/mcp rustchain_epoch
/mcp rustchain_miners
```

---

## Using from CrewAI

[CrewAI](https://crewai.com) is a framework for orchestrating multi-agent workflows. The RustChain MCP server can be registered as a CrewAI tool provider.

### Setup

```python
# crewai_integration.py
import os
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from mcp.client import StdioMCPClient
from mcp import Client

# Register the RustChain MCP server as a tool
class RustChainMCPWrapper(BaseTool):
    name = "rustchain_mcp"
    description = "Access to RustChain network via MCP protocol"

    def __init__(self):
        super().__init__()
        self.mcp_client = None

    def connect(self):
        self.mcp_client = StdioMCPClient(
            command="python",
            args=["-m", "rustchain_mcp.server"],
            cwd="integrations/rustchain-mcp"
        )
        self.mcp_client.__enter__()

    def disconnect(self):
        if self.mcp_client:
            self.mcp_client.__exit__(None, None, None)

    def run(self, tool_name: str, **kwargs):
        """Execute an MCP tool by name with arguments."""
        return self.mcp_client.call_tool(tool_name, kwargs)


# Define a RustChain analyst agent
analyst = Agent(
    role="RustChain Analyst",
    goal="Monitor the RustChain network and report on miner activity",
    backstory="You are an expert in the RustChain RIP-200 protocol and blockchain analytics.",
    tools=[RustChainMCPWrapper()]
)

# Define tasks
monitor_task = Task(
    description="Check the current epoch number, enrolled miner count, and reward pot.",
    agent=analyst,
    expected_output="A summary of current epoch stats"
)

report_task = Task(
    description="List the top 5 miners by antiquity multiplier and their entropy scores.",
    agent=analyst,
    expected_output="A formatted table of top miners"
)

# Run the crew
crew = Crew(agents=[analyst], tasks=[monitor_task, report_task])
results = crew.kickoff()
print(results)
```

### MCP Server Registration for CrewAI

Alternatively, use the `MCPClient` from the `mcp` Python package directly in your CrewAI agents:

```python
from mcp import Client
import asyncio

async def get_rustchain_tools():
    async with Client(
        command="python",
        args=["-m", "rustchain_mcp.server"],
        cwd="integrations/rustchain-mcp"
    ) as client:
        tools = await client.list_tools()
        return [tool.name for tool in tools]
```

---

## Direct REST API Integration

Any HTTP-capable environment can integrate with RustChain directly.

### cURL Examples

```bash
# Health check
curl -sk https://50.28.86.131/health

# Epoch info
curl -sk https://50.28.86.131/epoch

# Miner list
curl -sk https://50.28.86.131/api/miners

# Wallet balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=victus-x86-scott"

# Lottery eligibility
curl -sk "https://50.28.86.131/lottery/eligibility?miner_id=victus-x86-scott"

# Network stats
curl -sk https://50.28.86.131/stats

# Get attestation challenge
curl -sk -X POST https://50.28.86.131/attest/challenge \
  -H 'Content-Type: application/json' \
  -d '{}'

# Enroll for epoch
curl -sk -X POST https://50.28.86.131/epoch/enroll \
  -H 'Content-Type: application/json' \
  -d '{"miner_id": "victus-x86-scott"}'
```

### JavaScript / Node.js

```javascript
const https = require('https');

const BASE_URL = 'https://50.28.86.131';
const OPTIONS = { rejectUnauthorized: false }; // Self-signed cert

function request(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const reqOptions = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method,
      ...OPTIONS
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch {
          resolve(data);
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Usage
(async () => {
  const epoch = await request('GET', '/epoch');
  console.log(`Epoch ${epoch.epoch}: ${epoch.enrolled_miners} miners, ${epoch.epoch_pot} RTC pot`);

  const miners = await request('GET', '/api/miners');
  const top = miners.sort((a, b) => b.antiquity_multiplier - a.antiquity_multiplier).slice(0, 5);
  console.table(top.map(m => ({
    miner: m.miner,
    hardware: m.device_arch,
    multiplier: m.antiquity_multiplier,
    entropy: m.entropy_score
  })));
})();
```

### Go

```go
package main

import (
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "time"
)

func main() {
    client := &http.Client{
        Timeout: 10 * time.Second,
        Transport: &http.Transport{
            TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, // dev only
        },
    }

    base, _ := url.Parse("https://50.28.86.131")

    // GET /epoch
    req, _ := http.NewRequest("GET", base.String()+"/epoch", nil)
    resp, err := client.Do(req)
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    var epoch struct {
        Epoch           int     `json:"epoch"`
        Slot            int     `json:"slot"`
        EnrolledMiners int     `json:"enrolled_miners"`
        EpochPot       float64 `json:"epoch_pot"`
    }
    body, _ := io.ReadAll(resp.Body)
    json.Unmarshal(body, &epoch)

    fmt.Printf("Epoch %d: %d miners, %.1f RTC pot\n",
        epoch.Epoch, epoch.EnrolledMiners, epoch.EpochPot)
}
```

### Ruby

```ruby
require 'net/http'
require 'json'
require 'uri'

BASE_URL = 'https://50.28.86.131'

def get(path)
  uri = URI.join(BASE_URL, path)
  Net::HTTP.start(uri.host, uri.port, use_ssl: true) do |http|
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE # dev only
    response = http.get(uri.path)
    JSON.parse(response.body)
  end
end

# Get epoch info
epoch = get('/epoch')
puts "Epoch #{epoch['epoch']}: #{epoch['enrolled_miners']} miners"

# Get miner list and sort by multiplier
miners = get('/api/miners')
top = miners.sort_by { |m| -m['antiquity_multiplier'] }.first(5)
top.each { |m| puts "  #{m['miner']}: #{m['antiquity_multiplier']}x (#{m['device_arch']})" }
```

---

## Webhook Callbacks

For production integrations that need real-time event notifications, register webhooks for attestation events. The node will `POST` to your endpoint when events occur.

### Registering a Webhook

Contact the RustChain team or submit a PR to `docs/WEBHOOKS.md` to register your endpoint URL. Approved webhooks receive `POST` requests for these events:

| Event | Trigger |
|---|---|
| `attestation.success` | A miner successfully attests |
| `attestation.failed` | An attestation attempt fails |
| `epoch.started` | A new epoch begins |
| `lottery.drawn` | The lottery for an epoch is completed |
| `miner.enrolled` | A miner enrolls in an epoch |
| `miner.payout` | A payout is triggered for a miner |

### Webhook Payload Format

```json
{
  "event": "attestation.success",
  "timestamp": "2025-01-20T11:30:00Z",
  "data": {
    "miner_id": "victus-x86-scott",
    "attestation_id": "att_f9b3c2a1e8d4...",
    "entropy_score": 0.91,
    "slot": 10554
  }
}
```

### Verifying Webhook Signatures

All webhook payloads are signed with the node's HMAC-SHA256 key. Verify the `X-RustChain-Signature` header:

```python
import hmac
import hashlib

WEBHOOK_SECRET = "your-webhook-secret-from-node-operator"

def verify_webhook(payload_bytes: bytes, signature_header: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

---

## Rate Limits and Best Practices

### Rate Limits

| Endpoint Type | Limit | Backoff Strategy |
|---|---|---|
| Read endpoints (`GET`) | 120 req/min per IP | None needed unless exceeding limit |
| Write endpoints (`POST`) | 3–10 req/min per miner_id | Exponential backoff, 1s base, 60s max |
| Attestation (`POST /attest/*`) | 6 req/min per miner_id | Respect `retry_after` from 429 response |

### Best Practices

**1. Cache read responses**
Most data (epoch, miner list, stats) doesn't change second-to-second. Cache responses for at least 30 seconds:
```python
from functools import lru_cache
import time

cache = {}

def cached_get(url, ttl=30):
    now = time.time()
    if url in cache and cache[url]['expires'] > now:
        return cache[url]['data']
    data = requests.get(url, verify=False).json()
    cache[url] = {'data': data, 'expires': now + ttl}
    return data
```

**2. Handle failover gracefully**
The `RustChainClient` handles node failover automatically. For direct API usage:
```python
PRIMARY = "https://50.28.86.131"
BACKUPS = ["https://backup1.rustchain.io"]

def get_with_failover(path):
    for node in [PRIMARY] + BACKUPS:
        try:
            r = requests.get(f"{node}{path}", verify=False, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            continue
    raise RuntimeError("All RustChain nodes unreachable")
```

**3. Use the correct balance field**
Use `amount_i64` for precise comparisons (integer arithmetic avoids floating-point errors):
```python
# BAD — floating point
if balance['amount_rtc'] >= 10.0:
    transfer(...)

# GOOD — integer comparison
if balance['amount_i64'] >= 10_000_000:  # 10 RTC in raw units
    transfer(...)
```

**4. Don't poll continuously**
For monitoring, poll at most every 30 seconds for read endpoints. For production monitoring, use Prometheus metrics (`/metrics`) if available, or set up a webhook.

**5. Store challenge nonces safely**
Attestation challenge nonces are single-use and expire in 300 seconds. Don't store them long-term.

---

## Testing with Dry Run

### MCP Server Dry Run

When using the MCP server, several tools support a `dry_run` parameter (or equivalent):

```python
# In the RustChainClient, add ?dry_run=1 for endpoints that support it:
# POST /wallet/transfer/signed?dry_run=true
# Validates the transaction without broadcasting

signed_tx = sign_transaction(...)
r = requests.post(
    f"{BASE_URL}/wallet/transfer/signed",
    json={"signed_tx_hex": signed_tx, "broadcast": False},
    verify=False
)
result = r.json()
if result.get('valid'):
    print("Transaction is valid. Ready to broadcast.")
```

### Miner Dry Run Mode

The miner script supports `--dry-run` for testing attestation flow without creating on-chain records:

```bash
python3 miners/linux/rustchain_linux_miner.py \
  --wallet YOUR_MINER_ID \
  --dry-run \
  --fingerprint-only
```

In `--fingerprint-only` mode:
- Hardware fingerprinting runs but is not submitted
- Entropy score is calculated and displayed but not stored on-chain
- Useful for testing hardware detection before committing to real attestation

### Testing Node Connectivity

```bash
# Test 1: Basic connectivity
curl -sk https://50.28.86.131/health | jq .ok

# Test 2: Measure latency
curl -sk -w "\nTime: %{time_total}s\n" https://50.28.86.131/health -o /dev/null

# Test 3: Check if your miner_id is enrolled
curl -sk https://50.28.86.131/api/miners | jq '.[] | select(.miner == "YOUR_MINER_ID")'

# Test 4: Verify attestation challenge works
curl -sk -X POST https://50.28.86.131/attest/challenge | jq .
```
