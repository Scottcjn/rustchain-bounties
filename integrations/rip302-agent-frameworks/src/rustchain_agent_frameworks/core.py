from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping

from rustchain_agent_economy import DEFAULT_BASE_URL, AgentEconomyClient, Ed25519Signer


class ToolkitConfigurationError(RuntimeError):
    """Raised when a mutating tool needs missing process configuration."""


def _env_bool(value: str | None, *, default: bool = True) -> bool:
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise ToolkitConfigurationError(
        "RUSTCHAIN_VERIFY_TLS must be one of 1/0, true/false, yes/no, on/off"
    )


@dataclass(frozen=True)
class ToolkitConfig:
    base_url: str = DEFAULT_BASE_URL
    verify_tls: bool = True
    ca_file: str | None = None
    poster_private_key_hex: str | None = field(default=None, repr=False)
    worker_wallet: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ToolkitConfig":
        source = os.environ if env is None else env
        base_url = source.get("RUSTCHAIN_NODE_URL", DEFAULT_BASE_URL).strip()
        if not base_url:
            raise ToolkitConfigurationError("RUSTCHAIN_NODE_URL cannot be empty")
        private_key = source.get("RUSTCHAIN_POSTER_PRIVATE_KEY")
        worker = source.get("RUSTCHAIN_WORKER_WALLET")
        ca_file = source.get("RUSTCHAIN_CA_FILE")
        return cls(
            base_url=base_url.rstrip("/"),
            verify_tls=_env_bool(source.get("RUSTCHAIN_VERIFY_TLS"), default=True),
            ca_file=ca_file.strip() if ca_file and ca_file.strip() else None,
            poster_private_key_hex=(
                private_key.strip() if private_key and private_key.strip() else None
            ),
            worker_wallet=worker.strip() if worker and worker.strip() else None,
        )


class AgentEconomyToolkit:
    """Framework-neutral RIP-302 operations used by LangChain and CrewAI adapters."""

    def __init__(
        self,
        *,
        config: ToolkitConfig | None = None,
        client: AgentEconomyClient | None = None,
        signer: Ed25519Signer | None = None,
    ):
        self.config = config or ToolkitConfig.from_env()
        self.client = client or AgentEconomyClient(
            self.config.base_url,
            verify_tls=self.config.verify_tls,
            ca_file=self.config.ca_file,
        )
        if signer is not None:
            self.signer = signer
        elif self.config.poster_private_key_hex:
            self.signer = Ed25519Signer.from_private_key_hex(
                self.config.poster_private_key_hex
            )
        else:
            self.signer = None

    def status(self) -> dict[str, Any]:
        """Show non-secret RustChain Agent Economy connection/signing state."""
        return {
            "base_url": self.config.base_url,
            "verify_tls": self.config.verify_tls,
            "signed_posting_enabled": self.signer is not None,
            "poster_wallet": self.signer.rtc_address if self.signer else None,
            "default_worker_wallet": self.config.worker_wallet,
        }

    def list_jobs(
        self,
        status: str = "open",
        category: str | None = None,
        min_reward: float = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Browse RIP-302 jobs by status, category, reward and pagination."""
        return self.client.list_jobs(
            status=status,
            category=category,
            min_reward=min_reward,
            limit=limit,
            offset=offset,
        )

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Get one RIP-302 job including its activity log and ratings."""
        return self.client.get_job(job_id)

    def post_job(
        self,
        title: str,
        description: str,
        reward_rtc: float,
        category: str = "other",
        ttl_seconds: int = 604800,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Post a signed job using the process-configured RTC identity."""
        if self.signer is None:
            raise ToolkitConfigurationError(
                "Signed posting is disabled. Set RUSTCHAIN_POSTER_PRIVATE_KEY in "
                "the agent process environment; private keys are never tool inputs."
            )
        return self.client.post_job(
            poster_wallet=self.signer.rtc_address,
            title=title,
            description=description,
            reward_rtc=reward_rtc,
            category=category,
            ttl_seconds=ttl_seconds,
            tags=tags,
            signer=self.signer,
        )

    def _worker(self, worker_wallet: str | None) -> str:
        worker = self.config.worker_wallet if worker_wallet is None else worker_wallet
        if not isinstance(worker, str) or not worker.strip():
            raise ToolkitConfigurationError(
                "worker_wallet must be a non-empty string, or omitted when "
                "RUSTCHAIN_WORKER_WALLET is set"
            )
        return worker.strip()

    def claim_job(
        self,
        job_id: str,
        worker_wallet: str | None = None,
    ) -> dict[str, Any]:
        """Claim an open job with an explicit or process-default worker wallet."""
        return self.client.claim_job(job_id, self._worker(worker_wallet))

    def deliver_job(
        self,
        job_id: str,
        worker_wallet: str | None = None,
        deliverable_url: str | None = None,
        deliverable_hash: str | None = None,
        result_summary: str | None = None,
    ) -> dict[str, Any]:
        """Deliver or redeliver work for the assigned worker."""
        return self.client.deliver_job(
            job_id,
            worker_wallet=self._worker(worker_wallet),
            deliverable_url=deliverable_url,
            deliverable_hash=deliverable_hash,
            result_summary=result_summary,
        )

    def get_reputation(self, wallet_id: str) -> dict[str, Any]:
        """Read RIP-302 reputation for a wallet or agent id."""
        return self.client.get_reputation(wallet_id)

    def get_marketplace_stats(self) -> dict[str, Any]:
        """Read aggregate Agent Economy marketplace statistics."""
        return self.client.get_stats()
