# Self-Audit: node/utxo_db.py

## Wallet
RTC019e78d600fb3131c29d7ba80aba8fe644be426e

## Module reviewed
- Path: node/utxo_db.py
- Commit: 2cf9640
- Lines reviewed: whole file (912 lines)

## Deliverable: 3 specific findings

1. **Box ID collision: tokens and registers excluded from `compute_box_id` hash**
   - Severity: high
   - Location: node/utxo_db.py:53-61
   - Description: The `compute_box_id()` function constructs a deterministic box ID by hashing `value_nrtc`, `proposition`, `creation_height`, `transaction_id`, and `output_index`. Critically, it does **not** include `tokens_json` or `registers_json` in the hash input. Since `box_id` is the PRIMARY KEY of `utxo_boxes`, two distinct boxes with the same core fields but different tokens or registers will produce identical box IDs. This means the second box will fail insertion (PRIMARY KEY conflict) or overwrite the first, enabling an attacker to destroy tokens/registers by exploiting this collision.
   - Reproduction: 1) Create box A with value=1000, proposition="0008616263", creation_height=1, tx_id="aabb", output_index=0, tokens="[{id:'x'}]". 2) Create box B with identical core fields but tokens="[{id:'y'}]". 3) `compute_box_id` returns the same hash for both. 4) Second INSERT fails or overwrites first box.

2. **Transaction ID malleability: fee and tx_type excluded from `compute_tx_id`**
   - Severity: medium
   - Location: node/utxo_db.py:64-73
   - Description: The `compute_tx_id()` function hashes only input box_ids, output box_ids, and timestamp. It does not include `fee_nrtc` or `tx_type` in the hash. This means two transactions with identical inputs and outputs but different fees (or different types) produce the same `tx_id`. An attacker could submit a transaction with fee=0, observe its tx_id, then resubmit with a higher fee — both transactions share the same tx_id, creating ambiguity in transaction tracking, mempool management, and downstream consumers that key off tx_id.
   - Reproduction: 1) Construct tx A with inputs=[box1], outputs=[box2], fee=0, timestamp=T. 2) Compute tx_id = compute_tx_id(inputs, outputs, T). 3) Construct tx B with same inputs/outputs/timestamp but fee=1000. 4) Both produce identical tx_id. 5) Submit both to mempool — only one is stored by tx_id PK, but fee differs.

3. **State root computation loads entire UTXO set into memory — DoS vector at scale**
   - Severity: low
   - Location: node/utxo_db.py:485-488
   - Description: The `compute_state_root()` method fetches ALL unspent boxes from the database in a single `SELECT` without pagination or streaming (`rows = conn.execute("SELECT box_id FROM utxo_boxes WHERE spent_at IS NULL ORDER BY box_id ASC").fetchall()`). It then builds a full Python list of SHA256 hashes in memory. As the UTXO set grows to millions of entries (expected in production), this will consume significant memory per call, and since this function is used for cross-node consensus, it could be triggered frequently. An attacker could trigger repeated calls to exhaust node memory.
   - Reproduction: 1) Populate UTXO set with >1M unspent boxes. 2) Call `compute_state_root()`. 3) Observe memory spike as all rows and hashes are loaded. 4) Repeat in a loop to trigger OOM conditions.

## Known failures of this audit
- Did not check external dependency versions
- Did not run dynamic analysis
- Confidence limited to static code review only

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.8, 0.7, 0.6]

## What I would test next
- Run property-based tests on UTXO serialization
- Test concurrent access patterns
- Verify Merkle proof generation edge cases
