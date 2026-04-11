# Attestation Replay Cross-Node Attack — Full Security Analysis

**Bounty**: #2418 (200 RTC)  
**Target**: Scottcjn/Rustchain  
**Wallet**: C4c7r9WPsnEe6CUfegMU9M7ReHD1pWg8qeSfTBoRcLbg  
**Branch**: `kuanglaodi2-sudo/feature/attestation-replay-full-analysis`  
**Date**: 2026-03-26  

---

## 1. Executive Summary

A **cross-node attestation replay vulnerability** exists in RustChain's P2P gossip system (`node/rustchain_p2p_gossip.py`). An attacker can intercept a valid attestation proof generated for Node A, then **replay it to Node B**, causing Node B to accept and store the attestation as legitimate — without any cryptographic verification at the gossip layer.

The root cause: the gossip protocol (`LWWRegister`) trusts attestation announcements at face value, using only timestamps as ordering — with no verification that the attestation was actually generated for the receiving node.

**Severity: HIGH** — Enables Sybil-style reward theft across nodes without compromising any keys.

---

## 2. Attack Surface Analysis

### 2.1 Relevant Code Components

| File | Role |
|------|------|
| `node/rustchain_p2p_gossip.py` | P2P gossip protocol, CRDT state management |
| `rustchain-miner/src/attestation.rs` | Miner-side attestation generation (challenge→nonce→report) |
| `node/sophia_attestation_inspector.py` | Sophia AI inspection logic |
| `sophia_api.py` | Flash REST API for attestation inspection |
| `node/tests/test_attest_nonce_replay.py` | Nonce replay tests (per-node, not cross-node) |
| `node/tests/test_attest_submit_challenge_binding.py` | Challenge binding tests (single-node) |

### 2.2 Attestation Flow (Normal)

```
Miner A                    Node A                       Node B
  |                           |                           |
  |---get /attest/challenge-->|                           |
  |<--{nonce: "abc123"}------|                           |
  |                           |                           |
  |---perform CPU timing------|                           |
  |---post /attest/submit---->|                           |
  |   {miner, nonce, report,  |                           |
  |    device, signals}       |                           |
  |                           |                           |
  |                    validate nonce                    |
  |                    store in DB                       |
  |                           |                           |
  |                    [later: gossip to B]              |
  |                           |---INV_attest(minerA,ts)->|
  |                           |<--GET_attest(full_data)--|
  |                           |---full attestation------->|
```

### 2.3 The Vulnerability — Cross-Node Replay

```
Attacker                  Node A                       Node B
   |                         |                           |
   |                    [normal flow]                    |
   |                         |                           |
   |---intercept------->{valid attestation for A}       |
   |                         |                           |
   |                         |---INV_attest(minerA,ts)-->|
   |                         |<--GET_attest-------------|
   |                         |---full data-------------->|
   |                         |                           |
   |---relay to B----------{minerA attestation}--------->|
   |                         |    (ts_fake > ts_legit)   |
   |                         |                           |
   |                    [Node B stores fake attestation] |
   |                    [no verification of proof origin]|
```

---

## 3. Vulnerability Details

### 3.1 Root Cause: Gossip Layer Blind Trust

In `rustchain_p2p_gossip.py`, the `LWWRegister` (Last-Write-Wins Register) is used to track attestations:

```python
class LWWRegister:
    def set(self, key: str, value: Dict, timestamp: int) -> bool:
        """Set value if timestamp is newer"""
        if key not in self.data or timestamp > self.data[key][0]:
            self.data[key] = (timestamp, value)
            return True
        return False
```

The `_handle_inventory_announcement` method processes attestation inventory messages:

```python
def _handle_inv_attestation(self, msg: GossipMessage) -> Dict:
    miner_id = msg.payload.get("miner_id")
    remote_ts = msg.payload.get("ts_ok", 0)

    local = self.attestation_crdt.get(miner_id)
    if local is None or remote_ts > self.attestation_crdt.data.get(miner_id, (0, {}))[0]:
        # Request full data
        return {"status": "need_data", "miner_id": miner_id}

    return {"status": "have_data"}
```

**Problem**: If the attacker sends an inventory announcement with `ts_fake > ts_legit`, Node B will request the full data and then store it.

