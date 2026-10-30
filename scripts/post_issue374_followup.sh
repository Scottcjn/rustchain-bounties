#!/usr/bin/env bash
set -euo pipefail

ISSUE_NUMBER="${1:-374}"
MODE="${2:---post}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_DIR}"

mkdir -p reports
SCAN_JSON="reports/node_miner_scan_latest.json"
SCAN_MD="reports/node_miner_scan_latest.md"

python3 scripts/node_miner_weekly_scan.py \
  --expected-miners-file expected_miners.txt \
  --out-json "${SCAN_JSON}" \
  --out-md "${SCAN_MD}"

BODY_FILE="$(mktemp)"
python3 - <<'PY' > "${BODY_FILE}"
import json
from pathlib import Path
from datetime import datetime, timezone

report = json.loads(Path("reports/node_miner_scan_latest.json").read_text(encoding="utf-8"))
summary = report.get("summary", {})
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

lines = []
lines.append("24h follow-up scan update")
lines.append("")
lines.append(f"- Posted: {stamp}")
lines.append(f"- Scan generated: {report.get('generated_at', '-')}")
lines.append(f"- Nodes scanned: {summary.get('nodes_scanned', 0)}")
lines.append(f"- Node hosts weekly payout eligible: {summary.get('node_hosts_weekly_payout_eligible', 0)}")
lines.append(f"- Miners observed: {summary.get('miners_observed', 0)}")
lines.append(f"- Miners weekly payout eligible: {summary.get('miners_weekly_payout_eligible', 0)}")
lines.append(f"- Expected miners missing: {summary.get('expected_miners_missing', 0)}")
lines.append(f"- Version mismatch nodes: {summary.get('version_mismatch_nodes', 0)}")
lines.append("")
lines.append("If your miner is not visible in `/api/miners`, upgrade to latest from `Scottcjn/Rustchain` main and restart.")
print("\n".join(lines))
PY

if [[ "${MODE}" == "--dry-run" ]]; then
  cat "${BODY_FILE}"
  rm -f "${BODY_FILE}"
  exit 0
fi

gh issue comment "${ISSUE_NUMBER}" --repo Scottcjn/rustchain-bounties --body-file "${BODY_FILE}"
rm -f "${BODY_FILE}"
