from database_access import get_miner_attestation_history, get_miner_earnings, get_miner_architecture

def generate_eulogy(miner_id):
    """
    Generate a poetic eulogy for a retired miner
    Args:
        miner_id: ID of the miner
    Returns:
        Eulogy text
    """
    # Get miner information from database
    attestation_history = get_miner_attestation_history(miner_id)
    total_rtc = get_miner_earnings(miner_id)
    architecture = get_miner_architecture(miner_id)

    # Calculate years of service
    first_attestation = attestation_history[-1]['timestamp']
    last_attestation = attestation_history[0]['timestamp']
    years_of_service = (datetime.datetime.fromisoformat(last_attestation) -
                       datetime.datetime.fromisoformat(first_attestation)).days / 365

    # Generate eulogy text
    eulogy = f"""
    Here lies {architecture['model']}, a {architecture['type']}.
    It attested for {len(attestation_history)} epochs and earned {total_rtc} RTC.
    Its {architecture['cache_type']} was as unique as a snowflake in a blizzard of modern silicon.
    It served for {years_of_service:.1f} years and is survived by its power supply, which still works.
    """

    return eulogy.strip()