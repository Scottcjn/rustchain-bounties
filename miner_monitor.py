import datetime
from database_access import get_miner_attestation_history

def detect_offline_miners():
    """
    Detect miners that haven't attested in 7+ days
    Returns list of miner IDs that are offline
    """
    offline_miners = []
    current_time = datetime.datetime.now()

    # Get all active miners from database
    active_miners = get_active_miners()

    for miner in active_miners:
        last_attestation = get_miner_attestation_history(miner['id'], limit=1)

        if last_attestation:
            last_attestation_time = datetime.datetime.fromisoformat(last_attestation[0]['timestamp'])
            days_offline = (current_time - last_attestation_time).days

            if days_offline >= 7:
                offline_miners.append(miner['id'])

    return offline_miners

def get_active_miners():
    """
    Get all active miners from the database
    """
    # Implementation would query the database for active miners
    # This is a placeholder - actual implementation would use database_access.py
    pass