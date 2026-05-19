"""
bridge/dashboard_api.py

Dashboard health API endpoints with error redaction.
Provides a health check endpoint that verifies connectivity to database,
Solana RPC, and wRTC mint services. Sensitive error details are redacted
from client responses while full context is logged server‑side.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Tuple

import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from solana.rpc.api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.core import RPCException

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ServiceHealth(BaseModel):
    status: str  # "ok" | "error"
    message: str = ""
    latency_ms: float = 0.0


class HealthResponse(BaseModel):
    status: str
    services: Dict[str, ServiceHealth]


# ---------------------------------------------------------------------------
# DashboardAPI class
# ---------------------------------------------------------------------------


class DashboardAPI:
    """Encapsulates health‑check logic for database, Solana RPC, and wRTC mint.

    Configuration is provided via constructor arguments. Each check returns a
    structured dict with status, message, and latency.
    """

    def __init__(
        self,
        database_url: str,
        solana_rpc_url: str,
        wrtc_mint_address: str,
    ) -> None:
        self._database_url = database_url
        self._solana_rpc_url = solana_rpc_url
        self._wrtc_mint_address = wrtc_mint_address

    # -----------------------------------------------------------------------
    # Private health‑check methods
    # -----------------------------------------------------------------------

    async def _check_database(self) -> Tuple[bool, str, float]:
        """Check connectivity to the PostgreSQL database.

        Returns:
            Tuple of (success: bool, message: str, latency_ms: float)
        """
        start = time.monotonic()
        try:
            conn = await asyncpg.connect(self._database_url, timeout=5)
            await conn.execute("SELECT 1")
            await conn.close()
            latency = (time.monotonic() - start) * 1000
            logger.info("Database health check succeeded (%.2f ms)", latency)
            return True, "", latency
        except asyncpg.PostgresError as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Database health check failed")
            return False, f"Database error: {exc}", latency
        except asyncio.TimeoutError:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Database health check timed out")
            return False, "Database connection timed out", latency
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Unexpected database health check error")
            return False, f"Unexpected error: {exc}", latency

    async def _check_solana_rpc(self) -> Tuple[bool, str, float]:
        """Check connectivity to the Solana RPC endpoint.

        Sends a ``getHealth`` request and returns the result.

        Returns:
            Tuple of (success: bool, message: str, latency_ms: float)
        """
        start = time.monotonic()
        try:
            client = AsyncClient(self._solana_rpc_url)
            response = await client.get_health()
            # get_health returns a dict with 'result' == 'ok' on success
            if response.get("result") == "ok":
                latency = (time.monotonic() - start) * 1000
                logger.info("Solana RPC health check succeeded (%.2f ms)", latency)
                return True, "", latency
            latency = (time.monotonic() - start) * 1000
            logger.warning("Solana RPC health returned unexpected response: %s", response)
            return False, "Solana RPC returned unexpected response", latency
        except RPCException as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Solana RPC health check failed")
            return False, f"RPC error: {exc}", latency
        except asyncio.TimeoutError:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Solana RPC health check timed out")
            return False, "Solana RPC connection timed out", latency
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Unexpected Solana RPC health check error")
            return False, f"Unexpected error: {exc}", latency

    async def _check_wrtc_mint(self) -> Tuple[bool, str, float]:
        """Verify the wRTC mint account is accessible on Solana.

        Queries the mint account info using the configured RPC.

        Returns:
            Tuple of (success: bool, message: str, latency_ms: float)
        """
        start = time.monotonic()
        try:
            client = AsyncClient(self._solana_rpc_url)
            response = await client.get_account_info(
                self._wrtc_mint_address,
                commitment=Confirmed,
            )
            # A valid mint account will have a non‑zero lamport balance
            # and proper account data (we just check existence).
            if response.get("result") and response["result"]["value"]:
                latency = (time.monotonic() - start) * 1000
                logger.info("wRTC mint health check succeeded (%.2f ms)", latency)
                return True, "", latency
            latency = (time.monotonic() - start) * 1000
            logger.warning("wRTC mint account not found or empty")
            return False, "wRTC mint account not found", latency
        except RPCException as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("wRTC mint health check failed")
            return False, f"RPC error: {exc}", latency
        except asyncio.TimeoutError:
            latency = (time.monotonic() - start) * 1000
            logger.exception("wRTC mint health check timed out")
            return False, "wRTC mint check timed out", latency
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.exception("Unexpected wRTC mint health check error")
            return False, f"Unexpected error: {exc}", latency

    # -----------------------------------------------------------------------
    # Public health‑check endpoint handler
    # -----------------------------------------------------------------------

    async def health_check(self) -> HealthResponse:
        """Returns the health status of all dependent services.

        Each service is checked independently. On failure, the client receives
        a generic error message while the full exception (including stack trace)
        is logged on the server.

        Returns:
            A ``HealthResponse`` with per‑service status, latency, and overall
            health.
        """
        services: Dict[str, ServiceHealth] = {}
        overall_status = "ok"

        checks = [
            ("database", self._check_database),
            ("solana_rpc", self._check_solana_rpc),
            ("wrtc_mint", self._check_wrtc_mint),
        ]

        for name, func in checks:
            try:
                success, message, latency = await func()
                if success:
                    services[name] = ServiceHealth(
                        status="ok", message=message, latency_ms=latency
                    )
                else:
                    services[name] = ServiceHealth(
                        status="error",
                        message="Service unavailable",
                        latency_ms=latency,
                    )
                    overall_status = "error"
            except Exception as exc:
                logger.exception("Unexpected error during health check for '%s'", name)
                services[name] = ServiceHealth(
                    status="error",
                    message="Service unavailable",
                    latency_ms=0.0,
                )
                overall_status = "error"

        return HealthResponse(status=overall_status, services=services)


# ---------------------------------------------------------------------------
# Router – uses an instance of DashboardAPI
# ---------------------------------------------------------------------------

# Replace these placeholders with actual configuration values.
# In production, these should come from environment variables or a config file.
_DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
_SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
_WRTC_MINT_ADDRESS = "YourWRtcMintAddressHere"

dashboard = DashboardAPI(
    database_url=_DATABASE_URL,
    solana_rpc_url=_SOLANA_RPC_URL,
    wrtc_mint_address=_WRTC_MINT_ADDRESS,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/health", response_model=HealthResponse)
async def health_check_endpoint() -> HealthResponse:
    """Expose the DashboardAPI health check via FastAPI."""
    return await dashboard.health_check()


# ---------------------------------------------------------------------------
# Error handler (optional, included for completeness)
# ---------------------------------------------------------------------------


def _redact_error_response(exc: Exception) -> Dict[str, Any]:
    """Converts an exception into a generic client‑safe response.

    The full exception is logged server‑side.
    """
    logger.exception("Internal server error")
    return {"detail": "An internal error occurred"}