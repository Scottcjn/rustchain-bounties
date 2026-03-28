# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Build a deployable fossil-record dataset from RustChain sources."""

from __future__ import annotations

import argparse
import json
import sqlite3
import ssl
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

API_BASE = "https://50.28.86.131"
DEFAULT_OUTPUT = Path(__file__).with_name("fossil-record.sample.json")
SECONDS_PER_EPOCH = 600 * 144

ARCHITECTURES = [
    {"key": "68k", "label": "68K", "color": "#8c5a22", "depth": 0},
    {"key": "g3_g4", "label": "G3/G4", "color": "#b86a2f", "depth": 1},
    {"key": "g5", "label": "G5", "color": "#c07a3a", "depth": 2},
    {"key": "sparc", "label": "SPARC", "color": "#9f334b", "depth": 3},
    {"key": "mips", "label": "MIPS", "color": "#2d8f62", "depth": 4},
    {"key": "power8", "label": "POWER8", "color": "#20558c", "depth": 5},
    {"key": "riscv", "label": "RISC-V", "color": "#6b4fd1", "depth": 6},
    {"key": "apple_silicon", "label": "Apple Silicon", "color": "#bfc6ce", "depth": 7},
    {"key": "arm", "label": "ARM", "color": "#6ba7a8", "depth": 8},
    {"key": "modern_x86", "label": "Modern x86", "color": "#d8d8d2", "depth": 9},
    {"key": "unknown", "label": "Unknown", "color": "#767b82", "depth": 10},
]


@dataclass(frozen=True)
class FossilRecord:
    epoch: int
    architecture: str
    architecture_label: str
    miner_id: str
    device: str
    rtc_earned: float
    fingerprint_quality: float
    multiplier: float
    attested_at: int


def _architecture_meta(key: str) -> dict[str, Any]:
    for item in ARCHITECTURES:
        if item["key"] == key:
            return item
    return ARCHITECTURES[-1]


def canonical_architecture(
    device_arch: str | None,
    hardware_type: str | None = None,
    device_family: str | None = None,
) -> str:
    joined = " ".join(
        [(device_arch or "").lower(), (hardware_type or "").lower(), (device_family or "").lower()]
    )
    if "68k" in joined or "680" in joined:
        return "68k"
    if "g3" in joined or "g4" in joined or "powerbook g4" in joined:
        return "g3_g4"
    if "g5" in joined:
        return "g5"
    if "sparc" in joined:
        return "sparc"
    if "mips" in joined:
        return "mips"
    if "power8" in joined or "ppc64le" in joined:
        return "power8"
    if "risc" in joined:
        return "riscv"
    if "apple silicon" in joined:
        return "apple_silicon"
    if "aarch64" in joined or "arm" in joined:
        return "arm"
    if "x86" in joined or "modern" in joined or "amd64" in joined:
        return "modern_x86"
    return "unknown"


def _load_json_url(url: str) -> Any:
    ctx = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=ctx) as response:
        return json.load(response)


def fetch_live_snapshot() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    miners = _load_json_url(f"{API_BASE}/api/miners?limit=200")
    epoch = _load_json_url(f"{API_BASE}/epoch")
    if isinstance(miners, dict):
        miners = miners.get("miners", [])
    return list(miners), epoch


def _estimate_first_epoch(current_epoch: int, last_attest: int | None, multiplier: float) -> int:
    multiplier = max(multiplier, 0.001)
    implied_span = min(96, max(8, int(round(multiplier * 18))))
    return max(1, current_epoch - implied_span)


def generate_sample_history(
    miners: Iterable[dict[str, Any]],
    current_epoch: int,
    sample_epochs: int = 48,
) -> list[FossilRecord]:
    records: list[FossilRecord] = []
    start_epoch = max(1, current_epoch - sample_epochs + 1)
    for index, miner in enumerate(miners):
        multiplier = float(miner.get("antiquity_multiplier") or 0.001)
        first_epoch = max(start_epoch, _estimate_first_epoch(current_epoch, miner.get("last_attest"), multiplier))
        arch_key = canonical_architecture(miner.get("device_arch"), miner.get("hardware_type"), miner.get("device_family"))
        arch = _architecture_meta(arch_key)
        device = miner.get("hardware_type") or miner.get("device_family") or miner.get("device_arch") or "Unknown device"
        entropy = float(miner.get("entropy_score") or 0.0)
        miner_id = str(miner.get("miner") or miner.get("miner_id") or f"miner-{index + 1}")
        last_attest = int(miner.get("last_attest") or 0)
        epochs_active = max(1, current_epoch - first_epoch + 1)
        step = max(1, int(round(max(1.0, 6.0 - multiplier * 1.5))))
        for epoch in range(first_epoch, current_epoch + 1, step):
            age_ratio = (epoch - first_epoch + 1) / epochs_active
            fingerprint_quality = min(1.0, max(0.15, 0.35 + entropy * 0.4 + age_ratio * 0.35))
            earned = max(0.05, round(multiplier * (0.6 + age_ratio * 1.4), 4))
            attested_at = last_attest - (current_epoch - epoch) * SECONDS_PER_EPOCH
            records.append(
                FossilRecord(
                    epoch=epoch,
                    architecture=arch["key"],
                    architecture_label=arch["label"],
                    miner_id=miner_id,
                    device=device,
                    rtc_earned=earned,
                    fingerprint_quality=round(fingerprint_quality, 4),
                    multiplier=round(multiplier, 4),
                    attested_at=attested_at,
                )
            )
    return sorted(records, key=lambda item: (item.epoch, item.architecture, item.miner_id))


