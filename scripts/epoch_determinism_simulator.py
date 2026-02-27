#!/usr/bin/env python3
"""Epoch determinism simulator + cross-node replay checker."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class NodeResult:
    node_id: str
    epoch_digest: str
    event_count: int


def _digest_events(events: List[Dict[str, Any]]) -> str:
    h = hashlib.sha256()
    for ev in events:
        norm = json.dumps(ev, sort_keys=True, separators=(",", ":"))
        h.update(norm.encode())
    return h.hexdigest()


def replay_for_node(node_id: str, events: List[Dict[str, Any]]) -> NodeResult:
    # deterministic ordering by (epoch, height, txid)
    ordered = sorted(
        events,
        key=lambda e: (
            int(e.get("epoch", 0)),
            int(e.get("height", 0)),
            str(e.get("txid", "")),
        ),
    )
    return NodeResult(node_id=node_id, epoch_digest=_digest_events(ordered), event_count=len(ordered))


def run(payload: Dict[str, Any]) -> Dict[str, Any]:
    nodes = payload.get("nodes", [])
    if not nodes:
        raise ValueError("payload.nodes is required")

    results = []
    for node in nodes:
        res = replay_for_node(node["node_id"], node.get("events", []))
        results.append(res)

    baseline = results[0].epoch_digest
    mismatches = [
        {"node_id": r.node_id, "digest": r.epoch_digest, "reason": "digest_mismatch"}
        for r in results
        if r.epoch_digest != baseline
    ]

    return {
        "deterministic": len(mismatches) == 0,
        "baseline_digest": baseline,
        "nodes": [r.__dict__ for r in results],
        "mismatches": mismatches,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Epoch determinism simulator")
    ap.add_argument("--input", required=True, help="JSON payload path")
    ap.add_argument("--output", help="output path (default stdout)")
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text())
    report = run(payload)
    out = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
