# RustChain Troubleshooting Guide

Common issues and solutions organized by category. Use this guide to diagnose and resolve problems when working with RustChain mining, wallets, and APIs.

---

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Wallet Problems](#wallet-problems)
3. [Mining Issues](#mining-issues)
4. [API Issues](#api-issues)
5. [Sync Issues](#sync-issues)
6. [Performance Issues](#performance-issues)

---

## Connection Issues

### Miner Won't Connect to Network

**Symptoms:**
- Miner starts but cannot reach RustChain endpoints
- Logs: `"connection refused"` or `"timeout"`

**Solutions:**

1. **Check endpoint connectivity:**
   ```bash
   # Test health endpoint
   curl -sk https://rustchain.org/health
   # Expected: {"ok": true, "version": "2.2.1-rip200", ...}
   # Note: The node uses a self-signed certificate; -k skips verification.
   # Direct node access: curl -sk https://50.28.86.131/health
   ```

2. **Check firewall rules:**
   ```bash
   # Ensure outbound HTTPS is allowed
   sudo ufw allow out 443/tcp
   ```

3. **Verify DNS resolution:**
   ```bash
   # Check that rustchain.org resolves
   nslookup rustchain.org
   ```

4. **Check NAT configuration:**
   - Ensure your router allows outbound connections
   - Verify your external IP is correct
   - Test with `curl ifconfig.me`

### Docker Container Cannot Connect

**Symptoms:**
- Miner container starts but fails to reach rustchain.org
- Logs: `"network unreachable"` or `"no route to host"`

**Solutions:**

1. **Check Docker network:**
   ```bash
   docker network ls
   docker network inspect bridge
   ```

2. **Test connectivity from container:**
   ```bash
   docker exec -it rustchain-miner curl -sk https://rustchain.org/health
   ```

3. **Check docker-compose network config:**
   ```yaml
   services:
     miner:
       network_mode: bridge  # or host
   ```

---

## Wallet Problems

### Balance Not Showing

**Symptoms:**
- Wallet shows 0 balance when tokens should exist
- Balance doesn't match expected value

**Solutions:**

1. **Check balance via API:**
   ```bash
   curl -sk https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID
   ```

2. **Verify wallet address:**
   - Ensure you're checking the correct address
   - Compare with the address used for mining rewards

3. **Check if rewards have been distributed:**
   - Mining rewards are distributed per epoch (1.5 RTC/epoch to active miners)
   - Check miner status: `curl -sk https://rustchain.org/api/miners`

### Cannot Send Transaction

**Symptoms:**
- Transaction fails or returns error
- "insufficient balance" or "invalid transaction"

**Solutions:**

1. **Check sufficient balance:**
   ```bash
   curl -sk https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID
   ```

2. **Verify transaction parameters:**
   - Correct recipient address
   - Amount within available balance
   - No extra whitespace in addresses

3. **Check node health:**
   ```bash
   curl -sk https://rustchain.org/health
   ```

### Cannot Import Wallet

**Symptoms:**
- Wallet import fails
- "invalid key" error

**Solutions:**

1. **Check key format:**
   - Verify the key is in the correct format expected by rustchain-wallet
   - Check for hidden characters or whitespace

2. **Try with clean input:**
   ```bash
   # Ensure no whitespace or newlines in key
   echo -n "YOUR_KEY" | wc -c
   ```

3. **Check rustchain-wallet version:**
   ```bash
   cd rustchain-wallet && cargo run -- --version
   ```

---

## Mining Issues

### Miner Not Receiving Epoch Rewards

**Symptoms:**
- Miner is running but balance not increasing
- No epoch rewards appearing

**Solutions:**

1. **Verify miner is in active list:**
   ```bash
   curl -sk https://rustchain.org/api/miners
   # Check your miner appears as active
   ```

2. **Check hardware certification:**
   - PoAn requires hardware certification to participate
   - Ensure your hardware has passed certification
   - Re-run hardware certification if needed

3. **Check node health:**
   ```bash
   curl -sk https://rustchain.org/health
   ```

4. **Review miner logs:**
   ```bash
   docker logs rustchain-miner --tail 100
   # Look for errors or warnings
   ```

### Miner Keeps Disconnecting

**Symptoms:**
- Miner connects but drops off periodically
- Intermittent "inactive" status

**Solutions:**

1. **Check system resources:**
   ```bash
   # CPU, memory, disk I/O
   top -bn1 | head -20
   df -h
   iostat -x 1 5
   ```

2. **Check network stability:**
   ```bash
   # Test latency to rustchain.org
   ping -c 10 rustchain.org
   ```

3. **Check Docker container health:**
   ```bash
   docker inspect rustchain-miner --format='{{.State.Status}}'
   docker logs rustchain-miner --tail 50
   ```

4. **Recommended hardware:**
   - CPU: 4+ cores
   - RAM: 8 GB minimum
   - Disk: SSD with 500+ MB/s sequential read
   - Network: 100 Mbps+, low latency (<50ms)

### Docker Build Fails

**Symptoms:**
- `docker build -f Dockerfile.miner` fails
- Build errors or missing dependencies

**Solutions:**

1. **Check Dockerfile.miner exists:**
   ```bash
   ls -la Dockerfile.miner
   ```

2. **Check Python dependencies:**
   ```bash
   # Verify pyproject.toml is valid
   cat pyproject.toml
   ```

3. **Check Rust wallet build:**
   ```bash
   cd rustchain-wallet
   cargo build --release
   ```

4. **Clean and rebuild:**
   ```bash
   docker system prune -f
   docker build --no-cache -f Dockerfile.miner -t rustchain-miner .
   ```

---

## API Issues

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

2. **Cache responses** to reduce redundant requests

3. **Use batch requests** instead of individual calls

### API Returns Unexpected Results

**Symptoms:**
- `/api/miners` returns unexpected data
- `/wallet/balance?miner_id=YOUR_MINER_ID` shows wrong value

**Solutions:**

1. **Check endpoint is correct:**
   ```bash
   # All endpoints are under rustchain.org (not *.rustchain.io)
   curl -sk https://rustchain.org/health
   curl -sk https://rustchain.org/api/miners
   curl -sk https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID
   ```

2. **Verify response format:**
   ```bash
   # Pretty-print JSON response
   curl -sk https://rustchain.org/api/miners | python -m json.tool
   ```

3. **Check for stale cached data:**
   - Clear browser/HTTP cache
   - Add cache-busting parameter: `?t=$(date +%s)`

### Health Check Failing

**Symptoms:**
- `/health` returns error or non-200 status
- Monitoring alerts firing

**Solutions:**

1. **Verify endpoint:**
   ```bash
   curl -vsk https://rustchain.org/health
   ```

2. **Check if miner process is running:**
   ```bash
   docker ps | grep rustchain
   ```

3. **Restart miner:**
   ```bash
   docker-compose restart
   ```

---

## Sync Issues

### Node Stuck / Not Syncing

**Symptoms:**
- Block number stops advancing
- Node appears out of sync

**Solutions:**

1. **Check miner status:**
   ```bash
   curl -sk https://rustchain.org/health
   curl -sk https://rustchain.org/api/miners
   ```

2. **Restart sync:**
   ```bash
   docker-compose restart
   ```

3. **Check disk space:**
   ```bash
   df -h
   # Need sufficient free space
   ```

4. **Reset and resync:**
   ```bash
   # ⚠️ Backup wallet data first
   docker-compose down
   # Remove chain data only, keep wallet
   rm -rf ./data/chain
   docker-compose up -d
   ```

### Slow Sync Speed

**Symptoms:**
- Sync progressing but very slowly

**Solutions:**

1. **Use SSD storage:**
   - HDD can be 10-50x slower than SSD
   - NVMe SSD recommended

2. **Increase system resources:**
   - RAM: 16 GB recommended
   - CPU: 8+ cores

3. **Check network bandwidth:**
   - Ensure stable, high-bandwidth connection
   - Test: `speedtest-cli`

---

## Performance Issues

### High Memory Usage

**Symptoms:**
- Miner using excessive RAM (>8 GB)
- System becomes unresponsive

**Solutions:**

1. **Limit Docker memory:**
   ```yaml
   # docker-compose.yml
   services:
     miner:
       deploy:
         resources:
           limits:
             memory: 4G
   ```

2. **Check for memory leaks:**
   ```bash
   docker stats rustchain-miner
   # Monitor over time
   ```

3. **Restart periodically if needed:**
   ```bash
   # Set up a weekly restart cron if memory grows
   0 4 * * 0 cd /path/to/rustchain && docker-compose restart
   ```

### Slow API Responses

**Symptoms:**
- API calls take seconds to respond
- Timeouts on queries

**Solutions:**

1. **Check if node is healthy:**
   ```bash
   curl -sk https://rustchain.org/health
   ```

2. **Use connection pooling:**
   ```python
   import requests

   session = requests.Session()
   response = session.get("https://rustchain.org/api/miners", verify=False)
   ```

3. **Cache frequently accessed data:**
   - Miner status
   - Wallet balances
   - Health check results

---

## Quick Diagnostic Checklist

When something isn't working, check these in order:

- [ ] **Miner running?** `docker ps | grep rustchain`
- [ ] **Health OK?** `curl -sk https://rustchain.org/health`
- [ ] **Miner active?** `curl -sk https://rustchain.org/api/miners`
- [ ] **Balance correct?** `curl -sk https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID`
- [ ] **Disk space?** `df -h` (need free space)
- [ ] **Memory available?** `free -h`
- [ ] **Docker OK?** `docker logs rustchain-miner --tail 50`
- [ ] **Network OK?** `ping -c 3 rustchain.org`
- [ ] **Logs for errors?** Check Docker logs for error/warning messages

---

*Last updated: 2026-05*
