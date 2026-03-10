# Attestation Fuzz Harness + Crash Regression Corpus

This directory contains the fuzz harness for attestation testing and a corpus of crash regression test cases.

## Overview

The fuzz harness is designed to test the RustChain attestation system for robustness and security. It includes:

- A libFuzzer harness for testing attestation parsing and validation
- A corpus of crash-inducing inputs for regression testing
- Continuous integration to catch new crashes

## Structure

```
fuzz_harness/
├── Cargo.toml              # Fuzz harness configuration
├── fuzz_targets/
│   └── attestation_fuzzer.rs # Main fuzz target implementation
├── corpus/
│   ├── crash1.txt         # Example crash case
│   ├── crash2.txt         # Example crash case
│   └── ...                # Additional crash cases
└── .gitignore             # Ignore generated files
```

## Fuzz Target

The `attestation_fuzzer.rs` target focuses on:

- Parsing attestation data structures
- Validating cryptographic signatures
- Handling edge cases in attestation formats
- Testing boundary conditions

## Corpus

The corpus directory contains inputs that have previously caused crashes. These are used to:

1. Prevent regressions (ensure old crashes don't reappear)
2. Serve as seed inputs for finding new crashes

## Running the Fuzzer

To run the fuzzer locally:

```bash
cargo fuzz run attestation_fuzzer
cargo fuzz run attestation_fuzzer corpus/
```

## Adding New Crash Cases

When a new crash is found:

1. Reproduce the crash with the minimal input
2. Add the input to the corpus directory
3. Commit with a descriptive message
4. Create a pull request with the new crash case

## Continuous Integration

The fuzz harness is integrated into CI to run on:

- Pull requests
- Scheduled runs
- New commits to main branch

This helps catch crashes early and maintain system robustness.
