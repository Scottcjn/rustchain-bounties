"""
RFC-003: RustChain Foundation Council
=======================================
Governance process for formalizing community governance via an elected council.

This module implements the data models, validation logic, and logging for the
RustChain Foundation Council as described in RFC-003. It is designed for
production use with strong typing, comprehensive error handling, input validation,
and audit logging.
"""

import logging
import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from pydantic import BaseModel, Field, validator, root_validator, ValidationError

# ------------------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------------------
logger = logging.getLogger("rfc003")
logger.setLevel(logging.INFO)

# Avoid adding duplicate handlers if the module is reloaded
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(_handler)

# Optionally add a rotating file handler for persistent logs
# _file_handler = logging.handlers.RotatingFileHandler(
#     "rfc003.log", maxBytes=10**6, backupCount=5
# )
# _file_handler.setFormatter(logging.Formatter(
#     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# ))
# logger.addHandler(_file_handler)

# ------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------
class RFCValidationError(Exception):
    """Base exception for RFC validation failures."""


class MembershipCriteriaError(RFCValidationError):
    """Raised when membership criteria validation fails."""


class CouncilActionError(RFCValidationError):
    """Raised when a council decision action is invalid."""


class AuditError(RFCValidationError):
    """Raised when audit log entry creation fails."""


class CouncilDecisionError(RFCValidationError):
    """Raised when a council decision fails validation or business rules."""


class ConfigurationError(RFCValidationError):
    """Raised when configuration parameters are invalid."""


# ------------------------------------------------------------------
# Constants & Enums
# ------------------------------------------------------------------
MINIMUM_RTC_HOLDING: float = 1000.0
MINIMUM_MERGED_PRS: int = 10
CONTRIBUTION_PERIOD_DAYS: int = 90
MINIMUM_PUBLIC_CONTENT_PIECES: int = 2
PROMOTION_MONTHS: int = 6
TERM_DURATION_DAYS: int = 365
TERM_DURATION_TOLERANCE: int = 10  # ± days
RTC_ADDRESS_REGEX: str = r"^[A-HJ-NP-Za-km-z1-9]{32,44}$"
URL_REGEX: str = r"^https?://[^\s]+$"
MAX_VALIDATION_HISTORY: int = 1000


class DecisionType(Enum):
    """Types of decisions the council can make."""
    CHAIN_DIRECTION = "chain_direction"
    TIER0_ESCALATION = "tier0_escalation"
    BOUNTY_CALIBRATION = "bounty_calibration"
    FEDERATION_PARTNERSHIP = "federation_partnership"
    CONSTITUTIONAL_AMENDMENT = "constitutional_amendment"


class RiskLevel(Enum):
    """Risk level associated with a council decision."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ValidationStatus(Enum):
    """Status of a validation check."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    CORRECTED = "corrected"


class DecisionStatus(Enum):
    """Overall status of a council decision."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    VOTING = "voting"
    PASSED = "passed"
    REJECTED = "rejected"
    ENACTED = "enacted"
    VETOED = "vetoed"
    EXPIRED = "expired"


class VoteOption(Enum):
    """Possible vote choices for council members."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


# ------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------
def validate_rtc_address(address: str) -> bool:
    """
    Validate a RustChain token (RTC) address format.

    Args:
        address: The address string to validate.

    Returns:
        True if the address matches the expected format, False otherwise.

    Security:
        Uses regex to prevent injection via malformed strings.
    """
    if not isinstance(address, str):
        return False
    return bool(re.match(RTC_ADDRESS_REGEX, address))


def validate_url(url: str) -> bool:
    """
    Validate a URL string (http or https only).

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is valid, False otherwise.

    Security:
        Only http/https schemes allowed to reduce risk of file:// etc.
    """
    if not isinstance(url, str):
        return False
    return bool(re.match(URL_REGEX, url))


