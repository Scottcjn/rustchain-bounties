# Self-Audit: node/governance.py

**Wallet:** RTC52d4fe5e93bda2349cb848ee33ffebeca9b2f68f
**Module:** `node/governance.py`
**Commit reviewed:** `92888df054821c3355836ae0cd442b2cf29a1280`
**Auditor:** @universe7creator

---

## Module Overview

Implements RIP-0002 on-chain governance: proposal creation/voting,Sophia AI evaluation, founder veto. Key entry points: `create_proposal()`, `cast_vote()`, `_verify_miner_signature()`.

---

## Finding 1 — HIGH: Cross-proposal Signature Replay via Actionless Signed Payload

**Severity:** High
**Confidence:** 0.92
**Location:** `_verify_miner_signature()`, lines ~58–74; `cast_vote()`, lines ~240–243

### Description

The signed payload is `f"{action}:{miner_id}:{timestamp}"`. For the `cast_vote` action, the payload **does not include `proposal_id`** — only the action name ("vote"), the miner ID, and timestamp.

```python
# governance.py:59–74
message = f"{action}:{miner_id}:{ts}".encode()
verify_key.verify(message, bytes.fromhex(signature_hex))
```

For voting, the action is always `"vote"`. A captured valid signature for miner X for action `"vote"` at timestamp T remains valid for any other proposal within `_SIGNATURE_MAX_AGE_SECONDS` (5 minutes).

```python
# cast_vote() — only validates timestamp and miner_id control:
if not _verify_miner_signature(miner_id, "vote", data):
    return jsonify({"error": "invalid or missing signature"}), 401
```

No `proposal_id` or `vote` value in the signed payload means an attacker who intercepts or observes one vote submission can replay it to change X's vote on a different proposal within the same 5-minute window.

### PoC

```python
import json, time, nacl.signing, nacl.hash

# Miner X submits legitimate vote on proposal 7 — this signature is captured
miner_id = "MinerX_pubkey_hex"
ts_orig = int(time.time()) - 30  # 30 seconds ago
sig_orig = sign(f"vote:{miner_id}:{ts_orig}")

# Attacker replays same signature to change miner's vote on proposal 5
malicious_payload = {
    "miner_id": miner_id,
    "proposal_id": 5,      # <-- different proposal, NOT in signed payload
    "vote": "against",
    "signature": sig_orig, # <-- same signature, still within 5-min window
    "timestamp": ts_orig,
}
# Server accepts: miner_id and signature verify, proposal_id is never checked
```

### Fix

Include `proposal_id` and the `vote` value in the signed payload:

```python
message = f"vote:{miner_id}:{proposal_id}:{vote_choice}:{ts}".encode()
```

---

## Finding 2 — MEDIUM: Quorum Threshold Bypassed by Single High-Weight Miner

**Severity:** Medium
**Confidence:** 0.75
**Location:** `cast_vote()` lines ~280–287; `_count_active_miners()`, `_get_miner_antiquity_weight()`

### Description

Quorum is checked against **miner count** but votes are tallied in **weighted units**:

```python
# cast_vote() — quorum check:
total = sum(updated)                    # weighted sum (antiquity multipliers)
active_miners = _count_active_miners(db_path)
quorum_met = (total >= active_miners * QUORUM_THRESHOLD)
```

If one miner has antiquity multiplier = 1000 (mining since genesis), their single vote = 1000 weight units. With 1 active miner, quorum threshold = 0.33. A vote of 1000 > 0.33, so quorum is met by 1 vote.

An attacker who accumulates high antiquity weight can single-handedly meet the 33% quorum threshold, making the governance vulnerable to a weight-concentration attack.

### Mitigation

The quorum check should be based on voter **count** (not weight), or weight should be capped per miner:

```python
# Option A: quorum check based on vote count
num_voters = conn.execute(
    "SELECT COUNT(DISTINCT miner_id) FROM governance_votes WHERE proposal_id = ?",
    (proposal_id,)
).fetchone()[0]
quorum_met = (num_voters >= active_miners * QUORUM_THRESHOLD)

# Option B: cap weight per miner in quorum calculation
capped_weight = min(weight, QUORUM_THRESHOLD * active_miners)
```

---

## Finding 3 — MEDIUM: `balance_tolerance` Magic Number Uncommented (consensus_probe.py)

**Severity:** Low (code clarity)
**Confidence:** 0.62
**Location:** `node/consensus_probe.py`, `detect_divergence()`, `balance_tolerance=1e-6`

### Note

This is in `consensus_probe.py` (the other module reviewed this session), but documented for completeness:

```python
def detect_divergence(snapshots: List[NodeSnapshot], balance_tolerance: float = 1e-6) -> List[str]:
```

The value `1e-6` has no inline comment explaining why 1e-6. This is a floating-point comparison threshold for RTC balances — 1e-6 might represent 1 micro-RTC, but without context a future developer may change it to an inappropriate value.

---

## Known Failures

1. The `consensus_probe.py` already submitted in previous cycle: partial-failure silent data loss, sequential fetch under shared timeout budget.
2. The `balance_tolerance = 1e-6` default is already flagged in this module's code but not yet fixed.
