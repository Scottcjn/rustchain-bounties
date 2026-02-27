from scripts.sybil_risk_scorer import classify, score_claim


def test_high_risk_claim_scores_block_under_medium_policy():
    claim = {
        "claim_id": "c-1",
        "user": "attacker",
        "account_created_at": "2026-02-26T00:00:00Z",
        "claims_last_7d": 20,
        "wallet_overlap_count": 4,
        "graph_shared_hops": 6,
        "behavior_anomalies": ["same_ip_cluster", "timing_burst", "template_reuse"],
    }
    result = score_claim(claim, now_iso="2026-02-28T00:00:00Z")
    assert result["score"] >= 60
    assert classify(result["score"], "medium") == "block"


def test_low_risk_claim_is_allow():
    claim = {
        "claim_id": "c-2",
        "user": "normal-user",
        "account_created_at": "2025-01-01T00:00:00Z",
        "claims_last_7d": 1,
        "wallet_overlap_count": 0,
        "graph_shared_hops": 0,
        "behavior_anomalies": [],
    }
    result = score_claim(claim, now_iso="2026-02-28T00:00:00Z")
    assert result["score"] < 35
    assert classify(result["score"], "medium") == "allow"
