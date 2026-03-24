# BCOS v2 GitHub Action

[![BCOS L1 Certified](https://img.shields.io/badge/BCOS-L1_CERTIFIED-blue)](https://github.com/Scottcjn/Rustchain)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Reusable GitHub Action for BCOS v2 (Beacon Certified Open Source) certification scanning.

## What is BCOS v2?

BCOS v2 is a certification system that evaluates open source repositories for trust and quality metrics. It scans for:

- ✅ License file
- ✅ README documentation
- ✅ Security policy
- ✅ Test coverage
- ✅ CI/CD configuration
- ✅ Documentation
- ✅ Security audits

## Usage

### Basic Usage

Add this to your `.github/workflows/bcos-scan.yml`:

```yaml
name: BCOS Scan

on:
  pull_request:
    branches: [main]

jobs:
  bcos-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run BCOS Certification Scan
        uses: FraktalDeFiDAO/bcos-action@v1
        with:
          tier: L1  # L0, L1, or L2
          reviewer: 'security-team'
```

### Advanced Usage

```yaml
name: BCOS Scan

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  bcos-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run BCOS Certification Scan
        uses: FraktalDeFiDAO/bcos-action@v1
        with:
          tier: L2
          reviewer: 'automated-bcos'
          node-url: 'https://50.28.86.131'  # RustChain node
          github-token: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Get Results
        run: |
          echo "Trust Score: ${{ steps.scan.outputs.trust_score }}"
          echo "Certificate ID: ${{ steps.scan.outputs.cert_id }}"
          echo "Tier Met: ${{ steps.scan.outputs.tier_met }}"
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `tier` | BCOS certification tier (L0, L1, or L2) | ✅ Yes | - |
| `reviewer` | Reviewer identifier | ❌ No | `github-actions` |
| `node-url` | RustChain node URL for attestation | ❌ No | `https://50.28.86.131` |
| `github-token` | GitHub token for PR comments | ❌ No | `${{ github.token }}` |

## Outputs

| Output | Description |
|--------|-------------|
| `trust_score` | BCOS trust score (0-100) |
| `cert_id` | Certificate ID |
| `tier_met` | Whether tier requirements were met (true/false) |

## BCOS Tiers

### L0 - Basic (50+ points)
- License file
- README
- Security policy

### L1 - Standard (70+ points)
- All L0 requirements
- Test suite
- CI/CD pipeline

### L2 - Advanced (90+ points)
- All L1 requirements
- Documentation
- Security audit

## Example Output

When run on a pull request, the action posts a comment like:

```markdown
## 🏆 BCOS v2 Certification Scan

| Metric | Value |
|--------|-------|
| Trust Score | **85/100** |
| Tier | L1 |
| Tier Met | ✅ Yes |
| Certificate | `BCOS-A1B2C3D4E5F6` |

![BCOS Badge](https://img.shields.io/badge/BCOS-L1_CERTIFIED-blue)

<details>
<summary>Scan Details</summary>

```json
{
  "trust_score": 85,
  "breakdown": {
    "license": 15,
    "readme": 10,
    "security": 15,
    "tests": 15,
    "ci": 15,
    "docs": 10,
    "audit": 0
  },
  ...
}
```

</details>
```

## Development

### Local Testing

```bash
# Clone the action
git clone https://github.com/FraktalDeFiDAO/bcos-action.git
cd bcos-action

# Run scan locally
python action/scan.py \
  --tier L1 \
  --reviewer test \
  --repo owner/repo
```

### Publishing

1. Update version in `action.yml`
2. Create git tag: `git tag v1.0.0 && git push origin v1.0.0`
3. Create GitHub release

## License

MIT License - see [LICENSE](LICENSE) for details.

## References

- [BCOS v2 Specification](https://github.com/Scottcjn/Rustchain/blob/main/docs/BEACON_CERTIFIED_OPEN_SOURCE.md)
- [BCOS Engine](https://github.com/Scottcjn/Rustchain/blob/main/tools/bcos_engine.py)
- [BCOS Verification](https://rustchain.org/bcos/)
