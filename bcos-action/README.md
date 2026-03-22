# BCOS Action — Beacon Certified Open Source v2

> Bounty #2291 — Reusable GitHub Action for BCOS v2 scans.

A GitHub Action that runs the [BCOS v2 engine](https://github.com/Scottcjn/Rustchain/blob/main/tools/bcos_engine.py)
on any repository, posts a score badge on PRs, and anchors the attestation to RustChain on merge.

## Usage

```yaml
# .github/workflows/bcos.yml
name: BCOS Scan

on:
  pull_request:
  push:
    branches: [main, master]

jobs:
  bcos:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: BCOS v2 Scan
        id: bcos
        uses: Scottcjn/bcos-action@v1
        with:
          tier: L1          # L0 | L1 | L2
          reviewer: myname  # required for L2
          node-url: https://50.28.86.131

      - name: Use outputs
        run: |
          echo "Score: ${{ steps.bcos.outputs.trust_score }}"
          echo "Cert:  ${{ steps.bcos.outputs.cert_id }}"
```

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `tier` | `L1` | Minimum tier: `L0` (≥40), `L1` (≥60), `L2` (≥80 + signature) |
| `reviewer` | `''` | Reviewer name/handle (required for L2) |
| `node-url` | `https://50.28.86.131` | RustChain node for anchoring |
| `path` | `.` | Repo path to scan |
| `token` | `github.token` | Token for posting PR comments |
| `anchor-on-merge` | `true` | Anchor to RustChain on merge to main/master |
| `fail-on-tier-miss` | `false` | Fail workflow if tier not met |

## Outputs

| Output | Description |
|--------|-------------|
| `trust_score` | BCOS trust score (0-100) |
| `cert_id` | Certificate ID (`BCOS-xxx`) |
| `tier_met` | Whether tier threshold was met (`true`/`false`) |
| `badge_url` | URL to the BCOS badge SVG |
| `report_json` | Full report JSON (truncated to 4KB) |

## PR Comment

On every PR, the action posts (or updates) a comment with:

```
## 🟡 BCOS v2 Scan Results

[![BCOS](https://50.28.86.131/bcos/badge/BCOS-abc1234.svg)](https://rustchain.org/bcos/verify/BCOS-abc1234)

| Field | Value |
|-------|-------|
| Status | ✅ PASS |
| Trust Score | 72 / 100 |
| Tier | L1 |
| Cert ID | BCOS-abc1234 |
```

## Trust Score Formula

| Check | Points |
|-------|--------|
| License compliance (SPDX headers) | 20 |
| Vulnerability scan (0 CVEs = 25) | 25 |
| Static analysis (semgrep) | 20 |
| SBOM completeness (CycloneDX) | 10 |
| Dependency freshness | 5 |
| Test evidence | 10 |
| Review attestation | 10 |
| **Total** | **100** |

## License

MIT