### 3.2 No Binding Between Challenge and Miner Identity

In `attestation.rs`:

```rust
// Step 1: Get challenge nonce from node
let response = transport.post_json("/attest/challenge", &serde_json::json!({})).await?;
let nonce = challenge.get("nonce").and_then(|n| n.as_str()).unwrap_or("").to_string();

// Step 3: Build commitment
let commitment_string = format!("{}{}{}", nonce, wallet, entropy_json);
let commitment_hash = Sha256::digest(commitment_string.as_bytes());
let commitment = hex::encode(commitment_hash);
```

The `nonce` is fetched without any binding to the node's identity. If an attacker obtains the same nonce (or a previously-used nonce), they can replay the attestation to another node.

**Critical Gap**: The `nonce` in the attestation report is not cryptographically bound to the specific node that issued the challenge. Any node can use any nonce that was ever issued by any node.

### 3.3 The Inventory Announcement Attack Path

1. **Capture Phase**: The attacker participates in the P2P network as a regular node. When a legitimate miner submits an attestation to Node A, the gossip layer distributes it. The attacker observes the `INV_attest` announcement (containing miner_id + timestamp).

2. **Timestamp Manipulation**: The attacker creates a fake inventory announcement with the same miner_id but with `ts_ok = now() + ε`, ensuring it's "newer" than the legitimate attestation's timestamp.

3. **Supply Phase**: When Node B receives the fake inventory announcement and requests the full attestation data, the attacker supplies the legitimate attestation data it captured earlier.

4. **Acceptance**: Node B's `LWWRegister` accepts the attestation because the timestamp is newer, and the attestation data appears cryptographically valid (it is — it was legitimately generated).

### 3.4 Why Node B Doesn't Detect the Fraud

Node B's gossip layer calls `_handle_attestation` which only stores the data:

```python
def _handle_attestation(self, msg: GossipMessage) -> Dict:
    attestation = msg.payload
    miner_id = attestation.get("miner")
    ts_ok = attestation.get("ts_ok", int(time.time()))

    # Update CRDT
    if self.attestation_crdt.set(miner_id, attestation, ts_ok):
        self._save_attestation_to_db(attestation, ts_ok)
        logger.info(f"Merged attestation for {miner_id[:16]}...")

    return {"status": "ok"}
```

There is **no verification** that:
- The attestation's `nonce` was issued by (or for) this specific node
- The attestation's `miner` field matches the requesting entity
- The attestation's `report.nonce` hasn't been used on a different node

---

## 4. Attack Impact

### 4.1 Reward Theft (Per-Epoch)

When a miner submits a valid attestation to Node A, the attestation is stored and the miner is credited for that epoch. If the attacker replays this attestation to Node B:

1. Node B stores the attestation for the same miner
2. The miner appears to have submitted attestations to multiple nodes
3. In a system where miners earn rewards based on attestation counts per node, the attacker can cause double-counting or confusion in the reward distribution

### 4.2 Sophie Inspector Pollution

The Sophia AI inspector (`sophia_core.py`) evaluates attestations based on hardware fingerprints. A replayed attestation will have device info from the legitimate miner's hardware, causing:

- Incorrect hardware verification results
- Pollution of the inspector's confidence scoring
- Potential false positives for "APPROVED" verdicts on hardware that wasn't actually measured

### 4.3 Epoch Consensus Corruption

In the epoch consensus mechanism (`EpochConsensus` class in `rustchain_p2p_gossip.py`), epoch settling depends on the attestation CRDT state across nodes. If different nodes have different attestation states due to replay attacks:

- Merkle root calculations will diverge
- Leader election for epoch settlement may be compromised
- The 2-phase commit protocol for epoch settlement can be disrupted

---

## 5. Full Fix Implementation

### 5.1 Fix 1: Attestation-Node Binding (attestation.rs)

**File**: `rustchain-miner/src/attestation.rs`

The nonce must be bound to the specific node's identity. Add the node's peer ID to the commitment:

