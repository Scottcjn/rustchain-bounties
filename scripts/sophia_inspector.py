#!/usr/bin/env python3
"""SophiaCore Attestation Inspector — Inspection Engine + HTTP API.

AI-powered validation layer where Sophia Elya (Elyan-class edge LLM)
inspects hardware fingerprint attestation bundles via Ollama and issues
confidence-scored verdicts.

Usage:
    python sophia_inspector.py --port 9130 --db sophia_inspections.db

RIP-306: SophiaCore Attestation Inspector
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError

logger = logging.getLogger("sophia.inspector")

# ---------------------------------------------------------------------------
# Configuration (env-driven)
# ---------------------------------------------------------------------------

DEFAULT_OLLAMA_HOSTS = "http://192.168.0.160:11434,http://100.75.100.89:11434,http://localhost:11434"
DEFAULT_MODEL = "elyan-sophia:7b-q4_K_M"
DEFAULT_PORT = 9130
DEFAULT_DB_PATH = "sophia_inspections.db"
DEFAULT_NODE_URL = "https://50.28.86.131"
PER_HOST_TIMEOUT = 10  # seconds per Ollama host attempt
HEALTH_CHECK_INTERVAL = 300  # seconds between host health checks


def get_config() -> Dict[str, Any]:
    """Read configuration from environment variables with sane defaults."""
    hosts_str = os.environ.get("SOPHIA_OLLAMA_HOSTS", DEFAULT_OLLAMA_HOSTS)
    return {
        "ollama_hosts": [h.strip() for h in hosts_str.split(",") if h.strip()],
        "model": os.environ.get("SOPHIA_MODEL", DEFAULT_MODEL),
        "db_path": os.environ.get("SOPHIA_DB_PATH", DEFAULT_DB_PATH),
        "port": int(os.environ.get("SOPHIA_PORT", str(DEFAULT_PORT))),
        "node_url": os.environ.get("NODE_API_URL", DEFAULT_NODE_URL),
        "admin_user": os.environ.get("SOPHIA_ADMIN_USER", ""),
        "admin_pass": os.environ.get("SOPHIA_ADMIN_PASS", ""),
        "trigger_secret": os.environ.get("SOPHIA_TRIGGER_SECRET", ""),
    }


# ---------------------------------------------------------------------------
# Prompt Engineering
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Sophia Elya, a hardware attestation inspector for the RustChain blockchain.
Your role is to analyze hardware fingerprint bundles and determine if they represent
genuine physical hardware or spoofed/emulated environments.

You MUST respond with ONLY a JSON object (no markdown fences, no explanation outside the JSON).
The JSON must contain exactly these fields:
- "verdict": one of "APPROVED", "CAUTIOUS", "SUSPICIOUS", "REJECTED"
- "confidence": float from 0.0 to 1.0 indicating how confident you are
- "reasoning": string explaining your analysis in 1-3 sentences
- "flags": array of anomaly codes (empty array if none found)

Valid anomaly codes:
  CLOCK_DRIFT_MISMATCH, CACHE_HIERARCHY_INVALID, SIMD_ARCH_CONFLICT,
  THERMAL_PROFILE_ANOMALY, FINGERPRINT_INSTABILITY, CROSS_EPOCH_DISCONTINUITY,
  PERFECT_VALUES, CORRELATION_FAILURE, VM_INDICATORS

Example response:
{"verdict":"CAUTIOUS","confidence":0.65,"reasoning":"Clock drift CV is within range for claimed CPU age, but cache timing L2/L3 ratio is atypically uniform for this architecture.","flags":["CACHE_HIERARCHY_INVALID"]}"""