def _sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return [row[0] for row in rows]


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


def _match_history_table(conn: sqlite3.Connection) -> tuple[str, list[str]] | None:
    candidates = {"attestations", "attestation_history", "fossils", "miner_attestations", "sophia_history"}
    for table in _sqlite_tables(conn):
        columns = _table_columns(conn, table)
        lowered = {column.lower() for column in columns}
        if table.lower() in candidates or {"epoch", "miner_id"} <= lowered or {"epoch", "miner"} <= lowered:
            return table, columns
    return None


def load_sqlite_history(db_path: Path) -> list[FossilRecord]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        match = _match_history_table(conn)
        if not match:
            raise ValueError(f"No attestation-like table found in {db_path}")
        table, columns = match
        lowered = {column.lower(): column for column in columns}
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        results: list[FossilRecord] = []
        for row in rows:
            row_dict = dict(row)
            miner_id = str(
                row_dict.get(lowered.get("miner_id", ""))
                or row_dict.get(lowered.get("miner", ""))
                or "unknown-miner"
            )
            epoch = int(row_dict.get(lowered.get("epoch", "epoch"), 0) or 0)
            if epoch <= 0:
                continue
            arch_key = canonical_architecture(
                str(row_dict.get(lowered.get("device_arch", ""), "")),
                str(row_dict.get(lowered.get("hardware_type", ""), "")),
                str(row_dict.get(lowered.get("device_family", ""), "")),
            )
            arch = _architecture_meta(arch_key)
            results.append(
                FossilRecord(
                    epoch=epoch,
                    architecture=arch["key"],
                    architecture_label=arch["label"],
                    miner_id=miner_id,
                    device=str(
                        row_dict.get(lowered.get("device", ""), "")
                        or row_dict.get(lowered.get("hardware_type", ""), "")
                        or row_dict.get(lowered.get("device_family", ""), "")
                        or arch["label"]
                    ),
                    rtc_earned=float(row_dict.get(lowered.get("rtc_earned", ""), 0.0) or 0.0),
                    fingerprint_quality=float(
                        row_dict.get(lowered.get("fingerprint_quality", ""), 0.0)
                        or row_dict.get(lowered.get("entropy_score", ""), 0.0)
                        or 0.0
                    ),
                    multiplier=float(
                        row_dict.get(lowered.get("antiquity_multiplier", ""), 0.0)
                        or row_dict.get(lowered.get("multiplier", ""), 0.0)
                        or 0.0
                    ),
                    attested_at=int(
                        row_dict.get(lowered.get("attested_at", ""), 0)
                        or row_dict.get(lowered.get("last_attest", ""), 0)
                        or row_dict.get(lowered.get("timestamp", ""), 0)
                        or 0
                    ),
                )
            )
        return sorted(results, key=lambda item: (item.epoch, item.architecture, item.miner_id))
    finally:
        conn.close()


def build_dataset(records: list[FossilRecord], current_epoch: int, title: str) -> dict[str, Any]:
    first_seen: dict[str, int] = {}
    by_epoch: dict[int, dict[str, int]] = {}
    for record in records:
        first_seen.setdefault(record.architecture, record.epoch)
        epoch_row = by_epoch.setdefault(record.epoch, {})
        epoch_row[record.architecture] = epoch_row.get(record.architecture, 0) + 1
    summary = [
        {
            "epoch": epoch,
            "layers": [
                {"architecture": arch, "count": count}
                for arch, count in sorted(layer_counts.items(), key=lambda item: _architecture_meta(item[0])["depth"])
            ],
        }
        for epoch, layer_counts in sorted(by_epoch.items())
    ]
    return {
        "title": title,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "current_epoch": current_epoch,
        "architectures": ARCHITECTURES,
        "first_appearance": [{"architecture": key, "epoch": epoch} for key, epoch in sorted(first_seen.items(), key=lambda item: item[1])],
        "settlement_markers": [epoch for epoch in range(10, current_epoch + 1, 10)],
        "summary": summary,
        "records": [record.__dict__ for record in records],
    }


def _load_json_file(path: Path) -> tuple[list[dict[str, Any]], int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    miners = payload["miners"] if isinstance(payload, dict) and "miners" in payload else payload
    current_epoch = int(payload.get("current_epoch", 0) or payload.get("epoch", 0) or 0) if isinstance(payload, dict) else 0
    return list(miners), current_epoch or 115


def main() -> int:
    parser = argparse.ArgumentParser(description="Export RustChain attestation history into a fossil-record dataset.")
    parser.add_argument("--sqlite", type=Path, help="Path to a SQLite export containing attestation history.")
    parser.add_argument("--json", type=Path, help="Path to a JSON miners snapshot.")
    parser.add_argument("--sample", action="store_true", help="Generate a deterministic sample history from the live API.")
    parser.add_argument("--epochs", type=int, default=48, help="Number of epochs to synthesize in sample mode.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path.")
    args = parser.parse_args()

    if args.sqlite:
        records = load_sqlite_history(args.sqlite)
        current_epoch = max(record.epoch for record in records) if records else 0
        title = "RustChain Fossil Record (SQLite export)"
    else:
        if args.json:
            miners, current_epoch = _load_json_file(args.json)
        else:
            miners, epoch_payload = fetch_live_snapshot()
            current_epoch = int(epoch_payload.get("epoch", 115))
        records = generate_sample_history(miners, current_epoch, sample_epochs=args.epochs)
        title = "RustChain Fossil Record (live snapshot approximation)"

    dataset = build_dataset(records, current_epoch, title)
    args.output.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
