# RustChain API Load Test Suite

Load testing suite for the RustChain API, supporting multiple load testing frameworks.

## 🎯 Bounty

**Issue:** #1614 - Create a load test suite for the RustChain API  
**Reward:** 5 RTC  
**Tags:** load-testing, performance, locust, k6, bounty, api, devops

## 📋 Overview

This load test suite provides comprehensive performance testing for the RustChain API endpoints:

- **Health Check** (`/health`) - Node health and status
- **Epoch Info** (`/epoch`) - Current epoch and slot information
- **Miners List** (`/api/miners`) - Active miner enumeration
- **Wallet Balance** (`/wallet/balance`) - Miner balance queries
- **Attestation** (`/attest/challenge`) - PoA challenge generation
- **Lottery Eligibility** (`/lottery/eligibility`) - Miner eligibility checks
- **Explorer** (`/explorer`) - Explorer UI redirect

## 🛠️ Supported Tools

### 1. Locust (Python)

**Best for:** Distributed load testing, custom test scenarios, Python developers

#### Installation

```bash
cd load_tests
pip install -r requirements-loadtest.txt
```

#### Usage

```bash
# Start Locust web UI
locust -f locustfile.py --host https://50.28.86.131

# Headless mode - run for 2 minutes with 10 users
locust -f locustfile.py --host https://50.28.86.131 --headless -u 10 -t 2m

# Stress test with 50 users
locust -f locustfile.py --host https://50.28.86.131 --headless -u 50 -t 5m

# Rate limit testing
locust -f locustfile.py --host https://50.28.86.131 --headless -u 100 -t 1m --class RateLimitTestUser
```

#### User Classes

- `RustChainAPIUser` - Normal API usage patterns
- `StressTestUser` - Aggressive stress testing
- `RateLimitTestUser` - Rate limiting behavior testing

### 2. k6 (JavaScript)

**Best for:** CI/CD integration, developer-friendly scripting, performance thresholds

#### Installation

```bash
# macOS
brew install k6

# Windows (with Scoop)
scoop install k6

# Linux
sudo apt install k6
```

#### Usage

```bash
# Run with default configuration
k6 run k6-loadtest.js

# Run with custom VUs and duration
k6 run --vus 10 --duration 30s k6-loadtest.js

# Run stress test scenario
k6 run --scenario stress_test k6-loadtest.js

# Run with thresholds disabled (for baseline testing)
k6 run --no-threshold k6-loadtest.js

# Output results to JSON
k6 run --out json=results.json k6-loadtest.js
```

#### Built-in Scenarios

- `normal_load` - Ramping load test (default)
- `stress_test` - High load stress testing (commented out)
- `spike_test` - Sudden traffic spike testing (commented out)

#### Performance Thresholds

- 50% of requests < 500ms
- 90% of requests < 1000ms
- 95% of requests < 2000ms
- Error rate < 10%
- Health check success rate > 95%

### 3. Artillery (YAML)

**Best for:** Quick setup, YAML configuration, built-in reporting

#### Installation

```bash
npm install -g artillery
```

#### Usage

```bash
# Run load test
artillery run artillery-loadtest.yml

# Run with custom target
artillery run --target https://50.28.86.131 artillery-loadtest.yml

# Quick smoke test
artillery quick --count 10 --num 100 https://50.28.86.131/health

# Generate HTML report
artillery run artillery-loadtest.yml --output report.html
```

## 📊 Test Scenarios

### Normal Load Test

Simulates typical API usage patterns:

- Health checks (30% of requests)
- Epoch queries (30% of requests)
- Miner list retrieval (20% of requests)
- Wallet balance checks (10% of requests)
- Attestation challenges (5% of requests)
- Explorer access (5% of requests)

### Stress Test

High-load scenario to identify breaking points:

- 50+ concurrent users
- Rapid request intervals (0.1-0.5s)
- Sustained load for 5-10 minutes

### Rate Limit Test

Tests API rate limiting behavior:

- Very rapid requests (0.01-0.1s intervals)
- Verifies HTTP 429 responses
- Measures backoff effectiveness

