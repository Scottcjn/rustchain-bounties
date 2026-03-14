# RustChain Unit Tests

Unit tests for RustChain utility functions.

## Coverage

- **Math functions** - add, subtract, multiply, divide
- **Address validation** - Format validation for RTC addresses
- **Balance formatting** - Wei to RTC conversion

## Usage

```bash
# Run all tests
python test_sample.py

# Run with verbosity
python -m unittest -v test_sample.py

# Run with coverage
coverage run -m unittest
coverage report
```

## Files

- `test_sample.py` - Unit test suite
- `README.md` - Documentation

---

Fixes #1589
