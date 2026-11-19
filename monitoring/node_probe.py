import urllib.request
import urllib.error
import json
import time
from enum import Enum
from typing import TypedDict, Optional, Union

class NodeState(str, Enum):
    UP = "up"
    DOWN = "down"
    IMPOSTOR = "impostor"
    DEGRADED = "degraded"
    UNREACHABLE = "unreachable"

class ProbeResult(TypedDict):
    state: NodeState
    version: str
    uptime_s: Optional[int]
    message: str
    data: dict

def probe_health(url: str, timeout: int = 5, tip_age_threshold: int = 100) -> ProbeResult:
    """
    Validates a RustChain node health endpoint.
    Checks for HTTP status, Content-Type, and JSON body integrity.
    """
    result: ProbeResult = {
        "state": NodeState.UNREACHABLE,
        "version": "unknown",
        "uptime_s": None,
        "message": "",
        "data": {}
    }

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status = response.getcode()
            content_type = response.info().get_content_type()
            body = response.read().decode('utf-8')

            # 1. Check for HTML Impostor
            if "text/html" in content_type or body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html"):
                result["state"] = NodeState.IMPOSTOR
                result["message"] = "Returned HTML instead of JSON"
                return result

            # 2. Try parsing JSON
            try:
                data = json.loads(body)
                result["data"] = data
            except json.JSONDecodeError:
                result["state"] = NodeState.IMPOSTOR
                result["message"] = "Invalid JSON body"
                return result

            # 3. Validate Mandatory Keys
            required_keys = {"ok", "version", "uptime_s"}
            if not required_keys.issubset(data.keys()):
                result["state"] = NodeState.IMPOSTOR
                result["message"] = f"Missing keys: {required_keys - data.keys()}"
                return result

            result["version"] = str(data.get("version", "unknown"))
            result["uptime_s"] = data.get("uptime_s")

            # 4. Check for Degraded State
            is_ok = data.get("ok") is True
            db_rw = data.get("db_rw", True) is True
            tip_age = data.get("tip_age_slots", 0)
            
            if not is_ok or not db_rw or tip_age > tip_age_threshold:
                result["state"] = NodeState.DEGRADED
                reasons = []
                if not is_ok: reasons.append("ok=false")
                if not db_rw: reasons.append("db_rw=false")
                if tip_age > tip_age_threshold: reasons.append(f"stale_tip({tip_age})")
                result["message"] = f"Node degraded: {', '.join(reasons)}"
                return result

            # 5. Success
            result["state"] = NodeState.UP
            result["message"] = "Node healthy"
            return result

    except urllib.error.HTTPError as e:
        result["state"] = NodeState.DOWN
        result["message"] = f"HTTP Error {e.code}"
    except urllib.error.URLError as e:
        result["state"] = NodeState.UNREACHABLE
        result["message"] = f"Unreachable: {str(e.reason)}"
    except Exception as e:
        result["state"] = NodeState.DOWN
        result["message"] = f"Unexpected error: {str(e)}"

    return result