def build_user_prompt(
    fingerprint: Mapping[str, Any],
    hardware: Mapping[str, Any],
    historical: Optional[Sequence[str]] = None,
) -> str:
    """Build the user-facing prompt with current + historical fingerprint data."""
    parts = [
        "Analyze this hardware attestation bundle:\n",
        "CURRENT FINGERPRINT:",
        json.dumps(fingerprint, indent=2),
        "\nCLAIMED HARDWARE:",
        json.dumps(hardware, indent=2),
    ]

    if historical:
        parts.append("\nHISTORICAL FINGERPRINTS (previous epochs, newest first):")
        for i, h in enumerate(historical[:3]):
            parts.append(f"\n--- Epoch -{ i + 1} ---")
            parts.append(h if isinstance(h, str) else json.dumps(h, indent=2))

    parts.append(
        "\nEvaluate: signal coherence, cross-metric correlations, temporal consistency, "
        "and whether this data pattern matches genuine physical hardware."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Response Parsing (robust)
# ---------------------------------------------------------------------------

VALID_VERDICTS = frozenset({"APPROVED", "CAUTIOUS", "SUSPICIOUS", "REJECTED"})
VALID_FLAGS = frozenset({
    "CLOCK_DRIFT_MISMATCH", "CACHE_HIERARCHY_INVALID", "SIMD_ARCH_CONFLICT",
    "THERMAL_PROFILE_ANOMALY", "FINGERPRINT_INSTABILITY", "CROSS_EPOCH_DISCONTINUITY",
    "PERFECT_VALUES", "CORRELATION_FAILURE", "VM_INDICATORS",
})

# Strip markdown code fences
_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)
# Fallback: extract JSON object
_JSON_OBJ_RE = re.compile(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", re.DOTALL)


def parse_sophia_response(raw: str) -> Dict[str, Any]:
    """Parse Sophia Elya's response with graceful degradation.

    Attempts:
      1. Direct json.loads
      2. Strip markdown code fences, then json.loads
      3. Regex extraction of JSON object
      4. Fallback to CAUTIOUS with parse_error flag
    """
    text = raw.strip()

    # Attempt 1: direct parse
    try:
        parsed = json.loads(text)
        return _validate_parsed(parsed)
    except (json.JSONDecodeError, ValueError):
        pass

    # Attempt 2: strip code fences
    fence_match = _CODE_FENCE_RE.search(text)
    if fence_match:
        try:
            parsed = json.loads(fence_match.group(1).strip())
            return _validate_parsed(parsed)
        except (json.JSONDecodeError, ValueError):
            pass

    # Attempt 3: regex extraction
    obj_match = _JSON_OBJ_RE.search(text)
    if obj_match:
        try:
            parsed = json.loads(obj_match.group(0))
            return _validate_parsed(parsed)
        except (json.JSONDecodeError, ValueError):
            pass

    # Attempt 4: graceful degradation
    logger.warning("Failed to parse Sophia response, falling back to CAUTIOUS: %s",
                    text[:200])
    return {
        "verdict": "CAUTIOUS",
        "confidence": 0.3,
        "reasoning": f"Parse error: model response was not valid JSON. Raw prefix: {text[:100]}",
        "flags": ["parse_error"],
    }


def _validate_parsed(parsed: Any) -> Dict[str, Any]:
    """Validate and normalize a parsed response dict."""
    if not isinstance(parsed, dict):
        raise ValueError("Response is not a JSON object")

    verdict = str(parsed.get("verdict", "")).upper()
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Invalid verdict: {verdict!r}")

    try:
        confidence = float(parsed.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    reasoning = str(parsed.get("reasoning", ""))

    raw_flags = parsed.get("flags", [])
    if isinstance(raw_flags, list):
        flags = [str(f) for f in raw_flags]
    else:
        flags = []

    return {
        "verdict": verdict,
        "confidence": confidence,
        "reasoning": reasoning,
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# Ollama Client with failover
# ---------------------------------------------------------------------------


class OllamaClient:
    """HTTP client for Ollama with multi-host failover and health tracking."""

    def __init__(
        self,
        hosts: List[str],
        model: str = DEFAULT_MODEL,
        per_host_timeout: int = PER_HOST_TIMEOUT,
    ) -> None:
        self.hosts = hosts
        self.model = model
        self.per_host_timeout = per_host_timeout
        self._host_health: Dict[str, bool] = {h: True for h in hosts}
        self._host_last_check: Dict[str, float] = {h: 0.0 for h in hosts}
        self._host_latency: Dict[str, List[float]] = {h: [] for h in hosts}
        self._host_errors: Dict[str, int] = {h: 0 for h in hosts}

    def check_host_health(self, host: str) -> bool:
        """Lightweight health check — GET /api/tags."""
        try:
            url = f"{host.rstrip('/')}/api/tags"
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "sophia-inspector/1.0")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            has_model = any(self.model in m for m in models)
            self._host_health[host] = has_model
            self._host_last_check[host] = time.time()
            if has_model:
                logger.debug("Host %s healthy, model available", host)
            else:
                logger.warning("Host %s reachable but model %s not found. Available: %s",
                              host, self.model, models)
            return has_model
        except Exception as e:
            logger.warning("Host %s health check failed: %s", host, e)
            self._host_health[host] = False
            self._host_last_check[host] = time.time()
            return False

    def _get_ordered_hosts(self) -> List[str]:
        """Return hosts ordered by health status and average latency."""
        now = time.time()
        for host in self.hosts:
            if now - self._host_last_check.get(host, 0) > HEALTH_CHECK_INTERVAL:
                self.check_host_health(host)

        healthy = [h for h in self.hosts if self._host_health.get(h, True)]
        unhealthy = [h for h in self.hosts if not self._host_health.get(h, True)]

        def avg_latency(h):
            lats = self._host_latency.get(h, [])
            return sum(lats[-5:]) / max(len(lats[-5:]), 1)

        healthy.sort(key=avg_latency)
        return healthy + unhealthy

    def generate(self, system: str, user: str) -> Tuple[str, str, int]:
        """Generate a response from the LLM.

        Returns: (response_text, host_used, latency_ms)
        Raises RuntimeError if all hosts fail.
        """
        errors = []
        for host in self._get_ordered_hosts():
            t0 = time.monotonic()
            try:
                result = self._call_host(host, system, user)
                latency_ms = int((time.monotonic() - t0) * 1000)
                self._host_latency.setdefault(host, []).append(latency_ms / 1000)
                self._host_health[host] = True
                self._host_errors[host] = 0
                return result, host, latency_ms
            except Exception as e:
                latency_ms = int((time.monotonic() - t0) * 1000)
                self._host_errors[host] = self._host_errors.get(host, 0) + 1
                if self._host_errors[host] >= 3:
                    self._host_health[host] = False
                errors.append(f"{host}: {e}")
                logger.warning("Ollama host %s failed (%dms): %s", host, latency_ms, e)
                continue

        raise RuntimeError(f"All Ollama hosts failed: {'; '.join(errors)}")

    def _call_host(self, host: str, system: str, user: str) -> str:
        """Send generate request to a single Ollama host."""
        url = f"{host.rstrip('/')}/api/generate"
        payload = json.dumps({
            "model": self.model,
            "system": system,
            "prompt": user,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 512,
            },
        }).encode()

        req = urllib.request.Request(url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "sophia-inspector/1.0")

        with urllib.request.urlopen(req, timeout=self.per_host_timeout) as resp:
            body = json.loads(resp.read().decode())

        return body.get("response", "")

    def get_host_stats(self) -> Dict[str, Any]:
        """Return per-host statistics for Prometheus/dashboard."""
        stats = {}
        for host in self.hosts:
            lats = self._host_latency.get(host, [])
            stats[host] = {
                "healthy": self._host_health.get(host, False),
                "errors": self._host_errors.get(host, 0),
                "avg_latency_ms": round(sum(lats[-10:]) / max(len(lats[-10:]), 1) * 1000, 1) if lats else 0,
                "total_calls": len(lats),
            }
        return stats


# ---------------------------------------------------------------------------
# Inspector (orchestrates everything)
# ---------------------------------------------------------------------------


class SophiaInspector:
    """High-level inspector: prompt building → Ollama → response parsing → DB."""

    def __init__(self, ollama: OllamaClient, db) -> None:
        self.ollama = ollama
        self.db = db

    def inspect(
        self,
        miner_id: str,
        fingerprint: Mapping[str, Any],
        hardware: Optional[Mapping[str, Any]] = None,
        epoch: Optional[int] = None,
    ):
        """Run a full Sophia Elya inspection.

        Returns an InspectionResult (imported from sophia_db).
        """
        from sophia_db import InspectionResult, fingerprint_hash

        hw = hardware or {}
        fp_hash = fingerprint_hash(fingerprint)
        fp_data = json.dumps(fingerprint, sort_keys=True)

        # Fetch historical fingerprints for cross-epoch comparison
        historical = self.db.get_historical_fingerprints(miner_id, limit=3)

        # Build prompt
        user_prompt = build_user_prompt(fingerprint, hw, historical)

        # Call Ollama with failover
        try:
            raw_response, host_used, latency_ms = self.ollama.generate(
                SYSTEM_PROMPT, user_prompt
            )
            parsed = parse_sophia_response(raw_response)
        except RuntimeError as e:
            logger.error("All Ollama hosts failed for %s: %s", miner_id, e)
            result = InspectionResult(
                miner_id=miner_id,
                verdict="CAUTIOUS",
                confidence=0.1,
                reasoning=f"SERVICE_UNAVAILABLE: {e}",
                flags=("service_unavailable",),
                epoch=epoch,
                fingerprint_hash=fp_hash,
                fingerprint_data=fp_data,
                ollama_host="none",
                latency_ms=0,
            )
            self.db.record_inspection(result)
            return result

        result = InspectionResult(
            miner_id=miner_id,
            verdict=parsed["verdict"],
            confidence=parsed["confidence"],
            reasoning=parsed["reasoning"],
            flags=tuple(parsed["flags"]),
            epoch=epoch,
            fingerprint_hash=fp_hash,
            fingerprint_data=fp_data,
            ollama_host=host_used,
            latency_ms=latency_ms,
        )

        self.db.record_inspection(result)
        return result


# ---------------------------------------------------------------------------
# HTTP API Server
# ---------------------------------------------------------------------------


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a thread pool."""
    daemon_threads = True


class SophiaHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Sophia API endpoints."""

    # Injected by server setup
    inspector: SophiaInspector = None  # type: ignore
    db = None
    config: Dict[str, Any] = {}

    def log_message(self, format, *args):
        logger.info("%s - %s", self.client_address[0], format % args)

    # ── Auth helpers ────────────────────────────────────────────────────

    def _check_admin_auth(self) -> bool:
        """Verify HTTP Basic Auth for admin endpoints."""
        user = self.config.get("admin_user", "")
        pwd = self.config.get("admin_pass", "")
        if not user:
            return True  # no auth configured = trusted network

        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            self._send_json(401, {"error": "Authentication required"},
                           extra_headers={"WWW-Authenticate": 'Basic realm="SophiaCore"'})
            return False

        try:
            decoded = base64.b64decode(auth_header[6:]).decode()
            provided_user, _, provided_pass = decoded.partition(":")
        except Exception:
            self._send_json(401, {"error": "Invalid auth header"})
            return False

        if provided_user != user or provided_pass != pwd:
            self._send_json(403, {"error": "Invalid credentials"})
            return False
        return True

    def _check_trigger_auth(self) -> bool:
        """Verify trigger secret for anomaly trigger endpoint."""
        secret = self.config.get("trigger_secret", "")
        if not secret:
            return True

        auth = self.headers.get("Authorization", "")
        if auth != f"Bearer {secret}":
            self._send_json(403, {"error": "Invalid trigger secret"})
            return False
        return True

    # ── Response helpers ────────────────────────────────────────────────

    def _send_json(self, status: int, data: Any,
                   extra_headers: Optional[Dict[str, str]] = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode())

    def _read_json_body(self) -> Optional[Dict[str, Any]]:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            self._send_json(400, {"error": "Empty request body"})
            return None
        try:
            body = json.loads(self.rfile.read(length).decode())
            if not isinstance(body, dict):
                self._send_json(400, {"error": "Request body must be a JSON object"})
                return None
            return body
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return None

    def _path_param(self, prefix: str) -> Optional[str]:
        """Extract path parameter after prefix, e.g. /sophia/status/MINER."""
        path = urllib.parse.urlparse(self.path).path
        if path.startswith(prefix):
            return urllib.parse.unquote(path[len(prefix):].strip("/"))
        return None

    def _query_params(self) -> Dict[str, str]:
        parsed = urllib.parse.urlparse(self.path)
        return dict(urllib.parse.parse_qsl(parsed.query))

    # ── Route dispatch ──────────────────────────────────────────────────

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        if path.startswith("/sophia/status/"):
            return self._handle_status()
        elif path.startswith("/sophia/history/"):
            return self._handle_history()
        elif path == "/sophia/stats":
            return self._handle_stats()
        elif path == "/sophia/pending":
            return self._handle_pending()
        elif path == "/sophia/dashboard":
            return self._handle_dashboard()
        elif path == "/sophia/metrics":
            return self._handle_metrics()
        elif path == "/sophia/health":
            return self._handle_health()
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path.rstrip("/")

        if path == "/sophia/inspect":
            return self._handle_inspect()
        elif path == "/sophia/override":
            return self._handle_override()
        elif path == "/sophia/batch-status":
            return self._handle_batch_status()
        elif path.startswith("/sophia/trigger/"):
            return self._handle_trigger()
        else:
            self._send_json(404, {"error": "Not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    # ── Endpoint handlers ───────────────────────────────────────────────

    def _handle_inspect(self):
        body = self._read_json_body()
        if not body:
            return

        miner_id = body.get("miner_id")
        fingerprint = body.get("fingerprint")
        if not miner_id or not fingerprint:
            self._send_json(400, {"error": "miner_id and fingerprint are required"})
            return

        hardware = body.get("hardware", body.get("device", {}))
        epoch = body.get("epoch")

        result = self.inspector.inspect(miner_id, fingerprint, hardware, epoch)
        response = result.to_dict()
        response["phase"] = "advisory"
        self._send_json(200, response)

    def _handle_status(self):
        miner_id = self._path_param("/sophia/status/")
        if not miner_id:
            self._send_json(400, {"error": "miner_id required in path"})
            return

        record = self.db.get_latest(miner_id)
        if not record:
            self._send_json(404, {"error": f"No inspections found for {miner_id}"})
            return

        data = record.to_dict()
        data["effective_verdict"] = record.effective_verdict
        data["emoji"] = record.emoji
        data["phase"] = "advisory"
        self._send_json(200, data)

    def _handle_history(self):
        miner_id = self._path_param("/sophia/history/")
        if not miner_id:
            self._send_json(400, {"error": "miner_id required in path"})
            return

        params = self._query_params()
        limit = min(int(params.get("limit", "50")), 200)
        records = self.db.get_history(miner_id, limit)
        self._send_json(200, {
            "miner_id": miner_id,
            "count": len(records),
            "inspections": [r.to_dict() for r in records],
        })

    def _handle_stats(self):
        stats = self.db.get_stats()
        stats["ollama_hosts"] = self.inspector.ollama.get_host_stats()
        self._send_json(200, stats)

    def _handle_pending(self):
        records = self.db.get_pending_reviews()
        self._send_json(200, {
            "count": len(records),
            "reviews": [r.to_dict() for r in records],
        })

    def _handle_override(self):
        if not self._check_admin_auth():
            return

        body = self._read_json_body()
        if not body:
            return

        inspection_id = body.get("inspection_id")
        verdict = body.get("verdict", "").upper()
        reason = body.get("reason", "")
        admin = body.get("admin", self.headers.get("X-Admin-User", "unknown"))

        if not inspection_id or not verdict or not reason:
            self._send_json(400, {"error": "inspection_id, verdict, and reason are required"})
            return

        try:
            updated = self.db.record_override(inspection_id, verdict, reason, admin)
        except ValueError as e:
            self._send_json(400, {"error": str(e)})
            return

        if updated:
            self._send_json(200, {
                "status": "override_recorded",
                "inspection_id": inspection_id,
                "verdict": verdict,
                "admin": admin,
            })
        else:
            self._send_json(404, {"error": f"Inspection #{inspection_id} not found"})

    def _handle_batch_status(self):
        body = self._read_json_body()
        if not body:
            return

        miner_ids = body.get("miner_ids", [])
        if not isinstance(miner_ids, list) or not miner_ids:
            self._send_json(400, {"error": "miner_ids must be a non-empty array"})
            return

        results = self.db.get_batch_status(miner_ids[:100])
        out = {}
        for mid, rec in results.items():
            if rec:
                out[mid] = {
                    "verdict": rec.effective_verdict,
                    "emoji": rec.emoji,
                    "confidence": rec.confidence,
                    "phase": "advisory",
                    "created_at": rec.created_at,
                }
            else:
                out[mid] = None
        self._send_json(200, {"results": out})

    def _handle_trigger(self):
        if not self._check_trigger_auth():
            return

        miner_id = self._path_param("/sophia/trigger/")
        if not miner_id:
            self._send_json(400, {"error": "miner_id required in path"})
            return

        body = self._read_json_body()
        if not body:
            return

        fingerprint = body.get("fingerprint", {})
        hardware = body.get("hardware", body.get("device", {}))
        epoch = body.get("epoch")

        result = self.inspector.inspect(miner_id, fingerprint, hardware, epoch)
        response = result.to_dict()
        response["phase"] = "advisory"
        response["triggered"] = True
        self._send_json(200, response)

    def _handle_health(self):
        host_stats = self.inspector.ollama.get_host_stats()
        any_healthy = any(s["healthy"] for s in host_stats.values())
        self._send_json(200, {
            "status": "healthy" if any_healthy else "degraded",
            "ollama_hosts": host_stats,
            "db_path": self.db.db_path,
        })

    def _handle_metrics(self):
        """Prometheus-format metrics endpoint."""
        stats = self.db.get_stats()
        host_stats = self.inspector.ollama.get_host_stats()

        lines = [
            "# HELP sophia_inspections_total Total inspections by verdict",
            "# TYPE sophia_inspections_total counter",
        ]
        for verdict, count in stats.get("by_verdict", {}).items():
            lines.append(f'sophia_inspections_total{{verdict="{verdict}"}} {count}')

        lines.extend([
            "# HELP sophia_avg_confidence Average confidence score",
            "# TYPE sophia_avg_confidence gauge",
            f'sophia_avg_confidence {stats.get("avg_confidence", 0)}',
            "# HELP sophia_pending_reviews Pending human reviews",
            "# TYPE sophia_pending_reviews gauge",
            f'sophia_pending_reviews {stats.get("pending_reviews", 0)}',
            "# HELP sophia_avg_latency_ms Average inference latency",
            "# TYPE sophia_avg_latency_ms gauge",
            f'sophia_avg_latency_ms {stats.get("avg_latency_ms", 0)}',
        ])

        for host, hs in host_stats.items():
            safe_host = host.replace('"', '\\"')
            lines.extend([
                f'sophia_ollama_host_healthy{{host="{safe_host}"}} {1 if hs["healthy"] else 0}',
                f'sophia_ollama_host_errors{{host="{safe_host}"}} {hs["errors"]}',
                f'sophia_ollama_host_calls{{host="{safe_host}"}} {hs["total_calls"]}',
            ])

        body = "\n".join(lines) + "\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def _handle_dashboard(self):
        """Serve the admin spot-check dashboard (inline HTML)."""
        try:
            from sophia_dashboard import DASHBOARD_HTML
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode())
        except ImportError:
            self._send_json(500, {"error": "Dashboard module not available"})


# ---------------------------------------------------------------------------
# CLI & Entry Point
# ---------------------------------------------------------------------------


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="SophiaCore Attestation Inspector — AI-powered hardware validation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--port", type=int, default=DEFAULT_PORT,
                    help="HTTP server port")
    p.add_argument("--db", default=DEFAULT_DB_PATH,
                    help="SQLite database path")
    p.add_argument("--ollama-hosts", default=DEFAULT_OLLAMA_HOSTS,
                    help="Comma-separated Ollama host URLs")
    p.add_argument("--model", default=DEFAULT_MODEL,
                    help="Ollama model name")
    p.add_argument("--log-level", default="INFO",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                    help="Logging level")
    return p.parse_args(argv)


def create_server(port: int, db_path: str, ollama_hosts: List[str],
                  model: str, config: Optional[Dict[str, Any]] = None):
    """Create and configure the Sophia HTTP server."""
    import sys
    # Allow imports from scripts/ directory
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from sophia_db import SophiaDB

    db = SophiaDB(db_path)
    ollama = OllamaClient(hosts=ollama_hosts, model=model)
    inspector = SophiaInspector(ollama=ollama, db=db)

    SophiaHTTPHandler.inspector = inspector
    SophiaHTTPHandler.db = db
    SophiaHTTPHandler.config = config or get_config()

    server = ThreadingHTTPServer(("0.0.0.0", port), SophiaHTTPHandler)
    return server, inspector, db


def main(argv=None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    hosts = [h.strip() for h in args.ollama_hosts.split(",") if h.strip()]
    config = get_config()
    config["db_path"] = args.db

    from pathlib import Path
    import sys
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    server, inspector, db = create_server(
        port=args.port,
        db_path=args.db,
        ollama_hosts=hosts,
        model=args.model,
        config=config,
    )

    logger.info("SophiaCore Inspector starting on :%d", args.port)
    logger.info("  Database: %s", args.db)
    logger.info("  Ollama hosts: %s", hosts)
    logger.info("  Model: %s", args.model)
    logger.info("  Endpoints: /sophia/{inspect,status,history,stats,pending,override,batch-status,trigger,dashboard,metrics,health}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
