# Epoch Determinism Simulator + Cross-Node Replay

Utility script for replaying per-node attestation event streams and comparing epoch digests.

## What it checks
- deterministic sorting/replay of events per node
- digest equality across nodes for the same epoch input
- explicit mismatch report when divergence appears

## Run
```bash
python3 scripts/epoch_determinism_simulator.py --input replay.json
```

## Input format
```json
{
  "nodes": [
    {
      "node_id": "n1",
      "events": [{"epoch": 1, "height": 10, "txid": "abc"}]
    }
  ]
}
```
