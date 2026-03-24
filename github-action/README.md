# BCOS v2 GitHub Action

A reusable GitHub Action that runs BCOS v2 scans on any repository.

## Features

- 🔒 Automated BCOS certification scans
- 📊 Trust score calculation (0-100)
- 🏅 Tier validation (L0/L1/L2)
- 💬 Automatic PR comments with results
- 🔗 RustChain attestation on merge

## Usage

### Basic Usage

```yaml
name: BCOS Certification
on: [push, pull_request]

jobs:
  certify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Scottcjn/bcos-action@v1
        with:
          tier: L1
          reviewer: 'github-actions'
```

### Advanced Usage

```yaml
name: BCOS Certification
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  certify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: BCOS L2 Certification
        uses: Scottcjn/bcos-action@v1
        id: bcos
        with:
          tier: L2
          reviewer: 'security-team'
          node-url: 'https://rustchain.org'
          path: '.'
      
      - name: Check Results
        run: |
          echo "Trust Score: ${{ steps.bcos.outputs.trust_score }}"
          echo "Cert ID: ${{ steps.bcos.outputs.cert_id }}"
          echo "Tier Met: ${{ steps.bcos.outputs.tier_met }}"
      
      - name: Anchor to RustChain
        if: github.event_name == 'push' && steps.bcos.outputs.tier_met == 'true'
        run: |
          # Anchor attestation to RustChain
          echo "Anchoring ${{ steps.bcos.outputs.cert_id }} to RustChain..."
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `tier` | Certification tier (L0, L1, or L2) | No | L0 |
| `reviewer` | Name of the reviewer | No | github-actions |
| `node-url` | RustChain node URL | No | https://rustchain.org |
| `path` | Path to scan | No | . |

## Outputs

| Output | Description |
|--------|-------------|
| `trust_score` | Calculated trust score (0-100) |
| `cert_id` | BCOS certification ID |
| `tier_met` | Whether target tier was achieved |
| `report` | Full BCOS JSON report |

## Trust Score Formula

| Category | Points |
|----------|--------|
| License Compliance | 20 |
| Vulnerability Scan | 25 |
| Static Analysis | 20 |
| SBOM Completeness | 10 |
| Dependency Freshness | 5 |
| Test Evidence | 10 |
| Review Attestation | 10 |
| **Total** | **100** |

**Tier Thresholds:**
- L0: ≥ 40 points
- L1: ≥ 60 points
- L2: ≥ 80 points + human signature

## License

MIT — See [LICENSE](LICENSE)

## Links

- BCOS Documentation: https://rustchain.org/bcos/
- BCOS Engine: https://github.com/Scottcjn/Rustchain/tree/main/tools
- RustChain: https://rustchain.org
