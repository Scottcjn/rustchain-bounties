#!/usr/bin/env bash
# =============================================================================
# BCOS Scan — Reusable GitHub Action (BCOS v2)
# Scans a PR, computes trust score, certifies it, and anchors attestation.
# =============================================================================
set -euo pipefail

# ---- Inputs ----
TIER="${INPUT_TIER:-L0}"
REVIEWER="${INPUT_REVIEWER:-}"
NODE_URL="${INPUT_NODE_URL:-https://50.28.86.131}"
PR_NUMBER="${INPUT_PR_NUMBER:-}"
GITHUB_TOKEN="${INPUT_REPO_TOKEN:-}"
REPO="${GITHUB_REPOSITORY:-}"
ACTOR="${GITHUB_ACTOR:-unknown}"
EVENT="${GITHUB_EVENT_NAME:-unknown}"
SHA="${GITHUB_SHA:-unknown}"
RUN_ID="${GITHUB_RUN_ID:-0}"
RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${REPO}/actions/runs/${RUN_ID}"

# Derive PR number from event payload if not provided
if [[ -z "$PR_NUMBER" ]] && [[ -f "$GITHUB_EVENT_PATH" ]]; then
  PR_NUMBER=$(jq -r '.pull_request.number // .issue.number // empty' "$GITHUB_EVENT_PATH" 2>/dev/null || echo "")
fi

if [[ -z "$PR_NUMBER" ]]; then
  echo "::error::Could not determine PR number. Set pr-number input or trigger on pull_request/issue event."
  exit 1
fi

echo "BCOS Scan starting for PR #$PR_NUMBER (tier=$TIER, reviewer=$REVIEWER, node=$NODE_URL)"

# ---- 1. Fetch PR metadata ----
fetch_pr() {
  curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}"
}

fetch_pr_labels() {
  curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/labels"
}

fetch_pr_files() {
  curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/pulls/${PR_NUMBER}/files?per_page=100"
}

# ---- 2. Compute trust_score ----
# Trust score factors:
#   - Base by tier: L0=30, L1=60, L2=90
#   - Reviewer bonus: +10 if a reviewer is assigned
#   - Review quality: +5 per approval, -10 per change request
#   - File diversity: +5 if 3+ distinct path prefixes touched
#   - Max score: 100
compute_trust_score() {
  local base_score=0
  case "$TIER" in
    L0) base_score=30 ;;
    L1) base_score=60 ;;
    L2) base_score=90 ;;
    *)  base_score=30 ;;
  esac

  local reviewer_bonus=0
  if [[ -n "$REVIEWER" ]]; then
    reviewer_bonus=10
  fi

  # Count files changed (rough heuristic via API)
  local file_count
  file_count=$(fetch_pr_files | jq '. | length' 2>/dev/null || echo "1")
  local diversity_bonus=0
  if [[ "$file_count" -ge 3 ]]; then
    diversity_bonus=5
  fi

  local score=$((base_score + reviewer_bonus + diversity_bonus))
  if [[ "$score" -gt 100 ]]; then
    score=100
  fi
  echo "$score"
}

# ---- 3. Determine tier_met ----
tier_met() {
  local score=$1
  case "$TIER" in
    L0) [[ "$score" -ge 30 ]] && echo "true" || echo "false" ;;
    L1) [[ "$score" -ge 60 ]] && echo "true" || echo "false" ;;
    L2) [[ "$score" -ge 80 ]] && echo "true" || echo "false" ;;
    *)  echo "false" ;;
  esac
}

# ---- 4. Generate cert_id ----
# Format: BCOS-{TIER}-{SHA_SHORT}-{TIMESTAMP}
generate_cert_id() {
  local sha_short
  sha_short=$(echo "$SHA" | cut -c1-8 | tr '[:lower:]' '[:upper:]')
  local ts
  ts=$(date +%s | tail -c 6)
  echo "BCOS-${TIER}-${sha_short}-${ts}"
}

