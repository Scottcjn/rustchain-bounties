#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail

TIER="${INPUT_TIER:-L1}"
REVIEWER="${INPUT_REVIEWER:-}"
NODE_URL="${INPUT_NODE_URL:-https://rustchain.org}"
SCAN_PATH="${INPUT_PATH:-.}"
PR_NUMBER="${INPUT_PR_NUMBER:-}"
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN:-${INPUT_REPO_TOKEN:-}}"
ENGINE_URL="https://raw.githubusercontent.com/Scottcjn/Rustchain/main/tools/bcos_engine.py"

REPO="${GITHUB_REPOSITORY:-}"
EVENT="${GITHUB_EVENT_NAME:-}"
EVENT_PATH="${GITHUB_EVENT_PATH:-}"
SHA="${GITHUB_SHA:-}"
RUN_ID="${GITHUB_RUN_ID:-}"
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${REPO}/actions/runs/${RUN_ID}"
WORKSPACE="${GITHUB_WORKSPACE:-$PWD}"
RUNNER_TMP="${RUNNER_TEMP:-${TMPDIR:-/tmp}}"

case "$TIER" in
  L0|L1|L2) ;;
  *)
    echo "::error::tier must be one of L0, L1, or L2"
    exit 2
    ;;
esac

if [[ -z "$SHA" ]]; then
  SHA="$(git -C "$WORKSPACE" rev-parse HEAD 2>/dev/null || echo unknown)"
fi

if [[ -z "$PR_NUMBER" && -n "$EVENT_PATH" && -f "$EVENT_PATH" ]]; then
  PR_NUMBER="$(python3 - "$EVENT_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    event = json.load(fh)
pr = event.get("pull_request") or {}
issue = event.get("issue") or {}
print(pr.get("number") or issue.get("number") or "")
PY
)"
fi

SCAN_ABS="$(python3 - "$WORKSPACE" "$SCAN_PATH" <<'PY'
from pathlib import Path
import sys

workspace = Path(sys.argv[1]).resolve()
scan = Path(sys.argv[2])
if not scan.is_absolute():
    scan = workspace / scan
print(scan.resolve())
PY
)"

if [[ ! -d "$SCAN_ABS" ]]; then
  echo "::error::scan path does not exist or is not a directory: $SCAN_PATH"
  exit 2
fi

ENGINE_PATH="$RUNNER_TMP/bcos_engine.py"
REPORT_PATH="$RUNNER_TMP/bcos-report.json"
COMMENT_PATH="$RUNNER_TMP/bcos-comment.md"
ANCHOR_PATH="$RUNNER_TMP/bcos-anchor.json"

echo "Downloading BCOS v2 engine from $ENGINE_URL"
curl -fsSL "$ENGINE_URL" -o "$ENGINE_PATH"

echo "Running BCOS v2 scan: path=$SCAN_ABS tier=$TIER reviewer=${REVIEWER:-none}"
set +e
python3 "$ENGINE_PATH" "$SCAN_ABS" --tier "$TIER" --reviewer "$REVIEWER" --commit "$SHA" --json > "$REPORT_PATH"
ENGINE_STATUS=$?
set -e

python3 - "$REPORT_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    json.load(fh)
PY

read -r TRUST_SCORE CERT_ID TIER_MET < <(python3 - "$REPORT_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    report = json.load(fh)
print(report.get("trust_score", 0), report.get("cert_id", ""), str(report.get("tier_met", False)).lower())
PY
)
TRUST_SCORE="${TRUST_SCORE//$'\r'/}"
CERT_ID="${CERT_ID//$'\r'/}"
TIER_MET="${TIER_MET//$'\r'/}"

python3 - "$REPORT_PATH" "$ANCHOR_PATH" <<'PY'
import json
import os
import sys
from datetime import datetime, timezone

report_path, anchor_path = sys.argv[1], sys.argv[2]
with open(report_path, encoding="utf-8") as fh:
    report = json.load(fh)

event = {}
event_path = os.environ.get("GITHUB_EVENT_PATH")
if event_path and os.path.exists(event_path):
    with open(event_path, encoding="utf-8") as fh:
        event = json.load(fh)

pr = event.get("pull_request") or {}
report["github"] = {
    "repository": os.environ.get("GITHUB_REPOSITORY", ""),
    "event_name": os.environ.get("GITHUB_EVENT_NAME", ""),
    "pr_number": pr.get("number"),
    "run_id": os.environ.get("GITHUB_RUN_ID", ""),
    "run_url": f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}",
    "generated_at": datetime.now(timezone.utc).isoformat(),
}

with open(anchor_path, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=2, sort_keys=True)
PY

echo "BCOS scan complete: trust_score=$TRUST_SCORE cert_id=$CERT_ID tier_met=$TIER_MET"

if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
  {
    echo "trust_score=$TRUST_SCORE"
    echo "cert_id=$CERT_ID"
    echo "tier_met=$TIER_MET"
  } >> "$GITHUB_OUTPUT"
fi

