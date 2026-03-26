#!/usr/bin/env python3
"""
verify_anchors.py — Independent Audit Tool for Ergo Anchor Chain Proof

Verifies RustChain anchor commitments against the Ergo blockchain.

Usage:
    python verify_anchors.py [--db rustchain_v2.db] [--api http://localhost:9053] [--epoch EPOCH] [--offline]

Requirements:
    Python 3.9+, requests, sqlite3 (stdlib)

Ergo Node API Reference:
    GET /info                          - Node info
    GET /transactions/byId/{id}        - Get transaction by ID
    GET /utxo/byId/{id}                - Get box (UTXO) by transaction ID
"""

import argparse
import hashlib
import json
import sqlite3
import sys
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urljoin
import requests

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class AnchorRecord:
    """Represents a single anchor record from the ergo_anchors table."""
    id: int
    tx_id: str
    epoch: int
    slot_height: int
    stored_commitment: str
    miner_count: int
    miner_ids: str
    architectures: str
    timestamp: int
    confirmations: int = 0

@dataclass
class AttestationRecord:
    """Represents a miner attestation from miner_attest_recent table."""
    miner_id: str
    wallet: str
    commitment: str
    nonce: str
    epoch: int
    arch: str
    timestamp: int

@dataclass
class ErgoBox:
    """Represents an Ergo box with registers."""
    box_id: str
    tx_id: str
    value: int
    registers: Dict[str, Any]  # R4, R5, R6, R7, R8, R9

@dataclass
class VerificationResult:
    """Result of verifying a single anchor."""
    anchor_id: int
    tx_id: str
    epoch: int
    status: str  # "MATCH", "MISMATCH", "MISSING_TX", "ERROR"
    stored_commitment: str = ""
    on_chain_commitment: str = ""
    recomputed_commitment: str = ""
    miner_count_stored: int = 0
    miner_count_on_chain: int = 0
    miner_count_recomputed: int = 0
    reason: str = ""

# ---------------------------------------------------------------------------
# Commitment Computation
# ---------------------------------------------------------------------------

def compute_epoch_commitment(attestations: List[AttestationRecord]) -> str:
    """
    Recomputes the Blake2b256 commitment for an epoch from attestation records.
    
    Commitment = Blake2b256(
        sorted(miner_id + wallet + commitment + nonce + arch for each miner)
    )
    """
    if not attestations:
        return "0" * 64  # Empty commitment
    
    # Build sorted list of miner commitment data
    miner_data = []
    for att in attestations:
        data_str = f"{att.miner_id}:{att.wallet}:{att.commitment}:{att.nonce}:{att.arch}"
        miner_data.append(data_str)
    
    miner_data.sort()
    combined = "|".join(miner_data).encode()
    return hashlib.blake2b(combined, digest_size=32).hexdigest()

# ---------------------------------------------------------------------------
# Database Operations
# ---------------------------------------------------------------------------

def open_db(db_path: str) -> sqlite3.Connection:
    """Opens and returns a SQLite database connection."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_anchor_records(conn: sqlite3.Connection, epoch: Optional[int] = None) -> List[AnchorRecord]:
    """
    Retrieves anchor records from the ergo_anchors table.
    
    Schema expected:
        ergo_anchors(id, tx_id, epoch, slot_height, commitment, 
                     miner_count, miner_ids, architectures, timestamp, confirmations)
    """
    cursor = conn.cursor()
    if epoch is not None:
        cursor.execute(
            "SELECT * FROM ergo_anchors WHERE epoch = ? ORDER BY id",
            (epoch,)
        )
    else:
        cursor.execute("SELECT * FROM ergo_anchors ORDER BY id")
    
    rows = cursor.fetchall()
    return [
        AnchorRecord(
            id=row["id"],
            tx_id=row["tx_id"],
            epoch=row["epoch"],
            slot_height=row["slot_height"],
            stored_commitment=row["commitment"],
            miner_count=row["miner_count"],
            miner_ids=row["miner_ids"],
            architectures=row["architectures"],
            timestamp=row["timestamp"],
            confirmations=row["confirmations"] if "confirmations" in row.keys() else 0
        )
        for row in rows
    ]

def get_attestations_for_epoch(conn: sqlite3.Connection, epoch: int) -> List[AttestationRecord]:
    """
    Retrieves attestation records for a specific epoch from miner_attest_recent.
    
    Schema expected:
        miner_attest_recent(miner_id, wallet, commitment, nonce, epoch, arch, timestamp)
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM miner_attest_recent WHERE epoch = ? ORDER BY miner_id",
        (epoch,)
    )
    rows = cursor.fetchall()
    return [
        AttestationRecord(
            miner_id=row["miner_id"],
            wallet=row["wallet"],
            commitment=row["commitment"],
            nonce=row["nonce"],
            epoch=row["epoch"],
            arch=row["arch"],
            timestamp=row["timestamp"]
        )
        for row in rows
    ]

