# Claim Risk Scorer

RustChain's auto-triage flow includes an explainable risk scorer for bounty claims.
It does not auto-ban or auto-reject contributors. It is a maintainer aid for ranking suspicious claims.

## What It Scores

The scorer assigns a numeric score and `low` / `medium` / `high` risk bucket using only reproducible metadata from the claim set.

Current heuristics:
- `ACCOUNT_AGE` — new or very young GitHub accounts
- `CLAIM_VELOCITY` — the same user claiming many targets in one triage window
- `REPO_SPREAD` — the same user rapidly claiming across multiple repos
- `WALLET_REUSE` — the same payout wallet reused by multiple accounts
- `PROOF_DUPLICATE` — identical proof links reused across different claimants
- `TEXT_SIMILARITY` — near-template-equivalent claim text across different users

## Risk Policy

The scorer supports three built-in policies:
- `relaxed`
- `balanced`
- `strict`

`auto_triage_claims.py` uses `balanced` by default.
Override with:

```bash
TRIAGE_RISK_POLICY=strict
```

## Report Output

The auto-triage report now includes:
- a `Suspicious Claims` summary sorted by descending score
- per-issue `risk`, `score`, and `reasons` columns

This keeps maintainers in the existing triage workflow instead of introducing a parallel review process.

## CLI Usage

You can also run the scorer directly on a synthetic claim set:

```bash
python3 scripts/sybil_risk_scorer.py --input claims.json --policy balanced
```

Input schema:

```json
{
  "claims": [
    {
      "claim_id": "c-1",
      "user": "alice",
      "issue_ref": "Scottcjn/rustchain-bounties#476",
      "created_at": "2026-02-28T00:00:00Z",
      "body": "Claiming this bounty with a deterministic plan.",
      "account_age_days": 3,
      "wallet": "alice_wallet",
      "proof_links": ["https://example.com/proof"]
    }
  ]
}
```

## Limitations

- This is a ranking tool, not a verdict engine.
- Missing fields degrade gracefully and reduce available signal.
- False positives are possible for legitimate contributors using similar claim templates.
- Maintainers should always review linked code, proof, and actual implementation progress before making payout decisions.