def sanitize_string_for_log(value: str, max_len: int = 128) -> str:
    """
    Truncate and sanitize a string for safe logging.

    Args:
        value: The input string.
        max_len: Maximum allowed length (default 128).

    Returns:
        A sanitized string safe for logs.
    """
    if not isinstance(value, str):
        return str(value)
    # Remove control characters
    cleaned = re.sub(r'[\x00-\x1f\x7f]', '', value)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "..."
    return cleaned


# ------------------------------------------------------------------
# Data Models
# ------------------------------------------------------------------
class ContributorLadder(BaseModel):
    """Represents contributor tier per RustChain Contributor Ladder.

    Attributes:
        tier: Name of the ladder tier (e.g., "Foreman").
        threshold_prs: Minimum number of merged PRs to reach this tier.
        threshold_cadence: Maximum days between contributions (lower is better).
    """
    tier: str = Field(..., min_length=1, max_length=100)
    threshold_prs: int = Field(..., ge=1, le=10000)
    threshold_cadence: int = Field(..., ge=1, le=365)

    class Config:
        frozen = True
        use_enum_values = False

    def __str__(self) -> str:
        return f"{self.tier} (PRs≥{self.threshold_prs}, cadence≤{self.threshold_cadence}d)"


class ValidationEvent(BaseModel):
    """
    Represents a single validation check event.

    Attributes:
        criterion: Name of the criterion validated.
        passed: Whether validation passed.
        timestamp: When the check occurred.
        details: Additional context (e.g., actual values).
    """
    criterion: str = Field(..., min_length=1, max_length=100)
    passed: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None


