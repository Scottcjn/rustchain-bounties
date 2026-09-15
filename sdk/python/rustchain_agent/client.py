"""
Synchronous and Asynchronous client for the RustChain RIP-302 Agent Economy.
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union
import urllib.parse
import urllib.request
import urllib.error

from .exceptions import (
    AgentEconomyError,
    APIError,
    ConnectionError,
    InsufficientEscrowError,
    JobExpiredError,
    JobNotFoundError,
    JobStateError,
    RateLimitExceededError,
    UnauthorizedError,
    ValidationError,
)
from .models import Job, JobCategory, MarketplaceStats, Reputation

logger = logging.getLogger("rustchain_agent.client")

# Optional httpx support for modern async workflows
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def compute_deliverable_hash(content: Union[str, bytes]) -> str:
    """Compute SHA-256 hex digest for a deliverable payload or artifact string."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def calculate_escrow(reward_rtc: float) -> Dict[str, float]:
    """Calculate platform fee (5%) and total required escrow for a given RTC reward."""
    if reward_rtc < 0.01:
        raise ValidationError("Minimum reward is 0.01 RTC")
    if reward_rtc > 10000.0:
        raise ValidationError("Maximum reward is 10,000 RTC")

    reward_i64 = int(reward_rtc * 1_000_000)
    platform_fee_i64 = int(reward_i64 * 0.05)
    escrow_i64 = reward_i64 + platform_fee_i64

    return {
        "reward_rtc": reward_rtc,
        "platform_fee_rtc": platform_fee_i64 / 1_000_000,
        "escrow_total_rtc": escrow_i64 / 1_000_000,
        "platform_fee_rate": "5.0%",
    }


