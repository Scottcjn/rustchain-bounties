# BCOS v2 Scan Action

MIT-licensed reusable GitHub Action for running Beacon Certified Open Source
(BCOS) v2 scans in any repository.

The action downloads and runs the upstream RustChain engine from
`Scottcjn/Rustchain/tools/bcos_engine.py`, exposes the engine outputs, posts a
PR comment with a score badge and per-check breakdown, and anchors the
attestation to RustChain when a pull request is merged.

## Usage

Published action syntax:

```yaml
name: BCOS v2

on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  bcos:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run BCOS scan
        id: bcos
        uses: Scottcjn/bcos-action@v1
        with:
          tier: L1
          reviewer: ${{ github.actor }}
          node-url: https://rustchain.org
```

Local repository development syntax:

```yaml
- uses: ./.github/actions/bcos-scan
  with:
    tier: L1
    reviewer: ${{ github.actor }}
    node-url: https://rustchain.org
```

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `tier` | yes | `L1` | Review tier: `L0`, `L1`, or `L2`. |
| `reviewer` | no | empty | GitHub login or Beacon identity of the reviewer. Required by the engine for full L2 credit. |
| `node-url` | no | `https://rustchain.org` | RustChain node URL used for badge links and merge anchoring. |
| `path` | no | `.` | Repository path to scan. |
| `pr-number` | no | auto | Pull request number for the status comment. |
| `github-token` | no | `github.token` | Token used to create or update the PR comment. |
| `repo-token` | no | empty | Deprecated alias for `github-token`. |

## Outputs

| Output | Description |
| --- | --- |
| `trust_score` | BCOS v2 trust score from `tools/bcos_engine.py` (`0` to `100`). |
| `cert_id` | Engine-generated BCOS certificate ID. |
| `tier_met` | `true` when the score satisfies the requested tier, otherwise `false`. |

Example:

```yaml
- name: Use BCOS outputs
  run: |
    echo "Score: ${{ steps.bcos.outputs.trust_score }}"
    echo "Cert:  ${{ steps.bcos.outputs.cert_id }}"
    echo "Met:   ${{ steps.bcos.outputs.tier_met }}"
```

## PR Comment

On pull request events, the action creates or updates a single comment marked
with `<!-- bcos-scan-action v2 -->`. The comment includes:

- score badge
- trust score and requested tier
- certificate ID
- verification link
- per-check score breakdown from the BCOS v2 engine

## Merge Attestation

When the workflow runs for a merged pull request (`pull_request.closed` with
`merged: true`), the action POSTs the enriched BCOS report to:

```text
${node-url}/attest
```

If the node is unavailable, the action saves `bcos-attestation.json` in the
workspace so the workflow log and artifacts still contain the attestation
payload.

## Engine And Spec

- Engine: <https://github.com/Scottcjn/Rustchain/blob/main/tools/bcos_engine.py>
- Spec: <https://github.com/Scottcjn/Rustchain/blob/main/docs/BEACON_CERTIFIED_OPEN_SOURCE.md>
- Verify: <https://rustchain.org/bcos/>

## License

MIT. The action is intended to be published as `Scottcjn/bcos-action@v1` for
cross-repository use.
