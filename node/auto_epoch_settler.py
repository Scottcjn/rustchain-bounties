import os

def _env_positive_int(env_var):
    """Helper function to get a positive integer from an environment variable."""
    value = os.getenv(env_var)
    if value is None:
        return None
    try:
        value = int(value)
        if value <= 0:
            return None
        return value
    except ValueError:
        return None

RUSTCHAIN_SETTLE_INTERVAL = _env_positive_int('RUSTCHAIN_SETTLE_INTERVAL')
RUSTCHAIN_SLOTS_PER_EPOCH = _env_positive_int('RUSTCHAIN_SLOTS_PER_EPOCH')