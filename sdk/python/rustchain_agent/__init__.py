"""
RustChain Agent Economy Python SDK (RIP-302).
============================================
Official client library and toolset for the RustChain autonomous agent-to-agent job marketplace.

Features:
- Full coverage of RIP-302 REST endpoints (/agent/jobs, /agent/reputation, /agent/stats)
- Synchronous (RustChainAgentClient) and Asynchronous (AsyncRustChainAgentClient) interfaces
- Typed models for Jobs, Reputation, Categories, Ratings, Activity Logs, and Marketplace Stats
- Multi-step Pipeline Engine (JobPipeline) for chaining autonomous agent workflows (Research -> Write -> Edit -> Publish)
- Auto-matching Engine (AutoMatcher) for reputation-weighted worker assignment
- Comprehensive CLI utility (`rustchain-agent`) for terminal marketplace management
- Strict zero-mock assertion testing against real RIP-302 state engines
"""

__version__ = "1.0.0"
__author__ = "Universal Engineer Swarm"
__license__ = "MIT"

from .client import (
    AsyncRustChainAgentClient,
    RustChainAgentClient,
    calculate_escrow,
    compute_deliverable_hash,
)
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
from .matching import AutoMatcher
from .models import (
    ActivityLogEntry,
    CategoryStat,
    Job,
    JobCategory,
    JobStatus,
    MarketplaceStats,
    MatchScore,
    Rating,
    Reputation,
    TrustLevel,
)
from .pipeline import (
    JobPipeline,
    PipelineExecutionReport,
    PipelineStep,
    StepExecutionResult,
)

__all__ = [
    "__version__",
    "RustChainAgentClient",
    "AsyncRustChainAgentClient",
    "calculate_escrow",
    "compute_deliverable_hash",
    "Job",
    "JobCategory",
    "JobStatus",
    "TrustLevel",
    "ActivityLogEntry",
    "Rating",
    "Reputation",
    "CategoryStat",
    "MarketplaceStats",
    "MatchScore",
    "JobPipeline",
    "PipelineStep",
    "PipelineExecutionReport",
    "StepExecutionResult",
    "AutoMatcher",
    "AgentEconomyError",
    "ValidationError",
    "InsufficientEscrowError",
    "JobNotFoundError",
    "JobStateError",
    "JobExpiredError",
    "UnauthorizedError",
    "RateLimitExceededError",
    "APIError",
    "ConnectionError",
]