# ---------------------------------------------------------------------------
# Ergo Node API
# ---------------------------------------------------------------------------

class ErgoNodeAPI:
    """Client for Ergo node REST API (localhost:9053)."""
    
    def __init__(self, base_url: str = "http://localhost:9053"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_info(self) -> Dict[str, Any]:
        """Returns node info."""
        resp = self.session.get(f"{self.base_url}/info")
        resp.raise_for_status()
        return resp.json()
    
    def get_transaction(self, tx_id: str) -> Dict[str, Any]:
        """
        Fetches a transaction by ID.
        
        Returns transaction data including inputs and outputs.
        """
        resp = self.session.get(f"{self.base_url}/transactions/byId/{tx_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    
    def get_box(self, box_id: str) -> Dict[str, Any]:
        """
        Fetches a box (UTXO) by its ID.
        
        Returns box data with registers R4-R9.
        """
        resp = self.session.get(f"{self.base_url}/utxo/byId/{box_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    
    def get_output_boxes(self, tx_id: str) -> List[Dict[str, Any]]:
        """
        Gets output boxes for a transaction.
        
        For anchor transactions, the commitment is stored in the first output box's R4 register.
        """
        tx = self.get_transaction(tx_id)
        if not tx:
            return []
        
        # Transaction outputs contain the boxes
        outputs = tx.get("outputs", [])
        return outputs
    
    def extract_r4_from_box(self, box_data: Dict[str, Any]) -> Optional[str]:
        """
        Extracts the R4 register value (Blake2b256 commitment) from a box.
        
        Registers are stored as JSON objects with 'sigmaProp' type containing hex-encoded bytes.
        """
        registers = box_data.get("registers", [])
        if len(registers) < 4:
            return None
        
        # R4 is at index 3 (0-indexed)
        r4 = registers[3]
        
        # R4 format: {"sigmaProp": {"hex": "..."}}
        if isinstance(r4, dict):
            sigma_prop = r4.get("sigmaProp", {})
            hex_value = sigma_prop.get("hex", "")
        elif isinstance(r4, str):
            # Already a hex string
            hex_value = r4
        else:
            return None
        
        if not hex_value:
            return None
        
        # Decode and re-encode to get the actual hash (Ergo stores sigma proposition)
        # For a constant, the hex represents the raw bytes
        return hex_value.lower()
    
    def extract_miner_count_from_box(self, box_data: Dict[str, Any]) -> Optional[int]:
        """Extracts miner count from R5 register."""
        registers = box_data.get("registers", [])
        if len(registers) < 5:
            return None
        
        r5 = registers[4]
        if isinstance(r5, dict):
            return r5.get("confidential", r5.get("value"))
        elif isinstance(r5, (int, float)):
            return int(r5)
        return None
    
    def get_anchor_commitment(self, tx_id: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Fetches the anchor commitment (R4) from an Ergo transaction.
        
        Returns:
            Tuple of (commitment_hash, box_data) or (None, None) if not found.
        """
        boxes = self.get_output_boxes(tx_id)
        for box in boxes:
            commitment = self.extract_r4_from_box(box)
            if commitment:
                return commitment, box
        
        # Fallback: try getting box directly by ID (tx_id == box_id for unspent)
        box_data = self.get_box(tx_id)
        if box_data:
            commitment = self.extract_r4_from_box(box_data)
            if commitment:
                return commitment, box_data
        
        return None, None

# ---------------------------------------------------------------------------
# Verification Logic
# ---------------------------------------------------------------------------

def verify_single_anchor(
    anchor: AnchorRecord,
    api: ErgoNodeAPI,
    attestations: List[AttestationRecord]
) -> VerificationResult:
    """
    Verifies a single anchor against on-chain data and recomputed commitment.
    """
    result = VerificationResult(
        anchor_id=anchor.id,
        tx_id=anchor.tx_id,
        epoch=anchor.epoch,
        status="ERROR",
        stored_commitment=anchor.stored_commitment,
        miner_count_stored=anchor.miner_count
    )
    
    try:
        # 1. Fetch on-chain commitment from Ergo
        on_chain_commitment, box_data = api.get_anchor_commitment(anchor.tx_id)
        
        if on_chain_commitment is None:
            result.status = "MISSING_TX"
            result.reason = f"Transaction {anchor.tx_id[:16]}... not found or not confirmed"
            return result
        
        result.on_chain_commitment = on_chain_commitment
        
        # Extract on-chain miner count if available
        if box_data:
            on_chain_miner_count = api.extract_miner_count_from_box(box_data)
            if on_chain_miner_count is not None:
                result.miner_count_on_chain = on_chain_miner_count
        
        # 2. Recompute commitment from attestations
        recomputed = compute_epoch_commitment(attestations)
        result.recomputed_commitment = recomputed
        result.miner_count_recomputed = len(attestations)
        
        # 3. Compare: stored == on-chain == recomputed
        if anchor.stored_commitment != on_chain_commitment:
            result.status = "MISMATCH"
            result.reason = f"Stored commitment differs from on-chain. Stored: {anchor.stored_commitment[:16]}..., On-chain: {on_chain_commitment[:16]}..."
            return result
        
        if on_chain_commitment != recomputed:
            result.status = "MISMATCH"
            result.reason = f"On-chain commitment differs from recomputed. On-chain: {on_chain_commitment[:16]}..., Recomputed: {recomputed[:16]}..."
            return result
        
        # All match!
        result.status = "MATCH"
        result.reason = f"Verified: {len(attestations)} miners, commitment matches"
        
    except requests.exceptions.ConnectionError:
        result.status = "ERROR"
        result.reason = f"Cannot connect to Ergo node at {api.base_url}"
    except requests.exceptions.Timeout:
        result.status = "ERROR"
        result.reason = f"Timeout connecting to Ergo node"
    except Exception as e:
        result.status = "ERROR"
        result.reason = f"Unexpected error: {str(e)}"
    
    return result

def verify_anchors_offline(
    anchors: List[AnchorRecord],
    attestations_by_epoch: Dict[int, List[AttestationRecord]]
) -> List[VerificationResult]:
    """
    Performs offline verification without Ergo node API.
    
    Only verifies: stored commitment == recomputed commitment.
    """
    results = []
    
    for anchor in anchors:
        result = VerificationResult(
            anchor_id=anchor.id,
            tx_id=anchor.tx_id,
            epoch=anchor.epoch,
            status="ERROR",
            stored_commitment=anchor.stored_commitment,
            miner_count_stored=anchor.miner_count
        )
        
        attestations = attestations_by_epoch.get(anchor.epoch, [])
        result.miner_count_recomputed = len(attestations)
        
        if not attestations:
            result.status = "ERROR"
            result.reason = f"No attestation data found for epoch {anchor.epoch}"
            results.append(result)
            continue
        
        recomputed = compute_epoch_commitment(attestations)
        result.recomputed_commitment = recomputed
        
        if anchor.stored_commitment != recomputed:
            result.status = "MISMATCH"
            result.reason = f"Stored commitment differs from recomputed. Stored: {anchor.stored_commitment[:16]}..., Recomputed: {recomputed[:16]}..."
        else:
            result.status = "MATCH"
            result.reason = f"Verified (offline): {len(attestations)} miners"
        
        results.append(result)
    
    return results

# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_result(result: VerificationResult) -> str:
    """Formats a single verification result for output."""
    tx_short = result.tx_id[:8] + "..."
    
    if result.status == "MATCH":
        return (
            f"Anchor #{result.anchor_id}: TX {tx_short} | "
            f"Commitment MATCH ✓ | "
            f"{result.miner_count_stored} miners | "
            f"Epoch {result.epoch}"
        )
    elif result.status == "MISMATCH":
        return (
            f"Anchor #{result.anchor_id}: TX {tx_short} | "
            f"Commitment MISMATCH ✗ | "
            f"Expected: {result.recomputed_commitment[:8]}... "
            f"Got: {result.on_chain_commitment[:8] if result.on_chain_commitment else 'N/A'}... | "
            f"Epoch {result.epoch}"
        )
    elif result.status == "MISSING_TX":
        return (
            f"Anchor #{result.anchor_id}: TX {tx_short} | "
            f"TX NOT FOUND ✗ | "
            f"Epoch {result.epoch}"
        )
    else:  # ERROR
        return (
            f"Anchor #{result.anchor_id}: TX {tx_short} | "
            f"ERROR ✗ | "
            f"{result.reason} | "
            f"Epoch {result.epoch}"
        )

def print_summary(results: List[VerificationResult]):
    """Prints a summary of verification results."""
    total = len(results)
    matches = sum(1 for r in results if r.status == "MATCH")
    mismatches = sum(1 for r in results if r.status == "MISMATCH")
    missing = sum(1 for r in results if r.status == "MISSING_TX")
    errors = sum(1 for r in results if r.status == "ERROR")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total anchors verified: {total}")
    print(f"  ✓ Matches:    {matches}")
    print(f"  ✗ Mismatches: {mismatches}")
    print(f"  ? Missing TX: {missing}")
    print(f"  ! Errors:    {errors}")
    
    if mismatches > 0:
        print("\nMismatch Details:")
        for r in results:
            if r.status == "MISMATCH":
                print(f"  - Anchor #{r.anchor_id} (Epoch {r.epoch}): {r.reason}")
    
    if missing > 0:
        print("\nMissing Transaction Details:")
        for r in results:
            if r.status == "MISSING_TX":
                print(f"  - Anchor #{r.anchor_id} (Epoch {r.epoch}): {r.reason}")
    
    if errors > 0:
        print("\nError Details:")
        for r in results:
            if r.status == "ERROR":
                print(f"  - Anchor #{r.anchor_id} (Epoch {r.epoch}): {r.reason}")
    
    print("=" * 60)

# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="verify_anchors.py — Ergo Anchor Chain Proof Verifier for RustChain"
    )
    parser.add_argument(
        "--db", "-d",
        default="rustchain_v2.db",
        help="Path to rustchain_v2.db (default: rustchain_v2.db)"
    )
    parser.add_argument(
        "--api", "-a",
        default="http://localhost:9053",
        help="Ergo node API URL (default: http://localhost:9053)"
    )
    parser.add_argument(
        "--epoch", "-e",
        type=int,
        default=None,
        help="Verify only a specific epoch"
    )
    parser.add_argument(
        "--offline", "-o",
        action="store_true",
        help="Offline mode: verify against DB only, skip Ergo node API"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of anchors to verify"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Open database
    try:
        conn = open_db(args.db)
    except FileNotFoundError:
        print(f"ERROR: Database not found: {args.db}")
        print("Hint: Download a DB dump or run against a live node")
        sys.exit(1)
    
    # Get anchor records
    anchors = get_anchor_records(conn, args.epoch)
    if not anchors:
        print(f"No anchors found in database (epoch={args.epoch})")
        sys.exit(0)
    
    if args.limit:
        anchors = anchors[:args.limit]
    
    print(f"Found {len(anchors)} anchor(s) to verify")
    if args.offline:
        print("Mode: OFFLINE (DB only, no Ergo node API)")
    else:
        print(f"Mode: ONLINE (Ergo node: {args.api})")
    
    # Pre-load attestations by epoch for offline mode
    attestations_by_epoch: Dict[int, List[AttestationRecord]] = {}
    
    if args.offline:
        epochs = set(a.epoch for a in anchors)
        for epoch in epochs:
            attestations_by_epoch[epoch] = get_attestations_for_epoch(conn, epoch)
    
    conn.close()
    
    # Initialize Ergo API client
    api = ErgoNodeAPI(args.api) if not args.offline else None
    
    # Verify each anchor
    results = []
    for i, anchor in enumerate(anchors):
        if args.verbose:
            print(f"\nVerifying Anchor #{anchor.id} (Epoch {anchor.epoch}, TX {anchor.tx_id[:16]}...)")
        
        if args.offline:
            attestations = attestations_by_epoch.get(anchor.epoch, [])
            result = verify_single_anchor_offline_mode(anchor, attestations)
        else:
            # Fetch attestations for this epoch
            conn = open_db(args.db)
            attestations = get_attestations_for_epoch(conn, anchor.epoch)
            conn.close()
            
            result = verify_single_anchor(anchor, api, attestations)
        
        print(format_result(result))
        results.append(result)
    
    # Print summary
    print_summary(results)
    
    # Exit with error code if any mismatches or errors
    mismatches = sum(1 for r in results if r.status in ("MISMATCH", "ERROR"))
    sys.exit(1 if mismatches else 0)

def verify_single_anchor_offline_mode(
    anchor: AnchorRecord,
    attestations: List[AttestationRecord]
) -> VerificationResult:
    """Offline verification for a single anchor."""
    result = VerificationResult(
        anchor_id=anchor.id,
        tx_id=anchor.tx_id,
        epoch=anchor.epoch,
        status="ERROR",
        stored_commitment=anchor.stored_commitment,
        miner_count_stored=anchor.miner_count
    )
    
    result.miner_count_recomputed = len(attestations)
    
    if not attestations:
        result.status = "ERROR"
        result.reason = f"No attestation data found for epoch {anchor.epoch}"
        return result
    
    recomputed = compute_epoch_commitment(attestations)
    result.recomputed_commitment = recomputed
    
    if anchor.stored_commitment != recomputed:
        result.status = "MISMATCH"
        result.reason = f"Stored commitment differs from recomputed. Stored: {anchor.stored_commitment[:16]}..., Recomputed: {recomputed[:16]}..."
    else:
        result.status = "MATCH"
        result.reason = f"Verified (offline): {len(attestations)} miners"
    
    return result

if __name__ == "__main__":
    main()
