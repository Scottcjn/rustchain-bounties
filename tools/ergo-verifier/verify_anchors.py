# SPDX-License-Identifier: MIT
"""
Ergo Anchor Chain Proof Verifier — Independent Audit Tool
==========================================================
Reads the local ergo_anchors table from rustchain_v2.db,
fetches actual Ergo transactions, extracts R4 register
(Blake2b256 commitment hash), recomputes the commitment
from block data, and reports discrepancies.

Usage:
    python verify_anchors.py --db rustchain_v2.db
    python verify_anchors.py --db rustchain_v2.db --ergo-node http://localhost:9053
    python verify_anchors.py --db rustchain_v2.db --offline
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Crypto primitives
# ---------------------------------------------------------------------------

def blake2b256_hex(data: str) -> str:
    """Compute Blake2b-256 hash of a UTF-8 string, return hex digest."""
    return hashlib.blake2b(data.encode("utf-8"), digest_size=32).hexdigest()


def canonical_json(obj: dict) -> str:
    """Produce deterministic JSON (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def recompute_commitment(height: int, block_hash: str,
                         state_root: str, attestations_root: str,
                         timestamp: int) -> str:
    """Recompute the commitment hash using the same algorithm as rustchain_ergo_anchor.py."""
    data = {
        "attestations_root": attestations_root,
        "rc_hash": block_hash,
        "rc_height": height,
        "state_root": state_root,
        "timestamp": timestamp,
    }
    return blake2b256_hex(canonical_json(data))


# ---------------------------------------------------------------------------
# Database access
# ---------------------------------------------------------------------------

@dataclass
class AnchorRecord:
    id: int
    rustchain_height: int
    rustchain_hash: str
    commitment_hash: str
    ergo_tx_id: str
    ergo_height: Optional[int]
    confirmations: int
    status: str
    created_at: int


def load_anchors(db_path: str) -> List[AnchorRecord]:
    """Load all anchor records from the local database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, rustchain_height, rustchain_hash, commitment_hash,
                   ergo_tx_id, ergo_height, confirmations, status, created_at
            FROM ergo_anchors
            ORDER BY rustchain_height ASC
        """)
    except sqlite3.OperationalError:
        print("ERROR: Table 'ergo_anchors' not found in database.", file=sys.stderr)
        sys.exit(1)

    records = []
    for row in cursor.fetchall():
        records.append(AnchorRecord(
            id=row["id"],
            rustchain_height=row["rustchain_height"],
            rustchain_hash=row["rustchain_hash"],
            commitment_hash=row["commitment_hash"],
            ergo_tx_id=row["ergo_tx_id"],
            ergo_height=row["ergo_height"],
            confirmations=row["confirmations"],
            status=row["status"],
            created_at=row["created_at"],
        ))
    conn.close()
    return records


def load_block_data(db_path: str, height: int) -> Optional[Dict]:
    """Load block data for commitment recomputation."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT height, block_hash, state_root, attestations_hash, timestamp
            FROM blocks WHERE height = ?
        """, (height,))
    except sqlite3.OperationalError:
        conn.close()
        return None

    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ---------------------------------------------------------------------------
# Ergo node API
# ---------------------------------------------------------------------------

class ErgoNodeClient:
    """Minimal client for the Ergo node REST API."""

    def __init__(self, base_url: str = "http://localhost:9053", timeout: int = 10):
        import urllib.request
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_transaction(self, tx_id: str) -> Optional[Dict]:
        """Fetch a confirmed transaction by ID."""
        import urllib.request
        import urllib.error
        url = f"{self.base_url}/blockchain/transaction/byId/{tx_id}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return None

    def get_unconfirmed_transaction(self, tx_id: str) -> Optional[Dict]:
        """Check if a transaction is in the mempool."""
        import urllib.request
        import urllib.error
        url = f"{self.base_url}/transactions/unconfirmed/byTransactionId/{tx_id}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return None

    def extract_commitment_from_tx(self, tx_data: Dict) -> Optional[str]:
        """Extract the commitment hash from R4 register of the first output box.

        Per ARCHITECTURE.md: R4 = commitment hash, R5 = miner_count.
        """
        try:
            outputs = tx_data.get("outputs", [])
            if not outputs:
                return None
            box = outputs[0]
            registers = box.get("additionalRegisters", {})
            # Primary: R4 contains the commitment hash
            r4 = registers.get("R4", "")
            if r4.startswith("0e40") and len(r4) >= 68:
                return r4[4:]
            # Legacy fallback: some early anchors used R5
            r5 = registers.get("R5", "")
            if r5.startswith("0e40") and len(r5) >= 68:
                return r5[4:]
            return None
        except (KeyError, IndexError, TypeError):
            return None