```rust
// In attest() function, modify Step 3:

// Fetch node identity for binding
let node_peer_id = transport.get_peer_id().await
    .unwrap_or_else(|| "unknown".to_string());

// Step 3: Build commitment with node binding
let entropy_json = serde_json::to_string(&entropy).unwrap();
let commitment_string = format!("{}:{}:{}:{}",
    nonce,           // challenge nonce
    wallet,          // miner's wallet
    node_peer_id,    // Bind to specific node
    entropy_json     // hardware entropy
);
let commitment_hash = Sha256::digest(commitment_string.as_bytes());
let commitment = hex::encode(commitment_hash);
```

Then modify the report submission to include the node_peer_id:

```rust
let report = AttestationReport {
    // ... existing fields ...
    node_peer_id: node_peer_id,  // NEW: bind attestation to node
    // ... existing fields ...
};
```

### 5.2 Fix 2: Gossip Layer Verification (rustchain_p2p_gossip.py)

**File**: `node/rustchain_p2p_gossip.py`

Add verification in `_handle_attestation` before accepting:

```python
def _handle_attestation(self, msg: GossipMessage) -> Dict:
    attestation = msg.payload
    miner_id = attestation.get("miner")
    ts_ok = attestation.get("ts_ok", int(time.time()))

    # NEW: Verify attestation was generated for THIS node
    expected_node_peer_id = self.node_id  # This node's peer ID
    attestation_node_peer_id = attestation.get("node_peer_id")
    
    if attestation_node_peer_id != expected_node_peer_id:
        logger.warning(
            f"REJECTED replayed attestation for {miner_id[:16]}: "
            f"attestation was for node {attestation_node_peer_id}, "
            f"not {expected_node_peer_id}"
        )
        return {"status": "rejected", "reason": "attestation_node_mismatch"}

    # Existing: Update CRDT
    if self.attestation_crdt.set(miner_id, attestation, ts_ok):
        self._save_attestation_to_db(attestation, ts_ok)
        logger.info(f"Merged attestation for {miner_id[:16]}...")

    return {"status": "ok"}
```

### 5.3 Fix 3: Inventory Announcement Source Verification

**File**: `node/rustchain_p2p_gossip.py`

The `INV_attest` announcement should include the originating node's peer ID, and receiving nodes should verify the announcement path:

```python
def _announce_attestation(self, miner_id: str, ts_ok: int, attestation_hash: str):
    """Announce attestation with source node binding"""
    msg = self.create_message(MessageType.INV_ATTESTATION, {
        "miner_id": miner_id,
        "ts_ok": ts_ok,
        "attestation_hash": attestation_hash,
        "source_node_id": self.node_id,  # NEW: track origin
    })
    self.broadcast(msg, exclude_peer=self.node_id)


def _handle_inv_attestation(self, msg: GossipMessage) -> Dict:
    payload = msg.payload
    miner_id = payload.get("miner_id")
    remote_ts = payload.get("ts_ok", 0)
    source_node_id = payload.get("source_node_id")

    local = self.attestation_crdt.get(miner_id)
    
    # NEW: Only request if the announcement comes directly from 
    # a known peer (not via multi-hop)
    # This prevents relayed replay attacks
    if source_node_id not in self.peers and source_node_id != msg.sender_id:
        logger.warning(
            f"Rejecting attestation announcement from non-direct peer "
            f"{source_node_id}"
        )
        return {"status": "rejected", "reason": "non_direct_peer"}

    if local is None or remote_ts > self.attestation_crdt.data.get(miner_id, (0, {}))[0]:
        return {"status": "need_data", "miner_id": miner_id}

    return {"status": "have_data"}
```

### 5.4 Fix 4: Nonce Uniqueness Per (Miner, Node) Pair

**File**: `node/sophia_attestation_inspector.py` (or wherever challenge generation happens)

The nonce must be unique per (miner, node) pair and expire quickly:

