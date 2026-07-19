import re

def validate_architecture(arch, fingerprint_data, brand):
    # Define the valid vintage architectures and their multipliers
    VINTAGE_ARCHS = {
        '486': 2.0,
        '386': 2.5,
        'pentium': 1.5,
        'pentium_mmx': 1.7,
    }

    # Anchored, case-insensitive brand matching
    def anchored_match(brand, target):
        return bool(re.match(f'^{re.escape(target)}$', brand, re.IGNORECASE))

    # Check if the architecture is in the list of vintage architectures
    if arch.lower() not in VINTAGE_ARCHS:
        return None

    # Validate the brand
    if arch == 'pentium' and not anchored_match(brand, 'Pentium'):
        return None
    if arch == 'pentium_mmx' and not anchored_match(brand, 'Pentium MMX'):
        return None

    # Corroborate using the fingerprint signals
    if not fingerprint_data.get('cache-timing') or not fingerprint_data.get('SIMD') or not fingerprint_data.get('thermal') or not fingerprint_data.get('jitter'):
        return None

    # Check for TSC-less vintage
    if arch in ['486', '386'] and not fingerprint_data.get('RDTSC'):
        return VINTAGE_ARCHS[arch]

    # Check for validated evidence
    if not fingerprint_data.get('validated'):
        return None

    # Return the multiplier if all checks pass
    return VINTAGE_ARCHS[arch]

def process_miner(miner_data):
    arch = miner_data.get('arch')
    brand = miner_data.get('brand')
    fingerprint_data = miner_data.get('fingerprint_data')

    multiplier = validate_architecture(arch, fingerprint_data, brand)
    if multiplier is not None:
        miner_data['reward_multiplier'] = multiplier
    else:
        miner_data['reward_multiplier'] = 1.0  # Default multiplier

    return miner_data

# Example usage
miner_data = {
    'arch': '486',
    'brand': 'Am486DX4',
    'fingerprint_data': {
        'cache-timing': True,
        'SIMD': False,
        'thermal': True,
        'jitter': True,
        'RDTSC': False,
        'validated': True,
    }
}

processed_miner = process_miner(miner_data)
print(processed_miner)
