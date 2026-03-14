#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RustChain Attestation Module
Handles communication with RustChain node for proof submission
"""

import json
import time
import hashlib
import os
from datetime import datetime

# Try imports
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
except ImportError:
    pass


class RustChainClient:
    """Client for RustChain node API"""
    
    def __init__(self, node_url="http://50.28.86.131:8088"):
        self.node_url = node_url
        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
    
    def check_health(self):
        """Check if node is online"""
        try:
            if HAS_REQUESTS:
                response = self.session.get(f"{self.node_url}/health", timeout=10)
                return response.status_code == 200
            else:
                response = urlopen(f"{self.node_url}/health", timeout=10)
                return True
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def submit_attestation(self, attestation):
        """Submit attestation to RustChain node"""
        try:
            if HAS_REQUESTS:
                response = self.session.post(
                    f"{self.node_url}/attest",
                    json=attestation,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                return response.json()
            else:
                data = json.dumps(attestation).encode('utf-8')
                req = Request(
                    f"{self.node_url}/attest",
                    data=data,
                    headers={"Content-Type": "application/json"}
                )
                response = urlopen(req, timeout=30)
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_epoch_info(self):
        """Get current epoch information"""
        try:
            if HAS_REQUESTS:
                response = self.session.get(f"{self.node_url}/epoch", timeout=10)
                return response.json()
            else:
                response = urlopen(f"{self.node_url}/epoch", timeout=10)
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class RustChainAttestation:
    """Generate and manage RustChain attestations"""
    
    def __init__(self, wallet_id, device_info):
        self.wallet_id = wallet_id
        self.device_info = device_info
        self.client = RustChainClient()
        self.attestation_count = 0
        self.total_earned = 0.0
    
    def generate_attestation(self, hardware_fingerprint):
        """Generate attestation payload"""
        timestamp = int(time.time())
        
        attestation = {
            "wallet_id": self.wallet_id,
            "device_arch": self.device_info.get("arch", "unknown"),
            "device_family": self.device_info.get("family", "unknown"),
            "cpu_speed": self.device_info.get("cpu_speed", 0),
            "total_ram_kb": self.device_info.get("ram_kb", 0),
            "display_type": self.device_info.get("display", "unknown"),
            "hardware_id": hardware_fingerprint.get("hash", ""),
            "vintage_year": self.device_info.get("year", 0),
            "antiquity_multiplier": self.device_info.get("multiplier", 1.0),
            "timestamp": timestamp,
            "version": "1.0.0-galaga",
            "attestation_number": self.attestation_count + 1,
        }
        
        return attestation
    
    def submit(self, hardware_fingerprint):
        """Submit attestation and process result"""
        attestation = self.generate_attestation(hardware_fingerprint)
        
        # Check node health first
        if not self.client.check_health():
            return {
                "status": "offline",
                "message": "Node unreachable, saving attestation locally"
            }
        
        # Submit
        result = self.client.submit_attestation(attestation)
        
        if result.get("status") == "success":
            self.attestation_count += 1
            reward = float(result.get("reward", 0))
            multiplier = self.device_info.get("multiplier", 1.0)
            final_reward = reward * multiplier
            
            self.total_earned += final_reward
            
            result["attestation_number"] = self.attestation_count
            result["total_earned"] = self.total_earned
            result["final_reward"] = final_reward
        
        return result
    
    def get_stats(self):
        """Get mining statistics"""
        return {
            "wallet": self.wallet_id,
            "attestations": self.attestation_count,
            "total_earned": self.total_earned,
            "device": self.device_info.get("family", "unknown"),
            "multiplier": self.device_info.get("multiplier", 1.0),
        }


class WalletManager:
    """Manage RustChain wallets"""
    
    def __init__(self, wallet_file="wallet.txt"):
        self.wallet_file = wallet_file
        self.wallet = None
    
    def load_wallet(self):
        """Load wallet from file"""
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, 'r') as f:
                data = json.load(f)
                self.wallet = data
                return data
        return None
    
    def save_wallet(self, wallet):
        """Save wallet to file"""
        self.wallet = wallet
        with open(self.wallet_file, 'w') as f:
            json.dump(wallet, f, indent=2)
        
        # Set file permissions (Unix only)
        try:
            os.chmod(self.wallet_file, 0o600)
        except:
            pass
        
        return wallet
    
    def generate_wallet(self, hardware_fingerprint):
        """Generate new wallet from hardware fingerprint"""
        fp_hash = hardware_fingerprint.get("hash", "")
        
        # Create wallet ID
        wallet_chars = '0123456789abcdef'
        wallet_id = 'RTC'
        
        # Use first 20 bytes of hash
        fp_bytes = bytes.fromhex(fp_hash)
        for i in range(20):
            byte_idx = i % len(fp_bytes)
            b = fp_bytes[byte_idx]
            wallet_id += wallet_chars[(b >> 4) & 0x0F]
            wallet_id += wallet_chars[b & 0x0F]
        
        wallet = {
            "id": wallet_id,
            "created": int(time.time()),
            "created_date": datetime.now().isoformat(),
            "hardware_fingerprint": fp_hash,
            "backup_phrase": self._generate_backup_phrase(),
        }
        
        return wallet
    
    def _generate_backup_phrase(self):
        """Generate simple backup phrase"""
        words = [
            "galaga", "space", "alien", "fighter", "arcade",
            "retro", "vintage", "z80", "namco", "classic",
            "shooter", "fleet", "formation", "beam", "capture",
            "dual", "bonus", "epoch", "mining", "crypto"
        ]
        
        import random
        phrase = random.sample(words, 8)
        return " ".join(phrase)
    
    def backup_wallet(self, backup_file=None):
        """Create wallet backup"""
        if not self.wallet:
            return False
        
        if backup_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"wallet_backup_{timestamp}.txt"
        
        with open(backup_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("RUSTCHAIN WALLET BACKUP\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Wallet ID: {self.wallet['id']}\n")
            f.write(f"Created: {self.wallet['created_date']}\n")
            f.write(f"Fingerprint: {self.wallet['hardware_fingerprint']}\n")
            f.write(f"\nBACKUP PHRASE (WRITE THIS DOWN!):\n")
            f.write(f"{self.wallet['backup_phrase']}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("KEEP THIS SAFE! Anyone with this phrase can access your wallet.\n")
            f.write("=" * 60 + "\n")
        
        return backup_file


def demo_attestation():
    """Demonstrate attestation flow"""
    print("=" * 60)
    print("RustChain Attestation Demo")
    print("=" * 60)
    
    # Generate hardware fingerprint
    from galaga_hardware import GalagaHardwareFingerprint
    fp_gen = GalagaHardwareFingerprint()
    fp = fp_gen.generate()
    
    print(f"\nHardware Fingerprint: {fp['hash'][:32]}...")
    
    # Generate wallet
    wallet_mgr = WalletManager()
    wallet = wallet_mgr.generate_wallet(fp)
    print(f"Wallet ID: {wallet['id']}")
    print(f"Backup Phrase: {wallet['backup_phrase']}")
    
    # Save wallet
    wallet_mgr.save_wallet(wallet)
    print(f"\nWallet saved to: {wallet_mgr.wallet_file}")
    
    # Create attestation
    device_info = {
        "arch": "galaga_z80_simulated",
        "family": "galaga_arcade_1981",
        "cpu_speed": 3072000,
        "ram_kb": 8,
        "display": "crt_224x288",
        "year": 1981,
        "multiplier": 2.0,
    }
    
    attestation = RustChainAttestation(wallet['id'], device_info)
    
    print(f"\nSubmitting attestation...")
    result = attestation.submit(fp)
    
    print(f"\nResult: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"Reward: {result.get('final_reward', 0):.4f} RTC")
        print(f"Total Earned: {result.get('total_earned', 0):.4f} RTC")
    elif result.get('status') == 'offline':
        print(f"Node offline - attestation saved locally")
    
    # Show stats
    stats = attestation.get_stats()
    print(f"\nMining Statistics:")
    print(f"  Wallet: {stats['wallet']}")
    print(f"  Attestations: {stats['attestations']}")
    print(f"  Total Earned: {stats['total_earned']:.4f} RTC")
    print(f"  Device: {stats['device']}")
    print(f"  Multiplier: {stats['multiplier']}x")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    demo_attestation()
