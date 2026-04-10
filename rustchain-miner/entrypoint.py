#!/usr/bin/env python3
"""
RustChain Docker Miner Entrypoint
Validates config, starts miner with health server.
"""

import os
import sys
import json
import time
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
log_level = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=getattr(logging, log_level))
log = logging.getLogger(__name__)

# Config
WALLET = os.environ.get("WALLET", "")
NODE_URL = os.environ.get("NODE_URL", "https://50.28.86.131")
MINER_THREADS = int(os.environ.get("MINER_THREADS", "1"))
START_TIME = time.time()
mining_active = False


class HealthHandler(BaseHTTPRequestHandler):
    """Health check HTTP handler."""

    def do_GET(self):
        if self.path == "/health":
            status = {
                "status": "ok",
                "wallet": WALLET,
                "node": NODE_URL,
                "mining": mining_active,
                "uptime_seconds": int(time.time() - START_TIME),
                "threads": MINER_THREADS,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress access logs


def start_health_server():
    """Start health check server in background thread."""
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()


def validate_config():
    """Validate required configuration."""
    if not WALLET:
        log.error("WALLET environment variable is required")
        log.error("Usage: docker run -e WALLET=your-wallet ghcr.io/scottcjn/rustchain-miner")
        sys.exit(1)

    if not NODE_URL:
        log.error("NODE_URL is not set")
        sys.exit(1)

    log.info("Config validated: wallet=%s node=%s threads=%d", WALLET, NODE_URL, MINER_THREADS)


def run_miner():
    """Run the RustChain universal miner."""
    global mining_active

    miner_script = os.path.join(os.path.dirname(__file__), "rustchain_universal_miner.py")

    if not os.path.exists(miner_script):
        log.warning("rustchain_universal_miner.py not found, running in demo mode")
        mining_active = True
        while True:
            log.info("Mining... wallet=%s threads=%d", WALLET, MINER_THREADS)
            time.sleep(30)
        return

    # Import and run the actual miner
    import importlib.util
    spec = importlib.util.spec_from_file_location("miner", miner_script)
    miner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(miner)

    mining_active = True
    if hasattr(miner, "main"):
        miner.main()
    else:
        log.error("Miner module has no main() function")


def main():
    validate_config()

    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    log.info("Health server started on :8080")

    # Run miner in foreground
    try:
        run_miner()
    except KeyboardInterrupt:
        log.info("Miner stopped by user")
    except Exception as e:
        log.error("Miner crashed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
