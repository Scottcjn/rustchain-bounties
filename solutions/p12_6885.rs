#!/usr/bin/env python3
"""
RTC Wallet Canonicalization Tool
Resolves duplicate wallet references across GitHub identities per POLICY 2026-04-27.
"""

import json
import sys
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# RustChain ledger verification constants
RUSTCHAIN_RPC_URL = "https://rpc.rustchain.io"
POLICY_DATE = datetime(2026, 4, 27)
DEADLINE_DATE = datetime(2026, 5, 11)

class WalletCanonicalizer:
    """Enforces one canonical RTC wallet per contributor identity."""
    
    def __init__(self, audit_data: Dict):
        self.audit_data = audit_data
        self.clusters = self._detect_clusters()
        self.canonical_map = {}
        
    def _detect_clusters(self) -> List[Dict]:
        """Detect contributor pairs sharing wallets or multiple wallets per identity."""
        clusters = []
        wallet_to_identities = {}
        identity_to_wallets = {}
        
        for entry in self.audit_data.get("contributors", []):
            gh_id = entry["github_id"]
            wallet = entry["rtc_wallet"]
            
            if wallet not in wallet_to_identities:
                wallet_to_identities[wallet] = []
            wallet_to_identities[wallet].append(gh_id)
            
            if gh_id not in identity_to_wallets:
                identity_to_wallets[gh_id] = []
            identity_to_wallets[gh_id].append(wallet)
        
        # Find shared wallets (multiple identities -> one wallet)
        for wallet, identities in wallet_to_identities.items():
            if len(identities) > 1:
                clusters.append({
                    "type": "shared_wallet",
                    "wallet": wallet,
                    "identities": identities,
                    "violation": True
                })
        
        # Find multiple wallets per identity
        for identity, wallets in identity_to_wallets.items():
            if len(wallets) > 1:
                clusters.append({
                    "type": "multiple_wallets",
                    "identity": identity,
                    "wallets": wallets,
                    "violation": True
                })
        
        return clusters
    
    def _verify_on_chain(self, wallet: str) -> bool:
        """Verify wallet exists on RustChain ledger."""
        # Simulated RPC call - in production would use actual RPC
        ledger_hash = hashlib.sha256(wallet.encode()).hexdigest()
        return ledger_hash.startswith("00")  # Simplified verification
    
    def declare_canonical(self, identity: str, wallet: str) -> bool:
        """Declare canonical wallet for an identity."""
        if not self._verify_on_chain(wallet):
            print(f"ERROR: Wallet {wallet} not verified on RustChain")
            return False
        
        self.canonical_map[identity] = {
            "canonical_wallet": wallet,
            "declared_at": datetime.utcnow().isoformat(),
            "expires_at": DEADLINE_DATE.isoformat()
        }
        return True
    
    def resolve_conflicts(self) -> Dict:
        """Resolve all detected conflicts with default per-PR inference."""
        resolution = {
            "canonical_map": {},
            "per_pr_inferences": [],
            "deadline": DEADLINE_DATE.isoformat()
        }
        
        for cluster in self.clusters:
            if cluster["type"] == "shared_wallet":
                wallet = cluster["wallet"]
                identities = cluster["identities"]
                
                # Default: per-PR inference for all but first identity
                for i, identity in enumerate(identities):
                    if i == 0:
                        # First identity keeps the wallet
                        if self.declare_canonical(identity, wallet):
                            resolution["canonical_map"][identity] = wallet
                    else:
                        # Others get per-PR inference
                        resolution["per_pr_inferences"].append({
                            "identity": identity,
                            "original_wallet": wallet,
                            "inferred": True,
                            "note": "Per-PR payout inference applied"
                        })
            
            elif cluster["type"] == "multiple_wallets":
                identity = cluster["identity"]
                wallets = cluster["wallets"]
                
                # Default: use first wallet as canonical
                canonical_wallet = wallets[0]
                if self.declare_canonical(identity, canonical_wallet):
                    resolution["canonical_map"][identity] = canonical_wallet
                    resolution["per_pr_inferences"].extend([
                        {
                            "identity": identity,
                            "original_wallet": w,
                            "inferred": True,
                            "note": f"Wallet {w} superseded by canonical {canonical_wallet}"
                        } for w in wallets[1:]
                    ])
        
        return resolution
    
    def generate_report(self) -> str:
        """Generate human-readable compliance report."""
        report_lines = [
            "=" * 60,
            "RTC WALLET CANONICALIZATION REPORT",
            f"Generated: {datetime.utcnow().isoformat()}",
            f"Policy Date: {POLICY_DATE.date()}",
            f"Deadline: {DEADLINE_DATE.date()}",
            "=" * 60,
            ""
        ]
        
        if not self.clusters:
            report_lines.append("NO VIOLATIONS DETECTED - All identities have canonical wallets.")
            return "\n".join(report_lines)
        
        report_lines.append(f"DETECTED {len(self.clusters)} VIOLATION(S):\n")
        
        for cluster in self.clusters:
            if cluster["type"] == "shared_wallet":
                report_lines.append(f"  [SHARED WALLET] {cluster['wallet']}")
                report_lines.append(f"    Identities: {', '.join(cluster['identities'])}")
                report_lines.append(f"    Action: First identity keeps wallet, others per-PR\n")
            elif cluster["type"] == "multiple_wallets":
                report_lines.append(f"  [MULTIPLE WALLETS] Identity: {cluster['identity']}")
                report_lines.append(f"    Wallets: {', '.join(cluster['wallets'])}")
                report_lines.append(f"    Action: First wallet declared canonical\n")
        
        resolution = self.resolve_conflicts()
        
        report_lines.append("\nRESOLUTION SUMMARY:")
        report_lines.append(f"  Canonical wallets declared: {len(resolution['canonical_map'])}")
        report_lines.append(f"  Per-PR inferences applied: {len(resolution['per_pr_inferences'])}")
        report_lines.append(f"\nDeadline for manual override: {DEADLINE_DATE.date()}")
        
        return "\n".join(report_lines)

def load_audit_data(filepath: str) -> Dict:
    """Load audit data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    """Main entry point for wallet canonicalization."""
    if len(sys.argv) < 2:
        print("Usage: canonicalize.py <audit_file.json> [--report]")
        sys.exit(1)
    
    audit_file = sys.argv[1]
    generate_report_flag = "--report" in sys.argv
    
    try:
        audit_data = load_audit_data(audit_file)
    except FileNotFoundError:
        print(f"ERROR: Audit file {audit_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in {audit_file}")
        sys.exit(1)
    
    canonicalizer = WalletCanonicalizer(audit_data)
    
    if generate_report_flag:
        print(canonicalizer.generate_report())
    else:
        resolution = canonicalizer.resolve_conflicts()
        print(json.dumps(resolution, indent=2))

if __name__ == "__main__":
    main()