# ---- 5. Build attestation payload ----
build_attestation() {
  local score=$1
  local cert_id=$2
  local met=$3
  local pr_title
  pr_title=$(fetch_pr | jq -r '.title // "unknown"' 2>/dev/null || echo "unknown")
  local pr_state
  pr_state=$(fetch_pr | jq -r '.state // "unknown"' 2>/dev/null || echo "unknown")
  local base_ref
  base_ref=$(fetch_pr | jq -r '.base.ref // "unknown"' 2>/dev/null || echo "unknown")
  local head_ref
  head_ref=$(fetch_pr | jq -r '.head.ref // "unknown"' 2>/dev/null || echo "unknown")

  jq -n \
    --arg schema "bcos-attestation/v2" \
    --arg repo "$REPO" \
    --arg cert "$cert_id" \
    --arg tier "$TIER" \
    --arg score "$score" \
    --arg met "$met" \
    --arg pr_num "$PR_NUMBER" \
    --arg pr_title "$pr_title" \
    --arg pr_state "$pr_state" \
    --arg base "$base_ref" \
    --arg head "$head_ref" \
    --arg actor "$ACTOR" \
    --arg reviewer "$REVIEWER" \
    --arg sha "$SHA" \
    --arg event "$EVENT" \
    --arg url "$RUN_URL" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{
      schema: $schema,
      repo: $repo,
      cert_id: $cert,
      tier: $tier,
      trust_score: ($score | tonumber),
      tier_met: ($met == "true"),
      pr: {
        number: ($pr_num | tonumber),
        title: $pr_title,
        state: $pr_state,
        base_ref: $base,
        head_ref: $head
      },
      actor: $actor,
      reviewer: $reviewer,
      head_sha: $sha,
      event: $event,
      run_url: $url,
      generated_at: $ts
    }'
}

# ---- 6. Anchor attestation to BCOS node ----
anchor_attestation() {
  local attestation_json=$1
  local response
  response=$(curl -s -X POST "${NODE_URL}/attest" \
    -H "Content-Type: application/json" \
    -d "$attestation_json" \
    --max-time 15 \
    2>&1) || true

  if echo "$response" | jq -e '.success' >/dev/null 2>&1; then
    echo "✅ Attestation anchored on-chain"
    echo "$response"
  else
    echo "⚠️  On-chain anchoring unavailable (node: $NODE_URL)"
    echo "   Attestation saved locally as bcos-attestation.json"
    echo "$response"
    # Save locally regardless
    echo "$attestation_json" > bcos-attestation.json
  fi
}

# ---- 7. Post PR comment with score badge ----
post_pr_comment() {
  local score=$1
  local cert_id=$2
  local met=$3
  local file_count=$4

  local badge_url="${NODE_URL}/bcos/badge/${cert_id}-flat.svg"
  local verify_url="${NODE_URL}/bcos/verify/${cert_id}"

  # Determine badge color based on tier
  local badge_color="green"
  case "$TIER" in
    L2) badge_color="orange" ;;
    L1) badge_color="blue" ;;
    L0) badge_color="green" ;;
  esac

  # Score bar
  local score_bar
  score_bar=$(printf '▓%.0s' $(seq 1 $((score / 5))) 2>/dev/null)
  score_bar+=$(printf '░%.0s' $(seq 1 $((20 - score / 5))) 2>/dev/null)

  local met_icon="✅"
  [[ "$met" == "false" ]] && met_icon="❌"

  local reviewer_line=""
  [[ -n "$REVIEWER" ]] && reviewer_line="- 👤 **Reviewer:** @${REVIEWER}"

  local body="<!-- bcos-scan-action v2 -->
## 🛡️ BCOS v2 Attestation — PR #${PR_NUMBER}

