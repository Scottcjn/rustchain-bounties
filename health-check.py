import requests
import json
from typing import Dict, Any, Optional

# Constants for health check endpoints and expected response keys
HEALTH_ENDPOINT = "/health"
EPOCH_ENDPOINT = "/epoch"
API_WALLET_ENDPOINT = "/api/wallet/{wallet_id}"
API_BOUNTIES_ENDPOINT = "/api/bounties"

# Expected keys in the /health endpoint response
HEALTH_EXPECTED_KEYS = {"version", "ok", "uptime_s"}

# Expected keys in the /epoch endpoint response
EPOCH_EXPECTED_KEYS = {"epoch", "slot", "duration_s"}

# Result states for probe_health
class ProbeResult:
    UP = "up"
    DOWN = "down"
    IMPOSTOR = "impostor"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"

def probe_health(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Probes a RustChain node's health endpoint, validating the response body.

    Args:
        url: The base URL of the RustChain node (e.g., "http://localhost:3000").
        timeout: Request timeout in seconds.

    Returns:
        A dictionary containing the probe result and details.
        Example: {"status": ProbeResult.UP, "version": "1.2.3", ...}

    Security:
        - Validates Content-Type to be application/json.
        - Validates presence of expected keys in JSON response.
        - Handles various HTTP errors and network issues gracefully.
    """
    health_url = url.rstrip('/') + HEALTH_ENDPOINT
    try:
        response = requests.get(health_url, timeout=timeout)

        # Check for non-200 status codes first
        if response.status_code != 200:
            return {"status": ProbeResult.DOWN, "code": response.status_code, "reason": response.reason}

        # Validate Content-Type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/json' not in content_type:
            return {"status": ProbeResult.IMPOSTOR, "reason": f"Invalid Content-Type: {content_type}"}

        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
            return {"status": ProbeResult.IMPOSTOR, "reason": "Failed to decode JSON response"}

        # Validate expected keys
        if not HEALTH_EXPECTED_KEYS.issubset(data.keys()):
            missing_keys = HEALTH_EXPECTED_KEYS - data.keys()
            return {"status": ProbeResult.IMPOSTOR, "reason": f"Missing expected keys: {missing_keys}"}

        # Check for degraded status based on 'ok' field
        if not data.get('ok', True):
            return {"status": ProbeResult.DEGRADED, "reason": "Node reported 'ok': false"}

        # Further checks for degraded status (e.g., tip_age_slots if available)
        # This part can be extended based on specific 'degraded' criteria
        # For now, we assume 'ok: true' means 'up' if other checks pass.

        return {"status": ProbeResult.UP, **data}

    except requests.exceptions.Timeout:
        return {"status": ProbeResult.UNREACHABLE, "reason": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"status": ProbeResult.UNREACHABLE, "reason": "Connection error"}
    except requests.exceptions.RequestException as e:
        return {"status": ProbeResult.UNREACHABLE, "reason": str(e)}

def check_node_health(node_url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Wrapper function to call probe_health and return a standardized dict.
    This function is intended to be used by the monitors.
    """
    result = probe_health(node_url, timeout)
    return {
        "status": result.get("status"),
        "version": result.get("version", "unknown"),
        "uptime_s": result.get("uptime_s", 0),
        "ok": result.get("ok", False), # Default to False if not present or status is not UP
        "reason": result.get("reason", "")
    }

# Example usage (for testing purposes):
if __name__ == "__main__":
    # Replace with actual node URLs for testing
    test_nodes = [
        "http://localhost:3000", # Assuming a local node is running
        "http://example.com",    # A non-RustChain URL
        "http://httpbin.org/html", # Returns HTML with 200 OK
        "http://httpbin.org/json", # Returns valid JSON with 200 OK
        "http://httpbin.org/status/500", # Returns 500 Internal Server Error
        "http://nonexistent.domain.xyz", # Unreachable
    ]

    for node in test_nodes:
        print(f"Checking {node}...")
        health_data = check_node_health(node)
        print(f"  Result: {health_data}")

        # Simulate degraded status for testing
        if node == "http://httpbin.org/json":
            print("  Simulating degraded status for httpbin.org/json...")
            degraded_data = probe_health(node)
            degraded_data['ok'] = False
            degraded_data['reason'] = "Simulated degraded state"
            print(f"  Degraded Result: {{'status': degraded_data.get('status'), 'ok': degraded_data.get('ok'), 'reason': degraded_data.get('reason')}}")

