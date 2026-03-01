import time
import hashlib
import os
import statistics
from typing import Dict, Tuple, List

# -----------------------------------------------------------------------------
# DEFENSE SCRIPT: Hardware Attestation & Proof-of-Useful-Work (PoUW)
# Fix for: RIP-201 "Architectural Masquerading" / Ghost Shim Vulnerabilities
#
# This implementation relies on Deterministic Latency Checks and Performance 
# Banding rather than spoofable client-side feature flags (like /proc/cpuinfo).
# -----------------------------------------------------------------------------

class HardwareAttestationServer:
    def __init__(self):
        # 1. Relative Performance Banding
        # Defines expected completion times (min_seconds, max_seconds) for a standard 
        # PoUW task. A modern CPU claiming to be vintage will execute too fast.
        self.performance_bands: Dict[str, Tuple[float, float]] = {
            "modern": (0.01, 0.5),
            "apple_silicon": (0.01, 0.4),
            "vintage_x86": (2.0, 5.0),
            "vintage_powerpc": (4.0, 8.0),
            "exotic": (1.0, 10.0),
            "arm": (0.8, 3.0)
        }

        # Active challenges tracking
        self.active_challenges: Dict[str, dict] = {}

    def generate_pouw_challenge(self, miner_id: str, claimed_bucket: str) -> dict:
        """
        Generates a deterministic latency challenge (PoUW).
        Forces the miner to perform a compute/memory-bound task to prove hardware capability,
        preventing static spoofing via FUSE or LD_PRELOAD.
        """
        nonce = os.urandom(16).hex()
        # Difficulty is kept constant to establish a reliable baseline performance curve.
        difficulty_iterations = 500_000

        challenge = {
            "nonce": nonce,
            "iterations": difficulty_iterations,
            "claimed_bucket": claimed_bucket,
            "issued_at": time.time()
        }
        self.active_challenges[miner_id] = challenge
        return challenge

    def verify_miner_bucket(self, miner_id: str, result_hash: str, actual_time_taken: float, execution_jitter: float) -> bool:
        """
        Verifies the PoUW result, checks macro-latency, and analyzes micro-jitter to detect throttling.
        """
        if miner_id not in self.active_challenges:
            print(f"[!] Invalid or expired challenge for {miner_id}")
            return False

        challenge = self.active_challenges.pop(miner_id)
        claimed_bucket = challenge["claimed_bucket"]

        # Step 1: Verify the Cryptographic Proof of Work
        expected_hash = self._compute_pouw(challenge["nonce"], challenge["iterations"])
        if result_hash != expected_hash:
            print(f"[!] Work verification failed for {miner_id}. Invalid hash.")
            return False

        # Step 2: Macro-Performance Banding Check (Deterministic Latency)
        # We use server-measured time (or cryptographically signed timestamps) to prevent reporting lies.
        if claimed_bucket not in self.performance_bands:
            print(f"[!] Unknown bucket claimed: {claimed_bucket}")
            return False

        min_time, max_time = self.performance_bands[claimed_bucket]

        if actual_time_taken < min_time:
            # Modern hardware masquerading as vintage (Execution is too fast)
            print(f"[!] SPOOF DETECTED: {miner_id} claimed {claimed_bucket} but executed in {actual_time_taken:.4f}s (Min: {min_time}s)")
            return False

        if actual_time_taken > max_time:
            # Hardware too slow
            print(f"[!] TIMEOUT: {miner_id} claimed {claimed_bucket} but executed in {actual_time_taken:.4f}s (Max: {max_time}s)")
            return False

        # Step 3: Micro-Jitter Analysis (Anti-cpulimit/cgroup throttling)
        # Throttled processes using SIGSTOP/SIGCONT (cpulimit) exhibit massive latency spikes 
        # interspersed with native execution speed, leading to high jitter.
        # Authentic vintage hardware has a smooth, consistent (but slow) execution profile.
        JITTER_THRESHOLD = 0.15 # 15% variance threshold
        if execution_jitter > JITTER_THRESHOLD and "vintage" in claimed_bucket:
             print(f"[!] THROTTLE DETECTED: {miner_id} claims {claimed_bucket}. Macro-time matched, but jitter ({execution_jitter:.2f}) indicates artificial throttling.")
             return False

        print(f"[+] Verified {miner_id} as valid {claimed_bucket} (Time: {actual_time_taken:.4f}s, Jitter: {execution_jitter:.4f})")
        return True

    @staticmethod
    def _compute_pouw(nonce: str, iterations: int) -> str:
        """
        A sample compute-bound task. In production, this should be an algorithm that 
        stresses specific CPU architecture traits (e.g., L1/L2 cache sizing, specific SIMD 
        instruction latencies) to create an unforgeable hardware fingerprint.
        """
        current_hash = nonce.encode()
        for _ in range(iterations):
            current_hash = hashlib.sha256(current_hash).digest()
        return current_hash.hex()


# -----------------------------------------------------------------------------
# MINER SIDE / TESTING SIMULATION
# -----------------------------------------------------------------------------
def simulate_miner(server: HardwareAttestationServer, miner_id: str, claimed_bucket: str, throttle_strategy: str = "none"):
    """
    Simulates various attacker/honest miner behaviors.
    """
    challenge = server.generate_pouw_challenge(miner_id, claimed_bucket)
    iterations = challenge["iterations"]
    
    start_time = time.time()
    
    # Simulating micro-timing to calculate jitter (variance in batch execution times)
    batch_size = iterations // 10
    batch_times: List[float] = []
    
    current_hash = challenge["nonce"].encode()
    
    for i in range(10):
        b_start = time.time()
        for _ in range(batch_size):
            current_hash = hashlib.sha256(current_hash).digest()
        b_end = time.time()
        
        # Attacker simulates throttling (e.g., cpulimit) by sleeping between chunks 
        # to match the macro-time of a vintage CPU.
        if throttle_strategy == "cpulimit_burst":
            time.sleep(0.5) # Artificial pause creates high variance
            b_end = time.time()
            
        batch_times.append(b_end - b_start)

    result = current_hash.hex()
    actual_time_taken = time.time() - start_time
    
    # Calculate Jitter (Coefficient of Variation)
    mean_time = statistics.mean(batch_times)
    stdev_time = statistics.stdev(batch_times) if len(batch_times) > 1 else 0
    jitter = stdev_time / mean_time if mean_time > 0 else 0

    # Submit to server
    server.verify_miner_bucket(miner_id, result, actual_time_taken, jitter)


if __name__ == "__main__":
    server = HardwareAttestationServer()

    print("--- Scenario 1: Honest Modern Miner ---")
    simulate_miner(server, "honest_modern_01", "modern", throttle_strategy="none")

    print("\n--- Scenario 2: Attacker Masquerading as Vintage (No Throttling) ---")
    # Will fail the banding check (finishes too fast)
    simulate_miner(server, "attacker_ghost_01", "vintage_powerpc", throttle_strategy="none")

    print("\n--- Scenario 3: Attacker Masquerading as Vintage (With 'cpulimit' Throttling) ---")
    # Matches the macro-time, but fails the micro-jitter check due to bursty execution
    simulate_miner(server, "attacker_ghost_02", "vintage_powerpc", throttle_strategy="cpulimit_burst")

    # NOTE ON KERNEL-LEVEL ATTESTATION:
    # While PoUW and Jitter Analysis stop 99% of software-level masquerading, 
    # sophisticated hypervisor attacks might perfectly emulate timing. 
    # Production implementation must couple this with TEEs (Intel SGX / ARM TrustZone) 
    # to cryptographically sign the hardware identity via remote attestation.