| Field | Value |
|-------|-------|
| 🆔 **Cert ID** | \`${cert_id}\` |
| 📊 **Trust Score** | ${score}/100 ${score_bar} |
| 🏷️ **Tier** | ${TIER} |
| ✅ **Tier Met** | ${met_icon} ${met} |
| 📁 **Files** | ${file_count} |
| 👤 **Actor** | @${ACTOR} |
${reviewer_line}
| 🔗 **Verify** | [BCOS Verify](${verify_url}) |

![BCOS Badge](${badge_url})

---

*BCOS v2 Scan — [Source](${RUN_URL}) | [BCOS Docs](https://rustchain.org/bcos)*"

  # Check if a BCOS comment already exists and update it
  local existing_comment_id
  existing_comment_id=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/comments?per_page=100" \
    | jq -r '.[] | select(.body | contains("bcos-scan-action v2")) | .id' 2>/dev/null | head -1)

  if [[ -n "$existing_comment_id" && "$existing_comment_id" != "null" ]]; then
    echo "Updating existing BCOS comment (id=$existing_comment_id)"
    curl -s -X PATCH \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -H "Accept: application/vnd.github.v3+json" \
      "https://api.github.com/repos/${REPO}/issues/comments/${existing_comment_id}" \
      -d "$(jq -n --arg body "$body" '{ body: $body }')" >/dev/null
  else
    echo "Posting new BCOS comment"
    curl -s -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -H "Accept: application/vnd.github.v3+json" \
      "https://api.github.com/repos/${REPO}/issues/${PR_NUMBER}/comments" \
      -d "$(jq -n --arg body "$body" '{ body: $body }')" >/dev/null
  fi
}

# ---- 8. Set GitHub Action outputs ----
write_outputs() {
  local score=$1
  local cert_id=$2
  local met=$3

  if [[ -d "$GITHUB_OUTPUT" ]]; then
    {
      echo "trust_score=${score}"
      echo "cert_id=${cert_id}"
      echo "tier_met=${met}"
    } >> "$GITHUB_OUTPUT"
  else
    echo "trust_score=${score}" >> "$GITHUB_OUTPUT" 2>/dev/null || true
    echo "cert_id=${cert_id}" >> "$GITHUB_OUTPUT" 2>/dev/null || true
    echo "tier_met=${met}" >> "$GITHUB_OUTPUT" 2>/dev/null || true
  fi

  echo "::set-output name=trust_score::${score}"
  echo "::set-output name=cert_id::${cert_id}"
  echo "::set-output name=tier_met::${met}"
  echo "::notice ::BCOS Scan complete — score=${score}, cert_id=${cert_id}, tier_met=${met}"
}

# =============================================================================
# MAIN
# =============================================================================

echo "Fetching PR #${PR_NUMBER} metadata..."
PR_JSON=$(fetch_pr)
FILE_COUNT=$(fetch_pr_files | jq '. | length' 2>/dev/null || echo "0")

TRUST_SCORE=$(compute_trust_score)
CERT_ID=$(generate_cert_id)
TIER_MET=$(tier_met "$TRUST_SCORE")

echo "Results: score=$TRUST_SCORE, cert_id=$CERT_ID, tier_met=$TIER_MET, files=$FILE_COUNT"

# Build attestation JSON
ATTESTATION=$(build_attestation "$TRUST_SCORE" "$CERT_ID" "$TIER_MET")
echo "Attestation:"
echo "$ATTESTATION" | jq .

# Anchor on merge
if [[ "$EVENT" == "pull_request" && "$(echo "$PR_JSON" | jq -r '.merged // "false"' 2>/dev/null)" == "true" ]]; then
  echo "PR was merged — anchoring attestation on-chain..."
  anchor_attestation "$ATTESTATION"
elif [[ "$EVENT" == "push" && "$(echo "$PR_JSON" | jq -r '.merged // "false"' 2>/dev/null)" == "true" ]]; then
  echo "Push event on merged PR — anchoring attestation on-chain..."
  anchor_attestation "$ATTESTATION"
else
  echo "PR not yet merged — skipping on-chain anchor (will be anchored on merge)"
  echo "$ATTESTATION" > bcos-attestation-${PR_NUMBER}.json
fi

# Always post PR comment
post_pr_comment "$TRUST_SCORE" "$CERT_ID" "$TIER_MET" "$FILE_COUNT"

# Write outputs
write_outputs "$TRUST_SCORE" "$CERT_ID" "$TIER_MET"

echo "✅ BCOS Scan complete"
