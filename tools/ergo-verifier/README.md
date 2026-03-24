# SPDX-License-Identifier: MIT

# Ergo Anchor Chain Proof Verifier

Independent audit tool for verifying RustChain → Ergo anchor commitments.

## Usage

```bash
# Full verification against live Ergo node
python verify_anchors.py --db rustchain_v2.db --ergo-node http://localhost:9053

# Offline mode (DB consistency check only, no network)
python verify_anchors.py --db rustchain_v2.db --offline

# JSON output (non-zero exit on any failure)
python verify_anchors.py --db rustchain_v2.db --offline --json
```

## What It Checks

1. Reads `ergo_anchors` table from the local database
2. Fetches actual Ergo transactions via node API and reads the commitment from the `R4` register (`R5` is used for `miner_count`)
3. Recomputes Blake2b-256 commitment from block data
4. Three-way comparison: stored == on-chain == recomputed
5. Reports discrepancies with anchor IDs and reasons

## Dependencies

- Runtime: Python 3.9+, standard library only (no third-party packages required for `verify_anchors.py`).
- Tests: [`pytest`](https://docs.pytest.org/) is required to run the test suite (install with `pip install pytest`).

## Tests

```bash
cd tools/ergo-verifier && pytest test_verify_anchors.py -v
```
