#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SophiaCore Attestation Inspector — Database Layer.

SQLite storage for Sophia Elya inspection verdicts, historical fingerprints,
and admin override audit trail.

RIP-306: https://github.com/ArokyaMatthew/rustchain-bounties/docs/protocol/RIP-0306-sophia-attestation-inspector.md
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

logger = logging.getLogger("sophia.db")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

VALID_VERDICTS = frozenset({"APPROVED", "CAUTIOUS", "SUSPICIOUS", "REJECTED"})
VALID_OVERRIDE_VERDICTS = frozenset({"APPROVED", "REJECTED"})


@dataclass(frozen=True)
class InspectionResult:
    """Result of a single Sophia Elya inspection."""
    miner_id: str
    verdict: str
    confidence: float
    reasoning: str = ""
    flags: tuple = ()
    epoch: Optional[int] = None
    fingerprint_hash: str = ""
    fingerprint_data: str = ""
    model_version: str = "elyan-sophia:7b-q4_K_M"
    ollama_host: str = ""
    latency_ms: int = 0
    phase: str = "advisory"

    def validate(self) -> "InspectionResult":
        """Return self if valid, raise ValueError otherwise."""
        if self.verdict not in VALID_VERDICTS:
            raise ValueError(f"Invalid verdict: {self.verdict!r}")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        return self

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["flags"] = list(self.flags)
        return d


