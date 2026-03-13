# Quick Start Guide - CDC 1604 Miner

## For Reviewers and Contributors

This guide shows you how to test the CDC 1604 miner implementation.

---

## Option 1: Test with Demo Data (Easiest)

No CDC 1604 or simulator required!

```bash
# Navigate to proxy directory
cd rustchain-cdc1604-miner/proxy

# Install dependencies
pip install -r requirements.txt

# Run with demo data
python cdc1604_proxy.py --demo --dry-run
```

**Expected Output:**
```
RustChain CDC 1604 Attestation Proxy
============================================================
Mode: Demo (simulated data)
Wallet:   RTC<random 40 hex chars>
Miner ID: CDC1604-<random 8 hex chars>
Source:   demo

Building attestation...
Validating attestation...
Validation passed

=== DRY RUN - Attestation JSON ===
{
  "miner": "RTC...",
  "miner_id": "CDC1604-...",
  "device": {
    "arch": "cdc1604",
    "year": 1960,
    "antiquity_multiplier": 5.0
  },
  ...
}
```

---

## Option 2: Test with Sample Output

Use the included sample CDC 1604 output.

```bash
cd rustchain-cdc1604-miner

# Run proxy with sample output
python proxy/cdc1604_proxy.py --input test/sample_cdc1604_output.txt --dry-run
```

**Expected Output:**
```
Mode: Text Output (test/sample_cdc1604_output.txt)
Wallet:   RTC4325AF95D26D59C3EF025963656D22AF638BB96B
Miner ID: CDC1604-A3F7B2E1
Source:   sample

Building attestation...
Validating attestation...
Validation passed
```

---

## Option 3: Run Full Test Suite

```bash
cd rustchain-cdc1604-miner

# Install pytest if needed
pip install pytest

# Run all tests
pytest test/test_entropy.py -v
```

**Expected Output:**
```
test_entropy.py::TestEntropyParsing::test_parse_valid_text_output PASSED
test_entropy.py::TestEntropyParsing::test_parse_missing_wallet PASSED
test_entropy.py::TestAttestation::test_build_attestation_structure PASSED
test_entropy.py::TestAttestation::test_cdc1604_metadata PASSED
test_entropy.py::TestAttestation::test_validate_attestation_success PASSED
test_entropy.py::TestAntiEmulation::test_anti_emulation_flags PASSED
test_entropy.py::TestDemoGeneration::test_demo_data_format PASSED
test_entropy.py::TestDemoGeneration::test_demo_data_uniqueness PASSED

12 passed in 0.38s
```

---

## Option 4: SIMH Simulator (Advanced)

Requires SIMH CDC 1604 simulator.

### Step 1: Install SIMH

```bash
# Linux/macOS
git clone https://github.com/simh/simulator.git
cd simulator
make cdc1604

# Windows: Download pre-built from http://simh.trailing-edge.com/
```

### Step 2: Assemble CDC 1604 Code

```bash
# Note: CDC 1604 assembler not included
# Use SIMH loader format or manual encoding
# See docs/IMPLEMENTATION_PLAN.md for details
```

### Step 3: Run Simulator

```bash
sim> cdc1604
sim> load entropy_collector.bin
sim> attach tp0 output.tap
sim> go

# Wait for completion
sim> detach tp0
sim> quit
```

### Step 4: Process Output

```bash
python proxy/cdc1604_proxy.py --tape output.tap --wallet YOUR_WALLET
```

---

## Option 5: Submit Real Attestation

To submit to RustChain node:

```bash
# Remove --dry-run flag
python proxy/cdc1604_proxy.py --input test/sample_cdc1604_output.txt --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b

# Or with demo data
python proxy/cdc1604_proxy.py --demo --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
```

**Expected Output:**
```
============================================================
✓ ATTESTATION SUCCESSFUL
============================================================
Wallet:     RTC4325AF95D26D59C3EF025963656D22AF638BB96B
Miner ID:   CDC1604-A3F7B2E1
Device:     CDC 1604 (1960)
Multiplier: 5.0x
Epoch:      1847
Reward:     0.60 RTC

🏛️ Pantheon Pioneer Badge Eligible!
```

---

## Troubleshooting

### Error: "requests library required"

```bash
pip install requests
```

### Error: "Could not find wallet ID"

Check that your CDC 1604 output includes:
```
WALLET:RTC<40 hex chars>
```

### Error: "Validation failed"

Run with `--dry-run` to see the attestation JSON and check for issues.

### Error: "Connection refused"

The RustChain node may be offline. Try:
```bash
curl -sk https://rustchain.org/health
```

---

## File Reference

| File | Purpose |
|------|---------|
| `README.md` | Full project documentation |
| `PROJECT_SUMMARY.md` | Implementation summary |
| `docs/CDC1604_ARCHITECTURE.md` | Technical architecture |
| `docs/IMPLEMENTATION_PLAN.md` | Development guide |
| `test/test_entropy.py` | Test suite |
| `proxy/cdc1604_proxy.py` | Attestation proxy |

---

## Questions?

See full documentation in `README.md` or open an issue.

**Wallet for bounty**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
