#!/usr/bin/env python3
"""
Run BCOS engine and write GitHub Actions outputs.
Called by action.yml composite action step.
"""

import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


def set_output(name: str, value: str) -> None:
    """Write a GitHub Actions output."""
    env_file = os.environ.get("GITHUB_OUTPUT")
    if env_file:
        with open(env_file, "a") as f:
            # Multiline-safe encoding
            delimiter = f"EOF_{uuid.uuid4().hex[:8]}"
            f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")
    else:
        # Local testing fallback
        print(f"::set-output name={name}::{value}")


def main() -> None:
    tier = os.environ.get("BCOS_TIER", "L1").upper()
    reviewer = os.environ.get("BCOS_REVIEWER", "")
    repo_path = os.environ.get("BCOS_PATH", ".")
    node_url = os.environ.get("BCOS_NODE", "https://50.28.86.131")

    engine = Path("/tmp/bcos_engine.py")
    if not engine.exists():
        print("::error::bcos_engine.py not found at /tmp/bcos_engine.py", flush=True)
        sys.exit(1)

    # Build command
    cmd = [
        sys.executable, str(engine),
        repo_path,
        "--tier", tier,
        "--json",
    ]
    if reviewer:
        cmd += ["--reviewer", reviewer]

    print(f"[BCOS] Running scan: tier={tier} path={repo_path}", flush=True)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode not in (0, 1):  # 1 = tier not met, still valid
        print("::error::BCOS engine failed:", result.stderr[:500], flush=True)
        sys.exit(result.returncode)

    # Parse JSON report from stdout
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Engine might print logs before JSON; find the last JSON block
        lines = result.stdout.strip().splitlines()
        json_lines = []
        in_json = False
        for line in lines:
            if line.strip().startswith("{"):
                in_json = True
            if in_json:
                json_lines.append(line)
        try:
            report = json.loads("\n".join(json_lines))
        except Exception:
            print("::error::Could not parse BCOS report JSON", flush=True)
            print("STDOUT:", result.stdout[:500], flush=True)
            sys.exit(1)

    trust_score = report.get("trust_score", report.get("score", 0))
    tier_met = report.get("tier_met", False)
    cert_id = report.get("cert_id") or f"BCOS-{uuid.uuid4().hex[:8]}"

    badge_url = f"{node_url}/bcos/badge/{cert_id}.svg"

    print(f"[BCOS] Score: {trust_score}/100  Tier {tier}: {'PASS' if tier_met else 'FAIL'}", flush=True)
    print(f"[BCOS] Cert: {cert_id}", flush=True)

    # Compact JSON for output (avoid huge multiline blobs)
    report_json = json.dumps(report, separators=(",", ":"))

    set_output("trust_score", str(trust_score))
    set_output("cert_id", cert_id)
    set_output("tier_met", str(tier_met).lower())
    set_output("badge_url", badge_url)
    set_output("report_json", report_json[:4000])  # cap at 4KB


if __name__ == "__main__":
    main()
