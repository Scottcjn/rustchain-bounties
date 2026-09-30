#!/usr/bin/env python3
"""Shape-check a bounty #16517 re-measurement log. No emulator run, no network."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_KEYS = ("figure", "repo_commit", "emulator", "raw_counts", "tokens_hex")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
HEX_BYTE_RE = re.compile(r"^(0x)?[0-9a-fA-F]{2}$")


def check_record(rec: object) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(rec, dict):
        return ["record must be a JSON object"]

    for k in REQUIRED_KEYS:
        if k not in rec:
            errors.append(f"missing key: {k}")

    sha = rec.get("repo_commit")
    if sha is not None and not (isinstance(sha, str) and SHA_RE.match(sha)):
        errors.append("repo_commit must be a 7–40 char hex SHA (pin before measuring)")

    emu = rec.get("emulator")
    if emu is not None and (not isinstance(emu, str) or not emu.strip()):
        errors.append("emulator must be a non-empty name + version string")

    rc = rec.get("raw_counts")
    if "raw_counts" in rec:
        if not isinstance(rc, list):
            errors.append("raw_counts must be a list")
        elif len(rc) != 16:
            errors.append(f"raw_counts must have 16 entries (16-token gate), got {len(rc)}")
        else:
            bad = next((v for v in rc if not isinstance(v, int) or isinstance(v, bool) or v <= 0), None)
            if bad is not None:
                errors.append(f"raw_counts entry invalid (must be positive int): {bad!r}")
            elif len(set(rc)) == 1:
                warnings.append(
                    "all 16 raw_counts are identical — that is usually the published mean "
                    "copied 16 times, not 16 measured deltas"
                )
            else:
                ordered = sorted(rc)
                med = (ordered[7] + ordered[8]) / 2.0
                for v in rc:
                    if med > 0 and (v > med * 4 or med > v * 4):
                        errors.append(
                            f"wrap/outlier suspect: value {v} vs median {med:g} (>4×). "
                            "inspect counter width."
                        )
                        break

    toks = rec.get("tokens_hex")
    if "tokens_hex" in rec:
        if not isinstance(toks, list):
            errors.append("tokens_hex must be a list")
        elif len(toks) != 16:
            errors.append(f"tokens_hex must have 16 entries, got {len(toks)}")
        else:
            bad_t = next((t for t in toks if not isinstance(t, str) or not HEX_BYTE_RE.match(t)), None)
            if bad_t is not None:
                errors.append(f"tokens_hex entry is not a hex byte: {bad_t!r}")

    if "ratio" in rec:
        if "numerator" not in rec or "denominator" not in rec:
            errors.append("ratio claimed without numerator+denominator raw counts")
        else:
            num, den, ratio = rec.get("numerator"), rec.get("denominator"), rec.get("ratio")
            if not isinstance(num, (int, float)) or not isinstance(den, (int, float)) or den == 0:
                errors.append("numerator/denominator must be numeric with denominator != 0")
            elif not isinstance(ratio, (int, float)):
                errors.append("ratio must be numeric")
            else:
                recomputed = num / den
                if abs(recomputed - ratio) > max(1e-9, abs(ratio) * 0.01):
                    errors.append(
                        f"ratio {ratio} does not match numerator/denominator "
                        f"({num}/{den} = {recomputed:.6g}); do not paste the published figure"
                    )

    src = rec.get("clock_source")
    if src is not None:
        if not isinstance(src, str) or src.strip().lower() not in ("emulated", "host"):
            errors.append("clock_source must be 'emulated' or 'host'")
        elif src.strip().lower() == "host":
            errors.append("clock_source=host is the Genesis 11.3× failure mode; use emulated cycles")

    return [f"WARN: {w}" for w in warnings] + errors


def example_record() -> dict:
    return {
        "figure": "NES cycles/token",
        "repo_commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "emulator": "Mesen <version>",
        "raw_counts": [1117248 + (i % 5) - 2 for i in range(16)],
        "tokens_hex": ["1a", "0f", "33", "07", "2c", "11", "08", "19",
                       "04", "21", "16", "0b", "2e", "13", "09", "1d"],
        "numerator": 17875968,
        "denominator": 16,
        "ratio": 1117248.0,
        "clock_source": "emulated",
    }


def self_test() -> int:
    cases: list[tuple[str, dict, bool]] = [
        ("example", example_record(), True),
        ("missing figure", {"repo_commit": "abc1234", "emulator": "x",
                            "raw_counts": [1] * 16, "tokens_hex": ["00"] * 16}, False),
        ("15 tokens", {**example_record(), "raw_counts": [1] * 15}, False),
        ("wrap", {**example_record(), "raw_counts": [100] * 15 + [10000]}, False),
        ("ratio without sides", {k: v for k, v in example_record().items()
                                 if k not in ("numerator", "denominator")} | {"ratio": 2.0}, False),
        ("pasted ratio", {**example_record(), "ratio": 1.674}, False),
        ("host clock", {**example_record(), "clock_source": "host"}, False),
        ("identical mean copied", {**example_record(), "raw_counts": [1117248] * 16}, True),
    ]
    failed = 0
    for name, rec, expect_pass in cases:
        msgs = check_record(rec)
        hard = [m for m in msgs if not m.startswith("WARN:")]
        ok = not hard
        if ok != expect_pass:
            print(f"SELFTEST FAIL: {name} (expected {'PASS' if expect_pass else 'FAIL'})")
            for m in msgs:
                print(f"  {m}")
            failed += 1
        elif name == "identical mean copied" and not any(m.startswith("WARN:") for m in msgs):
            print("SELFTEST FAIL: identical counts should warn")
            failed += 1
    if failed:
        print(f"SELFTEST: {failed} case(s) failed")
        return 1
    print("SELFTEST PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Shape-check a #16517 re-measurement JSON log (16-token gate, raw counts)."
    )
    ap.add_argument("--check", action="store_true", help="validate --log")
    ap.add_argument("--log", default="", help="path to JSON record")
    ap.add_argument("--example", action="store_true", help="print example record")
    ap.add_argument("--self-test", action="store_true", help="run built-in checker tests")
    args = ap.parse_args(argv)

    if args.example:
        print(json.dumps(example_record(), indent=2))
        return 0
    if args.self_test:
        return self_test()
    if args.check:
        if not args.log:
            print("usage: verify_retro_console.py --check --log record.json", file=sys.stderr)
            return 2
        path = Path(args.log)
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            print(f"FAIL\n- log not found: {path}", file=sys.stderr)
            return 2
        except json.JSONDecodeError as exc:
            print(f"FAIL\n- invalid JSON: {exc}", file=sys.stderr)
            return 1
        msgs = check_record(rec)
        hard = [m for m in msgs if not m.startswith("WARN:")]
        warns = [m for m in msgs if m.startswith("WARN:")]
        for w in warns:
            print(w)
        if hard:
            print("FAIL")
            for e in hard:
                print(f"- {e}")
            return 1
        print("PASS: 16-token gate, raw counts present, no 4× outlier")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
