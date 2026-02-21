docs/MECHANISM_SPEC_AND_FALSIFICATION_MATRIX.md

---

# RustChain Mechanism Specification and Falsification Matrix

## Document Information
- **Version:** 2.1
- **Last Updated:** 2024-01-15
- **Status:** REVISED (Addressing Critical Security Findings)
- **Classification:** Protocol Specification

---

## 1. Executive Summary

This document provides the complete mechanism specification for RustChain, a Byzantine Fault Tolerant (BFT) consensus protocol designed for distributed ledger systems. This revision addresses critical security and logic flaws identified during the initial audit, specifically correcting false quantum security claims, crash failure tolerance calculations, test parameter boundaries, threshold signature integration, collision resistance testing methodology, protocol state machine ambiguities, and client authentication requirements.

The protocol achieves safety and liveness under the synchronous and partially synchronous network models respectively, supporting up to f Byzantine faults in a network of n ≥ 3f + 1 nodes. This document establishes the formal specification, security proofs, and falsification test matrix required for implementation and verification.

---

## 2. System Model and Assumptions

### 2.1 Node Configuration and Fault Model

RustChain operates with a fixed node count n where n ≥ 3f + 1, with f representing the maximum number of faulty nodes the system can tolerate. The fault model encompasses three categories of node behavior: crash faults where nodes stop responding without malicious behavior, Byzantine faults where nodes exhibit arbitrary and potentially malicious behavior including collusion, and equivocation faults where nodes send conflicting messages to different subsets of nodes.

The system assumes a partially synchronous network model as defined by Dwork, Lynch, and Stockmeyer, where there exists a known bound Δ on message delivery latency after some global stabilization time (GST), but no such bound exists before GST. Before GST, the system guarantees safety but not liveness. After GST, the system guarantees both safety and liveness within the bounds of the fault tolerance threshold.

### 2.2 Cryptographic Primitives and Security Assumptions

**CRITICAL CORRECTION:** The protocol employs the following cryptographic primitives with explicitly stated security assumptions:

Ed25519 elliptic curve signatures provide 128-bit security against classical attacks but are VULNERABLE to Shor's algorithm for quantum computation. This protocol does NOT claim quantum resistance. Organizations requiring post-quantum security must implement additional mechanisms such as hash-based signatures (e.g., SPHINCS+) or lattice-based schemes (e.g., CRYSTALS-Dilithium), which are outside the scope of this specification.

BLS12-381 threshold signatures provide the same classical security level as Ed25519 and are similarly vulnerable to quantum attacks. The security of BLS12-381 against classical adversaries relies on the hardness of the elliptic curve discrete logarithm problem (ECDLP) and the decision Diffie-Hellman (DDH) assumption in the pairing-friendly group setting.

The hash function used throughout the protocol is SHA-256, providing 128-bit collision resistance and 128-bit preimage resistance against classical adversaries. Birthday attacks on SHA-256 require approximately 2^128 operations to find a collision, and the protocol's security proofs account for this computational bound.

### 2.3 Synchronization and Time Assumptions

The protocol assumes loosely synchronized clocks across nodes with a maximum drift rate of ε seconds per second. View timeouts are configured with a base timeout value T_base and a backoff multiplier α for exponential backoff on consecutive view changes. The protocol does not rely on a trusted time source but rather on logical timestamps derived from view numbers and sequence numbers.

---

## 3. Threshold Cryptography Framework

### 3.1 Shamir Secret Sharing Scheme

The protocol implements a (t, n) threshold scheme based on Shamir's secret sharing, where t = f + 1 represents the minimum number of shares required to reconstruct the secret. This threshold ensures that any coalition of up to f malicious nodes cannot reconstruct the secret, while any coalition of f + 1 or more honest nodes can reconstruct it.

The secret sharing scheme operates over the finite field GF(p) where p is a 256-bit prime. A secret s is divided into n shares by constructing a random polynomial q(x) of degree t - 1 such that q(0) = s, and computing share_i = q(i) for i = 1 to n. The Lagrange interpolation formula reconstructs the secret from any t shares:

s = Σ_{i∈S} share_i × L_i(0) mod p

where L_i(x) = Π_{j∈S, j≠i} (x - j) / (i - j) mod p and S is the set of shareholder indices.

