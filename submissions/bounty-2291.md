## Reusable GitHub Action for BCOS v2

Created a reusable GitHub Action to run BCOS v2 scans, evaluate requirements, post PR comments, and anchor attestations.

**Platform:** GitHub Actions
**Source Code:** [action_yml.md](./bounty-2291/action_yml.md), [main_py.md](./bounty-2291/main_py.md), [anchor_py.md](./bounty-2291/anchor_py.md)
**License:** [MIT License](./bounty-2291/LICENSE)

### Action Inputs
- `tier`: Certification tier (`L0`, `L1`, or `L2`) - default `L1`.
- `reviewer`: Human reviewer name (required for `L2`).
- `node-url`: RustChain node URL for anchoring attestations - default `https://rustchain.org`.
- `github-token`: GitHub token for posting PR comments.
- `post-comment`: Whether to post PR comment with score badge - default `true`.
- `anchor-on-merge`: Whether to anchor attestation to RustChain on merge - default `true`.

### Action Outputs
- `trust_score`: Trust score (0-100).
- `cert_id`: BCOS certification ID.
- `tier_met`: Whether the tier threshold was met.
- `report-json`: Full JSON report (base64 encoded).
- `commitment`: BLAKE2b commitment hash for on-chain anchoring.

### Usage Example
```yaml
- name: Run BCOS Scan
  uses: Scottcjn/bcos-action@v1
  with:
    tier: 'L1'
    github-token: ${{ secrets.GITHUB_TOKEN }}
    node-url: 'https://rustchain.org'
```

### Verification
- Setup the action in a public repository workflow file.
- Trigger on a Pull Request.
- Verify that BCOS evaluation is run, logs display the parsed files, a markdown comment is posted to the PR with the score/badge, and on-merge commits trigger BCOS anchoring to the RustChain node.

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1