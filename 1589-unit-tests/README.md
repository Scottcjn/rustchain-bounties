# RustChain Unit Tests

Unit tests for RustChain utility functions.

## Coverage

- Math functions (add, subtract, multiply, divide) - 10 test cases
- Address validation - 5 test cases
- Balance formatting - 3 test cases

## Usage

```bash
# Run all tests
python test_utils.py

# Run with verbosity
python -m unittest -v test_utils.py

# Run with coverage
coverage run -m unittest
coverage report
```

## Files

- test_utils.py - Unit test suite (18 test cases)
- README.md - Documentation

---

Fixes #1589
