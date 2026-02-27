# Sybil/Farming Risk Scorer

This module adds an auditable, deterministic risk score for bounty claims.

## Factors
- account age
- claim velocity (last 7 days)
- wallet overlap count
- graph proximity score
- behavior anomaly count

## Decisions
Policy presets:
- `low`  (warn >=45, block >=70)
- `medium` (warn >=35, block >=60)
- `high` (warn >=25, block >=50)

## CLI
```bash
python3 scripts/sybil_risk_scorer.py --input claims.json --policy medium
```

Input schema:
```json
{
  "claims": [
    {
      "claim_id": "c-1",
      "user": "alice",
      "account_created_at": "2026-02-01T00:00:00Z",
      "claims_last_7d": 3,
      "wallet_overlap_count": 0,
      "graph_shared_hops": 1,
      "behavior_anomalies": []
    }
  ]
}
```
