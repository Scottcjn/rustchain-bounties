import hashlib
import json
import random
import time
import uuid

class MinerSimulator:
    """Simulates a single RustChain miner with unique identity and hardware profile."""

    ARCH_PROFILES = {
        "g4": {"model": "PowerPC G4 (7447A)", "family": "PowerPC", "multiplier": 2.5},
        "g5": {"model": "PowerPC G5 (970MP)", "family": "PowerPC", "multiplier": 2.0},
        "apple_silicon": {"model": "Apple M2 Max", "family": "ARM64", "multiplier": 1.2},
        "modern_x86": {"model": "AMD Ryzen 9 7950X", "family": "x86_64", "multiplier": 1.0}
    }

    def __init__(self, miner_id=None, arch=None):
        self.arch_key = arch or random.choice(list(self.ARCH_PROFILES.keys()))
        self.profile = self.ARCH_PROFILES[self.arch_key]

        # Generate unique identity
        unique_suffix = uuid.uuid4().hex[:8]
        self.miner_id = miner_id or f"sim-{self.arch_key}-{unique_suffix}"
        self.wallet = self._generate_wallet()
        self.serial = f"SN-{uuid.uuid4().hex[:12].upper()}"
        self.hostname = f"host-{self.miner_id}"
        self.mac_address = ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])

    def _generate_wallet(self):
        """Generates a pseudo-random wallet address."""
        raw = f"{self.miner_id}-{time.time()}-{random.random()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:38] + "RTC"

    def generate_entropy_report(self, nonce):
        """Simulates CPU timing entropy collection."""
        # In a real miner, this measures tight loops.
        # Here we simulate valid-looking stats.
        base_time = random.uniform(20000, 30000)
        samples = [base_time + random.gauss(0, 500) for _ in range(12)]

        entropy = {
            "mean_ns": sum(samples) / len(samples),
            "variance_ns": random.uniform(100000, 500000),
            "min_ns": min(samples),
            "max_ns": max(samples),
            "sample_count": 48,
            "samples_preview": samples
        }

        commitment = hashlib.sha256(
            (nonce + self.wallet + json.dumps(entropy, sort_keys=True)).encode()
        ).hexdigest()

        return {
            "nonce": nonce,
            "commitment": commitment,
            "derived": entropy,
            "entropy_score": entropy["variance_ns"]
        }

    def build_attestation_payload(self, nonce):
        """Constructs the full JSON payload for /attest/submit."""
        report = self.generate_entropy_report(nonce)

        return {
            "miner": self.wallet,
            "miner_id": self.miner_id,
            "nonce": nonce,
            "report": report,
            "device": {
                "family": self.profile["family"],
                "arch": self.arch_key,
                "model": self.profile["model"],
                "cpu": self.profile["model"],
                "cores": random.choice([1, 2, 4, 8, 16]),
                "memory_gb": random.choice([2, 4, 8, 16, 32, 64]),
                "serial": self.serial
            },
            "signals": {
                "macs": [self.mac_address],
                "hostname": self.hostname
            },
            "fingerprint": {
                "all_passed": True,
                "checks": {
                    "anti_emulation": {"passed": True, "data": {"vm_indicators": []}},
                    "cpu_features": {"passed": True, "data": {"flags": ["altivec" if "PowerPC" in self.profile["family"] else "avx2"]}},
                    "io_latency": {"passed": True, "data": {"p95_ns": random.randint(100, 500)}},
                    "serial_binding": {"passed": True, "data": {"serial": self.serial}}
                }
            }
        }

    def build_enroll_payload(self):
        """Constructs the payload for /epoch/enroll."""
        return {
            "miner_pubkey": self.wallet,
            "miner_id": self.miner_id,
            "device": {
                "family": self.profile["family"],
                "arch": self.arch_key
            }
        }
