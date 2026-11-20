# Self-Audit: rustchain-wallet/src/keys.rs + rips/src/ergo_bridge.rs + rustchain-miner/src/transport.rs

## Wallet
RTC52d4fe5e93bda2349cb848ee33ffebeca9b2f68f

## Module reviewed
- **Audit bundle:** 3 modules
  1. `rustchain-wallet/src/keys.rs` (281 lines)
  2. `rips/src/ergo_bridge.rs` (648 lines)
  3. `rustchain-miner/src/transport.rs` (141 lines)
- **Commit:** `92888df054821c3355836ae0cd442b2cf29a1280`
- **Date reviewed:** 2026-04-28

---

## Deliverable: 3 specific findings

### Finding 1 — HIGH — `keys.rs:134-138`: SigningKey Drop does NOT zeroize secret material

**Severity:** High

**Location:** `rustchain-wallet/src/keys.rs:134-138`

**Description:**
The `Drop` implementation for `KeyPair` acknowledges that `SigningKey` from `ed25519-dalek` does not support zeroization, leaving the 32-byte secret key resident in memory after `KeyPair` is dropped. While the comment is honest, there is no mitigation: the bytes remain in heap memory until GC or memory reuse by other allocations. For wallet applications, this is a real risk: a core dump, crash log, or memory dump of a production node could expose private keys.

The comment even says "consider using a wrapper or alternative implementation" but no `unsafe` block, zeroize wrapper, or explicit zeroing mechanism is present.

**Reproduction:**
```rust
// 1. Create a keypair — secret is now in heap at address X
let kp = KeyPair::generate();
// 2. Drop it — bytes at X are NOT cleared
drop(kp);
// 3. A crash dump / core file now contains the raw secret key bytes
```

**Fix:** Use `zeroize::Zeroize` on the raw bytes, or replace ed25519-dalek with a crate that has zeroize support (e.g., `x25519-dalek` v3+).

---

### Finding 2 — HIGH — `ergo_bridge.rs:175-184`: UTXO spend_box O(n) address index cleanup causes unbounded quadratic behavior

**Severity:** High

**Location:** `rips/src/ergo_bridge.rs:175-184`

**Description:**
When `spend_box` removes a box from the UTXO set, it iterates through ALL addresses in `by_address` to remove the box ID. This is O(n) where n = total number of boxes across all addresses. The code comment at lines 172-174 explicitly calls this out: "The address index cleanup iterates all addresses, which is O(n). For high-throughput applications, consider maintaining a reverse index (box_id → address) for O(1) removal." The suggestion exists but was never implemented.

Under active mining with blocks containing 50+ transactions across a ledger with thousands of boxes, this creates quadratic cleanup cost per block.

**Reproduction:**
```rust
// Pseudocode: quadratic behavior
for tx in block.transactions {       // B transactions per block
    for input in tx.inputs {          // M inputs per tx
        // Each spend_box iterates ALL addresses — O(A) per spend
        utxo_set.spend_box(&input.box_id);  // A = total addresses
    }
}
// Total: O(B × M × A) per block — grows with ledger size
// With 2000 addresses, 50 txs, 3 inputs each: 300,000 iterations/block
```

**Fix:** Add `by_box_id: HashMap<BoxId, String>` reverse index for O(1) address lookup.

---

### Finding 3 — MEDIUM — `transport.rs:122-125`: Silent fallback to HTTPS with no verification creates false-positive connectivity

**Severity:** Medium

**Location:** `rustchain-miner/src/transport.rs:122-125`

**Description:**
When both direct HTTPS and proxy fail health checks, `probe_transport` silently falls back to direct HTTPS with `use_proxy = false`. Critically, it does NOT change the TLS configuration — the fallback is functionally identical to the failed first attempt. The log message at line 123 says "Falling back to direct HTTPS (verify=False)" implying cert validation is being disabled, but the code never actually sets `danger_accept_invalid_certs(true)`.

This creates a false-positive: the miner could spend the entire session attempting and failing to connect while believing it has a working transport path.

**Reproduction:**
```rust
// Scenario: Node's TLS cert is expired
// Step 1: First probe fails with TLS error
let response = client.get(&health_url).send().await; // ← TLS error

// Step 2: Fallback fires — same URL, same TLS config
tracing::warn!("[TRANSPORT] Falling back to direct HTTPS (verify=False)");
// But nothing changed! Same expired cert.
// Miner now repeatedly attempts to send to a node that rejects all connections.
```

**Fix:** Either actually disable cert verification in the fallback, or return an error instead of silently proceeding. Fix the misleading log message.

---

## Known failures of this audit

- **PoA consensus mechanism not reviewed.** `proof_of_antiquity.rs` (744 lines) was not read — hardware hash generation and anti-emulation logic contains the core security assumptions of the system.
- **Transaction construction not reviewed.** `rustchain-wallet/src/transaction.rs` (675 lines) handles replay attack protection, nonce management, and fee logic — not examined.
- **Network layer not reviewed.** `rips/src/network.rs` (658 lines) handles P2P gossip — MITM, eclipse, and Sybil attack surfaces not examined.
- **UTXO set consistency not validated.** `UtxoSet` has no consistency check or Merkle proof validation.
- **No runtime execution.** Findings are static code analysis only — no live node testing performed.
- **Ed25519 library version not confirmed.** The zeroization gap depends on which `ed25519-dalek` version is in use.

## Confidence

- **Overall confidence:** 0.72
- **Per-finding confidence:** [0.85, 0.80, 0.75]

Finding 1 is high-confidence (only requires reading the Drop impl). Finding 2 is well-documented in the code's own comments. Finding 3 requires understanding async Rust behavior; minor uncertainty about reqwest TLS error propagation.

## What I would test next

1. **Replay attack test:** Submit the same `ErgoTransaction` ID twice — verify second submission is rejected as double-spend.
2. **Memory forensics:** After dropping `KeyPair`, allocate buffer and search for raw key bytes. Run under Valgrind for definitive proof of residual bytes.
3. **TLS cert expiry test:** Start node with expired cert, observe `probe_transport` behavior, count TLS handshake failures.

---

*Cross-ref to bounty #2867 (Security Audit): Finding 1 is a candidate for escalation — a demonstrable residual key in heap memory qualifies as High severity per the rate table.*
