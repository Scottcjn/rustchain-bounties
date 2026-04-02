# BCOS GitHub Action

Reusable GitHub Action to run BCOS v2 security scans.

## Usage

```yaml
- uses: Scottcjn/bcos-action@v1
  with:
    tier: L1
    reviewer: myname
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| tier | true | L1 | Scan tier (L0/L1/L2) |
| reviewer | false | auto | Reviewer name |
| node-url | false | - | BCOS node URL |

## Outputs

| Output | Description |
|--------|-------------|
| trust_score | Trust score (0-100) |
| cert_id | BCOS certificate ID |
| tier_met | Whether tier requirements met |

## Example

```yaml
name: BCOS Scan
on: push

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: Scottcjn/bcos-action@v1
        with:
          tier: L1
```