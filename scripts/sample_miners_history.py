#!/usr/bin/env python3
"""Append /api/miners snapshots into JSONL so fossil-record.html can build history over time.

Example:
  python3 scripts/sample_miners_history.py --output widgets/data/miners-history.jsonl --count 12 --interval 300
"""
from __future__ import annotations
import argparse, json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace('+00:00', 'Z')

def fetch_json(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'rustchain-fossil-sampler/1.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)

def main():
    ap = argparse.ArgumentParser(description='Sample /api/miners into a JSONL history file')
    ap.add_argument('--url', default='https://bulbous-bouffant.metalseed.net/api/miners')
    ap.add_argument('--epoch-url', default='')
    ap.add_argument('--output', required=True)
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--interval', type=int, default=300, help='seconds between snapshots')
    args = ap.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    for i in range(args.count):
        miners = fetch_json(args.url)
        epoch = None
        if args.epoch_url:
            try:
                epoch_payload = fetch_json(args.epoch_url)
                epoch = epoch_payload.get('epoch') if isinstance(epoch_payload, dict) else None
            except Exception:
                epoch = None
        row = {
            'captured_at': now_iso(),
            'epoch': epoch,
            'source': args.url,
            'miners': miners,
        }
        with out.open('a') as fh:
            fh.write(json.dumps(row) + '
')
        print(f'[{i+1}/{args.count}] wrote snapshot with {len(miners)} miners to {out}')
        if i < args.count - 1:
            time.sleep(args.interval)

if __name__ == '__main__':
    main()
