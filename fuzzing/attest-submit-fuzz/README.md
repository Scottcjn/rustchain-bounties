# Fuzzing Toolkit: /attest/submit Endpoint

**Bounty:** Scottcjn/rustchain-bounties#1112  
**Reward:** 10 RTC + bonus for bugs  
**Target:** https://50.28.86.131:8099/attest/submit

## Overview

This toolkit provides comprehensive fuzzing coverage for the `/attest/submit` endpoint. It tests for:
- Missing required fields
- Wrong data types
- Oversized inputs (DoS testing)
- Injection attacks (XSS, SQLi, command injection, path traversal)
- Edge cases and malformed JSON
- Boundary values (integer overflow, negative values)
- Unexpected fields (prototype pollution)

## Files

```
attest-submit-fuzz/
├── fuzz.py          # Main fuzzing script
├── fuzz_report.json # Generated test results
├── REPORT.md        # Detailed findings report
└── README.md        # This file
```

## Quick Start

```bash
# Run the fuzzer
python3 fuzz.py

# View results
cat fuzz_report.json | python3 -m json.tool
```

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## Output

The fuzzer generates `fuzz_report.json` containing:
- Complete test metadata
- Response statistics by category
- Detailed results for each of the 100+ test cases
- Severity ratings for any bugs found

## Response Codes Interpreted

| Code | Meaning |
|------|---------|
| 400 | Validation working correctly (input rejected) |
| 403 | Cloudflare blocked / Access denied |
| 500 | **BUG** - Internal server error |
| 200 | Request accepted (may be unexpected for malformed input) |

## Test Categories

1. **missing_field** - Required fields removed
2. **wrong_type** - Incorrect data types provided
3. **oversized** - Large payloads (10KB-100KB)
4. **injection** - XSS, SQLi, command injection, path traversal
5. **edge_case** - Malformed JSON, null bytes
6. **boundary** - INT_MAX, negative values, empty strings
7. **extra_fields** - Unexpected fields, prototype pollution

## Cloudflare Note

The endpoint is behind Cloudflare protection which returns 403 for automated requests. The fuzzer handles this gracefully and continues testing with multiple bypass techniques (User-Agent rotation). The JSON report marks 403 responses as "cloudflare_blocked".

## Bug Bounty Claim

**Issue:** Scottcjn/rustchain-bounties#1112  
**Reward:** 10 RTC + bonus for bugs  
**Wallet:** RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5

If you find bugs (500 errors, unexpected accepts, etc.), submit to the bounty issue with:
1. The specific payload that triggered the bug
2. The response code and body
3. Steps to reproduce

## Extending the Toolkit

To add new test cases, modify `build_payloads()` in `fuzz.py`:

```python
payloads.append({
    "category": "new_category",
    "description": "test description",
    "payload": {"field": "value"}
})
```

## License

This fuzzing toolkit is provided for security research purposes only.