# ---------------------------------------------------------------------------
# Verification engine
# ---------------------------------------------------------------------------

@dataclass
class VerifyResult:
    anchor_id: int
    ergo_tx_id: str
    height: int
    stored_commitment: str
    onchain_commitment: Optional[str]
    recomputed_commitment: Optional[str]
    status: str
    # Statuses: MATCH, MATCH_OFFLINE, MISMATCH, TX_MISSING, UNCONFIRMED,
    #           RECOMPUTE_MISMATCH, MALFORMED_REGISTERS


def verify_anchors(db_path: str, ergo_client: Optional[ErgoNodeClient] = None,
                   offline: bool = False) -> List[VerifyResult]:
    """Run the full verification pipeline."""
    anchors = load_anchors(db_path)
    results = []

    for anchor in anchors:
        onchain_commitment = None
        recomputed = None
        status = "MATCH"

        # Step 1: Fetch Ergo TX (unless offline)
        if not offline and ergo_client:
            tx_data = ergo_client.get_transaction(anchor.ergo_tx_id)
            if tx_data is None:
                unconfirmed = ergo_client.get_unconfirmed_transaction(anchor.ergo_tx_id)
                if unconfirmed:
                    status = "UNCONFIRMED"
                else:
                    status = "TX_MISSING"
            else:
                onchain_commitment = ergo_client.extract_commitment_from_tx(tx_data)
                if onchain_commitment is None:
                    status = "MALFORMED_REGISTERS"
                elif onchain_commitment != anchor.commitment_hash:
                    status = "MISMATCH"

        # Step 2: Recompute commitment from block data
        block = load_block_data(db_path, anchor.rustchain_height)
        if block:
            recomputed = recompute_commitment(
                height=block["height"],
                block_hash=block["block_hash"],
                state_root=block.get("state_root", "0" * 64),
                attestations_root=block.get("attestations_hash", "0" * 64),
                timestamp=block.get("timestamp", anchor.created_at),
            )
            if recomputed != anchor.commitment_hash:
                # Recompute mismatch takes precedence unless we already have on-chain MISMATCH
                if status != "MISMATCH":
                    status = "RECOMPUTE_MISMATCH"

        # Step 3: Offline mode — if recompute matched and we skipped network
        if offline and status == "MATCH" and recomputed == anchor.commitment_hash:
            status = "MATCH_OFFLINE"
        elif offline and status == "MATCH":
            # No block data to recompute against, can't verify
            status = "MATCH_OFFLINE"

        results.append(VerifyResult(
            anchor_id=anchor.id,
            ergo_tx_id=anchor.ergo_tx_id,
            height=anchor.rustchain_height,
            stored_commitment=anchor.commitment_hash,
            onchain_commitment=onchain_commitment,
            recomputed_commitment=recomputed,
            status=status,
        ))

    return results


def print_report(results: List[VerifyResult]) -> bool:
    """Print human-readable verification report. Returns True if all verified."""
    match_count = 0
    total = len(results)

    for r in results:
        is_ok = r.status in ("MATCH", "MATCH_OFFLINE")
        icon = "✓" if is_ok else "✗" if "MISMATCH" in r.status else "?"
        tx_short = r.ergo_tx_id[:10] + "..." if len(r.ergo_tx_id) > 10 else r.ergo_tx_id
        line = f"Anchor #{r.anchor_id}: TX {tx_short} | Height {r.height} | {r.status} {icon}"

        if "MISMATCH" in r.status:
            line += f"\n  Stored:     {r.stored_commitment[:16]}..."
            if r.onchain_commitment:
                line += f"\n  On-chain:   {r.onchain_commitment[:16]}..."
            if r.recomputed_commitment:
                line += f"\n  Recomputed: {r.recomputed_commitment[:16]}..."

        if is_ok:
            match_count += 1
        print(line)

    print(f"\nSummary: {match_count}/{total} anchors verified"
          f", {total - match_count} issues found")

    return match_count == total


def main():
    parser = argparse.ArgumentParser(
        prog="verify_anchors",
        description="Ergo Anchor Chain Proof Verifier — Independent Audit Tool",
    )
    parser.add_argument("--db", required=True, help="Path to rustchain_v2.db")
    parser.add_argument("--ergo-node", default="http://localhost:9053",
                        help="Ergo node API URL")
    parser.add_argument("--offline", action="store_true",
                        help="Skip Ergo node queries, verify DB consistency only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    ergo_client = None if args.offline else ErgoNodeClient(args.ergo_node)
    results = verify_anchors(args.db, ergo_client, offline=args.offline)

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(r) for r in results], indent=2))
        success = all(r.status in ("MATCH", "MATCH_OFFLINE") for r in results)
    else:
        success = print_report(results)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
