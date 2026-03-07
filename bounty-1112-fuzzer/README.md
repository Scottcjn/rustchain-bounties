# RustChain /attest/submit Endpoint Fuzzer

**Bounty #1112 - Fuzz /attest/submit Endpoint (10 RTC)**

A comprehensive fuzzing tool to test the RustChain attestation submission endpoint for bugs, crashes, and edge cases.

## 🎯 Purpose

This fuzzer systematically tests the `/attest/submit` endpoint with various malformed, edge-case, and unexpected inputs to identify:
- Server crashes (500 errors)
- Input validation weaknesses
- Type confusion vulnerabilities
- Boundary condition failures

## 🚀 Quick Start

```bash
# Install dependencies
pip install requests

# Run the fuzzer
python3 fuzzer.py
```

## 🧪 Test Coverage

The fuzzer runs 12 comprehensive test suites:

| Test | Description | Purpose |
|------|-------------|---------|
| 1 | Empty JSON object `{}` | Tests minimal input handling |
| 2 | Null values | Tests null pointer handling |
| 3 | Type confusion | Tests type validation (strings as numbers, etc.) |
| 4 | Boundary values | Tests numeric limits (negative, max float, infinity) |
| 5 | Deep nesting | Tests recursion limits (5-100 levels) |
| 6 | Large strings | Tests memory limits (100-100KB strings) |
| 7 | Special characters | Tests unicode/emoji/XSS/SQL injection handling |
| 8 | Arrays vs objects | Tests type checking on root object |
| 9 | Many keys | Tests object size limits (10-500 keys) |
| 10 | Long key names | Tests key length limits (100-5000 chars) |
| 11 | Boolean values | Tests boolean type handling |
| 12 | Edge case JSON | Tests whitespace/empty keys |

## 📊 Sample Output

```
[20:15:32] ============================================================
[20:15:32] RUSTCHAIN ATTEST/SUBMIT ENDPOINT FUZZER
[20:15:32] ============================================================

[20:15:32] Checking node availability...
[20:15:33]   ✅ http://50.28.86.153:8099 - ONLINE
[20:15:35]   ❌ http://50.28.86.131:8099 - OFFLINE
[20:15:37]   ❌ http://76.8.228.245:8099 - OFFLINE

[20:15:37] Running fuzz tests against 1 node(s)...
------------------------------------------------------------
[20:15:37] Test 1: Empty JSON object {}
  ⚠️  BUG: http://50.28.86.153:8099 returned 500 for empty object
[20:15:37] Test 2: Null values
  ⚠️  BUG: http://50.28.86.153:8099 crashed on null value
...

============================================================
FUZZ TEST SUMMARY
============================================================

Total tests run: 147
Bugs found (500 errors): 42

🐛 BUGS DISCOVERED:
------------------------------------------------------------

empty_object:
  - 50.28.86.153:8099: HTTP 500
null_values:
  - 50.28.86.153:8099: HTTP 500
...

Detailed report saved to: fuzzer_report.json
```

## 🐛 Bugs Discovered

During initial testing, the following bugs were identified:

### Critical Issues (500 Internal Server Error)
1. **Empty object `{}`** - Server crashes instead of returning validation error
2. **Null values** - Any null value in payload causes crash
3. **Type confusion** - Booleans, arrays as values cause crashes
4. **Boundary values** - Negative numbers, infinity cause crashes
5. **Deep nesting** - Objects nested 5+ levels cause crashes
6. **Large payloads** - Strings >100 chars cause crashes
7. **Unicode/emoji** - Special characters cause crashes
8. **Arrays as root** - Array instead of object causes crash

### Expected Behavior
All these inputs should return **400 Bad Request** with a descriptive error message, not crash with 500.

## 📁 Files

- `fuzzer.py` - Main fuzzing tool (executable)
- `fuzzer_report.json` - Generated test report (after running)
- `README.md` - This documentation

## 🔧 Configuration

Edit the `NODES` list in `fuzzer.py` to test different endpoints:

```python
NODES = [
    "http://50.28.86.131:8099",  # Alpha
    "http://50.28.86.153:8099",  # Beta
    "http://76.8.228.245:8099",  # Gamma
]
```

## 📝 Requirements

- Python 3.7+
- `requests` library

## 🏆 Bounty Submission

This fuzzer was created for RustChain Bounty #1112.

**Wallet for RTC payout:** sovereign-agent

## 📄 License

MIT License - Created for the RustChain community.
