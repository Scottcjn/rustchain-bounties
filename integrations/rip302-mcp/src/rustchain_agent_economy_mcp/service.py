from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

from rustchain_agent_economy import (
    DEFAULT_BASE_URL,
    AgentEconomyClient,
    Ed25519Signer,
)


class McpConfigurationError(RuntimeError):
    """Raised when a mutating MCP tool needs missing process configuration."""


def _env_bool(value: str | None, *, default: bool = True) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise McpConfigurationError(
        "RUSTCHAIN_VERIFY_TLS must be one of 1/0, true/false, yes/no, on/off"
    )


@dataclass(frozen=True)
class RuntimeConfig:
    base_url: str = DEFAULT_BASE_URL
    verify_tls: bool = True
    ca_file: str | None = None
    poster_private_key_hex: str | None = None
    worker_wallet: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "RuntimeConfig":
        source = os.environ if env is None else env
        base_url = source.get("RUSTCHAIN_NODE_URL", DEFAULT_BASE_URL).strip()
        if not base_url:
            raise McpConfigurationError("RUSTCHAIN_NODE_URL cannot be empty")
        private_key = source.get("RUSTCHAIN_POSTER_PRIVATE_KEY")
        if private_key is not None:
            private_key = private_key.strip() or None
        worker = source.get("RUSTCHAIN_WORKER_WALLET")
        if worker is not None:
            worker = worker.strip() or None
        ca_file = source.get("RUSTCHAIN_CA_FILE")
        if ca_file is not None:
            ca_file = ca_file.strip() or None
        return cls(
            base_url=base_url.rstrip("/"),
            verify_tls=_env_bool(source.get("RUSTCHAIN_VERIFY_TLS"), default=True),
            ca_file=ca_file,
            poster_private_key_hex=private_key,
            worker_wallet=worker,
        )


class AgentEconomyMcpService:
    """Tool-facing service with secrets kept outside MCP tool arguments."""

    def __init__(
        self,
        *,
        config: RuntimeConfig | None = None,
        client: AgentEconomyClient | None = None,
        signer: Ed25519Signer | None = None,
    ):
        self.config = config or RuntimeConfig.from_env()
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
        """Return non-secret runtime capability state."""
        return {
            "base_url": self.config.base_url,
            "verify_tls": self.config.verify_tls,
            "signed_posting_enabled": self.signer is not None,
            "poster_wallet": self.signer.rtc_address if self.signer else None,
            "default_worker_wallet": self.config.worker_wallet,
        }

    def list_jobs(
        self,
        *,
        status: str = "open",
        category: str | None = None,
        min_reward: float = 0,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        return self.client.list_jobs(
            status=status,
            category=category,
            min_reward=min_reward,
            limit=limit,
            offset=offset,
        )

    def get_job(self, job_id: str) -> dict[str, Any]:
        return self.client.get_job(job_id)

    def post_job(
        self,
        *,
        title: str,
        description: str,
        reward_rtc: float,
        category: str = "other",
        ttl_seconds: int = 604800,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        if self.signer is None:
            raise McpConfigurationError(
                "Signed posting is disabled. Set RUSTCHAIN_POSTER_PRIVATE_KEY "
                "in the MCP process environment; private keys are never accepted "
                "as tool arguments."
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
        worker = (worker_wallet or self.config.worker_wallet or "").strip()
        if not worker:
            raise McpConfigurationError(
                "worker_wallet is required unless RUSTCHAIN_WORKER_WALLET is set"
            )
        return worker

    def claim_job(
        self,
        job_id: str,
        *,
        worker_wallet: str | None = None,
    ) -> dict[str, Any]:
        return self.client.claim_job(job_id, self._worker(worker_wallet))

    def deliver_job(
        self,
        job_id: str,
        *,
        worker_wallet: str | None = None,
        deliverable_url: str | None = None,
        deliverable_hash: str | None = None,
        result_summary: str | None = None,
    ) -> dict[str, Any]:
        return self.client.deliver_job(
            job_id,
            worker_wallet=self._worker(worker_wallet),
            deliverable_url=deliverable_url,
            deliverable_hash=deliverable_hash,
            result_summary=result_summary,
        )

    def get_reputation(self, wallet_id: str) -> dict[str, Any]:
        return self.client.get_reputation(wallet_id)

    def get_stats(self) -> dict[str, Any]:
        return self.client.get_stats()
