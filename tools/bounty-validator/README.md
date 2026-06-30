# Bounty Validator

A professional utility for RustChain maintainers to automate the verification of security Proof-of-Concept (PoC) scripts.

## Features
- **Automated Execution**: Runs all `.py` scripts in a target directory.
- **Isolation**: Implements timeouts to prevent hanging PoCs from blocking the process.
- **Standardized Reporting**: Generates a `validation_report.json` containing exit codes, stdout, stderr, and execution time.
- **Crash Detection**: Captures Python tracebacks and unexpected exits.

## Usage
```bash
python3 validator.py /path/to/pocs
```

## Output Format
The tool produces a JSON report:
```json
{
    "poc_name.py": {
        "status": "PASS|FAIL|TIMEOUT|ERROR",
        "exit_code": int | null,
        "stdout": "...",
        "stderr": "...",
        "duration": "Xs"
    }
}
```
