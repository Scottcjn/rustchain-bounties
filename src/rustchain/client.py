"""
RustChain SDK — Main client.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python SDK for the RustChain Proof-of-Antiquity blockchain node API.

Supports:
- Health, epoch, miner, and balance queries
- Lottery eligibility checks
- Attestation submission
- Signed Ed25519 transfers
- Self-signed SSL certificates
- Automatic retry with exponential back-off
- Full type hints (Python 3.8+)

Install
-------
    pip install git+https://github.com/Scottcjn/rustchain-bounties.git

    # or from PyPI (when published):
    pip install rustchain

Quick start
-----------
    from rustchain import RustChainClient

    # Use the public node (skip SSL verification for self-signed certs)
    client = RustChainClient(base_url="https://rustchain.org", verify_ssl=False)

    # Node health
    health = client.health()
    print(health.ok, health.version)

    # Current epoch
    epoch = client.get_epoch()
    print(f"Epoch {epoch.epoch}, pot={epoch.epoch_pot} RTC")

    # List active miners
    miners = client.get_miners()
    for m in miners:
        print(f"{m.miner}: {m.hardware_type} ({m.antiquity_multiplier}x)")

    # Wallet balance
    bal = client.get_balance("my-miner-id")
    print(f"Balance: {bal.amount_rtc} RTC")

    # Lottery eligibility
    eligibility = client.get_lottery_eligibility("my-miner-id")
    print(f"Eligible: {eligibility.eligible}, chance={eligibility.chance:.2%}")

    # Transfer RTC
    tx = client.signed_transfer(
        from_address="RTCaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        to_address="RTCbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        amount_rtc=1.0,
        nonce=12345,
        public_key="<ed25519_public_key_hex>",
        signature="<ed25519_signature_hex>",
    )
    print(f"Tx submitted: {tx.tx_hash}")

Attestation
-----------
    from rustchain.models import Fingerprint

    fp = Fingerprint(
        clock_skew={...},      # from hardware probe
        cache_timing={...},     # from hardware probe
        simd_identity={...},   # from hardware probe
        thermal_entropy={...},  # from hardware probe
        instruction_jitter={...},  # from hardware probe
        behavioral_heuristics={...},  # from hardware probe
    )

    result = client.submit_attestation(
        miner_id="my-miner-id",
        fingerprint=fp,
        signature="<base64_ed25519_signature>",
    )
    print(result.enrolled, result.multiplier)
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, List, Dict, Any

from rustchain.exceptions import (
    RustChainError,
    NodeUnreachableError,
    RateLimitError,
    AttestationError,
    TransferError,
    MinerNotFoundError,
    InvalidSignatureError,
    InsufficientBalanceError,
)
from rustchain.models import (
    HealthResponse,
    EpochResponse,
    Miner,
    BalanceResponse,
    TransferRecord,
    TransferResponse,
    AttestationResponse,
    LotteryEligibility,
    Fingerprint,
)

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# Default settings
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://rustchain.org"
DEFAULT_TIMEOUT = 30.0  # seconds
DEFAULT_MAX_RETRIES = 5

# ---------------------------------------------------------------------------
# Retry strategy helpers
# ---------------------------------------------------------------------------


def _default_retry_strategy(
    total: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = 0.5,
    status_forcelist: tuple = (429, 500, 502, 503, 504),
) -> Retry:
    """
    Build a urllib3 Retry object with exponential back-off.

    Used internally by :meth:`RustChainClient.make_session`.
    """
    return Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class RustChainClient:
    """
    Python client for the RustChain node HTTP API.

    Parameters
    ----------
    base_url:
        Base URL of the RustChain node. Default: ``https://rustchain.org``.
    verify_ssl:
        Whether to verify TLS certificates. Set ``False`` for self-signed
        certificates on private nodes. Default: ``True``.
    timeout:
        Request timeout in seconds. Default: ``30``.
    max_retries:
        Maximum retry attempts for transient HTTP errors (5xx, 429).
        Default: ``5``.
    session:
        Optional ``requests.Session`` to use for all HTTP calls.
        When omitted an internal session with retry logic is created.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        verify_ssl: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        session: Optional[requests.Session] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.max_retries = max_retries

        if session is not None:
            self._session = session
        else:
            self._session = self._build_session()

    # ── Session management ─────────────────────────────────────────────────

    def _build_session(self) -> requests.Session:
        """Create a requests session with retry adapter."""
        sess = requests.Session()
        adapter = HTTPAdapter(
            max_retries=_default_retry_strategy(total=self.max_retries)
        )
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)
        return sess

    def close(self) -> None:
        """Close the underlying session (no-op if an external session was passed)."""
        self._session.close()

    def __enter__(self) -> "RustChainClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ── Low-level request helper ────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        raises: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and return parsed JSON.

        Parameters
        ----------
        method:
            HTTP method (``GET``, ``POST``, …).
        path:
            URL path (appended to ``self.base_url``).
        params:
            Query-string parameters for GET requests.
        json:
            JSON body for POST requests.
        raises:
            If ``True`` (default), raise a typed exception on known
            RustChain error codes. If ``False``, return the raw response
            dict even on error.

        Returns
        -------
        dict
            Parsed JSON response.

        Raises
        ------
        NodeUnreachableError
            Connection error or non-retryable HTTP failure.
        RateLimitError
            HTTP 429 response.
        RustChainError
            Other known RustChain error codes surfaced in the response body.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
        except requests.RequestException as exc:
            raise NodeUnreachableError(
                f"Failed to connect to {url}: {exc}"
            ) from exc

        # Attempt to parse JSON error body for RustChain error codes
        try:
            data = resp.json()
        except ValueError:
            data = {}

        if not raises:
            return data

        # Surface typed errors where possible
        if resp.status_code == 429:
            raise RateLimitError(
                data.get("error", "API rate limit exceeded")
                if isinstance(data, dict) else
                "API rate limit exceeded"
            )

        if resp.status_code >= 400 and isinstance(data, dict):
            code = data.get("error") or data.get("code", "")
            msg = data.get("error") or data.get("message") or resp.text

            if code == "MINER_NOT_FOUND":
                raise MinerNotFoundError(data.get("miner_id", "unknown"))
            if code == "INVALID_SIGNATURE":
                raise InvalidSignatureError(msg)
            if code == "INSUFFICIENT_BALANCE":
                raise InsufficientBalanceError(
                    available=data.get("available_rtc", 0.0),
                    required=data.get("required_rtc", 0.0),
                )
            if code == "VM_DETECTED":
                raise AttestationError(
                    msg,
                    check_failed=data.get("check_failed"),
                    detail=data.get("detail"),
                )
            if code in ("RATE_LIMITED", "ATTESTATION_FAILED", "TRANSFER_FAILED"):
                # Return the raw dict for generic error handling
                pass

            if resp.status_code >= 500:
                raise NodeUnreachableError(f"Server error {resp.status_code}: {msg}")

            raise RustChainError(msg, code=code)

        resp.raise_for_status()
        return data

    # ── Public API ──────────────────────────────────────────────────────────

    # Health

    def health(self) -> HealthResponse:
        """
        Check node health and status.

        Returns
        -------
        HealthResponse
            Current node health information.

        Example::

            health = client.health()
            print(health.ok, health.version, health.uptime_s)
        """
        data = self._request("GET", "/health", raises=False)
        # Node may return non-JSON or error page for /health on some nodes
        if not isinstance(data, dict) or "ok" not in data:
            raise RustChainError(f"Unexpected /health response: {data}")
        return HealthResponse.from_dict(data)

    # Epoch

    def get_epoch(self) -> EpochResponse:
        """
        Get current epoch details.

        Returns
        -------
        EpochResponse
            Current epoch number, slot, pot size, and enrolled miner count.

        Example::

            epoch = client.get_epoch()
            print(f"Epoch {epoch.epoch}, slot {epoch.slot}/{epoch.blocks_per_epoch}")
            print(f"Pot: {epoch.epoch_pot} RTC, miners: {epoch.enrolled_miners}")
        """
        data = self._request("GET", "/epoch")
        return EpochResponse.from_dict(data)

    # Miners

    def get_miners(self) -> List[Miner]:
        """
        List all active / enrolled miners.

        Returns
        -------
        List[Miner]
            List of active miners with hardware info and antiquity multipliers.

        Example::

            miners = client.get_miners()
            for m in miners:
                print(f"{m.miner}: {m.hardware_type} ({m.antiquity_multiplier}x)")
        """
        data = self._request("GET", "/api/miners")
        if not isinstance(data, list):
            raise RustChainError(f"Unexpected /api/miners response: {data}")
        return [Miner.from_dict(item) for item in data]

    # Wallet Balance

    def get_balance(self, miner_id: str) -> BalanceResponse:
        """
        Get RTC balance for a miner / wallet.

        Parameters
        ----------
        miner_id:
            The miner ID (wallet address or registered name).

        Returns
        -------
        BalanceResponse
            Balance in both human-readable RTC and micro-RTC (6 decimal places).

        Example::

            bal = client.get_balance("eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC")
            print(f"Balance: {bal.amount_rtc} RTC")
        """
        data = self._request(
            "GET", "/wallet/balance", params={"miner_id": miner_id}
        )
        return BalanceResponse.from_dict(data)

    # Wallet History

    def get_wallet_history(
        self, miner_id: str, *, limit: int = 50
    ) -> List[TransferRecord]:
        """
        Read recent transfer history for a wallet.

        Parameters
        ----------
        miner_id:
            The miner ID / wallet address.
        limit:
            Maximum records to return (1–200, default: 50).

        Returns
        -------
        List[TransferRecord]
            Transfer history ordered newest first.

        Example::

            history = client.get_wallet_history("my-wallet", limit=10)
            for tx in history:
                print(f"{tx.direction} {tx.amount_rtc} RTC — {tx.status}")
        """
        data = self._request(
            "GET", "/wallet/history",
            params={"miner_id": miner_id, "limit": limit},
        )
        if not isinstance(data, list):
            raise RustChainError(f"Unexpected /wallet/history response: {data}")
        return [TransferRecord.from_dict(item) for item in data]

    # Lottery Eligibility

    def get_lottery_eligibility(self, miner_id: str) -> LotteryEligibility:
        """
        Check if a miner is eligible for the epoch lottery and what their
        selection chance is.

        Parameters
        ----------
        miner_id:
            The miner ID / wallet address.

        Returns
        -------
        LotteryEligibility
            Eligibility status, per-epoch selection chance, and hardware factors.

        Example::

            le = client.get_lottery_eligibility("my-miner-id")
            print(f"Eligible: {le.eligible}, chance={le.chance:.2%}")
            print(f"Antiquity multiplier: {le.antiquity_multiplier}x")
        """
        data = self._request(
            "GET", "/lottery/eligibility", params={"miner_id": miner_id}
        )
        return LotteryEligibility.from_dict(data)

    # Attestation

    def submit_attestation(
        self,
        miner_id: str,
        fingerprint: Fingerprint,
        signature: str,
    ) -> AttestationResponse:
        """
        Submit a hardware fingerprint attestation for epoch enrollment.

        Parameters
        ----------
        miner_id:
            The miner ID submitting the attestation.
        fingerprint:
            A :class:`~rustchain.models.Fingerprint` object with six probe
            results from the hardware.
        signature:
            Base64-encoded Ed25519 signature of the fingerprint bundle.

        Returns
        -------
        AttestationResponse
            Enrollment result including epoch, antiquity multiplier, and
            next settlement slot on success; or error details on failure.

        Raises
        ------
        AttestationError
            When the node rejects the attestation (VM detected, bad
            signature, etc.).

        Example::

            result = client.submit_attestation(
                miner_id="my-miner-id",
                fingerprint=my_fingerprint,
                signature="base64_sig_here",
            )
            print(result.enrolled, result.multiplier)
        """
        body = {
            "miner_id": miner_id,
            "fingerprint": fingerprint.to_dict(),
            "signature": signature,
        }
        try:
            data = self._request("POST", "/attest/submit", json=body)
        except RustChainError as exc:
            if isinstance(exc, AttestationError):
                raise
            # Wrap unknown errors in AttestationError for convenience
            raise AttestationError(str(exc)) from exc

        response = AttestationResponse.from_dict(data)

        if not response.success:
            raise AttestationError(
                f"Attestation failed: {response.error or 'unknown'}",
                check_failed=response.check_failed,
                detail=response.detail,
            )

        return response

    # Signed Transfer

    def signed_transfer(
        self,
        from_address: str,
        to_address: str,
        amount_rtc: float,
        nonce: int,
        public_key: str,
        signature: str,
        memo: str = "",
        chain_id: str = "rustchain-mainnet-v2",
    ) -> TransferResponse:
        """
        Transfer RTC to another wallet using an Ed25519 signature.

        Parameters
        ----------
        from_address:
            Sender wallet address (e.g. ``RTCaaa...``).
        to_address:
            Recipient wallet address.
        amount_rtc:
            Amount to transfer in RTC (human-readable, up to 6 decimals).
        nonce:
            Monotonic counter unique per sender. Must be incrementing.
        public_key:
            Hex-encoded Ed25519 public key of the sender.
        signature:
            Hex-encoded Ed25519 signature over the transfer payload.
        memo:
            Optional plaintext note attached to the transfer.
        chain_id:
            Chain identifier. Default: ``rustchain-mainnet-v2``.

        Returns
        -------
        TransferResponse
            Transfer submission result including tx hash and estimated
            confirmation time.

        Raises
        ------
        TransferError
            When the node rejects the transfer (bad signature, insufficient
            balance, etc.).

        Example::

            tx = client.signed_transfer(
                from_address="RTCaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                to_address="RTCbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                amount_rtc=1.0,
                nonce=12345,
                public_key="<hex_pubkey>",
                signature="<hex_signature>",
                memo="payment",
            )
            print(f"Tx hash: {tx.tx_hash}, confirms in {tx.confirms_in_hours}h")
        """
        body = {
            "from_address": from_address,
            "to_address": to_address,
            "amount_rtc": amount_rtc,
            "nonce": nonce,
            "memo": memo,
            "public_key": public_key,
            "signature": signature,
            "chain_id": chain_id,
        }
        data = self._request("POST", "/wallet/transfer/signed", json=body)

        response = TransferResponse.from_dict(data)

        if not response.ok:
            raise TransferError(
                f"Transfer failed: {data.get('error', 'unknown')}",
                tx_hash=response.tx_hash,
                verified=response.verified,
            )

        return response
