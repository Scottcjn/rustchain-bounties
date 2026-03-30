# BCOS v2 GitHub Action

[![BCOS Certified](https://img.shields.io/badge/BCOS-Certified-brightgreen?style=flat)](https://rustchain.org/bcos/)

Automated code certification for your GitHub repositories using **BCOS v2**.

## Quick Start

```yaml
jobs:
  certify:
    uses: Scottcjn/bcos-action/.github/workflows/bcos-action.yml@v1
    with:
      tier: L1
```

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `tier` | L1 | L0/L1/L2 |
| `min-trust-score` | 70 | Minimum score |
| `fail-on-vulnerabilities` | false | Fail on vulns |

## Outputs

- `trust_score` - 0-100 score
- `cert_id` - BCOS-xxxxxxxx
- `tier_met` - true/false
- `vuln_count` - vulnerabilities

## Learn More

- [BCOS Spec](https://github.com/Scottcjn/Rustchain/blob/main/docs/BEACON_CERTIFIED_OPEN_SOURCE.md)
- [Badge Generator](https://rustchain.org/bcos/badge-generator.html)

MIT License • Elyan Labs
