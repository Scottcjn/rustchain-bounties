#!/usr/bin/env python3
"""
RustChain Telegram Community Bot — API client.

Thin async client wrapping the public RustChain HTTP API. All methods return a
plain dict (or raise) and never swallow errors silently; callers decide how to
present failures to the user.
"""
from __future__ import annotations

import logging

import httpx

import config

logger = logging.getLogger(__name__)


async def _get(path: str, params: dict | None = None) -> dict:
    """GET a JSON endpoint from the RustChain node, raising on failure."""
    url = f"{config.RUSTCHAIN_API_BASE}{path}"
    async with httpx.AsyncClient(verify=config.VERIFY_TLS, timeout=config.REQUEST_TIMEOUT) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


async def get_health() -> dict:
    """Node health status from ``GET /health``."""
    return await _get("/health")


async def get_epoch() -> dict:
    """Current epoch info from ``GET /epoch``."""
    return await _get("/epoch")


async def get_miners() -> dict | list:
    """Active miner list from ``GET /api/miners``.

    The endpoint shape varies; the caller normalises it.
    """
    return await _get("/api/miners")


async def get_balance(wallet: str) -> dict:
    """RTC balance for a wallet/public key from ``GET /balance/{wallet}``."""
    return await _get(f"/balance/{wallet}")


async def get_price() -> dict:
    """Current wRTC price.

    RustChain has no first-party price endpoint, so we attempt to read the
    wRTC/WSOL pool price from Raydium's public API and degrade gracefully if it
    is unavailable.
    """
    url = "https://api.raydium.io/v2/main/pairs"
    async with httpx.AsyncClient(timeout=config.REQUEST_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        pairs = resp.json()
    if not isinstance(pairs, list):
        raise ValueError("Unexpected Raydium response")
    # wRTC mint per the RustChain docs/community; matched case-insensitively.
    wrtc_symbols = ("wrtc", "rtc")
    for pair in pairs:
        base = str(pair.get("baseSymbol", "")).lower()
        quote = str(pair.get("quoteSymbol", "")).lower()
        if base in wrtc_symbols or quote in wrtc_symbols:
            price = pair.get("price") or pair.get("priceUsd")
            if price is None and base in wrtc_symbols and quote in ("usdc", "usdt", "sol"):
                # Raydium returns price in quote terms; keep as-is.
                price = pair.get("price")
            return {
                "symbol": pair.get("baseSymbol", "wRTC"),
                "price": price,
                "liquidity": pair.get("liquidity"),
                "volume_24h": pair.get("volume24h"),
                "pair": pair.get("name", ""),
                "source": "raydium",
            }
    raise LookupError("wRTC pair not found on Raydium")


async def get_active_miner_count() -> int:
    """Return the number of active miners, normalising various response shapes."""
    data = await get_miners()
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        for key in ("count", "active_miners", "total_miners", "miners"):
            if key in data and isinstance(data[key], int):
                return data[key]
        if "miners" in data and isinstance(data["miners"], list):
            return len(data["miners"])
    return 0
