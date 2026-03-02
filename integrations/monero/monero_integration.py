#!/usr/bin/env python3
"""
Monero (RandomX) Integration for RustChain Dual-Mining

This module provides proof-of-mining functionality for Monero (XMR) integration
with RustChain's RIP-PoA consensus system.

Features:
- Node RPC proof: Query monerod at localhost:18081/json_rpc
- P2Pool proof: Query local P2Pool at localhost:18083/local/stats
- Pool account proof: Verify via HeroMiners or Nanopool APIs
- Process detection: Detect xmrig, monerod, p2pool, xmr-stak processes

Usage:
    python monero_integration.py --proof-type node --wallet YOUR_WALLET
    python monero_integration.py --proof-type p2pool --wallet YOUR_WALLET
    python monero_integration.py --proof-type pool --pool nanopool --wallet YOUR_WALLET
    python monero_integration.py --proof-type process
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


# Default ports as per XMR API Reference
MONEROD_RPC_PORT = 18081
MONEROD_RESTRICTED_PORT = 18082
P2POOL_PORT = 18083

# Pool API endpoints
POOL_APIS = {
    "nanopool": "https://xmr.nanopool.org/api2/v1",
    "herominers": "https://xmr.herominers.com/api",
}


@dataclass
class ProofResult:
    """Standardized proof result structure."""
    proof_type: str
    timestamp: str
    wallet: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    rustchain_bonus_multiplier: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def now_utc() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_rpc_request(url: str, method: str, params: Optional[Dict] = None, timeout: int = 10) -> Dict[str, Any]:
    """Make a JSON-RPC request to a Monero daemon or pool."""
    payload = {
        "jsonrpc": "2.0",
        "id": "0",
        "method": method,
    }
    if params:
        payload["params"] = params

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to connect to {url}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from {url}: {e}")


def make_rest_request(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Make a REST API request."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "rustchain-monero-integration/1.0")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ConnectionError(f"HTTP error {e.code} from {url}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Failed to connect to {url}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from {url}: {e}")


def detect_processes() -> List[Dict[str, Any]]:
    """
    Detect running Monero-related processes.
    
    Returns a list of detected processes with their details.
    """
    target_processes = ["xmrig", "monerod", "p2pool", "xmr-stak"]
    detected = []

    try:
        # Use ps to find processes
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in result.stdout.splitlines():
            for proc_name in target_processes:
                if proc_name in line.lower():
                    parts = line.split()
                    if len(parts) >= 11:
                        detected.append({
                            "process": proc_name,
                            "pid": parts[1],
                            "cpu_percent": parts[2],
                            "memory_percent": parts[3],
                            "command": " ".join(parts[10:])
                        })
                    break
        
        # Also try pgrep for more accurate detection
        for proc_name in target_processes:
            try:
                result = subprocess.run(
                    ["pgrep", "-x", proc_name],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split("\n")
                    for pid in pids:
                        if not any(d["pid"] == pid and d["process"] == proc_name for d in detected):
                            detected.append({
                                "process": proc_name,
                                "pid": pid,
                                "cpu_percent": "N/A",
                                "memory_percent": "N/A",
                                "command": proc_name
                            })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        # ps or pgrep not available
        pass

    return detected


def verify_node_rpc(wallet: str, host: str = "localhost", port: int = MONEROD_RPC_PORT) -> ProofResult:
    """
    Verify Monero node RPC proof.
    
    Queries monerod at localhost:18081/json_rpc with get_info method.
    Returns block height, difficulty, and tx pool size as proof.
    """
    url = f"http://{host}:{port}/json_rpc"
    
    try:
        # Get node info
        info_result = make_rpc_request(url, "get_info")
        
        if "error" in info_result:
            return ProofResult(
                proof_type="node_rpc",
                timestamp=now_utc(),
                wallet=wallet,
                success=False,
                data={},
                error=f"RPC error: {info_result['error']}"
            )
        
        result = info_result.get("result", {})
        
        # Build proof data
        proof_data = {
            "host": host,
            "port": port,
            "block_height": result.get("height", 0),
            "difficulty": result.get("difficulty", 0),
            "tx_pool_size": result.get("tx_pool_size", 0),
            "network_hashrate": result.get("network_hashrate", 0),
            "rpc_endpoint": url,
            "query_timestamp": now_utc()
        }
        
        # Generate proof hash for RustChain verification
        proof_hash = hashlib.sha256(
            f"{wallet}:{proof_data['block_height']}:{proof_data['difficulty']}:{now_utc()}".encode()
        ).hexdigest()
        proof_data["proof_hash"] = proof_hash
        
        # Node RPC proof gives 1.5x bonus as per bounty requirements
        return ProofResult(
            proof_type="node_rpc",
            timestamp=now_utc(),
            wallet=wallet,
            success=True,
            data=proof_data,
            rustchain_bonus_multiplier=1.5
        )
        
    except (ConnectionError, ValueError) as e:
        return ProofResult(
            proof_type="node_rpc",
            timestamp=now_utc(),
            wallet=wallet,
            success=False,
            data={"host": host, "port": port},
            error=str(e)
        )


def verify_p2pool(wallet: str, host: str = "localhost", port: int = P2POOL_PORT) -> ProofResult:
    """
    Verify P2Pool mining proof.
    
    Queries local P2Pool at localhost:18083/local/stats.
    Returns miner statistics as proof.
    """
    url = f"http://{host}:{port}/local/stats"
    
    try:
        stats = make_rest_request(url)
        
        # P2Pool returns stats with miner address as key
        # Format: {"data": {"<wallet_address>": {"hashrate": ..., "last_share": ...}}}
        data = stats.get("data", {})
        
        if not data:
            return ProofResult(
                proof_type="p2pool",
                timestamp=now_utc(),
                wallet=wallet,
                success=False,
                data={},
                error="No P2Pool stats available"
            )
        
        # Find wallet in stats (may be partial match)
        wallet_stats = None
        matched_wallet = None
        
        for addr, addr_stats in data.items():
            if wallet in addr or addr in wallet:
                wallet_stats = addr_stats
                matched_wallet = addr
                break
        
        if not wallet_stats:
            # Return general pool stats if wallet not found
            proof_data = {
                "host": host,
                "port": port,
                "pool_stats": data,
                "wallet_found": False,
                "queried_wallet": wallet,
                "rpc_endpoint": url,
                "query_timestamp": now_utc()
            }
        else:
            proof_data = {
                "host": host,
                "port": port,
                "wallet": matched_wallet,
                "hashrate": wallet_stats.get("hashrate", 0),
                "last_share": wallet_stats.get("last_share", 0),
                "hashes": wallet_stats.get("hashes", 0),
                "rpc_endpoint": url,
                "query_timestamp": now_utc()
            }
        
        # Generate proof hash
        proof_hash = hashlib.sha256(
            f"{wallet}:{proof_data.get('hashrate', 0)}:{now_utc()}".encode()
        ).hexdigest()
        proof_data["proof_hash"] = proof_hash
        
        return ProofResult(
            proof_type="p2pool",
            timestamp=now_utc(),
            wallet=wallet,
            success=True,
            data=proof_data
        )
        
    except (ConnectionError, ValueError) as e:
        return ProofResult(
            proof_type="p2pool",
            timestamp=now_utc(),
            wallet=wallet,
            success=False,
            data={"host": host, "port": port},
            error=str(e)
        )


def verify_pool_account(wallet: str, pool_name: str = "nanopool") -> ProofResult:
    """
    Verify mining pool account proof.
    
    Queries HeroMiners or Nanopool APIs to verify wallet mining activity.
    Returns 1.3x bonus as per bounty requirements.
    """
    if pool_name not in POOL_APIS:
        return ProofResult(
            proof_type="pool_account",
            timestamp=now_utc(),
            wallet=wallet,
            success=False,
            data={},
            error=f"Unsupported pool: {pool_name}. Supported: {list(POOL_APIS.keys())}"
        )
    
    api_base = POOL_APIS[pool_name]
    
    try:
        if pool_name == "nanopool":
            # Nanopool API: /account/{address}
            url = f"{api_base}/account/{wallet}"
            response = make_rest_request(url)
            
            if response.get("status") != "ok":
                return ProofResult(
                    proof_type="pool_account",
                    timestamp=now_utc(),
                    wallet=wallet,
                    success=False,
                    data={"pool": pool_name},
                    error=f"Pool API error: {response.get('error', 'Unknown error')}"
                )
            
            account_data = response.get("data", {})
            
            proof_data = {
                "pool": pool_name,
                "wallet": wallet,
                "balance": account_data.get("balance", 0),
                "unconfirmed_balance": account_data.get("unconfirmed", 0),
                "total_hashrate": account_data.get("hashrate", 0),
                "average_hashrate": account_data.get("avgHashrate", 0),
                "workers": account_data.get("workers", []),
                "api_endpoint": url,
                "query_timestamp": now_utc()
            }
            
        elif pool_name == "herominers":
            # HeroMiners API: /stats/{address}
            url = f"{api_base}/stats/{wallet}"
            response = make_rest_request(url)
            
            if "error" in response:
                return ProofResult(
                    proof_type="pool_account",
                    timestamp=now_utc(),
                    wallet=wallet,
                    success=False,
                    data={"pool": pool_name},
                    error=f"Pool API error: {response['error']}"
                )
            
            proof_data = {
                "pool": pool_name,
                "wallet": wallet,
                "balance": response.get("balance", 0),
                "unconfirmed_balance": response.get("unconfirmed", 0),
                "total_hashrate": response.get("hashrate", 0),
                "workers": response.get("workers", []),
                "api_endpoint": url,
                "query_timestamp": now_utc()
            }
        
        # Generate proof hash
        proof_hash = hashlib.sha256(
            f"{wallet}:{proof_data.get('balance', 0)}:{now_utc()}".encode()
        ).hexdigest()
        proof_data["proof_hash"] = proof_hash
        
        # Pool account proof gives 1.3x bonus
        return ProofResult(
            proof_type="pool_account",
            timestamp=now_utc(),
            wallet=wallet,
            success=True,
            data=proof_data,
            rustchain_bonus_multiplier=1.3
        )
        
    except (ConnectionError, ValueError) as e:
        return ProofResult(
            proof_type="pool_account",
            timestamp=now_utc(),
            wallet=wallet,
            success=False,
            data={"pool": pool_name},
            error=str(e)
        )


def verify_process(wallet: str) -> ProofResult:
    """
    Verify running Monero mining processes.
    
    Detects xmrig, monerod, p2pool, xmr-stak processes.
    """
    detected = detect_processes()
    
    if not detected:
        return ProofResult(
            proof_type="process",
            timestamp=now_utc(),
            wallet=wallet,
            success=False,
            data={},
            error="No Monero mining processes detected"
        )
    
    proof_data = {
        "detected_processes": detected,
        "process_count": len(detected),
        "process_names": list(set(p["process"] for p in detected)),
        "scan_timestamp": now_utc()
    }
    
    # Generate proof hash
    proof_hash = hashlib.sha256(
        f"{wallet}:{len(detected)}:{now_utc()}".encode()
    ).hexdigest()
    proof_data["proof_hash"] = proof_hash
    
    return ProofResult(
        proof_type="process",
        timestamp=now_utc(),
        wallet=wallet,
        success=True,
        data=proof_data
    )


def generate_rustchain_claim(proof: ProofResult) -> Dict[str, Any]:
    """
    Generate a RustChain claim structure from proof result.
    
    This can be submitted to the RustChain network for RTC rewards.
    """
    return {
        "claim_type": "monero_dual_mining",
        "wallet": proof.wallet,
        "timestamp": proof.timestamp,
        "proof_type": proof.proof_type,
        "success": proof.success,
        "bonus_multiplier": proof.rustchain_bonus_multiplier,
        "proof_data": proof.data,
        "verification_hash": proof.data.get("proof_hash", ""),
        "rustchain_epoch": int(time.time() // 600),  # 10-minute epochs
    }


def main():
    parser = argparse.ArgumentParser(
        description="Monero (RandomX) Integration for RustChain Dual-Mining",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify node RPC proof (1.5x bonus)
  python monero_integration.py --proof-type node --wallet my-wallet

  # Verify P2Pool proof
  python monero_integration.py --proof-type p2pool --wallet my-wallet

  # Verify pool account (1.3x bonus)
  python monero_integration.py --proof-type pool --pool nanopool --wallet my-wallet

  # Detect mining processes
  python monero_integration.py --proof-type process --wallet my-wallet

  # Run all proofs
  python monero_integration.py --proof-type all --wallet my-wallet
        """
    )
    
    parser.add_argument(
        "--proof-type",
        choices=["node", "p2pool", "pool", "process", "all"],
        required=True,
        help="Type of proof to verify"
    )
    
    parser.add_argument(
        "--wallet",
        required=True,
        help="Monero wallet address or RustChain miner ID"
    )
    
    parser.add_argument(
        "--pool",
        choices=["nanopool", "herominers"],
        default="nanopool",
        help="Mining pool for pool account verification"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for local RPC queries (default: localhost)"
    )
    
    parser.add_argument(
        "--output",
        choices=["json", "rustchain"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    results = []
    
    if args.proof_type in ["node", "all"]:
        if args.verbose:
            print(f"Verifying node RPC proof...", file=sys.stderr)
        result = verify_node_rpc(args.wallet, args.host)
        results.append(result)
        if args.proof_type != "all":
            print(result.to_json())
            return 0 if result.success else 1
    
    if args.proof_type in ["p2pool", "all"]:
        if args.verbose:
            print(f"Verifying P2Pool proof...", file=sys.stderr)
        result = verify_p2pool(args.wallet, args.host)
        results.append(result)
        if args.proof_type != "all":
            print(result.to_json())
            return 0 if result.success else 1
    
    if args.proof_type in ["pool", "all"]:
        if args.verbose:
            print(f"Verifying pool account proof...", file=sys.stderr)
        result = verify_pool_account(args.wallet, args.pool)
        results.append(result)
        if args.proof_type != "all":
            print(result.to_json())
            return 0 if result.success else 1
    
    if args.proof_type in ["process", "all"]:
        if args.verbose:
            print(f"Detecting mining processes...", file=sys.stderr)
        result = verify_process(args.wallet)
        results.append(result)
        if args.proof_type != "all":
            print(result.to_json())
            return 0 if result.success else 1
    
    # Output all results for "all" mode
    if args.output == "json":
        output = {
            "timestamp": now_utc(),
            "wallet": args.wallet,
            "proofs": [r.to_dict() for r in results]
        }
        print(json.dumps(output, indent=2))
    else:
        # RustChain claim format
        claims = [generate_rustchain_claim(r) for r in results]
        print(json.dumps({"claims": claims}, indent=2))
    
    # Return success if any proof succeeded
    return 0 if any(r.success for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
