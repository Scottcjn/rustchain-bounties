# SPDX-License-Identifier: MIT

# Ergo Anchor Chain Proof Verifier

Independent audit tool for verifying RustChain → Ergo anchor commitments.

## Usage

```bash
# Full verification against live Ergo node
python verify_anchors.py --db rustchain_v2.db --ergo-node http://localhost:9053

# Offline mode (DB consistency check only, no network)
python verify_anchors.py --db rustchain_v2.db --offline

# JSON output
python verify_anchors.py --db rustchain_v2.db --offline --json
```

## What It Checks

1. Reads `ergo_anchors` table from the local database
2. Fetches actual Ergo transactions via node API (R5 register)
3. Recomputes Blake2b-256 commitment from block data
4. Three-way comparison: stored == on-chain == recomputed
5. Reports discrepancies with anchor IDs and reasons

## Tests

```bash
pytest test_verify_anchors.py -v
```

## Dependencies

Python 3.9+, no exotic dependencies (stdlib only).
