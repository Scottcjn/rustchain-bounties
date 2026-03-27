# Windows Miner Bundle Smoke Test

This directory contains scripts and documentation for performing smoke tests on the Windows miner bundle for RustChain.

## Purpose

The smoke test verifies basic functionality of the Windows miner bundle including:
- Proper executable startup
- Command-line argument handling
- Basic configuration loading
- Dependency availability

## Usage

1. Download the Windows miner bundle from the RustChain releases
2. Extract the bundle to your test environment
3. Run the smoke test script:

```bash
python test_runner.py
```

## What the Test Does

The smoke test performs the following checks:

1. **Platform Verification**: Ensures the test is running on Windows
2. **Executable Discovery**: Attempts to locate the miner executable in common locations
3. **Basic Startup Test**: Verifies the miner responds to `--help` command
4. **Version Test**: Checks if the miner reports its version correctly
5. **Configuration Test**: Attempts to start the miner with a minimal configuration
6. **Dependency Check**: Verifies common Windows dependencies are available

## Expected Results

A successful smoke test will show:
- All tests passing (✓ symbols)
- No critical errors in the log
- Miner executable responding to commands

## Failure Analysis

If tests fail, the log file will contain detailed information about:
- Error messages from the miner
- Return codes
- Standard output and error streams
- Missing dependencies

## Log Files

Test results are saved to timestamped log files in the same directory:
- Format: `windows_miner_smoke_test_YYYYMMDD_HHMMSS.log`
- Contains full test output and error details

## Contributing

When submitting test results for bounties, please include:
1. The log file from your test run
2. Information about your Windows version
3. Any specific error messages encountered
4. Steps you took to reproduce the issue

## Notes

- This is a smoke test, not a comprehensive functionality test
- Some network-related failures may be expected if no server is available
- The test intentionally uses short timeouts to prevent hanging processes