## 📈 Metrics Collected

### Response Time

- Average response time
- P50, P90, P95, P99 percentiles
- Min/Max response times

### Reliability

- Success/failure rates
- HTTP status code distribution
- Error types and frequencies

### Throughput

- Requests per second (RPS)
- Concurrent users
- Data transfer rates

### Custom Metrics

- Health check success rate
- Epoch data consistency
- Miner list availability
- Rate limiting effectiveness

## 🔍 API Endpoints Tested

| Endpoint | Method | Description | Weight |
|----------|--------|-------------|--------|
| `/health` | GET | Node health status | 30% |
| `/epoch` | GET | Current epoch info | 30% |
| `/api/miners` | GET | Active miners list | 20% |
| `/wallet/balance` | GET | Miner balance query | 10% |
| `/attest/challenge` | POST | Attestation challenge | 5% |
| `/lottery/eligibility` | GET | Lottery eligibility | 5% |
| `/explorer` | GET | Explorer redirect | 5% |

## 🚀 Quick Start

### Option 1: Locust (Recommended for beginners)

```bash
cd load_tests
pip install -r requirements-loadtest.txt
locust -f locustfile.py --host https://50.28.86.131
```

Then open http://localhost:8089 in your browser.

### Option 2: k6 (Recommended for CI/CD)

```bash
k6 run k6-loadtest.js
```

### Option 3: Artillery (Recommended for quick tests)

```bash
artillery run artillery-loadtest.yml
```

## 📝 Output Examples

### Locust Web UI

- Real-time metrics dashboard
- Response time graphs
- RPS charts
- Failure tracking

### k6 Summary

```
     ✓ health_checks_passed..........: 100.00% ✓ 1234      ✗ 0
     ✓ epoch_checks_passed...........: 100.00% ✓ 1230      ✗ 0
     ✓ miners_checks_passed..........: 99.50%  ✓ 820       ✗ 4

     http_req_duration..............: avg=150ms min=50ms med=120ms max=800ms p(90)=300ms p(95)=450ms
     http_reqs......................: 5000    83.33/s
```

### Artillery Report

- JSON/HTML reports
- Latency distribution
- Error codes breakdown
- Timeline analysis

## ⚠️ Notes

### Self-Signed Certificate

The RustChain API uses a self-signed certificate. All test configurations include:

- Locust: `self.client.verify = False`
- k6: `insecureSkipTLSVerify: true`
- Artillery: `tls.rejectUnauthorized: false`

### Rate Limiting

The API implements rate limiting. Tests include:

- Graceful handling of HTTP 429 responses
- Exponential backoff recommendations
- Rate limit behavior verification

### Production Testing

⚠️ **Warning:** These tests generate significant load. Use caution when testing against production instances.

Recommendations:

1. Start with low user counts (1-5 VUs)
2. Gradually increase load
3. Monitor API health during tests
4. Have a rollback plan ready

## 🐛 Troubleshooting

### Connection Refused

```bash
# Check API availability
curl -sk https://50.28.86.131/health
```

### Certificate Errors

All tools are configured to accept self-signed certificates. If you see certificate errors, verify the configuration flags are set correctly.

### High Failure Rates

If failure rates exceed thresholds:

1. Check API health manually
2. Reduce concurrent users
3. Increase timeouts
4. Check network connectivity

## 📚 Additional Resources

- [Locust Documentation](https://docs.locust.io/)
- [k6 Documentation](https://k6.io/docs/)
- [Artillery Documentation](https://www.artillery.io/docs/)

## 🏆 Bounty Completion Checklist

- [x] Locust load test suite created
- [x] k6 load test suite created
- [x] Artillery load test suite created
- [x] Multiple test scenarios (normal, stress, rate limit)
- [x] Comprehensive endpoint coverage
- [x] Performance thresholds defined
- [x] Documentation and usage examples
- [x] Requirements files provided
- [x] Custom metrics and reporting

## 📄 License

Same license as the main RustChain project.

## 👤 Author

Created for RustChain Bounties #1614
