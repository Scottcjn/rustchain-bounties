"""RustChain MCP Server - Query the Chain from Claude Code
Reward: 75-100 RTC
"""
import json
import urllib.request
import ssl
from typing import Any

NODE_URL = "https://50.28.86.131"
NODE_URL_2 = "https://50.28.86.132"
NODE_URL_3 = "https://50.28.86.133"

# SSL context to skip verification (for self-signed certs)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def get_url(url: str) -> dict:
    """Helper to fetch JSON from URL"""
    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=10) as response:
            return {"ok": True, "data": json.loads(response.read())}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def rustchain_health() -> dict:
    """Check node health across all 3 attestation nodes"""
    result = {"primary": None, "node2": None, "node3": None}
    
    r1 = get_url(f"{NODE_URL}/health")
    result["primary"] = r1
    
    r2 = get_url(f"{NODE_URL_2}/health")
    result["node2"] = r2
    
    r3 = get_url(f"{NODE_URL_3}/health")
    result["node3"] = r3
    
    healthy = sum(1 for r in [r1, r2, r3] if r.get("ok") and r.get("data", {}).get("ok"))
    result["summary"] = f"{healthy}/3 nodes healthy"
    return result

def rustchain_miners(limit: int = 10) -> dict:
    """List active miners and their architectures"""
    url = f"{NODE_URL}/api/miners"
    try:
        with urllib.request.urlopen(url, context=ssl_context, timeout=10) as response:
            data = json.loads(response.read())
            return {"miners": data[:limit], "total_shown": min(limit, len(data))}
    except Exception as e:
        return {"error": str(e)}

def rustchain_epoch() -> dict:
    """Get current epoch info (slot, height, rewards)"""
    return get_url(f"{NODE_URL}/epoch")

def rustchain_balance(miner_id: str) -> dict:
    """Check RTC balance for any wallet"""
    url = f"{NODE_URL}/wallet/balance?miner_id={miner_id}"
    return get_url(url)

def rustchain_hall_of_fame() -> dict:
    """Query the hall of fame for top miners"""
    return get_url(f"{NODE_URL}/api/hall_of_fame")

def rustchain_fee_pool() -> dict:
    """Check the fee pool statistics"""
    return get_url(f"{NODE_URL}/api/fee_pool")

def rustchain_stats() -> dict:
    """Get chain statistics"""
    return get_url(f"{NODE_URL}/api/stats")

# MCP Server tools
TOOLS = {
    "rustchain_health": {
        "description": "Check node health across all 3 attestation nodes",
        "fn": rustchain_health
    },
    "rustchain_miners": {
        "description": "List active miners and their architectures",
        "fn": rustchain_miners
    },
    "rustchain_epoch": {
        "description": "Get current epoch info (slot, height, rewards)",
        "fn": rustchain_epoch
    },
    "rustchain_balance": {
        "description": "Check RTC balance for any wallet",
        "fn": rustchain_balance
    },
    "rustchain_hall_of_fame": {
        "description": "Query the hall of fame for top miners",
        "fn": rustchain_hall_of_fame
    },
    "rustchain_fee_pool": {
        "description": "Check the fee pool statistics",
        "fn": rustchain_fee_pool
    },
    "rustchain_stats": {
        "description": "Get chain statistics",
        "fn": rustchain_stats
    }
}

if __name__ == "__main__":
    import sys
    tool = sys.argv[1] if len(sys.argv) > 1 else "health"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    
    if tool == "health":
        print(json.dumps(rustchain_health(), indent=2))
    elif tool == "miners":
        limit = int(arg) if arg else 10
        print(json.dumps(rustchain_miners(limit), indent=2))
    elif tool == "epoch":
        print(json.dumps(rustchain_epoch(), indent=2))
    elif tool == "balance":
        miner_id = arg or "Ivan-houzhiwen"
        print(json.dumps(rustchain_balance(miner_id), indent=2))
    elif tool == "hall_of_fame":
        print(json.dumps(rustchain_hall_of_fame(), indent=2))
    elif tool == "fee_pool":
        print(json.dumps(rustchain_fee_pool(), indent=2))
    elif tool == "stats":
        print(json.dumps(rustchain_stats(), indent=2))
    else:
        print(json.dumps({"error": f"Unknown tool: {tool}"}))