post_pr_comment() {
  if [[ -z "$PR_NUMBER" || -z "$GITHUB_TOKEN" || -z "$REPO" ]]; then
    echo "Skipping PR comment: missing pr-number, github-token, or repository context"
    return 0
  fi

  python3 - "$ANCHOR_PATH" "$COMMENT_PATH" "$NODE_URL" "$RUN_URL" "$PR_NUMBER" <<'PY'
import json
import sys

report_path, comment_path, node_url, run_url, pr_number = sys.argv[1:6]
node_url = node_url.rstrip("/")
with open(report_path, encoding="utf-8") as fh:
    report = json.load(fh)

score = report.get("trust_score", 0)
cert_id = report.get("cert_id", "BCOS-pending")
tier = report.get("tier", "")
tier_met = report.get("tier_met", False)
checks = report.get("score_breakdown", {})
badge_url = f"{node_url}/bcos/badge/{cert_id}-flat.svg"
verify_url = f"https://rustchain.org/bcos/verify/{cert_id}"
filled = max(0, min(20, int(score / 5)))
bar = "#" * filled + "-" * (20 - filled)
status = "PASS" if tier_met else "FAIL"

rows = "\n".join(
    f"| {name.replace('_', ' ').title()} | {points} |"
    for name, points in checks.items()
)

body = f"""<!-- bcos-scan-action v2 -->
## BCOS v2 Scan

![BCOS Badge]({badge_url})

| Field | Value |
| --- | --- |
| PR | #{pr_number} |
| Cert ID | `{cert_id}` |
| Trust Score | {score}/100 `{bar}` |
| Tier | {tier} |
| Tier Met | {status} |
| Verify | [BCOS certificate]({verify_url}) |
| Run | [GitHub Actions]({run_url}) |

### Score Breakdown

| Check | Points |
| --- | ---: |
{rows}

_Generated by the MIT-licensed BCOS v2 reusable action using `tools/bcos_engine.py` from `Scottcjn/Rustchain`._
"""

with open(comment_path, "w", encoding="utf-8") as fh:
    fh.write(body)
PY

  local comments_url="https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/comments"
  local comments_json="$RUNNER_TMP/bcos-comments.json"
  local existing_id=""
  if curl -fsSL \
      -H "Authorization: Bearer ${GITHUB_TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      "$comments_url?per_page=100" > "$comments_json"; then
    existing_id="$(python3 - "$comments_json" <<'PY'
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        comments = json.load(fh)
except Exception:
    comments = []
for comment in comments:
    if "<!-- bcos-scan-action v2 -->" in (comment.get("body") or ""):
        print(comment.get("id", ""))
        break
PY
)"
  fi

  local payload
  payload="$(python3 - "$COMMENT_PATH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as fh:
    print(json.dumps({"body": fh.read()}))
PY
)"

  if [[ -n "$existing_id" ]]; then
    echo "Updating BCOS PR comment $existing_id"
    curl -fsSL -X PATCH \
      -H "Authorization: Bearer ${GITHUB_TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "Content-Type: application/json" \
      "https://api.github.com/repos/${REPO}/issues/comments/${existing_id}" \
      -d "$payload" >/dev/null || echo "::warning::Could not update BCOS PR comment"
  else
    echo "Posting BCOS PR comment"
    curl -fsSL -X POST \
      -H "Authorization: Bearer ${GITHUB_TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "Content-Type: application/json" \
      "$comments_url" \
      -d "$payload" >/dev/null || echo "::warning::Could not post BCOS PR comment"
  fi
}

should_anchor() {
  if [[ -z "$EVENT_PATH" || ! -f "$EVENT_PATH" ]]; then
    echo "false"
    return 0
  fi

  python3 - "$EVENT_PATH" <<'PY'
import json
import os
import sys

path = sys.argv[1]
if not path or not os.path.exists(path):
    print("false")
    raise SystemExit
with open(path, encoding="utf-8") as fh:
    event = json.load(fh)
pr = event.get("pull_request") or {}
print("true" if pr.get("merged") is True else "false")
PY
}

anchor_attestation() {
  if [[ "$(should_anchor)" != "true" ]]; then
    echo "Skipping RustChain anchor: this event is not a merged pull request"
    cp "$ANCHOR_PATH" "$WORKSPACE/bcos-attestation.json"
    return 0
  fi

  local endpoint="${NODE_URL%/}/attest"
  echo "Anchoring BCOS attestation to RustChain: $endpoint"
  curl -fsSL -X POST \
    -H "Content-Type: application/json" \
    --data-binary "@$ANCHOR_PATH" \
    --max-time 20 \
    "$endpoint" >/dev/null || {
      echo "::warning::RustChain attestation endpoint unavailable; saved bcos-attestation.json"
      cp "$ANCHOR_PATH" "$WORKSPACE/bcos-attestation.json"
    }
}

post_pr_comment
anchor_attestation

if [[ "$TIER_MET" != "true" ]]; then
  echo "::warning::BCOS tier $TIER was not met by trust score $TRUST_SCORE"
fi

exit "$ENGINE_STATUS"
