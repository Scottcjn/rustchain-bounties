import unittest
from src.device_classification import process_miner

class TestArchitectureValidation(unittest.TestCase):
    def test_spoofed_vintage_with_modern_features(self):
        miner_data = {
            'arch': '486',
            'brand': 'Intel Core i7',
            'fingerprint_data': {
                'cache-timing': True,
                'SIMD': True,
                'thermal': True,
                'jitter': True,
                'RDTSC': True,
                'validated': True,
            }
        }
        processed_miner = process_miner(miner_data)
        self.assertEqual(processed_miner['reward_multiplier'], 1.0)

    def test_honest_tsc_less_486(self):
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
        self.assertEqual(processed_miner['reward_multiplier'], 2.0)

    def test_anchored_brand_matching(self):
        miner_data = {
            'arch': 'pentium',
            'brand': 'Pentium III',
            'fingerprint_data': {
                'cache-timing': True,
                'SIMD': True,
                'thermal': True,
                'jitter': True,
                'RDTSC': True,
                'validated': True,
            }
        }
        processed_miner = process_miner(miner_data)
        self.assertEqual(processed_miner['reward_multiplier'], 1.0)

    def test_flags_only_bare_brand_no_evidence(self):
        miner_data = {
            'arch': 'pentium',
            'brand': 'Pentium',
            'fingerprint_data': {
                'cache-timing': False,
                'SIMD': False,
                'thermal': False,
                'jitter': False,
                'RDTSC': False,
                'validated': False,
            }
        }
        processed_miner = process_miner(miner_data)
        self.assertEqual(processed_miner['reward_multiplier'], 1.0)

    def test_tier_disambiguation(self):
        miner_data = {
            'arch': 'pentium_mmx',
            'brand': 'Pentium MMX',
            'fingerprint_data': {
                'cache-timing': True,
                'SIMD': True,
                'thermal': True,
                'jitter': True,
                'RDTSC': True,
                'validated': True,
            }
        }
        processed_miner = process_miner(miner_data)
        self.assertEqual(processed_miner['reward_multiplier'], 1.7)

if __name__ == '__main__':
    unittest.main()