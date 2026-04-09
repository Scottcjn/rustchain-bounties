# BCOS Scan — Reusable GitHub Action (BCOS v2)

A reusable GitHub Action that scans PRs, computes a BCOS v2 trust score, generates an attestation certificate, posts a PR comment with a score badge, and optionally anchors the attestation on-chain on merge.

---

## Usage

```yaml
jobs:
  bcos-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: BCOS Scan
        uses: ./.github/actions/bcos-scan
        with:
          tier: L1
          reviewer: octocat
          node-url: https://bcos.rustchain.org
          pr-number: ${{ github.event.pull_request.number }}
          repo-token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `tier` | ✅ | Review tier: `L0`, `L1`, or `L2` |
| `reviewer` | ❌ | GitHub login of the assigned reviewer |
| `node-url` | ❌ | BCOS v2 node RPC URL. Default: `https://50.28.86.131` |
| `pr-number` | ❌ | PR number to comment on. Auto-detected from event payload. |
| `repo-token` | ✅ | `secrets.GITHUB_TOKEN` — required for API calls and comments |

---

## Outputs

| Output | Description |
|--------|-------------|
| `trust_score` | BCOS trust score (0–100) |
| `cert_id` | BCOS attestation certificate ID (e.g. `BCOS-L1-A1B2C3D-39482`) |
| `tier_met` | Whether the required tier threshold was met (`true` / `false`) |

---

## Trust Score Algorithm

| Factor | Contribution |
|--------|-------------|
| Base by tier | L0: 30 pts, L1: 60 pts, L2: 90 pts |
| Reviewer assigned | +10 pts |
| 3+ distinct file paths | +5 pts |
| **Maximum** | **100 pts** |

**Tier thresholds:** L0 ≥ 30, L1 ≥ 60, L2 ≥ 80

---

## Attestation Schema (BCOS v2)

```json
{
  "schema": "bcos-attestation/v2",
  "cert_id": "BCOS-L1-A1B2C3D-39482",
  "tier": "L1",
  "trust_score": 75,
  "tier_met": true,
  "pr": {
    "number": 42,
    "title": "feat: add BCOS scan action",
    "state": "open",
    "base_ref": "main",
    "head_ref": "feature/bcos-action"
  },
  "actor": "octocat",
  "reviewer": "hubot",
  "head_sha": "abc123def456...",
  "event": "pull_request",
  "run_url": "https://github.com/...",
  "generated_at": "2026-04-04T02:00:00Z"
}
```

---

## PR Comment

The action posts (or updates) a formatted PR comment with:

- 📊 **Trust Score** with a visual bar (▓░)
- 🆔 **Cert ID** with a copyable code block
- 🏷️ **Tier** and ✅/❌ **Tier Met** status
- 📁 File count
- 🔗 Direct link to the BCOS verification page
- Embedded BCOS badge image (served from the node)

---

## On-Chain Anchoring

On `pull_request` events where `pull_request.merged == true`, the action POSTs the attestation JSON to `${node-url}/attest`. If the node is unavailable, the attestation is saved locally as `bcos-attestation-${PR_NUMBER}.json`.

---

## BCOS v2 Context

BCOS v2 is RustChain's on-chain bounty certification and trust attestation protocol. Learn more at [rustchain.org/bcos](https://rustchain.org/bcos).

**Badge endpoint:** `GET https://50.28.86.131/bcos/badge/{cert_id}-{style}.svg`  
**Verify page:** `https://rustchain.org/bcos/verify/{cert_id}`