### 3.2 BLS12-381 Threshold Signatures

The protocol employs BLS12-381 threshold signatures for distributed key generation and threshold signing operations. This section specifies the integration of threshold signatures into the consensus protocol, addressing the gap identified in the previous specification.

**Distributed Key Generation (DKG):** The protocol uses a multi-party computation approach based on Pedersen-VSS (Verifiable Secret Sharing) to generate the collective private key. Each node i generates a random polynomial f_i(x) of degree f and distributes shares f_i(j) to all other nodes j. Each node computes its share of the collective secret as s_i = Σ_j f_j(i). The public verification key is computed as the sum of each node's verification share: VK = Σ_i g^{s_i}.

**Threshold Signing Protocol:** When a node needs to produce a threshold signature σ on message m, it follows these steps:

1. Each node computes its partial signature σ_i = H(m)^s_i using its secret share s_i
2. Each node broadcasts σ_i to all other nodes
3. Each node verifies received partial signatures using the corresponding verification shares
4. Once t valid partial signatures are received, the node aggregates them using Lagrange coefficients: σ = Σ_{i∈S} σ_i × L_i(0)
5. The aggregated signature σ can be verified against the collective verification key VK

**Integration with Consensus Flow:** Threshold signatures replace individual signatures in the following protocol stages:

- **Prepare Certificate (PC):** Aggregated threshold signature from f + 1 distinct nodes on the Prepare message content
- **Commit Certificate (CC):** Aggregated threshold signature from f + 1 distinct nodes on the Commit message content
- **View-Change Certificate (VC):** Aggregated threshold signature from f + 1 distinct nodes on the View-Change message content

This integration ensures that only a threshold of honest nodes can produce valid certificates, preventing Byzantine nodes from forging signatures individually.

### 3.3 Key Rotation and Share Refresh

To limit exposure from potential key compromise, the protocol supports periodic key rotation and share refresh operations. The rotation protocol maintains the same threshold structure while changing the underlying secret. Nodes participate in a distributed key refresh protocol that generates new shares s'_i while preserving the collective verification key VK.

The refresh protocol operates in two phases: a refresh commitment phase where each node broadcasts a commitment to its refresh values, and a refresh opening phase where each node reveals its refresh values. Nodes compute new shares as s''_i = s_i + s'_i, maintaining the additive property that allows the collective key to remain unchanged.

---

## 4. Consensus Protocol Specification

### 4.1 Normal Operation Phase (Three-Phase Commit)

The consensus protocol follows a three-phase commit pattern adapted from Practical Byzantine Fault Tolerance (PBFT), with modifications to incorporate threshold signatures and explicit client authentication. A complete consensus round proceeds through pre-prepare, prepare, and commit phases, achieving total order broadcast under the specified fault model.

**State Machine Definition:** Each node maintains a state machine with the following components:

- **Current View (v):** Integer representing the current logical time, initialized to 0
- **Sequence Number (n):** Monotonically increasing integer assigned to client requests
- **Last Stable Checkpoint (stable_cp):** Sequence number of the last stable checkpoint
- **Operation Log (op_log):** Map of sequence numbers to operation records
- **Reply Cache (reply_cache):** Map of (client_id, request_id) to responses

**Phase 1: Client Request and Authentication**

Upon receiving a client request R = (client_id, request_id, operation, timestamp, signature), the primary performs the following authentication and validation steps before assigning a sequence number:

1. Verify client signature using client's known verification key
2. Check request_id freshness against client's last processed request
3. Validate request timestamp is within acceptable drift bounds
4. Check client has not exceeded rate limits
5. Verify client is authorized for the requested operation (if access control applies)

If any authentication step fails, the primary rejects the request and returns an error response to the client. Only authenticated requests proceed to the pre-prepare phase. This addresses the missing client authentication requirement identified in the audit.

**Phase 2: Pre-Prepare**

The primary node p broadcasts a pre-prepare message to all backup nodes:

Pre-Prepare(v, n, d, σ_p) where:
- v is the current view number
- n is the assigned sequence number
- d is the digest of the client request R
- σ_p is the primary's individual signature on (v, n, d)

