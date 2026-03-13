# Load Test Suite for RustChain API

**Bounty**: #1614
**Value**: 5 RTC (~$0.5)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install k6
brew install k6

# Or on Linux
sudo apt-get install k6
```

### Run Tests

```bash
# Smoke test (1 minute)
k6 run tests/smoke-test.js

# Load test (15 minutes)
k6 run tests/load-test.js

# Stress test (10 minutes)
k6 run tests/stress-test.js
```

---

## 📊 Test Scenarios

### 1. Smoke Test
- **Duration**: 1 minute
- **Users**: 10 concurrent
- **Purpose**: Verify API is working

### 2. Load Test
- **Duration**: 15 minutes
- **Users**: 300 concurrent
- **Purpose**: Test normal load

### 3. Stress Test
- **Duration**: 10 minutes
- **Users**: 500 concurrent
- **Purpose**: Find breaking point

### 4. Soak Test
- **Duration**: 1 hour
- **Users**: 50 concurrent
- **Purpose**: Check for memory leaks

### 5. Spike Test
- **Duration**: 5 minutes
- **Users**: 10 → 200 in 1 minute
- **Purpose**: Test auto-scaling

---

## 📈 Expected Results

| Test | QPS | P95 Latency | Error Rate |
|------|-----|-------------|------------|
| Smoke | 100+ | <100ms | <0.1% |
| Load | 500+ | <200ms | <1% |
| Stress | 300+ | <300ms | <5% |

---

## 🔧 Configuration

Edit `config.js`:

```javascript
export const BASE_URL = 'https://50.28.86.131';
export const DEFAULT_WALLET = 'test-wallet';
```

---

## 📝 Output

k6 will output:
- HTTP request statistics
- Response times (avg, min, max, p95)
- Error rates
- Throughput (req/s)

Example output:

```
http_req_duration..............: avg=150ms min=50ms med=140ms max=500ms p(95)=250ms
http_reqs......................: 10000  111.111111/s
```

---

## 🐛 Troubleshooting

### Issue: Connection timeout

```bash
# Check network connectivity
ping 50.28.86.131

# Check if API is up
curl https://50.28.86.131/health
```

### Issue: High error rate

```bash
# Reduce concurrent users
# Edit test file, reduce target in stages

# Check server logs
# Contact server admin
```

---

## 📚 References

- k6 Documentation: https://k6.io/docs/
- RustChain API: https://github.com/Scottcjn/RustChain

---

**Ready for PR submission!** 🚀
