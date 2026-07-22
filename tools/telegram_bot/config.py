#!/usr/bin/env python3
"""
RustChain Telegram Community Bot — config loader.

Loads configuration from environment variables and an optional .env file.
"""
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional; env vars still work.
    pass

DEFAULT_API_BASE = "https://50.28.86.131"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
RUSTCHAIN_API_BASE = os.getenv("RUSTCHAIN_API_BASE", DEFAULT_API_BASE).rstrip("/")

REQUEST_TIMEOUT = float(os.getenv("RUSTCHAIN_REQUEST_TIMEOUT", "10"))

# Optional chat(s) to receive bonus alerts (comma-separated list of chat ids).
ALERT_CHAT_IDS = [
    cid.strip()
    for cid in os.getenv("RUSTCHAIN_ALERT_CHAT_IDS", "").split(",")
    if cid.strip()
]

# TLS verification toggle. The public node uses a self-signed cert, so the
# default is to skip verification (mirrors `curl -k` in the API docs).
VERIFY_TLS = os.getenv("RUSTCHAIN_VERIFY_TLS", "0") not in ("0", "false", "False")