@dataclass(frozen=True)
class InspectionRecord(InspectionResult):
    """InspectionResult enriched with DB metadata."""
    id: int = 0
    created_at: str = ""
    override_verdict: Optional[str] = None
    override_reason: Optional[str] = None
    override_by: Optional[str] = None
    override_at: Optional[str] = None

    @property
    def effective_verdict(self) -> str:
        """Return override verdict if present, else original verdict."""
        return self.override_verdict or self.verdict

    @property
    def emoji(self) -> str:
        v = self.effective_verdict
        return {"APPROVED": "✨", "CAUTIOUS": "⚠️", "SUSPICIOUS": "🔍", "REJECTED": "❌"}.get(v, "❓")


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sophia_inspections (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    miner_id         TEXT NOT NULL,
    epoch            INTEGER,
    verdict          TEXT NOT NULL,
    confidence       REAL NOT NULL,
    reasoning        TEXT,
    flags            TEXT,
    fingerprint_hash TEXT,
    fingerprint_data TEXT,
    model_version    TEXT DEFAULT 'elyan-sophia:7b-q4_K_M',
    ollama_host      TEXT,
    latency_ms       INTEGER,
    phase            TEXT DEFAULT 'advisory',
    created_at       TEXT DEFAULT (datetime('now')),
    override_verdict TEXT,
    override_reason  TEXT,
    override_by      TEXT,
    override_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_sophia_miner    ON sophia_inspections(miner_id);
CREATE INDEX IF NOT EXISTS idx_sophia_verdict  ON sophia_inspections(verdict);
CREATE INDEX IF NOT EXISTS idx_sophia_created  ON sophia_inspections(created_at);
CREATE INDEX IF NOT EXISTS idx_sophia_override ON sophia_inspections(override_verdict);
"""


# ---------------------------------------------------------------------------
# Database class
# ---------------------------------------------------------------------------


class SophiaDB:
    """SQLite database for Sophia inspection results.

    Uses WAL mode for better concurrency and implements retry logic
    for database-locked errors.
    """

    MAX_RETRIES = 5
    RETRY_BASE_DELAY = 0.1

    def __init__(self, db_path: str = "sophia_inspections.db") -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(_SCHEMA_SQL)
            conn.commit()
        finally:
            conn.close()
        logger.info("SophiaDB initialized at %s", self.db_path)

    def _execute_with_retry(self, func, *args, **kwargs):
        """Execute a DB function with exponential backoff on lock errors."""
        last_err = None
        for attempt in range(self.MAX_RETRIES):
            conn = self._connect()
            try:
                result = func(conn, *args, **kwargs)
                conn.commit()
                return result
            except sqlite3.OperationalError as e:
                last_err = e
                if "locked" in str(e).lower() and attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning("DB locked, retry %d/%d in %.2fs",
                                   attempt + 1, self.MAX_RETRIES, delay)
                    time.sleep(delay)
                    continue
                raise
            finally:
                conn.close()
        raise last_err  # type: ignore[misc]

    # ── Write operations ────────────────────────────────────────────────

    def record_inspection(self, result: InspectionResult) -> int:
        """Store an inspection result. Returns the row ID."""
        result.validate()

        def _insert(conn: sqlite3.Connection) -> int:
            cur = conn.execute(
                """INSERT INTO sophia_inspections
                   (miner_id, epoch, verdict, confidence, reasoning, flags,
                    fingerprint_hash, fingerprint_data, model_version,
                    ollama_host, latency_ms, phase)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result.miner_id,
                    result.epoch,
                    result.verdict,
                    result.confidence,
                    result.reasoning,
                    json.dumps(list(result.flags)),
                    result.fingerprint_hash,
                    result.fingerprint_data,
                    result.model_version,
                    result.ollama_host,
                    result.latency_ms,
                    result.phase,
                ),
            )
            return cur.lastrowid  # type: ignore[return-value]

        row_id = self._execute_with_retry(_insert)
        logger.info("Recorded inspection #%d for %s → %s (%.2f)",
                     row_id, result.miner_id, result.verdict, result.confidence)
        return row_id

    def record_override(
        self,
        inspection_id: int,
        verdict: str,
        reason: str,
        admin: str,
    ) -> bool:
        """Record a human override on an existing inspection."""
        if verdict not in VALID_OVERRIDE_VERDICTS:
            raise ValueError(f"Override verdict must be APPROVED or REJECTED, got: {verdict!r}")
        if not reason.strip():
            raise ValueError("Override reason is required")

        def _update(conn: sqlite3.Connection) -> bool:
            cur = conn.execute(
                """UPDATE sophia_inspections
                   SET override_verdict = ?, override_reason = ?,
                       override_by = ?, override_at = datetime('now')
                   WHERE id = ?""",
                (verdict, reason.strip(), admin, inspection_id),
            )
            return cur.rowcount > 0

        updated = self._execute_with_retry(_update)
        if updated:
            logger.info("Override #%d → %s by %s: %s",
                        inspection_id, verdict, admin, reason)
        return updated

    # ── Read operations ─────────────────────────────────────────────────

    def _row_to_record(self, row: sqlite3.Row) -> InspectionRecord:
        """Convert a sqlite3.Row to an InspectionRecord."""
        d = dict(row)
        flags_raw = d.pop("flags", "[]")
        try:
            flags = tuple(json.loads(flags_raw or "[]"))
        except (json.JSONDecodeError, TypeError):
            flags = ()
        return InspectionRecord(
            id=d.get("id", 0),
            miner_id=d.get("miner_id", ""),
            epoch=d.get("epoch"),
            verdict=d.get("verdict", "CAUTIOUS"),
            confidence=d.get("confidence", 0.0),
            reasoning=d.get("reasoning", ""),
            flags=flags,
            fingerprint_hash=d.get("fingerprint_hash", ""),
            fingerprint_data=d.get("fingerprint_data", ""),
            model_version=d.get("model_version", ""),
            ollama_host=d.get("ollama_host", ""),
            latency_ms=d.get("latency_ms", 0),
            phase=d.get("phase", "advisory"),
            created_at=d.get("created_at", ""),
            override_verdict=d.get("override_verdict"),
            override_reason=d.get("override_reason"),
            override_by=d.get("override_by"),
            override_at=d.get("override_at"),
        )

    def get_latest(self, miner_id: str) -> Optional[InspectionRecord]:
        """Get the most recent inspection for a miner."""
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM sophia_inspections WHERE miner_id = ? ORDER BY id DESC LIMIT 1",
                (miner_id,),
            ).fetchone()
            return self._row_to_record(row) if row else None
        finally:
            conn.close()

    def get_history(self, miner_id: str, limit: int = 50) -> List[InspectionRecord]:
        """Get inspection history for a miner, newest first."""
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM sophia_inspections WHERE miner_id = ? ORDER BY id DESC LIMIT ?",
                (miner_id, limit),
            ).fetchall()
            return [self._row_to_record(r) for r in rows]
        finally:
            conn.close()

    def get_historical_fingerprints(self, miner_id: str, limit: int = 3) -> List[str]:
        """Get the last N fingerprint data blobs for cross-epoch comparison."""
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT fingerprint_data FROM sophia_inspections
                   WHERE miner_id = ? AND fingerprint_data IS NOT NULL
                         AND fingerprint_data != ''
                   ORDER BY id DESC LIMIT ?""",
                (miner_id, limit),
            ).fetchall()
            return [row["fingerprint_data"] for row in rows]
        finally:
            conn.close()

    def get_pending_reviews(self) -> List[InspectionRecord]:
        """Get all CAUTIOUS/SUSPICIOUS verdicts without overrides."""
        conn = self._connect()
        try:
            rows = conn.execute(
                """SELECT * FROM sophia_inspections
                   WHERE verdict IN ('CAUTIOUS', 'SUSPICIOUS')
                     AND override_verdict IS NULL
                   ORDER BY
                     CASE verdict WHEN 'SUSPICIOUS' THEN 0 ELSE 1 END,
                     id DESC""",
            ).fetchall()
            return [self._row_to_record(r) for r in rows]
        finally:
            conn.close()

    def get_batch_status(self, miner_ids: Sequence[str]) -> Dict[str, Optional[InspectionRecord]]:
        """Get the latest inspection for each miner ID in the batch."""
        result: Dict[str, Optional[InspectionRecord]] = {}
        conn = self._connect()
        try:
            for mid in miner_ids:
                row = conn.execute(
                    "SELECT * FROM sophia_inspections WHERE miner_id = ? ORDER BY id DESC LIMIT 1",
                    (mid,),
                ).fetchone()
                result[mid] = self._row_to_record(row) if row else None
        finally:
            conn.close()
        return result

    def get_last_inspected_time(self, miner_id: str) -> Optional[str]:
        """Get the created_at timestamp of the latest inspection for a miner."""
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT created_at FROM sophia_inspections WHERE miner_id = ? ORDER BY id DESC LIMIT 1",
                (miner_id,),
            ).fetchone()
            return row["created_at"] if row else None
        finally:
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics for Prometheus and the dashboard."""
        conn = self._connect()
        try:
            total = conn.execute("SELECT COUNT(*) AS c FROM sophia_inspections").fetchone()["c"]
            by_verdict = {}
            for row in conn.execute(
                "SELECT verdict, COUNT(*) AS c FROM sophia_inspections GROUP BY verdict"
            ).fetchall():
                by_verdict[row["verdict"]] = row["c"]

            avg_confidence = conn.execute(
                "SELECT AVG(confidence) AS a FROM sophia_inspections"
            ).fetchone()["a"] or 0.0

            pending = conn.execute(
                """SELECT COUNT(*) AS c FROM sophia_inspections
                   WHERE verdict IN ('CAUTIOUS', 'SUSPICIOUS')
                     AND override_verdict IS NULL"""
            ).fetchone()["c"]

            avg_latency = conn.execute(
                "SELECT AVG(latency_ms) AS a FROM sophia_inspections WHERE latency_ms > 0"
            ).fetchone()["a"] or 0.0

            return {
                "total_inspections": total,
                "by_verdict": by_verdict,
                "avg_confidence": round(avg_confidence, 4),
                "avg_latency_ms": round(avg_latency, 1),
                "pending_reviews": pending,
            }
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def fingerprint_hash(fingerprint: Mapping[str, Any]) -> str:
    """Compute a SHA-256 hash of a fingerprint bundle for dedup/integrity."""
    canonical = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
