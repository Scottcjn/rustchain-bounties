def test_successful_create_proposal_charges_proposal_fee():
    # Fund miner with 50 RTC
    _fund_miner(miner_id, 50)

    # Create a proposal
    response = client.post("/api/governance/propose", json={"data": "test"})

    # Assert 201 response and fee deduction
    assert response.status_code == 201
    assert _miner_balance_i64(miner_id) == 40