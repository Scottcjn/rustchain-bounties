def test_max_active_proposal_rejection_does_not_charge_fee():
    # Pre-fill 5 active proposals
    for _ in range(MAX_PROPOSALS_PER_MINER):
        create_proposal(miner_id, {"data": "test"})

    # Fund miner with 50 RTC
    _fund_miner(miner_id, 50)

    # Attempt to create a 6th proposal
    response = client.post("/api/governance/propose", json={"data": "test"})

    # Assert 429 response and no fee deduction
    assert response.status_code == 429
    assert response.json()["error"] == "Max 5 active proposals per miner"
    assert _miner_balance_i64(miner_id) == 50