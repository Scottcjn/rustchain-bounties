def create_proposal(miner_id, proposal_data):
    # Check if miner has exceeded maximum active proposals
    if get_active_proposal_count(miner_id) >= MAX_PROPOSALS_PER_MINER:
        return 429, "Max 5 active proposals per miner"

    # Start a new transaction
    with db.transaction():
        # Deduct proposal fee
        _deduct_proposal_fee(miner_id)

        # Insert proposal into database
        proposal_id = insert_proposal(miner_id, proposal_data)

        # Commit transaction
        db.commit()

    return 201, proposal_id