Backup nodes validate the pre-prepare message by:
1. Verifying the primary's signature σ_p
2. Checking that n is within the watermarks (higher than last stable checkpoint, below high watermark)
3. Checking that no other request with sequence number n is already prepared in view v
4. Verifying the digest d matches the client's request digest

If validation succeeds, backup nodes enter the prepared state and broadcast prepare messages.

**Phase 3: Prepare**

Each node broadcasts Prepare(v, n, d, σ_i) where σ_i is the node's individual signature. Upon receiving 2f prepare messages from distinct nodes (including its own), a node has a prepare quorum. The prepare quorum, combined with the pre-prepare message, forms a prepared certificate PC = {Pre-Prepare(v, n, d), 2f Prepare(v, n, d) messages}.

**Phase 4: Commit with Threshold Signatures**

Upon obtaining a prepared certificate, each node broadcasts a commit message and participates in the threshold signing protocol for the commit certificate:

1. Node i computes partial commit signature σ_commit_i on (v, n, d) using its threshold secret share
2. Node broadcasts Commit(v, n, d, σ_commit_i) to all nodes
3. Upon receiving f + 1 valid partial commit signatures, node aggregates them into the commit certificate CC

The commit certificate CC is an aggregated threshold signature from f + 1 distinct nodes on the tuple (v, n, d). This ensures that only a threshold of honest nodes can produce a valid commit certificate.

**Phase 5: Execute and Reply**

Upon receiving a valid commit certificate CC, the node executes the operation and sends a reply to the client. The reply includes the execution result, sequence number n, and view v, signed by the node. Nodes cache the response to handle duplicate requests from clients.

### 4.2 View-Change Protocol with VIEW-INIT State Transition

**CRITICAL CORRECTION:** This section provides the formal specification of the view-change protocol, addressing the protocol ambiguity identified in the audit. The protocol introduces a VIEW-INIT state as a distinct phase within view changes, separating the initiation from the completion to provide clearer state machine semantics.

**View-Change State Machine:**

The view-change protocol proceeds through the following states:

- **NORMAL:** Processing client requests in the current view
- **VIEW-INIT:** Primary has detected a timeout or received sufficient view-change requests, initializing the view transition
- **VIEW-PREPARE:** Collecting view-change certificates from nodes
- **VIEW-COMMIT:** Aggregating threshold signatures and completing the view change

**State Transition Conditions:**

From NORMAL to VIEW-INIT:
- Primary timeout expires without completing a request, OR
- Primary receives f valid view-change requests from distinct nodes

From VIEW-INIT to VIEW-PREPARE:
- Primary has collected at least f + 1 view-change requests
- Primary has constructed the new view certificate

From VIEW-PREPARE to VIEW-COMMIT:
- Primary has received f + 1 new-view messages from distinct nodes
- Primary has aggregated the threshold signature for the new-view certificate

From VIEW-COMMIT to NORMAL:
- New primary has broadcast new-view message
- Sufficient nodes have acknowledged the new view

**VIEW-INIT Message Format:**

VIEW-INIT(v+1, C, P, Q) where:
- v+1 is the target view number
- C is the set of checkpoint certificates from nodes
- P is the set of prepared certificates from nodes
- Q is the proof of quorum for the view change

The VIEW-INIT message is signed by the primary and broadcast to all nodes. Nodes verify the VIEW-INIT message by:
1. Checking the primary's signature
2. Verifying the checkpoint certificates C are valid
3. Verifying the prepared certificates P are consistent
4. Confirming the quorum proof Q demonstrates f + 1 nodes support the view change

**Formal Safety Property for VIEW-INIT:**

THEOREM: If the protocol correctly implements the VIEW-INIT state transitions as specified, then safety is preserved during view changes.

PROOF: The safety argument follows from the PBFT safety proof with modifications for the VIEW-INIT phase. Consider two correct nodes i and j in different views v_i and v_j. If node i has prepared certificate PC_i for sequence number n in view v_i, then at least f + 1 nodes have sent prepare messages for (v_i, n). Since at most f nodes are Byzantine, at least one correct node k has sent prepare messages for both (v_i, n) and (v_j, n) if v_j > v_i. The VIEW-INIT phase ensures that any new primary must include PC_i or a higher certificate in its VIEW-INIT message, preventing conflicting preparations for the same sequence number.

