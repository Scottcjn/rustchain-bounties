import pytest
from rustchain import BridgeTransfer

# ...

def test_stale_void_cannot_overwrite_completed_withdraw():
    # Create a withdraw
    withdraw = BridgeTransfer.create("withdraw", 10)
    # Confirm it externally to 'completed'
    withdraw.confirm_external("completed")
    # Monkey-patch get_bridge_transfer_by_hash to return a stale snapshot
    def stale_get_bridge_transfer_by_hash(hash):
        if hash == withdraw.hash:
            return BridgeTransfer(status="pending")
        return BridgeTransfer.get_by_hash(hash)
    BridgeTransfer.get_by_hash = stale_get_bridge_transfer_by_hash
    # Try to void the transfer
    with pytest.raises(sqlx.Error):
        void_bridge_transfer(withdraw.hash, 1)
    # Assert the void is rejected with the correct error
    assert withdraw.status == "completed"
    assert withdraw.voided_by is None
    # Assert the destination balance is intact
    assert withdraw.destination_balance == 10