```python
def get_challenge(self, request):
    miner_id = request.get("miner_id")
    if not miner_id:
        return jsonify({"error": "miner_id is required"}), 400

    # Generate nonce bound to miner_id and node identity
    node_id = self.get_node_id()
    nonce = secrets.token_hex(16)
    
    # Store nonce with expiry (5 minutes)
    nonce_key = f"{miner_id}:{node_id}"
    self.nonce_store.set(nonce_key, nonce, expire_seconds=300)
    
    return jsonify({
        "nonce": nonce,
        "node_id": node_id,  # Return node_id for verification
        "expires_at": time.time() + 300
    })


def submit_attestation(self, request):
    miner_id = request.get("miner_id")
    nonce = request.get("nonce")
    node_peer_id = request.get("node_peer_id")
    
    # Verify nonce is bound to this miner and this node
    nonce_key = f"{miner_id}:{node_peer_id}"
    stored_nonce = self.nonce_store.get(nonce_key)
    
    if not stored_nonce or stored_nonce != nonce:
        return jsonify({
            "error": "nonce_invalid_or_expired",
            "code": "NONCE_REPLAY"
        }), 409
    
    # Verify challenge hasn't been used before
    if self.nonce_store.exists_used(nonce):
        return jsonify({
            "error": "nonce_already_used",
            "code": "NONCE_REPLAY"
        }), 409
    
    self.nonce_store.mark_used(nonce)
    # ... rest of processing
```

---

## 6. Test Cases

### 6.1 Test: Cross-Node Replay Should Be Rejected

```python
def test_cross_node_replay_rejected(self):
    """
    Node A gets a valid attestation from Miner X.
    Attacker replays it to Node B.
    Node B should REJECT because node_peer_id doesn't match.
    """
    # Node A gets valid attestation from Miner X
    node_a.submit_attestation(miner_x_attestation)  # node_peer_id = "nodeA"
    
    # Attacker captures and replays to Node B
    node_b.submit_attestation(miner_x_attestation)  # same attestation
    
    # Node B should reject
    result = node_b.query_attestation(miner_x)
    assert result["status"] == "rejected"
    assert result["reason"] == "attestation_node_mismatch"
```

### 6.2 Test: Stale Nonce Replay Should Be Rejected

```python
def test_stale_nonce_replay_rejected(self):
    """
    Nonce used on Node A cannot be replayed on Node B.
    """
    # Get challenge from Node A
    challenge_a = node_a.get_challenge(miner_id="miner-X")
    nonce_a = challenge_a["nonce"]
    
    # Submit to Node A (valid)
    result_a = node_a.submit(miner_id="miner-X", nonce=nonce_a)
    assert result_a["ok"] == True
    
    # Try to use same nonce on Node B (should fail)
    result_b = node_b.submit(miner_id="miner-X", nonce=nonce_a)
    assert result_b["ok"] == False
    assert result_b["code"] == "NONCE_REPLAY"
```

---

## 7. Differential Analysis: What PR #1863 Got Right vs. What Was Missing

PR #1863 (from bounty #2296) addressed per-node nonce replay within the database validation layer (`attest_validate_and_store_nonce`), which correctly prevents the **same node** from reusing a nonce.

**What was MISSING in #1863**:
1. **Cross-node binding**: No verification that a nonce/challenge pair was bound to a specific node's identity
2. **Gossip layer verification**: No checks in `rustchain_p2p_gossip.py` to verify attestation provenance
3. **Inventory announcement source tracking**: No `source_node_id` in gossip announcements
4. **Epoch consensus impact analysis**: The full impact on epoch settlement was not documented

**This analysis extends #1863 by**:
- Identifying the P2P gossip layer as the attack vector
- Providing concrete code fixes for `rustchain_p2p_gossip.py`
- Adding node-binding to `attestation.rs` for cryptographic traceability
- Documenting the full attack tree from capture to epoch consensus corruption

---

## 8. Security Summary

| Category | Finding |
|----------|---------|
| **Vulnerability** | Cross-node attestation replay via P2P gossip |
| **Root Cause** | Gossip layer trusts attestation announcements without verifying node binding |
| **Attack Vector** | P2P network participation + gossip interception |
| **Impact** | Attestation theft, reward manipulation, inspector pollution |
| **Severity** | HIGH |
| **Fix Complexity** | Medium (requires changes to 3 components) |
| **Backward Compatible** | No — requires protocol version bump |

---

## 9. References

- Original issue: https://github.com/Scottcjn/rustchain-bounties/issues/2418
- Attestation code: `rustchain-miner/src/attestation.rs`
- Gossip protocol: `node/rustchain_p2p_gossip.py`
- Sophia inspector: `sophia_core.py`
- Existing nonce replay tests: `node/tests/test_attest_nonce_replay.py`
- Challenge binding tests: `node/tests/test_attest_submit_challenge_binding.py`