### 4.3 Checkpoint Protocol and Garbage Collection

Nodes periodically generate checkpoints to establish stable points in the execution history. A checkpoint is stable when at least f + 1 nodes have executed the same sequence number and produced matching checkpoints. The checkpoint protocol uses threshold signatures to certify stability:

1. Node i executes up to sequence number n and computes checkpoint C_i = (n, state_digest, σ_i)
2. Node broadcasts C_i to all nodes
3. Upon receiving f + 1 checkpoint messages with matching state_digest, node marks checkpoint as stable
4. Node can garbage collect all messages and certificates below the stable checkpoint sequence number

The checkpoint interval is configurable, with a default of 100 sequence numbers between checkpoints.

---

## 5. Falsification Test Matrix

### 5.1 Crash Failure Tolerance Tests

**CRITICAL CORRECTION:** This section revises the crash failure tolerance tests to use the tight bound n = 3f + 1, addressing the inconsistent test parameters finding.

**Test Configuration Parameters:**

All crash failure tolerance tests use the following configuration:
- n = 3f + 1 (tight bound, not the looser n = 4f + 1)
- f = 1 for minimal configuration (n = 4)
- f = 3 for standard configuration (n = 10)
- f = 5 for stress configuration (n = 16)

**Test CFT-1: Maximum Crash Tolerance**

Objective: Verify the system maintains safety and liveness with c = f crash failures.

Setup:
- Configure network with n = 3f + 1 nodes
- Simulate f nodes crashing at random intervals
- Inject client requests at rate R = 10 requests/second

Expected Outcome:
- All non-crashed nodes achieve consensus on all requests
- No divergent forks or conflicting sequence numbers
- System throughput remains at least (n - c) / n × theoretical maximum
- Liveness is maintained within the synchronous bound Δ

Verification Criteria:
- All surviving nodes report identical sequence numbers for all committed requests
- No node reports a prepare certificate that another node cannot achieve
- View changes complete within 3 × T_base timeout period

**Test CFT-2: Crash During View Change**

Objective: Verify view-change protocol handles crash failures during state transition.

Setup:
- Start consensus in view v
- Trigger view change to view v + 1
- Crash f/2 nodes during the VIEW-INIT phase
- Crash remaining f/2 nodes during the VIEW-PREPARE phase

Expected Outcome:
- Remaining f + 1 nodes complete view change
- New primary is elected from surviving nodes
- All surviving nodes converge on the same state
- Pending requests are reprocessed correctly

**Test CFT-3: Crash Recovery and State Synchronization**

Objective: Verify crashed nodes can recover state and rejoin consensus.

Setup:
- Run consensus for 1000 requests
- Crash a node
- Keep it down for 100 requests
- Restart the crashed node

Expected Outcome:
- Recovered node synchronizes state from other nodes
- Recovered node catches up to current sequence number
- No duplicate processing of requests
- State consistency is maintained

### 5.2 Byzantine Fault Tolerance Tests

**Test BFT-1: Maximum Byzantine Tolerance (Tight Bound)**

Objective: Verify safety and liveness with f Byzantine nodes using n = 3f + 1.

Setup:
- Configure network with n = 3f + 1 nodes
- f nodes are controlled by the adversary
- Adversary can send arbitrary messages to any subset of nodes
- Adversary can delay messages up to the synchronous bound Δ

Expected Outcome:
- All honest nodes achieve consensus on all requests
- No two honest nodes commit conflicting sequence numbers
- Liveness is maintained after GST

**Test BFT-2: Byzantine equivocation Attack**

Objective: Verify the protocol prevents double-signing and equivocation.

Setup:
- Adversary controls f nodes
- Attempt to send prepare messages for sequence number n with different digests to different honest nodes
- Attempt to create conflicting threshold signatures

Expected Outcome:
- Honest nodes detect equivocation through digest mismatch
- Conflicting messages are rejected
- The attack does not result in divergent prepare certificates

**Test BFT-3: Message Reordering and Replay**

Objective: Verify the protocol is resilient to message manipulation.

Setup:
- Adversary can reorder messages within the synchronous bound
- Adversary can replay old messages from previous views
- Adversary can drop messages