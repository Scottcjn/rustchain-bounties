# RustChain Windows Miner Bundle Smoke Test

## Overview
This document describes the smoke test for the RustChain Windows miner bundle. The smoke test is designed to perform basic validation of the bundle to ensure it contains all necessary components and is functional.

## Prerequisites
- Python 3.6 or higher
- The Windows miner bundle file (rustchain-miner-windows.zip)

## Running the Test

### Basic Usage
```bash
python bundle_smoke_test.py rustchain-miner-windows.zip
```

### Without Specifying Bundle Path
If you don't specify a bundle path, the test will look for a file named `rustchain-miner-windows.zip` in the current directory:
```bash
python bundle_smoke_test.py
```

## Test Components

The smoke test performs the following checks:

### 1. Bundle Structure
- Verifies the bundle is a valid zip file
- Checks for required files:
  - `rustchain-miner.exe` - Main executable
  - `config.json` - Configuration file
  - `README.txt` - User documentation
  - `libgcc_s_seh-1.dll` - GCC runtime library
  - `libstdc++-6.dll` - C++ standard library
- Checks for required directories:
  - `logs/` - Log directory
  - `temp/` - Temporary files directory

### 2. Executable
- Verifies the executable can be extracted
- Attempts to run the executable with `--help` flag
- Checks for any immediate errors

### 3. Config
- Verifies the config file is valid JSON
- Checks for required configuration fields:
  - `pool_url` - Mining pool URL
  - `wallet_address` - User's wallet address
  - `worker_name` - Worker name for identification

### 4. Dependencies
- Verifies required DLL files are present
- Checks that DLL files are not empty

### 5. README
- Verifies the README file is present and readable
- Checks that the README contains content

## Test Output

The test will output detailed information about each test component:

```
RustChain Windows Miner Bundle Smoke Test
==================================================
Testing bundle structure: rustchain-miner-windows.zip
Files in bundle: ['rustchain-miner.exe', 'config.json', ...]
Bundle structure test passed

--- Executable Test ---
Testing executable...
Executable help command succeeded
Help output: RustChain Miner v1.0.0
Usage: rustchain-miner.exe [OPTIONS]

Options:
  -h, --help     Print help
  -V, --version  Print version
...
```

## Failure Notes

If the bundle fails any tests, use the `failure_notes_template.md` to document the issues:

1. Copy the template to a new file with a descriptive name
2. Fill in the test results and failure details
3. Include root cause analysis and recommended actions
4. Document any re-testing performed after fixes

## Expected Test Results

A successful test should show:
- All test components marked as "PASS"
- No error messages
- A final summary showing all tests passed

## Troubleshooting

### Common Issues

1. **Bundle not found**: Ensure the bundle file exists and the path is correct
2. **Invalid zip file**: Re-create the bundle ensuring proper zip format
3. **Missing files**: Check that all required files are included in the bundle
4. **Executable errors**: Re-compile the miner and ensure all dependencies are included
5. **Config issues**: Verify the config file has all required fields

### Debug Mode
For more detailed output, you can modify the test script to add debug logging.

## Integration

This smoke test should be run as part of the CI/CD pipeline for Windows bundle creation. It ensures that only valid bundles are released to users.

## Contributing

To contribute improvements to the smoke test:
1. Fork the repository
2. Create a feature branch
3. Add new test cases or improve existing ones
4. Submit a pull request with test results

## License

This smoke test is part of the RustChain project and is subject to the same license terms.
