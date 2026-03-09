# Fuzzing the /attest/submit Endpoint

This directory contains tools for fuzzing the `/attest/submit` endpoint of the RustChain ecosystem.

## Overview

Fuzzing is a software testing technique that involves providing invalid, unexpected, or random data as input to a computer program. The goal is to find security vulnerabilities, crashes, or unexpected behavior in the system.

## Files

- `fuzz_attest_submit.py` - Main fuzzing script that generates random and malformed attestations
- `test_fuzz_attest_submit.py` - Test suite for the fuzzing script

## Usage

### Running the Fuzzer

```bash
python fuzz_attest_submit.py --url http://localhost:8000 --requests 1000
```

Arguments:
- `--url`: Base URL of the API (default: http://localhost:8000)
- `--requests`: Number of requests to send (default: 1000)

### Running Tests

```bash
python test_fuzz_attest_submit.py
```

## Fuzzing Strategy

The fuzzer uses two main strategies:

1. **Valid Attestations**: Generates random but valid attestation payloads to test normal operation
2. **Malformed Attestations**: Generates intentionally malformed payloads to test edge cases and error handling

### Test Cases

The fuzzer tests various scenarios:

- Missing required fields
- Invalid data types
- Empty data
- Extremely large values
- Invalid JSON structure
- Missing required fields entirely

## Expected Output

The fuzzer will output:

- Request-by-request status
- Success/failure counts
- Status code distribution
- Error messages for failed requests

## Security Considerations

- The fuzzer is designed to be safe and not cause permanent damage
- It only sends HTTP requests and doesn't modify any persistent data
- Always run the fuzzer in a development/testing environment
- Monitor server resources during testing

## Contributing

If you find interesting edge cases or crashes, please report them with:

1. The exact request payload that caused the issue
2. The server response or error message
3. Server logs if available

## Integration with CI/CD

This fuzzing script can be integrated into CI/CD pipelines as part of security testing:

```yaml
# Example GitHub Actions step
- name: Run fuzzing tests
  run: python fuzz_attest_submit.py --requests 500
  if: github.event_name == 'pull_request'
```
