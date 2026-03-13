#!/usr/bin/env python3
"""
AVIDAC Network Bridge

Bridge between AVIDAC simulator (1953 architecture) and modern blockchain network.
Communicates via paper tape protocol to exchange:
- Nonce values (AVIDAC → Network)
- Mining jobs (Network → AVIDAC)
- Solution submissions (AVIDAC → Network)

This bridge enables the AVIDAC to participate in RustChain mining
by translating between paper tape I/O and HTTPS API calls.
"""

import time
import hashlib
import json
import requests
from typing import Optional, Dict, Any

from simulator.paper_tape import PaperTapeIO, PaperTapeProtocol
from simulator.sha256 import sha256_hex


class AVIDACBridge:
    """
    Network bridge for AVIDAC miner.
    
    Responsibilities:
    1. Receive mining jobs from network
    2. Send jobs to AVIDAC via paper tape
    3. Receive solutions from AVIDAC
    4. Submit solutions to network
    5. Monitor AVIDAC health status
    """
    
    def __init__(
        self,
        network_url: str = "https://api.rustchain.io",
        wallet_address: str = "",
        paper_tape: Optional[PaperTapeIO] = None,
        poll_interval_s: float = 1.0
    ):
        """
        Initialize bridge.
        
        Args:
            network_url: RustChain API endpoint
            wallet_address: Wallet address for rewards
            paper_tape: PaperTapeIO instance for AVIDAC communication
            poll_interval_s: How often to poll network for jobs
        """
        self.network_url = network_url
        self.wallet_address = wallet_address
        self.paper_tape = paper_tape or PaperTapeIO()
        self.protocol = PaperTapeProtocol(self.paper_tape)
        self.poll_interval = poll_interval_s
        
        # State
        self.current_job: Optional[Dict[str, Any]] = None
        self.solutions_found = 0
        self.hashes_computed = 0
        
        # Statistics
        self.start_time = time.time()
        self.jobs_received = 0
        self.submissions = 0
        
    def get_mining_job(self) -> Optional[Dict[str, Any]]:
        """
        Fetch mining job from network.
        
        Returns:
            Job dict with block_header, target, job_id or None
        """
        try:
            response = requests.get(
                f"{self.network_url}/api/v1/mining/job",
                params={"wallet": self.wallet_address},
                timeout=10
            )
            
            if response.status_code == 200:
                job = response.json()
                self.jobs_received += 1
                return job
            else:
                print(f"Error fetching job: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return None
    
    def send_job_to_avidac(self, job: Dict[str, Any]) -> bool:
        """
        Send mining job to AVIDAC via paper tape.
        
        Protocol:
        [STX][JOB_ID_3][JOB_ID_2][JOB_ID_1][JOB_ID_0]
        [BLOCK_HEADER_31]...[BLOCK_HEADER_0]
        [TARGET_31]...[TARGET_0][ETX]
        
        Args:
            job: Mining job from network
            
        Returns:
            True if sent successfully
        """
        try:
            # Encode job ID (4 bytes)
            job_id = job.get('job_id', 0)
            job_id_bytes = [(job_id >> (i * 8)) & 0xFF for i in range(3, -1, -1)]
            
            # Encode block header (32 bytes)
            header_hex = job.get('block_header', '0' * 64)
            header_bytes = bytes.fromhex(header_hex)
            
            # Encode target (32 bytes)
            target_hex = job.get('target', '0' * 64)
            target_bytes = bytes.fromhex(target_hex)
            
            # Send via paper tape protocol
            message = job_id_bytes + list(header_bytes) + list(target_bytes)
            self.paper_tape.write_message(message)
            
            print(f"Sent job {job_id} to AVIDAC")
            return True
            
        except Exception as e:
            print(f"Error sending job: {e}")
            return False
    
    def receive_solution(self) -> Optional[int]:
        """
        Receive solution nonce from AVIDAC.
        
        Returns:
            64-bit nonce or None if no solution
        """
        try:
            # Read message from paper tape
            data = self.paper_tape.read_message()
            
            if data and len(data) == 8:
                # Decode 64-bit nonce
                nonce = 0
                for byte in data:
                    nonce = (nonce << 8) | byte
                return nonce
            
            return None
            
        except Exception as e:
            print(f"Error reading solution: {e}")
            return None
    
    def submit_solution(self, nonce: int, job_id: int) -> bool:
        """
        Submit solution to network.
        
        Args:
            nonce: Solution nonce found by AVIDAC
            job_id: Job ID for verification
            
        Returns:
            True if accepted
        """
        try:
            response = requests.post(
                f"{self.network_url}/api/v1/mining/submit",
                json={
                    "wallet": self.wallet_address,
                    "job_id": job_id,
                    "nonce": hex(nonce)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('accepted', False):
                    self.solutions_found += 1
                    self.submissions += 1
                    print(f"✓ Solution accepted! Nonce: {nonce:016X}")
                    return True
                else:
                    print(f"✗ Solution rejected: {result.get('reason', 'unknown')}")
                    return False
            else:
                print(f"Error submitting: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return False
    
    def verify_solution(self, block_header: str, nonce: int, target: int) -> bool:
        """
        Verify solution locally before submission.
        
        Args:
            block_header: Block header hex string
            nonce: Solution nonce
            target: Target threshold
            
        Returns:
            True if hash < target
        """
        try:
            # Combine header and nonce
            header_bytes = bytes.fromhex(block_header)
            nonce_bytes = nonce.to_bytes(8, 'big')
            data = header_bytes + nonce_bytes
            
            # Compute SHA256
            hash_hex = sha256_hex(data)
            hash_int = int(hash_hex, 16)
            
            self.hashes_computed += 1
            
            # Check if hash meets target
            return hash_int < target
            
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    def run(self, max_jobs: int = 0) -> None:
        """
        Run bridge main loop.
        
        Args:
            max_jobs: Maximum jobs to process (0 = unlimited)
        """
        print(f"AVIDAC Network Bridge started")
        print(f"Network: {self.network_url}")
        print(f"Wallet: {self.wallet_address}")
        print(f"Poll interval: {self.poll_interval}s")
        print()
        
        jobs_processed = 0
        
        try:
            while True:
                # Check job limit
                if max_jobs > 0 and jobs_processed >= max_jobs:
                    break
                
                # Get new mining job
                job = self.get_mining_job()
                
                if job:
                    self.current_job = job
                    jobs_processed += 1
                    
                    # Send to AVIDAC
                    if self.send_job_to_avidac(job):
                        # Wait for solution
                        print("Waiting for AVIDAC to find solution...")
                        
                        # Simulated: in real implementation, would wait for interrupt
                        time.sleep(self.poll_interval)
                        
                        # Check for solution
                        solution = self.receive_solution()
                        
                        if solution:
                            print(f"Solution found! Nonce: {solution:016X}")
                            
                            # Verify before submission
                            target = int(job.get('target', '0' * 64), 16)
                            if self.verify_solution(job.get('block_header', ''), solution, target):
                                self.submit_solution(solution, job.get('job_id', 0))
                            else:
                                print("Solution verification failed")
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            print("\nBridge stopped by user")
        
        # Print statistics
        self.print_statistics()
    
    def print_statistics(self) -> None:
        """Print bridge statistics."""
        elapsed = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("AVIDAC Bridge Statistics")
        print("=" * 60)
        print(f"Runtime: {elapsed:.2f} seconds")
        print(f"Jobs received: {self.jobs_received}")
        print(f"Solutions found: {self.solutions_found}")
        print(f"Submissions: {self.submissions}")
        print(f"Hashes computed: {self.hashes_computed}")
        if elapsed > 0:
            print(f"Hash rate: {self.hashes_computed / elapsed:.2f} H/s")
        print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AVIDAC Network Bridge')
    parser.add_argument(
        '--network',
        default='https://api.rustchain.io',
        help='Network API URL'
    )
    parser.add_argument(
        '--wallet',
        required=True,
        help='Wallet address for rewards'
    )
    parser.add_argument(
        '--poll-interval',
        type=float,
        default=1.0,
        help='Network poll interval in seconds'
    )
    parser.add_argument(
        '--max-jobs',
        type=int,
        default=0,
        help='Maximum jobs to process (0 = unlimited)'
    )
    
    args = parser.parse_args()
    
    bridge = AVIDACBridge(
        network_url=args.network,
        wallet_address=args.wallet,
        poll_interval_s=args.poll_interval
    )
    
    bridge.run(max_jobs=args.max_jobs)


if __name__ == '__main__':
    main()
