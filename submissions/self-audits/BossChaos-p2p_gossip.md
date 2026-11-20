<!-- SPDX-License-Identifier: MIT -->
# Self-Audit: node/rustchain_p2p_gossip.py

## Wallet
RTC6d1f27d28961279f1034d9561c2403697eb55602

## Module reviewed
- Path: node/rustchain_p2p_gossip.py
- Commit: 2bf16f232ae9
- Lines reviewed: 1–1290 (whole file)

## Deliverable: 3 specific findings

### 1. PNCounter `max()` merge allows permanent balance inflation — CRDT design flaw
- **Severity:** critical
- **Location:** node/rustchain_p2p_gossip.py lines 209–221 (`PNCounter.merge()`)
- **Description:** `PNCounter.merge()` uses `max()` to combine increment values for each `(miner_id, node_id)` pair. In a legitimate CRDT, `max()` is correct for grow-only counters because honest nodes only increase. However, any node sharing the `P2P_SECRET` can send a gossip message with `credit=999_999_999` for any miner_id. Since merge uses `max()`, the inflated value permanently replaces the real value across all nodes — the effect is irreversible because subsequent merges can never shrink below the max. The fix must authenticate node_id per-message with Ed25519 so that only the owning node can set its own slot.
- **Reproduction:**
  ```python
  import os; os.environ['RC_P2P_SECRET'] = 'test_secret_32_chars_minimum_ok'
  from rustchain_p2p_gossip import PNCounter
  
  honest = PNCounter()
  honest.credit('miner_alice', 'node_A', 20)  # legitimate 20 nRTC reward
  
  malicious = PNCounter()
  malicious.credit('miner_alice', 'node_A', 999_999_999)  # injected inflation
  
  honest.merge(malicious)
  print(honest.get_balance('miner_alice'))  # 999_999_999 — permanent
  malicious2 = PNCounter()
  malicious2.credit('miner_alice', 'node_A', 1)
  honest.merge(malicious2)
  print(honest.get_balance('miner_alice'))  # still 999_999_999 — irreversible
  ```

### 2. Dynamic `total_nodes` in quorum calculation enables live eclipse attack
- **Severity:** high
- **Location:** node/rustchain_p2p_gossip.py line 838 (`_handle_epoch_vote`)
- **Description:** `total_nodes = len(self.peers) + 1` is evaluated at vote-collection time, not at epoch-proposal time. An attacker who can drop peer connections (TCP RST, BGP hijack, or firewall between nodes) after a proposal is broadcast but before votes are counted can reduce `total_nodes` seen by the collecting node. With a 6-node network: normal quorum = max(3, 4) = 4. If attacker eclipses 3 nodes so collector sees only {self + 2 peers}, total_nodes = 3, quorum = max(3, 2) = 3, allowing 3 colluding nodes to commit an epoch that 3 legitimate nodes never voted on. The quorum floor of 3 helps in small networks but is insufficient for larger deployments.
- **Reproduction:**
  ```python
  import os; os.environ['RC_P2P_SECRET'] = 'test_secret_32_chars_minimum_ok'
  from rustchain_p2p_gossip import GossipNode
  import sqlite3
  
  # Simulate node with 2 visible peers (3 eclipsed out of 6 total)
  node = GossipNode('node_A', {'node_B': 'http://b', 'node_C': 'http://c'}, ':memory:')
  # total_nodes = 3, quorum = max(3, 2) = 3
  # node_A + node_B + node_C = 3 votes → commit passes
  # But real network has 6 nodes; 3 legitimate nodes never voted
  print(f"Quorum with 2 peers: {max(3, (3 // 2) + 1)}")  # 3
  print(f"Correct quorum for 6-node net: {max(3, (6 // 2) + 1)}")  # 4
  ```

### 3. Gossip message replay window is wall-clock only — no monotonic sequence binding
- **Severity:** medium
- **Location:** node/rustchain_p2p_gossip.py lines 464–502 (`verify_message`, `MESSAGE_EXPIRY = 300`)
- **Description:** Message freshness is checked via `abs(msg.timestamp - time.time()) < MESSAGE_EXPIRY` (5-minute window). There is no sequence number or nonce binding per sender. An attacker who records a valid gossip message (e.g., an epoch vote) can replay it within 5 minutes to any node that hasn't seen it (e.g., a node that just recovered from a restart). The deduplication via `msg_id` in `seen_messages` partially mitigates this, but `seen_messages` is an in-memory set that is cleared on restart. A node restart within the 5-minute window loses dedup history, allowing exact replay of any recent message.
- **Reproduction:**
  ```python
  import os, time; os.environ['RC_P2P_SECRET'] = 'test_secret_32_chars_minimum_ok'
  from rustchain_p2p_gossip import GossipNode
  
  node = GossipNode('node_A', {}, ':memory:')
  msg = node.create_message('ping', {'data': 'test'})
  
  node.seen_messages.add(msg.msg_id)  # simulate seen
  # Node restarts — seen_messages cleared
  node.seen_messages.clear()
  
  # Same message accepted again within 5-minute window
  result = node.verify_message(msg)
  print('Replayed message accepted:', result)  # True
  ```

## Known failures of this audit
- Did not audit the `EpochConsensus` class (lines 1046–1141) for vote-counting divergence between the outer `_handle_epoch_vote` path and the inner `EpochConsensus.vote()` path — two separate vote tallies exist and may desync
- Did not test Ed25519 dual-mode paths; audit focused on HMAC-mode vulnerabilities which are the default for most deployments
- Replay finding (#3) confidence is lower because `msg_id` dedup may be persisted to DB in production config not visible in this file alone

## Confidence
- Overall confidence: 0.88
- Per-finding confidence: [0.95, 0.82, 0.72]

## What I would test next
- Instrument `_handle_epoch_vote` to log both the in-file `_epoch_votes` tally and the `EpochConsensus.votes` tally side-by-side across a 3-node testnet to detect desync
- Implement a testnet eclipse simulation: start 6 nodes, drop 3 peer connections mid-epoch, confirm commit succeeds with only 3 votes
- Add persistent `seen_messages` to SQLite (with TTL cleanup) and verify replay is blocked across restarts

## Cross-reference
Finding #1 (PNCounter max() merge) also reported in Security Audit PR #2744 as finding C2 under Bounty #2867.
Finding #2 (dynamic quorum) is a new finding not covered in #2744.
Finding #3 (replay window) is a new finding not covered in #2744.