class RustChainAgentClient:
    """
    Synchronous client for interacting with the RustChain Agent-to-Agent Economy.

    Examples:
        >>> client = RustChainAgentClient("https://rustchain.org")
        >>> job = client.post_job(
        ...     poster_wallet="agent_alice",
        ...     title="Research PowerPC benchmarks",
        ...     description="Compile benchmark results for PowerPC 7450 CPU mining efficiency.",
        ...     category="research",
        ...     reward_rtc=5.0
        ... )
        >>> print(job["job_id"])
    """

    DEFAULT_BASE_URL = "https://rustchain.org"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "rustchain-agent-sdk/1.0.0",
        }
        if headers:
            self.headers.update(headers)

    def _handle_error(self, status_code: int, error_data: Dict[str, Any], url: str):
        err_msg = error_data.get("error", f"HTTP {status_code} error from {url}")
        if status_code == 400:
            if "Insufficient balance" in err_msg:
                raise InsufficientEscrowError(err_msg, status_code=status_code, details=error_data)
            raise ValidationError(err_msg, status_code=status_code, details=error_data)
        elif status_code == 403:
            raise UnauthorizedError(err_msg, status_code=status_code, details=error_data)
        elif status_code == 404:
            raise JobNotFoundError(err_msg, status_code=status_code, details=error_data)
        elif status_code == 409:
            raise JobStateError(err_msg, status_code=status_code, details=error_data)
        elif status_code == 410:
            raise JobExpiredError(err_msg, status_code=status_code, details=error_data)
        elif status_code == 429:
            raise RateLimitExceededError(err_msg, status_code=status_code, details=error_data)
        else:
            raise APIError(err_msg, status_code=status_code, details=error_data)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
            if query:
                url = f"{url}?{query}"

        data_bytes = None
        if json_data is not None:
            data_bytes = json.dumps(json_data).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers=self.headers,
            method=method.upper(),
        )

        import ssl
        context = None
        if not self.verify_ssl:
            context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=context) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return {}
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            error_data = {}
            try:
                error_data = json.loads(body)
            except Exception:
                error_data = {"error": body}
            self._handle_error(e.code, error_data, url)
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to connect to {url}: {e.reason}")
        except Exception as e:
            if isinstance(e, AgentEconomyError):
                raise
            raise ConnectionError(f"Request failed: {str(e)}")

    def post_job(
        self,
        poster_wallet: str,
        title: str,
        description: str,
        category: str = "other",
        reward_rtc: float = 0.01,
        ttl_seconds: int = 604800,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new job and lock RTC reward + 5% platform fee into escrow.

        Args:
            poster_wallet: Wallet name or public key of the posting agent.
            title: Concise summary of task (min 5 chars).
            description: Full task requirements and acceptance criteria (min 20 chars).
            category: One of 'research', 'code', 'video', 'audio', 'writing', 'translation', 'data', 'design', 'testing', 'other'.
            reward_rtc: RTC reward paid upon completion (0.01 to 10,000 RTC).
            ttl_seconds: Expiration TTL in seconds (3600 to 2,592,000s / 30 days). Default 7 days.
            tags: Optional string tags for filtering.

        Returns:
            Dict containing job_id, status, escrow details, and expiration.
        """
        validated_category = JobCategory.validate(category)
        if len(title.strip()) < 5:
            raise ValidationError("title must be at least 5 characters")
        if len(description.strip()) < 20:
            raise ValidationError("description must be at least 20 characters")
        if reward_rtc < 0.01 or reward_rtc > 10000.0:
            raise ValidationError("reward_rtc must be between 0.01 and 10,000 RTC")

        payload = {
            "poster_wallet": poster_wallet.strip(),
            "title": title.strip(),
            "description": description.strip(),
            "category": validated_category,
            "reward_rtc": reward_rtc,
            "ttl_seconds": ttl_seconds,
            "tags": tags or [],
        }
        return self._request("POST", "/agent/jobs", json_data=payload)

    def list_jobs(
        self,
        category: Optional[str] = None,
        status: str = "open",
        min_reward: float = 0.0,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Browse and filter jobs in the agent marketplace.

        Args:
            category: Filter by specific category.
            status: Filter by status ('open', 'claimed', 'delivered', 'completed', 'disputed', 'expired', 'cancelled').
            min_reward: Minimum reward threshold in RTC.
            limit: Number of jobs to return (1-100).
            offset: Pagination offset.

        Returns:
            Dict containing list of jobs, total count, limit, offset, and categories.
        """
        params: Dict[str, Any] = {
            "status": status,
            "min_reward": min_reward,
            "limit": limit,
            "offset": offset,
        }
        if category:
            params["category"] = JobCategory.validate(category)

        return self._request("GET", "/agent/jobs", params=params)

    def get_job(self, job_id: str) -> Job:
        """
        Retrieve complete job details including activity audit logs and ratings.

        Args:
            job_id: Unique job identifier.

        Returns:
            Job data model instance.
        """
        resp = self._request("GET", f"/agent/jobs/{urllib.parse.quote(job_id)}")
        if not resp.get("ok") or "job" not in resp:
            raise JobNotFoundError(f"Job '{job_id}' not found")
        return Job.from_dict(resp["job"])

    def claim_job(self, job_id: str, worker_wallet: str) -> Dict[str, Any]:
        """
        Claim an open job as a worker agent.

        Args:
            job_id: Job identifier to claim.
            worker_wallet: Wallet name of the worker agent.

        Returns:
            Dict confirming assignment and deadline.
        """
        if not worker_wallet.strip():
            raise ValidationError("worker_wallet required")
        payload = {"worker_wallet": worker_wallet.strip()}
        return self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/claim", json_data=payload)

    def deliver_job(
        self,
        job_id: str,
        worker_wallet: str,
        deliverable_url: Optional[str] = None,
        deliverable_hash: Optional[str] = None,
        result_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit deliverable artifacts and summary for a claimed job.

        Args:
            job_id: Job identifier.
            worker_wallet: Wallet of the assigned worker.
            deliverable_url: URL to deliverable (PR, repo, document, article, file).
            deliverable_hash: Optional SHA-256 hash of deliverable payload.
            result_summary: Text summary of work completed.

        Returns:
            Dict confirming delivery submission.
        """
        if not worker_wallet.strip():
            raise ValidationError("worker_wallet required")
        if not deliverable_url and not result_summary:
            raise ValidationError("deliverable_url or result_summary required")

        payload = {
            "worker_wallet": worker_wallet.strip(),
            "deliverable_url": deliverable_url.strip() if deliverable_url else "",
            "deliverable_hash": deliverable_hash.strip() if deliverable_hash else "",
            "result_summary": result_summary.strip() if result_summary else "",
        }
        return self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/deliver", json_data=payload)

    def accept_delivery(
        self,
        job_id: str,
        poster_wallet: str,
        rating: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Accept delivery as the poster, releasing escrowed RTC to the worker and 5% fee to platform.

        Args:
            job_id: Job identifier.
            poster_wallet: Wallet of the poster.
            rating: Optional rating from 1 to 5 stars.

        Returns:
            Dict confirming completion and payment release.
        """
        if not poster_wallet.strip():
            raise ValidationError("poster_wallet required")
        if rating is not None and not (1 <= int(rating) <= 5):
            raise ValidationError("rating must be an integer between 1 and 5")

        payload: Dict[str, Any] = {"poster_wallet": poster_wallet.strip()}
        if rating is not None:
            payload["rating"] = int(rating)

        return self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/accept", json_data=payload)

    def dispute_job(
        self,
        job_id: str,
        poster_wallet: str,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Reject a delivery and open a dispute.

        Args:
            job_id: Job identifier.
            poster_wallet: Wallet of the poster.
            reason: Explanation of rejection or missing requirements.

        Returns:
            Dict confirming dispute status.
        """
        if not poster_wallet.strip():
            raise ValidationError("poster_wallet required")
        if not reason.strip():
            raise ValidationError("reason required")

        payload = {
            "poster_wallet": poster_wallet.strip(),
            "reason": reason.strip(),
        }
        return self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/dispute", json_data=payload)

    def cancel_job(
        self,
        job_id: str,
        poster_wallet: str,
    ) -> Dict[str, Any]:
        """
        Cancel an open or disputed job, refunding full escrowed RTC to the poster.

        Args:
            job_id: Job identifier.
            poster_wallet: Wallet of the poster.

        Returns:
            Dict confirming cancellation and refunded escrow amount.
        """
        if not poster_wallet.strip():
            raise ValidationError("poster_wallet required")

        payload = {"poster_wallet": poster_wallet.strip()}
        return self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/cancel", json_data=payload)

    def get_reputation(self, wallet_id: str) -> Reputation:
        """
        Query an agent's on-chain trust score, tier, and job history.

        Args:
            wallet_id: Wallet identifier to inspect.

        Returns:
            Reputation data model.
        """
        resp = self._request("GET", f"/agent/reputation/{urllib.parse.quote(wallet_id)}")
        rep_data = resp.get("reputation")
        if not rep_data:
            return Reputation(wallet_id=wallet_id, trust_score=50, trust_level="neutral")
        return Reputation.from_dict(rep_data)

    def get_stats(self) -> MarketplaceStats:
        """
        Get global marketplace metrics, active agent counts, total volume, and category breakdowns.

        Returns:
            MarketplaceStats data model.
        """
        resp = self._request("GET", "/agent/stats")
        stats_data = resp.get("stats", {})
        return MarketplaceStats.from_dict(stats_data)


class AsyncRustChainAgentClient:
    """
    Asynchronous client for high-throughput autonomous AI agents.
    Requires `httpx`.
    """

    def __init__(
        self,
        base_url: str = RustChainAgentClient.DEFAULT_BASE_URL,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
    ):
        if not HAS_HTTPX:
            raise ImportError(
                "AsyncRustChainAgentClient requires 'httpx'. Install via `pip install httpx`."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "rustchain-agent-sdk-async/1.0.0",
        }
        if headers:
            self.headers.update(headers)
        self._sync_client = RustChainAgentClient(
            base_url=self.base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            headers=self.headers,
        )

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=json_data,
                    headers=self.headers,
                )
                if response.is_error:
                    try:
                        error_data = response.json()
                    except Exception:
                        error_data = {"error": response.text}
                    self._sync_client._handle_error(response.status_code, error_data, url)
                return response.json()
            except httpx.RequestError as e:
                raise ConnectionError(f"Async request failed to {url}: {str(e)}")

    async def post_job(
        self,
        poster_wallet: str,
        title: str,
        description: str,
        category: str = "other",
        reward_rtc: float = 0.01,
        ttl_seconds: int = 604800,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        validated_category = JobCategory.validate(category)
        payload = {
            "poster_wallet": poster_wallet.strip(),
            "title": title.strip(),
            "description": description.strip(),
            "category": validated_category,
            "reward_rtc": reward_rtc,
            "ttl_seconds": ttl_seconds,
            "tags": tags or [],
        }
        return await self._request("POST", "/agent/jobs", json_data=payload)

    async def list_jobs(
        self,
        category: Optional[str] = None,
        status: str = "open",
        min_reward: float = 0.0,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "status": status,
            "min_reward": min_reward,
            "limit": limit,
            "offset": offset,
        }
        if category:
            params["category"] = JobCategory.validate(category)
        return await self._request("GET", "/agent/jobs", params=params)

    async def get_job(self, job_id: str) -> Job:
        resp = await self._request("GET", f"/agent/jobs/{urllib.parse.quote(job_id)}")
        return Job.from_dict(resp["job"])

    async def claim_job(self, job_id: str, worker_wallet: str) -> Dict[str, Any]:
        payload = {"worker_wallet": worker_wallet.strip()}
        return await self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/claim", json_data=payload)

    async def deliver_job(
        self,
        job_id: str,
        worker_wallet: str,
        deliverable_url: Optional[str] = None,
        deliverable_hash: Optional[str] = None,
        result_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "worker_wallet": worker_wallet.strip(),
            "deliverable_url": deliverable_url or "",
            "deliverable_hash": deliverable_hash or "",
            "result_summary": result_summary or "",
        }
        return await self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/deliver", json_data=payload)

    async def accept_delivery(
        self,
        job_id: str,
        poster_wallet: str,
        rating: Optional[int] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"poster_wallet": poster_wallet.strip()}
        if rating is not None:
            payload["rating"] = rating
        return await self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/accept", json_data=payload)

    async def dispute_job(self, job_id: str, poster_wallet: str, reason: str) -> Dict[str, Any]:
        payload = {"poster_wallet": poster_wallet.strip(), "reason": reason.strip()}
        return await self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/dispute", json_data=payload)

    async def cancel_job(self, job_id: str, poster_wallet: str) -> Dict[str, Any]:
        payload = {"poster_wallet": poster_wallet.strip()}
        return await self._request("POST", f"/agent/jobs/{urllib.parse.quote(job_id)}/cancel", json_data=payload)

    async def get_reputation(self, wallet_id: str) -> Reputation:
        resp = await self._request("GET", f"/agent/reputation/{urllib.parse.quote(wallet_id)}")
        rep_data = resp.get("reputation")
        if not rep_data:
            return Reputation(wallet_id=wallet_id, trust_score=50, trust_level="neutral")
        return Reputation.from_dict(rep_data)

    async def get_stats(self) -> MarketplaceStats:
        resp = await self._request("GET", "/agent/stats")
        return MarketplaceStats.from_dict(resp.get("stats", {}))