class MembershipCriteria(BaseModel):
    """
    All three membership criteria for council seats.
    Validation enforced via lifecycle methods.

    Attributes:
        engineering_contribution_verified: Whether engineering contribution criterion is met.
        rtc_holding_verified: Whether RTC holding criterion is met.
        promotion_verified: Whether public promotion criterion is met.
        last_validation: Timestamp of most recent overall validation attempt.
        validation_log: Ordered list of validation events (max MAX_VALIDATION_HISTORY).
    """
    engineering_contribution_verified: bool = False
    rtc_holding_verified: bool = False
    promotion_verified: bool = False
    last_validation: Optional[datetime] = None
    validation_log: List[ValidationEvent] = Field(default_factory=list)

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    def _add_validation_event(self, criterion: str, passed: bool, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a validation event to the log, trimming older entries if necessary.

        Args:
            criterion: The criterion name.
            passed: Whether validation passed.
            details: Optional context dict.
        """
        if len(self.validation_log) >= MAX_VALIDATION_HISTORY:
            self.validation_log = self.validation_log[-(MAX_VALIDATION_HISTORY - 1):]
        event = ValidationEvent(
            criterion=criterion,
            passed=passed,
            details=details,
        )
        self.validation_log.append(event)

    def validate_engineering_contribution(
        self,
        merged_pr_count: int,
        total_prs: int,
        contribution_period_days: int = CONTRIBUTION_PERIOD_DAYS,
    ) -> bool:
        """
        Validate 'Continue building' criterion.
        Requires Foreman-tier or higher: non-trivial merged PRs with cadence.

        Args:
            merged_pr_count: Number of PRs merged in the observation period.
            total_prs: Total number of PRs submitted in the same period.
            contribution_period_days: Length of observation window in days.

        Returns:
            True if criterion is met, False otherwise.

        Raises:
            MembershipCriteriaError: If inputs are invalid or validation logic fails.

        Security:
            Inputs are validated to be non-negative, non-zero where required.
        """
        # Input validation
        if not isinstance(merged_pr_count, int):
            raise MembershipCriteriaError(
                f"merged_pr_count must be an int, got {type(merged_pr_count).__name__}"
            )
        if not isinstance(total_prs, int):
            raise MembershipCriteriaError(
                f"total_prs must be an int, got {type(total_prs).__name__}"
            )
        if merged_pr_count < 0:
            raise MembershipCriteriaError(
                f"merged_pr_count must be >= 0, got {merged_pr_count}"
            )
        if total_prs <= 0:
            raise MembershipCriteriaError(
                f"total_prs must be > 0, got {total_prs}"
            )
        if contribution_period_days <= 0:
            raise MembershipCriteriaError(
                f"contribution_period_days must be > 0, got {contribution_period_days}"
            )

        try:
            if merged_pr_count < MINIMUM_MERGED_PRS and contribution_period_days > 90:
                logger.warning(
                    "Engineering contribution insufficient: merged_prs=%d, period=%d days",
                    merged_pr_count, contribution_period_days
                )
                self._add_validation_event("engineering_contribution", False, {
                    "merged_pr_count": merged_pr_count,
                    "minimum_required": MINIMUM_MERGED_PRS,
                    "period_days": contribution_period_days
                })
                return False

            ratio = merged_pr_count / max(total_prs, 1)  # total_prs > 0 guaranteed so max is redundant but safe
            if ratio < 0.5:
                logger.warning(
                    "Contribution ratio too low: %.2f (merged=%d, total=%d)",
                    ratio, merged_pr_count, total_prs
                )
                self._add_validation_event("engineering_contribution", False, {
                    "ratio": ratio,
                    "merged_pr_count": merged_pr_count,
                    "total_prs": total_prs
                })
                return False

            self.engineering_contribution_verified = True
            self._add_validation_event("engineering_contribution", True, {
                "merged_pr_count": merged_pr_count,
                "total_prs": total_prs,
                "period_days": contribution_period_days
            })
            return True
        except ZeroDivisionError:
            raise MembershipCriteriaError("Unexpected zero division in ratio calculation")

    def validate_rtc_holding(
        self,
        balance: float,
        minimum_rtc: float = MINIMUM_RTC_HOLDING,
        address_public: Optional[str] = None,
    ) -> bool:
        """
        Validate 'Hold' criterion: minimum RTC held continuously
        in a single publicly associated address.

        Args:
            balance: Current RTC balance of the candidate's nominated address.
            minimum_rtc: Minimum balance required (default 1000.0).
            address_public: Public address of the candidate's wallet.

        Returns:
            True if criterion is met, False otherwise.

        Raises:
            MembershipCriteriaError: If inputs are invalid.

        Security:
            - Balance must be non-negative.
            - If address is provided, it is validated against regex.
            - address_public is sanitized for logging.
        """
        # Input validation
        if not isinstance(balance, (int, float)):
            raise MembershipCriteriaError(
                f"balance must be numeric, got {type(balance).__name__}"
            )
        if balance < 0:
            raise MembershipCriteriaError(
                f"balance must be >= 0, got {balance}"
            )
        if minimum_rtc <= 0:
            raise MembershipCriteriaError(
                f"minimum_rtc must be > 0, got {minimum_rtc}"
            )
        if address_public is not None:
            if not isinstance(address_public, str):
                raise MembershipCriteriaError("address_public must be a string or None")
            if not validate_rtc_address(address_public):
                sanitized = sanitize_string_for_log(address_public, max_len=20)
                raise MembershipCriteriaError(
                    f"Invalid RTC address format: {sanitized}"
                )

        if balance < minimum_rtc:
            logger.warning(
                "RTC holding insufficient: balance=%.4f, minimum=%.4f",
                balance, minimum_rtc
            )
            self._add_validation_event("rtc_holding", False, {
                "balance": balance,
                "minimum_rtc": minimum_rtc,
                "address": address_public
            })
            return False

        self.rtc_holding_verified = True
        self._add_validation_event("rtc_holding", True, {
            "balance": balance,
            "minimum_rtc": minimum_rtc,
            "address": address_public
        })
        return True

    def validate_promotion(
        self,
        content_links: List[str],
        minimum_pieces: int = MINIMUM_PUBLIC_CONTENT_PIECES,
        period_months: int = PROMOTION_MONTHS,
    ) -> bool:
        """
        Validate 'Advertise for the future' criterion:
        at least minimum_pieces pieces of public content published
        within the last period_months.

        Args:
            content_links: List of URLs to public content (blog posts, talks, etc.).
            minimum_pieces: Minimum number of pieces required (default 2).
            period_months: Lookback period in months (default 6).

        Returns:
            True if criterion is met, False otherwise.

        Raises:
            MembershipCriteriaError: If inputs are invalid.
            CouncilActionError: If any URL fails validation.

        Security:
            - Each URL is validated against allowed schemes.
            - List length is checked.
        """
        if not isinstance(content_links, list):
            raise MembershipCriteriaError("content_links must be a list of URL strings")
        if minimum_pieces <= 0:
            raise MembershipCriteriaError(
                f"minimum_pieces must be > 0, got {minimum_pieces}"
            )
        if period_months <= 0:
            raise MembershipCriteriaError(
                f"period_months must be > 0, got {period_months}"
            )

        # Validate each URL
        valid_links = []
        for idx, url in enumerate(content_links):
            if not isinstance(url, str):
                raise CouncilActionError(
                    f"Entry at index {idx} is not a string: {type(url).__name__}"
                )
            if not validate_url(url):
                sanitized = sanitize_string_for_log(url, max_len=64)
                raise CouncilActionError(
                    f"Invalid URL at index {idx}: {sanitized}"
                )
            valid_links.append(url)

        if len(valid_links) < minimum_pieces:
            logger.warning(
                "Promotion criterion not met: %d pieces, required %d",
                len(valid_links), minimum_pieces
            )
            self._add_validation_event("promotion", False, {
                "pieces_provided": len(valid_links),
                "minimum_required": minimum_pieces,
                "period_months": period_months
            })
            return False

        self.promotion_verified = True
        self._add_validation_event("promotion", True, {
            "pieces_provided": len(valid_links),
            "minimum_required": minimum_pieces,
            "period_months": period_months
        })
        return True

    def all_criteria_met(self) -> bool:
        """
        Check whether all three criteria are currently verified.

        Returns:
            True if all criteria verified, False otherwise.
        """
        return (
            self.engineering_contribution_verified
            and self.rtc_holding_verified
            and self.promotion_verified
        )


class CouncilSeat(BaseModel):
    """
    Represents a council seat occupied by a member.

    Attributes:
        seat_id: Unique identifier for this seat.
        member_name: Name or pseudonym of the council member.
        member_address: Public RTC address associated with the member.
        membership_criteria: MembershipCriteria instance with validation status.
        term_start: Start date of the term.
        term_end: End date of the term (typically one year).
        active: Whether the seat is currently active.
    """
    seat_id: str = Field(default_factory=lambda: f"seat-{uuid4().hex[:12]}")
    member_name: str = Field(..., min_length=1, max_length=200)
    member_address: str = Field(...)
    membership_criteria: MembershipCriteria = Field(default_factory=MembershipCriteria)
    term_start: datetime = Field(default_factory=datetime.utcnow)
    term_end: Optional[datetime] = None
    active: bool = True

    # Validators
    @validator("member_address")
    def validate_member_address(cls, value: str) -> str:
        if not validate_rtc_address(value):
            sanitized = sanitize_string_for_log(value, max_len=20)
            raise ValueError(f"Invalid RTC address: {sanitized}")
        return value

    @validator("term_end")
    def validate_term_end(cls, value: Optional[datetime], values: Dict[str, Any]) -> Optional[datetime]:
        if value is not None:
            term_start = values.get("term_start")
            if term_start and value <= term_start:
                raise ValueError("term_end must be after term_start")
            # Check duration tolerance
            expected_duration = timedelta(days=TERM_DURATION_DAYS)
            actual_duration = value - term_start
            if abs(actual_duration - expected_duration) > timedelta(days=TERM_DURATION_TOLERANCE):
                logger.warning(
                    "Term duration %s deviates from expected %s by more than tolerance.",
                    actual_duration, expected_duration
                )
        return value

    def __str__(self) -> str:
        status = "active" if self.active else "inactive"
        return f"CouncilSeat({self.seat_id}, {self.member_name}, {status})"


class CouncilDecision(BaseModel):
    """
    Represents a decision made by the council or in progress.

    Attributes:
        decision_id: Unique ID.
        decision_type: Type of decision.
        title: Short title.
        description: Detailed description.
        proposer: Name / address of the proposer.
        risk_level: Assessed risk level.
        status: Current lifecycle status.
        votes: Mapping of member_ids to VoteOption.
        created_at: Creation timestamp.
        voting_deadline: Deadline for voting.
        enacted_at: When decision was enacted (if applicable).
        rejection_reason: Reason if rejected or vetoed.
        metadata: Additional arbitrary data.
    """
    decision_id: str = Field(default_factory=lambda: f"dec-{uuid4().hex[:12]}")
    decision_type: DecisionType
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    proposer: str = Field(..., min_length=1, max_length=200)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    status: DecisionStatus = DecisionStatus.DRAFT
    votes: Dict[str, VoteOption] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    voting_deadline: Optional[datetime] = None
    enacted_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = False

    def __str__(self) -> str:
        return f"CouncilDecision({self.decision_id}, {self.decision_type.value}, {self.status.value})"

    def add_vote(self, member_id: str, vote: VoteOption) -> None:
        """
        Record a vote from a council member.

        Args:
            member_id: Unique identifier of the council member.
            vote: The vote option (APPROVE, REJECT, ABSTAIN).

        Raises:
            CouncilDecisionError: If decision is not in VOTING status or vote already recorded.
        """
        if self.status != DecisionStatus.VOTING:
            raise CouncilDecisionError(f"Cannot vote: decision status is {self.status.value}")
        if member_id in self.votes:
            raise CouncilDecisionError(f"Member {member_id} has already voted")
        self.votes[member_id] = vote
        logger.info("Vote recorded: member=%s, decision=%s, vote=%s", member_id, self.decision_id, vote.value)

    def tally_votes(self, required_approval_ratio: float = 0.6) -> bool:
        """
        Tally current votes and return whether the decision passes.

        Args:
            required_approval_ratio: Fraction of non-abstaining votes needed for approval (default 0.6).

        Returns:
            True if approval threshold met, False otherwise.
        """
        if not self.votes:
            return False
        approves = sum(1 for v in self.votes.values() if v == VoteOption.APPROVE)
        rejects = sum(1 for v in self.votes.values() if v == VoteOption.REJECT)
        total_exprimesed = approves + rejects
        if total_exprimesed == 0:
            return False
        return (approves / total_exprimesed) >= required_approval_ratio

    def pass_decision(self) -> None:
        """Mark decision as passed after successful vote."""
        if self.status != DecisionStatus.VOTING:
            raise CouncilDecisionError(f"Cannot pass: current status is {self.status.value}")
        self.status = DecisionStatus.PASSED
        logger.info("Decision %s passed.", self.decision_id)

    def reject_decision(self, reason: str) -> None:
        """Reject the decision with a reason."""
        if self.status not in (DecisionStatus.PROPOSED, DecisionStatus.VOTING):
            raise CouncilDecisionError(f"Cannot reject: current status is {self.status.value}")
        self.status = DecisionStatus.REJECTED
        self.rejection_reason = reason
        logger.warning("Decision %s rejected: %s", self.decision_id, reason)

    def enact_decision(self) -> None:
        """Enact a passed decision."""
        if self.status != DecisionStatus.PASSED:
            raise CouncilDecisionError(f"Cannot enact: current status is {self.status.value}")
        self.status = DecisionStatus.ENACTED
        self.enacted_at = datetime.utcnow()
        logger.info("Decision %s enacted at %s", self.decision_id, self.enacted_at)


class AuditEntry(BaseModel):
    """
    Immutable audit log entry for council actions.

    Attributes:
        entry_id: Unique entry ID.
        timestamp: When the action occurred.
        actor: Identifier of the entity that performed the action.
        action: Description of the action.
        resource_type: Type of resource affected (e.g., "seat", "decision").
        resource_id: ID of the affected resource.
        details: Additional context.
    """
    entry_id: str = Field(default_factory=lambda: f"audit-{uuid4().hex[:12]}")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str = Field(..., min_length=1, max_length=200)
    action: str = Field(..., min_length=1, max_length=500)
    resource_type: str = Field(..., min_length=1, max_length=100)
    resource_id: str = Field(..., min_length=1, max_length=200)
    details: Optional[Dict[str, Any]] = None

    class Config:
        frozen = True  # Audit entries should not be modified

    def __str__(self) -> str:
        return f"AuditEntry({self.entry_id}, {self.action}, {self.resource_type}:{self.resource_id})"


# ------------------------------------------------------------------
# Audit Logger
# ------------------------------------------------------------------
class AuditLogger:
    """
    Simple audit logger that writes entries to the logging system and stores in memory.
    Could be extended to write to a database or blockchain.
    """

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    def log(self, actor: str, action: str, resource_type: str, resource_id: str,
            details: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """
        Create a new audit entry and log it.

        Args:
            actor: Who performed the action.
            action: What was done.
            resource_type: Type of resource.
            resource_id: Resource identifier.
            details: Optional context.

        Returns:
            The created AuditEntry.

        Raises:
            AuditError: If creation fails.
        """
        try:
            entry = AuditEntry(
                actor=actor,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
            )
            self._entries.append(entry)
            logger.info("AUDIT: %s performed %s on %s/%s", actor, action, resource_type, resource_id)
            return entry
        except ValidationError as e:
            raise AuditError(f"Failed to create audit entry: {e}") from e

    def get_entries(self, resource_type: Optional[str] = None,
                    resource_id: Optional[str] = None) -> List[AuditEntry]:
        """
        Retrieve audit entries, optionally filtered.

        Args:
            resource_type: Filter by resource type.
            resource_id: Filter by resource ID.

        Returns:
            List of matching AuditEntry objects.
        """
        entries = self._entries
        if resource_type:
            entries = [e for e in entries if e.resource_type == resource_type]
        if resource_id:
            entries = [e for e in entries if e.resource_id == resource_id]
        return entries


# ------------------------------------------------------------------
# Global instances (optional, could be injected via dependency injection)
# ------------------------------------------------------------------
_default_audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Return the default audit logger instance."""
    return _default_audit_logger


# ------------------------------------------------------------------
# Performance optimization: Example of a cached validator result
# ------------------------------------------------------------------
class _CachedValidation:
    """Simple in-memory cache for expensive validation results (not persisted)."""
    def __init__(self) -> None:
        self._cache: Dict[str, bool] = {}

    def get(self, key: str) -> Optional[bool]:
        return self._cache.get(key)

    def set(self, key: str, value: bool) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


# ------------------------------------------------------------------
# Example configuration placeholder (to be loaded from env or config file)
# ------------------------------------------------------------------
class RFC003Config(BaseModel):
    """
    Configuration for RFC-003 module parameters.
    Allows overriding defaults via environment variables or config files.
    """
    minimum_rtc_holding: float = Field(default=MINIMUM_RTC_HOLDING, ge=0)
    minimum_merged_prs: int = Field(default=MINIMUM_MERGED_PRS, ge=0)
    contribution_period_days: int = Field(default=CONTRIBUTION_PERIOD_DAYS, ge=1)
    minimum_public_content_pieces: int = Field(default=MINIMUM_PUBLIC_CONTENT_PIECES, ge=1)
    promotion_months: int = Field(default=PROMOTION_MONTHS, ge=1)
    term_duration_days: int = Field(default=TERM_DURATION_DAYS, ge=1)
    term_duration_tolerance_days: int = Field(default=TERM_DURATION_TOLERANCE, ge=0)
    required_approval_ratio: float = Field(default=0.6, ge=0.0, le=1.0)
    max_validation_history: int = Field(default=MAX_VALIDATION_HISTORY, ge=1)


# Load configuration (could be from environment)
def load_rfc003_config() -> RFC003Config:
    """
    Load RFC003 configuration. Currently returns defaults.
    Future: read from environment variables or a config service.
    """
    # TODO: integrate with config system
    return RFC003Config()


# ------------------------------------------------------------------
# End of module
# ------------------------------------------------------------------