# RustChain Troubleshooting Guide

Common issues and solutions organized by category. Use this guide to diagnose and resolve problems when working with RustChain nodes, wallets, mining, and APIs.

---

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Wallet Problems](#wallet-problems)
3. [Mining / Validation Issues](#mining--validation-issues)
4. [API & RPC Issues](#api--rpc-issues)
5. [Smart Contract Issues](#smart-contract-issues)
6. [Sync Issues](#sync-issues)
7. [Performance Issues](#performance-issues)

---

## Connection Issues

### Node Won't Connect to Peers

**Symptoms:**
- `rustchain-node` starts but shows 0 peers
- Logs: `"no suitable peers found"` or `"handshake failed"`

**Solutions:**

1. **Check firewall rules:**
   ```bash
   # Ensure P2P port is open (default 30303)
   sudo ufw allow 30303/tcp
   sudo ufw allow 30303/udp
   ```

2. **Verify bootnodes are configured:**
   ```bash
   # Check your config includes bootnodes
   grep -i bootnode config.toml
   ```

3. **Test connectivity manually:**
   ```bash
   # Test if you can reach a known peer
   nc -zv peer.rustchain.io 30303
   ```

4. **Check NAT configuration:**
   - Ensure your router forwards port 30303 to your node
   - Verify your external IP is correct
   - Test with `curl ifconfig.me`

### RPC Connection Refused

**Symptoms:**
- `curl http://localhost:8545` returns "connection refused"
- dApps cannot connect to node

**Solutions:**

1. **Verify RPC is enabled:**
   ```bash
   # Check node is running with RPC enabled
   ps aux | grep rustchain
   # Should include --rpc flag
   ```

2. **Check bind address:**
   ```toml
   # config.toml - ensure not bound to 127.0.0.1 if accessing remotely
   [rpc]
   enabled = true
   address = "0.0.0.0"  # Not 127.0.0.1 for remote access
   port = 8545
   ```

3. **Verify port is listening:**
   ```bash
   netstat -tlnp | grep 8545
   # or
   ss -tlnp | grep 8545
   ```

### WebSocket Connection Drops

**Symptoms:**
- WebSocket connects but disconnects after a few seconds
- Subscriptions stop receiving events

**Solutions:**

1. **Check WebSocket configuration:**
   ```toml
   [ws]
   enabled = true
   address = "0.0.0.0"
   port = 8546
   max_connections = 100
   ```

2. **Implement reconnection logic:**
   ```javascript
   function connectWS(url, onMessage) {
     let ws = new WebSocket(url);
     ws.onmessage = onMessage;
     ws.onclose = () => {
       console.log("WebSocket closed, reconnecting in 5s...");
       setTimeout(() => connectWS(url, onMessage), 5000);
     };
     ws.onerror = (err) => {
       console.error("WebSocket error:", err);
       ws.close();
     };
     return ws;
   }
   ```

3. **Check proxy timeout settings** (if behind nginx/reverse proxy):
   ```nginx
   location /ws {
       proxy_pass http://localhost:8546;
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_read_timeout 3600s;  # Increase timeout
   }
   ```

---

## Wallet Problems

### Transaction Stuck as "Pending"

**Symptoms:**
- Transaction submitted but not confirmed
- Shows as "pending" in wallet for extended time

**Solutions:**

1. **Check current gas price:**
   ```bash
   curl -X POST http://localhost:8545 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}'
   ```

2. **Resend with higher gas price:**
   ```bash
   # Send the same transaction with higher gas price and same nonce
   rustchain-cli tx send \
     --to 0xRecipient \
     --value 1RTC \
     --gas-price 2000000000 \
     --nonce <STUCK_NONCE>
   ```

3. **Check if nonce is correct:**
   ```bash
   rustchain-cli tx nonce <YOUR_ADDRESS>
   ```

### MetaMask Shows Wrong Balance

**Symptoms:**
- Balance doesn't match explorer
- Shows 0 when tokens exist

**Solutions:**

1. **Reset MetaMask for RustChain:**
   - Settings → Advanced → Clear activity tab data
   - This resets the local nonce tracker without losing keys

2. **Verify RPC connection:**
   - Settings → Networks → RustChain → Check RPC URL
   - Ensure Chain ID is correct

3. **Force refresh:**
   - Click the account icon to trigger balance refresh
   - Or switch networks and switch back

### Cannot Import Private Key

**Symptoms:**
- `rustchain-cli account import` fails
- "invalid private key" error

**Solutions:**

1. **Check key format:**
   ```bash
   # Private key should be 64 hex characters (with or without 0x prefix)
   # Valid: 0x1234... (66 chars) or 1234... (64 chars)
   ```

2. **Try without 0x prefix:**
   ```bash
   rustchain-cli account import --private-key 1234567890abcdef...
   ```

3. **Check for hidden characters:**
   ```bash
   # Ensure no whitespace or newlines
   echo -n "YOUR_KEY" | wc -c  # Should be 64
   ```

### Forgot Keystore Password

**Symptoms:**
- Cannot unlock keystore file
- "invalid password" on every attempt

**Solutions:**

⚠️ **If the password is truly lost and no backup exists, the funds are inaccessible.**

1. **Try common variations:**
   - Check password manager
   - Try with/without spaces
   - Check keyboard layout differences

2. **Restore from seed phrase** (if available):
   ```bash
   rustchain-cli account import --mnemonic "word1 word2 ..."
   ```

3. **Check for backup keystores** in other locations

---

## Mining / Validation Issues

### Validator Not Producing Blocks

**Symptoms:**
- Node is synced but not in block producer rotation
- Logs show "not authorized to produce blocks"

**Solutions:**

1. **Verify validator status:**
   ```bash
   rustchain-cli validator status <YOUR_ADDRESS>
   # Check: is the address in the current validator set?
   ```

2. **Check Epoch timing:**
   - Validators rotate at Epoch boundaries
   - You may be in the validator set but waiting for the next Epoch
   - Check: `rustchain-cli epoch info`

3. **Ensure minimum stake:**
   ```bash
   rustchain-cli validator stake <YOUR_ADDRESS>
   # Verify stake meets minimum requirement
   ```

4. **Check node is fully synced:**
   ```bash
   rustchain-cli status
   # "synced" should be true
   ```

### Block Production Missed

**Symptoms:**
- Validator online but missing assigned slots
- Reduced block production rate

**Solutions:**

1. **Check system resources:**
   ```bash
   # CPU, memory, disk I/O
   top -bn1 | head -20
   df -h
   iostat -x 1 5
   ```

2. **Check network latency:**
   ```bash
   # High latency causes missed slots
   ping -c 10 peer.rustchain.io
   ```

3. **Review node logs for errors:**
   ```bash
   grep -i "error\|warn\|miss" /path/to/rustchain/logs/*.log | tail -50
   ```

4. **Recommended hardware:**
   - CPU: 4+ cores
   - RAM: 8 GB minimum
   - Disk: SSD with 500+ MB/s sequential read
   - Network: 100 Mbps+, low latency (<50ms to peers)

### Staking Rewards Not Received

**Symptoms:**
- Validator is producing blocks but rewards not appearing

**Solutions:**

1. **Check reward distribution schedule:**
   - Rewards are distributed at Epoch boundaries
   - Check current Epoch progress: `rustchain-cli epoch info`

2. **Verify reward address:**
   ```bash
   rustchain-cli validator info <YOUR_ADDRESS>
   # Check: coinbase / reward address is correct
   ```

3. **Check delegation status:**
   ```bash
   rustchain-cli delegation list --validator <YOUR_ADDRESS>
   ```

---

## API & RPC Issues

### Rate Limited (HTTP 429)

**Symptoms:**
- Requests return 429 errors
- "rate limit exceeded" in responses

**Solutions:**

1. **Implement exponential backoff:**
   ```python
   import time

   def retry_request(func, max_retries=5):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               wait = min(2 ** attempt, 60)
               time.sleep(wait)
       raise Exception("Max retries exceeded")
   ```

2. **Get an API key** for higher limits

3. **Cache responses** to reduce redundant requests

4. **Use batch requests** instead of individual calls

See [API Rate Limits documentation](../api-rate-limits/rate-limits.md) for full details.

### `eth_call` Returns Empty or Unexpected Results

**Symptoms:**
- Smart contract calls return `0x` or wrong values
- Different results at different block heights

**Solutions:**

1. **Specify block parameter:**
   ```json
   {
     "jsonrpc": "2.0",
     "method": "eth_call",
     "params": [{"to": "0x...", "data": "0x..."}, "latest"],
     "id": 1
   }
   ```

2. **Verify contract address is correct:**
   ```bash
   rustchain-cli contract code <ADDRESS>
   # Should return non-empty bytecode
   ```

3. **Check ABI encoding:**
   - Ensure function selector matches the ABI
   - Verify parameter encoding is correct
   - Use tools like `cast` from Foundry to debug

### `eth_getLogs` Timeout

**Symptoms:**
- Log queries take too long or time out
- "query timeout" error

**Solutions:**

1. **Reduce block range:**
   ```javascript
   // ❌ Too large range
   const logs = await provider.getLogs({
     fromBlock: 0,
     toBlock: "latest"
   });

   // ✅ Paginate in chunks
   const CHUNK = 5000;
   for (let from = startBlock; from < endBlock; from += CHUNK) {
     const to = Math.min(from + CHUNK - 1, endBlock);
     const logs = await provider.getLogs({
       fromBlock: from,
       toBlock: to,
       address: contractAddress
     });
     // Process logs...
   }
   ```

2. **Add address filter:**
   - Always specify `address` when possible to reduce search space

3. **Use specific topic filters:**
   - Filter by event signature to narrow results

---

## Smart Contract Issues

### Deployment Fails with "Out of Gas"

**Symptoms:**
- Transaction mined but contract not created
- Receipt shows `gasUsed == gasLimit` and `status: 0`

**Solutions:**

1. **Increase gas limit:**
   ```bash
   # Estimate gas first
   cast estimate --rpc-url https://rpc.rustchain.io --create <BYTECODE>
   
   # Deploy with extra buffer (2x estimated)
   cast send --rpc-url https://rpc.rustchain.io \
     --gas-limit <2x_ESTIMATE> \
     --create <BYTECODE>
   ```

2. **Check constructor parameters:**
   - Ensure constructor args are correctly encoded
   - Verify all required parameters are provided

3. **Check contract size:**
   - Max contract size: 24,576 bytes
   - Optimize with `--optimize` flag in solc

### Transaction Reverts Without Message

**Symptoms:**
- Transaction fails but no revert reason shown
- `status: 0` in receipt

**Solutions:**

1. **Simulate with `eth_call`:**
   ```bash
   cast call --rpc-url https://rpc.rustchain.io \
     <CONTRACT> <SIG>(<ARGS>) \
     --from <SENDER>
   # This will return the revert reason
   ```

2. **Enable debug tracing** (if node supports it):
   ```bash
   cast run --rpc-url https://rpc.rustchain.io <TX_HASH>
   ```

3. **Add require messages in Solidity:**
   ```solidity
   // ❌ Silent failure
   require(balance >= amount);

   // ✅ With message
   require(balance >= amount, "Insufficient balance");
   ```

---

## Sync Issues

### Node Stuck at Old Block

**Symptoms:**
- Block number stops advancing
- Logs: `"sync stalled"` or repeated `"imported block"` at same height

**Solutions:**

1. **Check peer count:**
   ```bash
   rustchain-cli net peers
   # Should have 5+ peers for reliable syncing
   ```

2. **Restart sync:**
   ```bash
   rustchain-node start --network mainnet --sync full
   ```

3. **Check disk space:**
   ```bash
   df -h
   # Need at least 50 GB free for mainnet
   ```

4. **Remove corrupt data and resync:**
   ```bash
   # ⚠️ This deletes chain data - backup first
   rm -rf ~/.rustchain/chain-data
   rustchain-node init --genesis genesis.json
   rustchain-node start --network mainnet
   ```

### Slow Sync Speed

**Symptoms:**
- Sync progressing but very slowly
- Takes days to catch up

**Solutions:**

1. **Use SSD storage:**
   - HDD sync can be 10-50x slower than SSD
   - NVMe SSD recommended for validators

2. **Increase system resources:**
   - RAM: 16 GB recommended for fast sync
   - CPU: 8+ cores

3. **Tune database cache:**
   ```toml
   [database]
   cache_size = "4GB"  # Increase from default
   ```

---

## Performance Issues

### High Memory Usage

**Symptoms:**
- Node using excessive RAM (>16 GB)
- System becomes unresponsive

**Solutions:**

1. **Limit cache size:**
   ```toml
   [database]
   cache_size = "2GB"
   ```

2. **Reduce peer count:**
   ```toml
   [network]
   max_peers = 25  # Reduce from default 50
   ```

3. **Disable unnecessary features:**
   ```bash
   # If you don't need WebSocket
   rustchain-node start --no-ws
   ```

### Slow RPC Responses

**Symptoms:**
- API calls take seconds to respond
- Timeouts on complex queries

**Solutions:**

1. **Check if node is still syncing:**
   - Syncing nodes are slow to respond
   - Wait for full sync before serving traffic

2. **Use connection pooling:**
   ```python
   import requests

   session = requests.Session()
   # Reuse connections instead of creating new ones
   response = session.post("https://rpc.rustchain.io", json=payload)
   ```

3. **Set up a load balancer** with multiple backend nodes

4. **Cache frequently accessed data:**
   - Block headers
   - Token decimals and names
   - Common contract ABIs

---

## Quick Diagnostic Checklist

When something isn't working, check these in order:

- [ ] **Node running?** `ps aux | grep rustchain`
- [ ] **Fully synced?** `rustchain-cli status`
- [ ] **Peers connected?** `rustchain-cli net peers` (should be 5+)
- [ ] **RPC responding?** `curl -s http://localhost:8545 -X POST -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'`
- [ ] **Disk space?** `df -h` (need free space)
- [ ] **Memory available?** `free -h`
- [ ] **Correct network?** Verify chain ID matches
- [ ] **Correct RPC URL?** Check in wallet/dApp config
- [ ] **Logs for errors?** Check `~/.rustchain/logs/`

---

*Last updated: 2025-05*
