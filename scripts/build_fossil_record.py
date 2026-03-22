#!/usr/bin/env python3
"""Build normalized fossil timeline data for the RustChain attestation archaeology visualizer.

Inputs supported:
1. SQLite database containing an attestations/history table.
2. JSON/JSONL snapshot samples collected over time from /api/miners.

Output is a normalized JSON file consumable by widgets/fossil-record.html.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ARCH_ORDER = [
    '68k', 'g3', 'g4', 'g5', 'sparc', 'mips', 'power8', 'apple_silicon', 'modern_x86', 'arm', 'other'
]

ARCH_META = {
    '68k': {'label': '68K', 'color': '#7a4a00', 'bucket': 'vintage'},
    'g3': {'label': 'G3', 'color': '#a85c2c', 'bucket': 'vintage'},
    'g4': {'label': 'G4', 'color': '#c46a2d', 'bucket': 'vintage'},
    'g5': {'label': 'G5', 'color': '#b87333', 'bucket': 'vintage'},
    'sparc': {'label': 'SPARC', 'color': '#9f2b2b', 'bucket': 'retro'},
    'mips': {'label': 'MIPS', 'color': '#1f8a70', 'bucket': 'retro'},
    'power8': {'label': 'POWER8', 'color': '#1f4e79', 'bucket': 'retro'},
    'apple_silicon': {'label': 'Apple Silicon', 'color': '#c0c0c0', 'bucket': 'modern'},
    'modern_x86': {'label': 'Modern x86', 'color': '#b9c0c9', 'bucket': 'modern'},
    'arm': {'label': 'ARM', 'color': '#4c9aff', 'bucket': 'modern'},
    'other': {'label': 'Other', 'color': '#6b7280', 'bucket': 'modern'},
}


def iso_utc(ts: int | float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def canonical_arch(row: Dict[str, Any]) -> str:
    arch = str(row.get('device_arch') or '').lower()
    hw = str(row.get('hardware_type') or '').lower()
    fam = str(row.get('device_family') or '').lower()
    if '68' in arch or '68k' in hw:
        return '68k'
    if 'g3' in arch or 'g3' in hw:
        return 'g3'
    if 'g4' in arch or 'g4' in hw:
        return 'g4'
    if 'g5' in arch or 'g5' in hw:
        return 'g5'
    if 'sparc' in arch or 'sparc' in hw:
        return 'sparc'
    if 'mips' in arch or 'mips' in hw:
        return 'mips'
    if 'power8' in arch or 'power8' in hw or 'powerpc' in fam:
        return 'power8'
    if 'apple_silicon' in arch or 'apple silicon' in hw:
        return 'apple_silicon'
    if 'modern' in arch or fam == 'x86' or 'x86' in hw or 'ivy_bridge' in arch:
        return 'modern_x86'
    if fam == 'arm' or fam == 'aarch64' or arch == 'aarch64' or arch == 'arm':
        return 'arm'
    return 'other'


def load_json_samples(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text()
    if path.suffix.lower() == '.jsonl':
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows
    data = json.loads(text)
    if isinstance(data, dict) and 'samples' in data:
        return data['samples']
    if isinstance(data, list):
        return data
    raise ValueError(f'Unsupported JSON structure in {path}')


def read_sqlite_rows(db_path: Path) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    target = None
    for candidate in ('attestations', 'attestation_history', 'miner_attestations', 'attestation_events'):
        if candidate in tables:
            target = candidate
            break
    if not target:
        raise SystemExit(f'No known attestation table found in {db_path}; tables={tables}')
    cols = [r[1] for r in cur.execute(f'PRAGMA table_info({target})')]
    colmap = {c.lower(): c for c in cols}
    query = f'SELECT * FROM {target} ORDER BY ' + (colmap.get('timestamp') or colmap.get('attested_at') or colmap.get('created_at') or cols[0])
    out = []
    for row in cur.execute(query):
        d = dict(row)
        out.append({
            'miner': d.get(colmap.get('miner')) or d.get(colmap.get('miner_id')),
            'device_arch': d.get(colmap.get('device_arch')),
            'device_family': d.get(colmap.get('device_family')),
            'hardware_type': d.get(colmap.get('hardware_type')),
            'entropy_score': d.get(colmap.get('entropy_score')),
            'fingerprint_quality': d.get(colmap.get('fingerprint_quality')) or d.get(colmap.get('quality_score')),
            'rtc_earned': d.get(colmap.get('rtc_earned')) or d.get(colmap.get('reward')) or 0,
            'epoch': d.get(colmap.get('epoch')),
            'timestamp': d.get(colmap.get('timestamp')) or d.get(colmap.get('attested_at')) or d.get(colmap.get('created_at')),
        })
    conn.close()
    return out


def normalize_samples(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []
    arch_seen: Dict[str, Dict[str, Any]] = {}
    settlements = []
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = defaultdict(list)

    for sample in samples:
        ts = sample.get('captured_at') or sample.get('timestamp') or sample.get('sampled_at')
        if isinstance(ts, str) and ts.endswith('Z'):
            sample_ts = int(datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp())
        else:
            sample_ts = int(ts)
        epoch = sample.get('epoch')
        miners = sample.get('miners') or sample.get('data') or []
        settlements.append({'timestamp': sample_ts, 'iso_time': iso_utc(sample_ts), 'epoch': epoch})
        for row in miners:
            arch = canonical_arch(row)
            event = {
                'miner': row.get('miner'),
                'arch': arch,
                'arch_label': ARCH_META[arch]['label'],
                'device_arch': row.get('device_arch'),
                'device_family': row.get('device_family'),
                'hardware_type': row.get('hardware_type'),
                'entropy_score': row.get('entropy_score'),
                'fingerprint_quality': row.get('fingerprint_quality', row.get('entropy_score')),
                'rtc_earned': row.get('rtc_earned', row.get('reward', 0)),
                'timestamp': sample_ts,
                'iso_time': iso_utc(sample_ts),
                'epoch': epoch,
                'source': sample.get('source', 'snapshot'),
            }
            events.append(event)
            grouped[(arch, sample_ts)].append(event)
            if arch not in arch_seen:
                arch_seen[arch] = {
                    'arch': arch,
                    'label': ARCH_META[arch]['label'],
                    'timestamp': sample_ts,
                    'iso_time': iso_utc(sample_ts),
                    'epoch': epoch,
                }

    layers = []
    for (arch, ts), rows in sorted(grouped.items(), key=lambda x: (x[0][1], ARCH_ORDER.index(x[0][0]) if x[0][0] in ARCH_ORDER else 999)):
        layers.append({
            'arch': arch,
            'arch_label': ARCH_META[arch]['label'],
            'timestamp': ts,
            'iso_time': iso_utc(ts),
            'epoch': rows[0].get('epoch'),
            'count': len(rows),
            'avg_entropy_score': round(sum(float(r.get('entropy_score') or 0) for r in rows) / max(len(rows), 1), 3),
            'avg_fingerprint_quality': round(sum(float(r.get('fingerprint_quality') or 0) for r in rows) / max(len(rows), 1), 3),
            'total_rtc_earned': round(sum(float(r.get('rtc_earned') or 0) for r in rows), 4),
            'miners': [r['miner'] for r in rows],
        })

    return {
        'generated_at': iso_utc(datetime.now(tz=timezone.utc).timestamp()),
        'arch_order': ARCH_ORDER,
        'arch_meta': ARCH_META,
        'summary': {
            'events': len(events),
            'samples': len(samples),
            'unique_miners': len({e['miner'] for e in events if e.get('miner')}),
            'architectures': len({e['arch'] for e in events}),
        },
        'first_seen_architectures': list(sorted(arch_seen.values(), key=lambda r: r['timestamp'])),
        'settlement_markers': settlements,
        'layers': layers,
        'events': events,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description='Build normalized fossil record data JSON')
    ap.add_argument('--input-json', default='', help='JSON or JSONL sample history')
    ap.add_argument('--input-sqlite', default='', help='SQLite DB with attestation history table')
    ap.add_argument('--output', required=True, help='Output JSON path')
    args = ap.parse_args()

    if not args.input_json and not args.input_sqlite:
        raise SystemExit('Provide --input-json or --input-sqlite')

    if args.input_sqlite:
        rows = read_sqlite_rows(Path(args.input_sqlite))
        samples = [{'captured_at': r['timestamp'], 'epoch': r.get('epoch'), 'miners': [r], 'source': 'sqlite'} for r in rows]
    else:
        samples = load_json_samples(Path(args.input_json))

    result = normalize_samples(samples)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f'Wrote {out} with {result["summary"]["events"]} events')


if __name__ == '__main__':
    main()
