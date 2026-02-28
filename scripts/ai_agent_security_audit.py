#!/usr/bin/env python3
"""Static security audit for AI agent Python codebases."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

RULES = [
    ("dynamic_exec", re.compile(r"\b(eval|exec)\s*\("), "high"),
    ("subprocess_shell_true", re.compile(r"subprocess\.(run|Popen)\([^\n]*shell\s*=\s*True"), "high"),
    ("pickle_loads", re.compile(r"\bpickle\.(load|loads)\s*\("), "medium"),
    ("requests_no_timeout", re.compile(r"requests\.(get|post|put|delete|patch)\((?![^\n]*timeout\s*=)"), "medium"),
    ("hardcoded_secret_like", re.compile(r"(?i)(api[_-]?key|token|secret)\s*=\s*[\"\'][^\"\']{12,}[\"\']"), "high"),
]


def scan_file(path: Path) -> List[Dict[str, object]]:
    findings = []
    text = path.read_text(errors="ignore")
    for i, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern, severity in RULES:
            if pattern.search(line):
                findings.append(
                    {
                        "file": str(path),
                        "line": i,
                        "rule": rule_id,
                        "severity": severity,
                        "snippet": line.strip()[:240],
                    }
                )
    return findings


def scan_tree(root: Path) -> Dict[str, object]:
    all_findings: List[Dict[str, object]] = []
    for py in root.rglob("*.py"):
        if any(p in {".git", ".venv", "venv", "__pycache__"} for p in py.parts):
            continue
        all_findings.extend(scan_file(py))

    severity_counts = {"high": 0, "medium": 0, "low": 0}
    for f in all_findings:
        severity_counts[f["severity"]] += 1

    return {
        "target": str(root),
        "summary": {
            "total_findings": len(all_findings),
            "severity": severity_counts,
        },
        "findings": all_findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="AI agent security audit")
    ap.add_argument("--target", default=".", help="directory to scan")
    ap.add_argument("--output", help="optional JSON output path")
    args = ap.parse_args()

    report = scan_tree(Path(args.target))
    rendered = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n")
    else:
        print(rendered)

    # non-zero exit on high severity findings for CI gating
    if report["summary"]["severity"]["high"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
