"""
RFC: RustChain Foundation Council Proposal
Status: Draft
Authors: RustChain Community
Created: 2026-05-30
Updated: 2026-05-30
License: MIT

Abstract
--------
This module implements the governance council for RustChain as proposed in RFC-xxx.
It provides a production‑ready, type‑safe, logged, and validated implementation
of the council structure, election process, voting, treasury management, and
emergency procedures.

Requirements
------------
- Python 3.11+
- No external dependencies (standard library only)

Usage
-----
    from rustchain_council import Council, CouncilMember, VoteCategory

    council = Council()
    council.initialize()
    members = council.get_active_members()
    result = council.cast_vote(...)
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_DOWN
from enum import Enum
from threading import RLock, Lock
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    final,
)

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
_logger = logging.getLogger("rustchain.council")
_handler = logging.StreamHandler()
_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
)
if not _logger.handlers:
    _logger.addHandler(_handler)
_logger.setLevel(logging.INFO)  # Default INFO; DEBUG for development

# ---------------------------------------------------------------------------
# Custom exceptions (all inherit from CouncilError)
# ---------------------------------------------------------------------------


class CouncilError(Exception):
    """Base exception for all council operations."""


class EligibilityError(CouncilError):
    """Raised when a candidate does not meet membership criteria."""


class VotingError(CouncilError):
    """Raised for invalid voting operations."""


class TreasuryError(CouncilError):
    """Raised for treasury/compensation issues."""


class EmergencyActionError(CouncilError):
    """Raised for improper emergency procedures."""


class QuorumError(CouncilError):
    """Raised when quorum is not met."""


class ProposalError(CouncilError):
    """Raised for invalid proposal operations."""


class ValidationError(CouncilError):
    """Raised for data validation failures."""


class ElectionError(CouncilError):
    """Raised for election process errors."""


# ---------------------------------------------------------------------------
# Constants and Enums
# ---------------------------------------------------------------------------

DEFAULT_SEATS: int = 5
"""Default number of council seats."""

TERM_MONTHS: int = 12
"""Duration of a single term in months."""

MAX_CONSECUTIVE_TERMS: int = 2
"""Maximum number of consecutive terms a member can serve."""

MIN_RTC_HELD: Decimal = Decimal("1000.0")
"""Minimum RTC tokens a candidate must hold continuously."""

EMERGENCY_THRESHOLD: int = 3
"""Number of yes votes required for emergency action (out of typical 5)."""

EMERGENCY_RATIFICATION_DAYS: int = 7
"""Days for community ratification of emergency actions."""

POSTMORTEM_DAYS: int = 14
"""Days allowed to produce a postmortem after emergency."""

MIN_SEATS: int = 3
"""Minimum number of seats for the council to be operational."""

MAX_PROPOSALS_PER_MEMBER: int = 5
"""Maximum active proposals a member can have at once."""

MIN_ATTENDANCE_LOG_ENTRIES: int = 1
"""Minimum attendance records required for term renewal."""

SECONDS_PER_MONTH: float = 2_592_000.0
"""Seconds in a 30‑day month."""

WALLET_PATTERN: re.Pattern = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")
"""Regex for valid Solana‑style base58 wallet addresses."""

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class VoteCategory(Enum):
    """Categories a council member can vote on a proposal."""

    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"

    def __str__(self) -> str:
        return self.value


class ProposalStatus(Enum):
    """Current status of a proposal in the lifecycle."""

    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EMERGENCY = "emergency"
    RATIFIED = "ratified"
    EXPIRED = "expired"

    def __str__(self) -> str:
        return self.value


class SeatStatus(Enum):
    """Occupancy status of a council seat."""

    ACTIVE = "active"
    VACANT = "vacant"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _validate_wallet(address: str) -> None:
    """Validate a wallet address against known pattern.

    Args:
        address: Wallet address string.

    Raises:
        ValidationError: If the address is invalid.
    """
    if not isinstance(address, str) or not WALLET_PATTERN.fullmatch(address):
        raise ValidationError(f"Invalid wallet address: {address!r}")


def _validate_positive_decimal(value: object, name: str = "value") -> Decimal:
    """Convert and validate a positive Decimal.

    Args:
        value: Input to convert.
        name: Name for error messages.

    Returns:
        Decimal representation.

    Raises:
        ValidationError: If conversion fails or value is negative.
    """
    try:
        d = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(f"{name} must be convertible to Decimal") from exc
    if d < Decimal("0"):
        raise ValidationError(f"{name} must be non-negative")
    return d


def _validate_non_negative_int(value: object, name: str = "value") -> int:
    """Validate a non‑negative integer.

    Args:
        value: Input to check.
        name: Name for error messages.

    Returns:
        The integer value.

    Raises:
        ValidationError: If value is not a non‑negative integer.
    """
    if not isinstance(value, int) or value < 0:
        raise ValidationError(
            f"{name} must be a non‑negative integer, got {type(value).__name__}"
        )
    return value


def _validate_instance(value: object, expected_type: type[T], name: str = "value") -> T:
    """Validate that a value is an instance of a given type.

    Args:
        value: Object to validate.
        expected_type: Expected type.
        name: Name for error messages.

    Returns:
        The validated value cast to the expected type.

    Raises:
        ValidationError: If type check fails.
    """
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{name} must be of type {expected_type.__name__}, got {type(value).__name__}"
        )
    return value


def _validate_string_not_empty(value: object, name: str = "value") -> str:
    """Validate a non‑empty string.

    Args:
        value: Input to check.
        name: Name for error messages.

    Returns:
        The validated string.

    Raises:
        ValidationError: If value is not a non‑empty string.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non‑empty string")
    return value.strip()


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContributionRecord:
    """Immutable record of a contributor's engineering activity.

    Attributes:
        merged_prs: Number of merged pull requests.
        non_trivial_ratio: Fraction of PRs considered non-trivial (0.0–1.0).
        cadence: Average number of PRs per month.
    """

    merged_prs: int
    non_trivial_ratio: float
    cadence: float

    def __post_init__(self) -> None:
        """Validate field ranges after initialization."""
        _validate_non_negative_int(self.merged_prs, "merged_prs")
        if not 0.0 <= self.non_trivial_ratio <= 1.0:
            raise ValidationError("non_trivial_ratio must be in [0.0, 1.0]")
        if self.cadence < 0.0:
            raise ValidationError("cadence must be non-negative")

    def meets_foreman_threshold(self) -> bool:
        """Check if contributor meets Foreman‑tier requirements.

        Returns:
            True if merged PRs >= 10, non_trivial_ratio >= 0.5, cadence >= 1.0.
        """
        return (
            self.merged_prs >= 10
            and self.non_trivial_ratio >= 0.5
            and self.cadence >= 1.0
        )


@dataclass(frozen=True)
class AdvocacyRecord:
    """Immutable record of public advocacy contributions.

    Attributes:
        blog_posts: Number of blog posts written.
        tutorials: Number of tutorials created.
        conference_talks: Number of conference talks given.
    """

    blog_posts: int = 0
    tutorials: int = 0
    conference_talks: int = 0

    def __post_init__(self) -> None:
        """Validate all fields are non‑negative."""
        _validate_non_negative_int(self.blog_posts, "blog_posts")
        _validate_non_negative_int(self.tutorials, "tutorials")
        _validate_non_negative_int(self.conference_talks, "conference_talks")

    @property
    def total_engagements(self) -> int:
        """Total number of advocacy activities."""
        return self.blog_posts + self.tutorials + self.conference_talks


@dataclass(frozen=True)
class AttendenceRecord:
    """Immutable record of meeting attendance.

    Attributes:
        meeting_id: Unique meeting identifier.
        timestamp: When the meeting occurred.
        present: Whether the member attended.
    """

    meeting_id: str
    timestamp: datetime
    present: bool

    def __post_init__(self) -> None:
        """Validate fields."""
        _validate_string_not_empty(self.meeting_id, "meeting_id")
        if not isinstance(self.timestamp, datetime):
            raise ValidationError("timestamp must be a datetime object")


class CouncilMember:
    """Mutable representation of a council member with thread‑safe state."""

    __slots__ = (
        "_lock",
        "_wallet",
        "_name",
        "_rtc_held",
        "_contribution",
        "_advocacy",
        "_seat_index",
        "_term_start",
        "_term_end",
        "_consecutive_terms",
        "_is_active",
        "_attendance_log",
        "_proposals_active",
    )

    def __init__(
        self,
        wallet: str,
        name: str,
        rtc_held: Decimal,
        contribution: ContributionRecord,
        advocacy: AdvocacyRecord,
        seat_index: Optional[int] = None,
    ) -> None:
        """Initialize a council member.

        Args:
            wallet: Wallet address (base58).
            name: Display name.
            rtc_held: Current RTC token balance.
            contribution: Engineering contribution record.
            advocacy: Public advocacy record.
            seat_index: Assigned seat index (if already seated).

        Raises:
            ValidationError: If any input is invalid.
        """
        _validate_wallet(wallet)
        _validate_string_not_empty(name, "name")
        _validate_instance(contribution, ContributionRecord, "contribution")
        _validate_instance(advocacy, AdvocacyRecord, "advocacy")

        self._lock = RLock()
        self._wallet = wallet
        self._name = name
        self._rtc_held = _validate_positive_decimal(rtc_held, "rtc_held")
        self._contribution = contribution
        self._advocacy = advocacy
        self._seat_index = seat_index
        self._term_start: Optional[datetime] = None
        self._term_end: Optional[datetime] = None
        self._consecutive_terms = 0
        self._is_active = False
        self._attendance_log: List[AttendenceRecord] = []
        self._proposals_active: Set[str] = set()

        _logger.debug("CouncilMember created: %s (wallet=%s)", self._name, self._wallet[:8])

    # --- Properties with thread safety ---
    @property
    def wallet(self) -> str:
        return self._wallet

    @property
    def name(self) -> str:
        return self._name

    @property
    def rtc_held(self) -> Decimal:
        with self._lock:
            return self._rtc_held

    @rtc_held.setter
    def rtc_held(self, value: Decimal) -> None:
        with self._lock:
            self._rtc_held = _validate_positive_decimal(value, "rtc_held")

    @property
    def contribution(self) -> ContributionRecord:
        return self._contribution

    @property
    def advocacy(self) -> AdvocacyRecord:
        return self._advocacy

    @property
    def seat_index(self) -> Optional[int]:
        with self._lock:
            return self._seat_index

    @seat_index.setter
    def seat_index(self, value: Optional[int]) -> None:
        with self._lock:
            if value is not None and value < 0:
                raise ValidationError("seat_index must be non‑negative")
            self._seat_index = value

    @property
    def term_start(self) -> Optional[datetime]:
        with self._lock:
            return self._term_start

    @property
    def term_end(self) -> Optional[datetime]:
        with self._lock:
            return self._term_end

    @property
    def consecutive_terms(self) -> int:
        with self._lock:
            return self._consecutive_terms

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._is_active

    @property
    def attendance_log(self) -> List[AttendenceRecord]:
        with self._lock:
            return list(self._attendance_log)

    @property
    def proposals_active(self) -> FrozenSet[str]:
        with self._lock:
            return frozenset(self._proposals_active)

    # --- Mutators ---
    def increment_consecutive_terms(self) -> None:
        """Increase consecutive term count by one."""
        with self._lock:
            self._consecutive_terms += 1
            _logger.debug(
                "%s consecutive terms now %d", self._name, self._consecutive_terms
            )

    def reset_consecutive_terms(self) -> None:
        """Reset consecutive term counter (e.g., after a break)."""
        with self._lock:
            self._consecutive_terms = 0

    def activate_term(self, start: datetime, end: datetime) -> None:
        """Activate member for a new term.

        Args:
            start: Term start datetime.
            end: Term end datetime.

        Raises:
            ValidationError: If start >= end or member already active.
        """
        with self._lock:
            if self._is_active:
                raise ValidationError(f"{self._name} is already active")
            if not isinstance(start, datetime) or not isinstance(end, datetime):
                raise ValidationError("start and end must be datetimes")
            if start >= end:
                raise ValidationError("start must be before end")
            self._term_start = start
            self._term_end = end
            self._is_active = True
            _logger.info(
                "Term activated for %s: %s to %s",
                self._name,
                start.isoformat(),
                end.isoformat(),
            )

    def deactivate(self) -> None:
        """Deactivate member (term ended or expelled)."""
        with self._lock:
            self._is_active = False
            self._term_start = None
            self._term_end = None
            self._attendance_log.clear()
            _logger.info("%s deactivated", self._name)

    def add_attendance(self, record: AttendenceRecord) -> None:
        """Record meeting attendance.

        Args:
            record: Attendance record to append.
        """
        _validate_instance(record, AttendenceRecord, "record")
        with self._lock:
            self._attendance_log.append(record)
            _logger.debug(
                "Attendance recorded for %s at meeting %s",
                self._name,
                record.meeting_id,
            )

    def add_proposal(self, proposal_id: str) -> None:
        """Associate a proposal with this member.

        Args:
            proposal_id: Unique proposal identifier.

        Raises:
            ProposalError: If max active proposals reached.
        """
        _validate_string_not_empty(proposal_id, "proposal_id")
        with self._lock:
            if len(self._proposals_active) >= MAX_PROPOSALS_PER_MEMBER:
                raise ProposalError(
                    f"{self._name} already has {MAX_PROPOSALS_PER_MEMBER} active proposals"
                )
            self._proposals_active.add(proposal_id)

    def remove_proposal(self, proposal_id: str) -> None:
        """Remove a proposal association.

        Args:
            proposal_id: Unique proposal identifier.
        """
        with self._lock:
            self._proposals_active.discard(proposal_id)

    # --- Eligibility ---
    def meets_eligibility_criteria(self) -> bool:
        """Check if member satisfies all three criteria : build, hold, advertise.

        Returns:
            True if all criteria met.
        """
        build_ok = self._contribution.meets_foreman_threshold()
        hold_ok = self._rtc_held >= MIN_RTC_HELD
        # Advocacy is considered positive if at least one engagement
        advertise_ok = self._advocacy.total_engagements >= 1
        return build_ok and hold_ok and advertise_ok


class CouncilProposal:
    """Represents a proposal submitted to the council for voting."""

    __slots__ = (
        "_proposal_id",
        "_title",
        "_description",
        "_proposer_wallet",
        "_created_at",
        "_voting_deadline",
        "_status",
        "_votes",
        "_emergency_executed",
    )

    def __init__(
        self,
        proposal_id: str,
        title: str,
        description: str,
        proposer_wallet: str,
        voting_deadline: Optional[datetime] = None,
    ) -> None:
        """Initialize a proposal.

        Args:
            proposal_id: Unique identifier.
            title: Short title.
            description: Full proposal text.
            proposer_wallet: Wallet of the proposer.
            voting_deadline: When voting closes (default 7 days from now).
        """
        _validate_string_not_empty(proposal_id, "proposal_id")
        _validate_string_not_empty(title, "title")
        _validate_string_not_empty(description, "description")
        _validate_wallet(proposer_wallet)

        if voting_deadline is None:
            voting_deadline = datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(days=7)

        self._proposal_id = proposal_id
        self._title = title
        self._description = description
        self._proposer_wallet = proposer_wallet
        self._created_at = datetime.now(timezone.utc)
        self._voting_deadline = voting_deadline
        self._status = ProposalStatus.PENDING
        self._votes: Dict[str, VoteCategory] = {}
        self._emergency_executed = False

        _logger.debug("Proposal created: %s by %s", proposal_id, proposer_wallet[:8])

    # --- Properties (read‑only from outside) ---
    @property
    def proposal_id(self) -> str:
        return self._proposal_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def proposer_wallet(self) -> str:
        return self._proposer_wallet

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def voting_deadline(self) -> datetime:
        return self._voting_deadline

    @property
    def status(self) -> ProposalStatus:
        return self._status

    @status.setter
    def status(self, value: ProposalStatus) -> None:
        _validate_instance(value, ProposalStatus, "status")
        self._status = value

    @property
    def votes(self) -> Dict[str, VoteCategory]:
        return dict(self._votes)

    @property
    def emergency_executed(self) -> bool:
        return self._emergency_executed

    @emergency_executed.setter
    def emergency_executed(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValidationError("emergency_executed must be bool")
        self._emergency_executed = value

    # --- Voting ---
    def cast_vote(self, voter_wallet: str, vote: VoteCategory) -> None:
        """Record a vote.

        Args:
            voter_wallet: Wallet of the council member.
            vote: Vote category.

        Raises:
            VotingError: If voter already voted or deadline passed.
        """
        _validate_wallet(voter_wallet)
        _validate_instance(vote, VoteCategory, "vote")

        if self._status not in (ProposalStatus.ACTIVE, ProposalStatus.EMERGENCY):
            raise VotingError("Proposal is not open for voting")
        if datetime.now(timezone.utc) > self._voting_deadline:
            raise VotingError("Voting deadline has passed")
        if voter_wallet in self._votes:
            raise VotingError(f"Voter {voter_wallet[:8]} already voted")

        self._votes[voter_wallet] = vote
        _logger.info("Vote cast by %s on proposal %s: %s", voter_wallet[:8], self._proposal_id, vote)


# ---------------------------------------------------------------------------
# Treasury
# ---------------------------------------------------------------------------


class Treasury:
    """Manages council treasury and compensation with thread safety."""

    def __init__(self, initial_balance: Decimal = Decimal("0")) -> None:
        """Initialize treasury.

        Args:
            initial_balance: Starting treasury balance.
        """
        _validate_positive_decimal(initial_balance, "initial_balance")
        self._lock = RLock()
        self._balance = initial_balance
        self._transactions: List[Dict[str, Any]] = []
        _logger.info("Treasury initialized with balance %s", initial_balance)

    @property
    def balance(self) -> Decimal:
        with self._lock:
            return self._balance

    def deposit(self, amount: Decimal, reason: str) -> None:
        """Add funds to the treasury.

        Args:
            amount: Positive amount to add.
            reason: Reason for deposit.

        Raises:
            TreasuryError: If amount is not positive.
        """
        amount = _validate_positive_decimal(amount, "deposit amount")
        _validate_string_not_empty(reason, "reason")
        with self._lock:
            self._balance += amount
            self._transactions.append(
                {
                    "type": "deposit",
                    "amount": amount,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
            _logger.info(
                "Treasury deposit: %s (reason: %s). New balance: %s",
                amount,
                reason,
                self._balance,
            )

    def withdraw(self, amount: Decimal, reason: str) -> None:
        """Remove funds from treasury.

        Args:
            amount: Positive amount to withdraw.
            reason: Reason for withdrawal.

        Raises:
            TreasuryError: If insufficient funds or invalid amount.
        """
        amount = _validate_positive_decimal(amount, "withdrawal amount")
        _validate_string_not_empty(reason, "reason")
        with self._lock:
            if amount > self._balance:
                raise TreasuryError(
                    f"Insufficient funds: {amount} requested, {self._balance} available"
                )
            self._balance -= amount
            self._transactions.append(
                {
                    "type": "withdrawal",
                    "amount": amount,
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc),
                }
            )
            _logger.info(
                "Treasury withdrawal: %s (reason: %s). New balance: %s",
                amount,
                reason,
                self._balance,
            )

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """Return a copy of all transactions."""
        with self._lock:
            return list(self._transactions)


# ---------------------------------------------------------------------------
# Main Council class
# ---------------------------------------------------------------------------


class Council:
    """Central governance council for RustChain."""

    def __init__(
        self,
        total_seats: int = DEFAULT_SEATS,
        treasury_initial: Decimal = Decimal("0"),
    ) -> None:
        """Initialize the council.

        Args:
            total_seats: Number of seats (default 5).
            treasury_initial: Starting treasury balance.

        Raises:
            ValidationError: If total_seats < MIN_SEATS.
        """
        _validate_non_negative_int(total_seats, "total_seats")
        if total_seats < MIN_SEATS:
            raise ValidationError(
                f"total_seats must be at least {MIN_SEATS}, got {total_seats}"
            )

        self._lock = RLock()
        self._total_seats = total_seats
        self._seats: List[Optional[CouncilMember]] = [None] * total_seats
        self._members: Dict[str, CouncilMember] = {}  # wallet -> member
        self._proposals: Dict[str, CouncilProposal] = {}
        self._treasury = Treasury(initial_balance=treasury_initial)
        self._initialized = False
        _logger.info(
            "Council initialized with %d seats, treasury %s",
            total_seats,
            treasury_initial,
        )

    # --- Initialization ---
    def initialize(self) -> None:
        """Mark council as initialized and log.

        Raises:
            CouncilError: If already initialized.
        """
        with self._lock:
            if self._initialized:
                raise CouncilError("Council already initialized")
            self._initialized = True
            _logger.info("Council initialization complete")

    @property
    def is_initialized(self) -> bool:
        with self._lock:
            return self._initialized

    @property
    def total_seats(self) -> int:
        return self._total_seats

    @property
    def treasury(self) -> Treasury:
        return self._treasury

    # --- Member management ---
    def register_member(
        self,
        wallet: str,
        name: str,
        rtc_held: Decimal,
        contribution: ContributionRecord,
        advocacy: AdvocacyRecord,
    ) -> CouncilMember:
        """Register a new member in the council registry.

        Args:
            wallet: Wallet address.
            name: Display name.
            rtc_held: Current RTC balance.
            contribution: Engineering contribution record.
            advocacy: Advocacy record.

        Returns:
            The created CouncilMember instance.

        Raises:
            ValidationError: If wallet already registered or inputs invalid.
        """
        _validate_wallet(wallet)
        _validate_string_not_empty(name, "name")
        _validate_positive_decimal(rtc_held, "rtc_held")
        _validate_instance(contribution, ContributionRecord, "contribution")
        _validate_instance(advocacy, AdvocacyRecord, "advocacy")

        with self._lock:
            if wallet in self._members:
                raise ValidationError(f"Wallet {wallet[:8]} already registered")
            member = CouncilMember(
                wallet=wallet,
                name=name,
                rtc_held=rtc_held,
                contribution=contribution,
                advocacy=advocacy,
            )
            self._members[wallet] = member
            _logger.info("Member registered: %s (wallet=%s)", name, wallet[:8])
            return member

    def get_member(self, wallet: str) -> Optional[CouncilMember]:
        """Retrieve a member by wallet.

        Args:
            wallet: Wallet address.

        Returns:
            Member or None.
        """
        with self._lock:
            return self._members.get(wallet)

    def get_active_members(self) -> List[CouncilMember]:
        """Return list of currently active (seated) members.

        Returns:
            List of active CouncilMember objects.
        """
        with self._lock:
            return [m for s in self._seats if s is not None]

    def get_vacant_seats(self) -> List[int]:
        """Return indices of vacant seats.

        Returns:
            List of seat indices (0-based).
        """
        with self._lock:
            return [i for i, m in enumerate(self._seats) if m is None]

    def assign_seat(self, wallet: str, seat_index: Optional[int] = None) -> int:
        """Assign a registered member to a council seat.

        Args:
            wallet: Wallet of the member.
            seat_index: Preferred seat index (optional).

        Returns:
            The assigned seat index.

        Raises:
            EligibilityError: If member does not meet eligibility criteria.
            ElectionError: If no vacant seats or invalid index.
        """
        _validate_wallet(wallet)
        with self._lock:
            member = self._members.get(wallet)
            if member is None:
                raise ElectionError(f"Unknown wallet: {wallet[:8]}")
            if not member.meets_eligibility_criteria():
                raise EligibilityError(
                    f"Member {member.name} does not meet eligibility criteria"
                )
            if member.seat_index is not None:
                raise ElectionError(f"Member {member.name} already seated at index {member.seat_index}")

            # Determine target index
            if seat_index is not None:
                if seat_index < 0 or seat_index >= self._total_seats:
                    raise ElectionError(f"Seat index {seat_index} out of range")
                if self._seats[seat_index] is not None:
                    raise ElectionError(f"Seat {seat_index} already occupied")
            else:
                vacant = self.get_vacant_seats()
                if not vacant:
                    raise ElectionError("No vacant seats available")
                seat_index = vacant[0]

            # Assign seat
            member.seat_index = seat_index
            member.activate_term(
                start=datetime.now(timezone.utc),
                end=datetime.now(timezone.utc).replace(second=0, microsecond=0)
                + timedelta(days=TERM_MONTHS * 30),
            )
            self._seats[seat_index] = member
            _logger.info("Member %s assigned to seat %d", member.name, seat_index)
            return seat_index

    def remove_member(self, wallet: str) -> None:
        """Remove a member from council (end term early).

        Args:
            wallet: Wallet of the member.

        Raises:
            ElectionError: If member not found or not seated.
        """
        _validate_wallet(wallet)
        with self._lock:
            member = self._members.get(wallet)
            if member is None:
                raise ElectionError(f"Unknown wallet: {wallet[:8]}")
            idx = member.seat_index
            if idx is None:
                raise ElectionError(f"Member {member.name} is not seated")
            self._seats[idx] = None
            member.seat_index = None
            member.deactivate()
            _logger.info("Member %s removed from seat %d", member.name, idx)

    # --- Proposals ---
    def submit_proposal(
        self,
        proposal_id: str,
        title: str,
        description: str,
        proposer_wallet: str,
        voting_deadline: Optional[datetime] = None,
    ) -> CouncilProposal:
        """Submit a new proposal for voting.

        Args:
            proposal_id: Unique identifier.
            title: Short title.
            description: Full proposal text.
            proposer_wallet: Wallet of the proposer (must be active member).
            voting_deadline: Optional voting deadline.

        Returns:
            The created CouncilProposal.

        Raises:
            ProposalError: If proposal ID already exists or proposer not active.
        """
        _validate_string_not_empty(proposal_id, "proposal_id")
        _validate_wallet(proposer_wallet)

        with self._lock:
            if proposal_id in self._proposals:
                raise ProposalError(f"Proposal {proposal_id} already exists")
            # Verify proposer is an active member
            member = self._members.get(proposer_wallet)
            if member is None or not member.is_active:
                raise ProposalError(f"Proposer {proposer_wallet[:8]} is not an active member")

            proposal = CouncilProposal(
                proposal_id=proposal_id,
                title=title,
                description=description,
                proposer_wallet=proposer_wallet,
                voting_deadline=voting_deadline,
            )
            proposal.status = ProposalStatus.ACTIVE
            self._proposals[proposal_id] = proposal
            member.add_proposal(proposal_id)
            _logger.info("Proposal %s submitted by %s", proposal_id, proposer_wallet[:8])
            return proposal

    def get_proposal(self, proposal_id: str) -> Optional[CouncilProposal]:
        """Retrieve a proposal by ID.

        Args:
            proposal_id: Unique proposal identifier.

        Returns:
            Proposal or None.
        """
        with self._lock:
            return self._proposals.get(proposal_id)

    def cast_vote(self, proposal_id: str, voter_wallet: str, vote: VoteCategory) -> None:
        """Cast a vote on an active proposal.

        Args:
            proposal_id: Proposal identifier.
            voter_wallet: Wallet of the voting council member.
            vote: Vote category.

        Raises:
            VotingError: If voter not an active member or proposal not found.
        """
        _validate_wallet(voter_wallet)
        _validate_instance(vote, VoteCategory, "vote")

        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None:
                raise VotingError(f"Proposal {proposal_id} not found")
            # Must be an active seated member
            member = self._members.get(voter_wallet)
            if member is None or not member.is_active:
                raise VotingError(f"Voter {voter_wallet[:8]} is not an active council member")
            proposal.cast_vote(voter_wallet, vote)

    def tally_votes(self, proposal_id: str) -> Tuple[int, int, int]:
        """Count votes for a proposal.

        Args:
            proposal_id: Proposal identifier.

        Returns:
            Tuple (for_count, against_count, abstain_count).

        Raises:
            ProposalError: If proposal not found.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None:
                raise ProposalError(f"Proposal {proposal_id} not found")
            for_votes = sum(
                1 for v in proposal.votes.values() if v == VoteCategory.FOR
            )
            against_votes = sum(
                1 for v in proposal.votes.values() if v == VoteCategory.AGAINST
            )
            abstain_votes = sum(
                1 for v in proposal.votes.values() if v == VoteCategory.ABSTAIN
            )
            return for_votes, against_votes, abstain_votes

    def close_proposal(self, proposal_id: str) -> ProposalStatus:
        """Finalize a proposal after voting deadline.

        Determines pass/fail based on majority of cast votes.

        Args:
            proposal_id: Proposal identifier.

        Returns:
            Final ProposalStatus (PASSED or REJECTED).

        Raises:
            ProposalError: If proposal not found or already closed.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None:
                raise ProposalError(f"Proposal {proposal_id} not found")
            if proposal.status in (ProposalStatus.PASSED, ProposalStatus.REJECTED):
                raise ProposalError(f"Proposal {proposal_id} already closed")
            if datetime.now(timezone.utc) < proposal.voting_deadline:
                raise ProposalError(f"Voting deadline for {proposal_id} has not passed")

            for_votes, against_votes, _ = self.tally_votes(proposal_id)
            total_seated = len(self.get_active_members())
            # Quorum: at least half of seated members must vote
            if for_votes + against_votes < (total_seated + 1) // 2:
                proposal.status = ProposalStatus.REJECTED
                _logger.warning("Proposal %s rejected: quorum not met", proposal_id)
            elif for_votes > against_votes:
                proposal.status = ProposalStatus.PASSED
                _logger.info("Proposal %s passed", proposal_id)
            else:
                proposal.status = ProposalStatus.REJECTED
                _logger.info("Proposal %s rejected: majority against", proposal_id)
            # Clean up proposer's active proposals list
            proposer = self._members.get(proposal.proposer_wallet)
            if proposer:
                proposer.remove_proposal(proposal_id)
            return proposal.status

    # --- Emergency actions ---
    def initiate_emergency_action(
        self, trigger_wallet: str, proposal_id: str, title: str, description: str
    ) -> CouncilProposal:
        """Initiate an emergency action with expedited voting.

        Args:
            trigger_wallet: Wallet of the emergency initiator (must be active member).
            proposal_id: Unique proposal identifier (should start with 'EM-').
            title: Short title.
            description: Description of the emergency.

        Returns:
            The emergency CouncilProposal.

        Raises:
            EmergencyActionError: If initiator not active or proposal exists.
        """
        _validate_wallet(trigger_wallet)
        _validate_string_not_empty(proposal_id, "proposal_id")
        # Recommend EM- prefix
        if not proposal_id.startswith("EM-"):
            _logger.warning("Emergency proposal ID '%s' does not start with 'EM-'", proposal_id)

        with self._lock:
            # Verify initiator is active
            member = self._members.get(trigger_wallet)
            if member is None or not member.is_active:
                raise EmergencyActionError(f"Initiator {trigger_wallet[:8]} is not an active member")
            if proposal_id in self._proposals:
                raise EmergencyActionError(f"Proposal {proposal_id} already exists")

            # Create emergency proposal with short deadline (24 hours)
            emergency_deadline = datetime.now(timezone.utc).replace(
                second=0, microsecond=0
            ) + timedelta(hours=24)
            proposal = CouncilProposal(
                proposal_id=proposal_id,
                title=title,
                description=description,
                proposer_wallet=trigger_wallet,
                voting_deadline=emergency_deadline,
            )
            proposal.status = ProposalStatus.EMERGENCY
            self._proposals[proposal_id] = proposal
            member.add_proposal(proposal_id)
            _logger.warning(
                "EMERGENCY action initiated by %s: %s - %s",
                trigger_wallet[:8],
                proposal_id,
                title,
            )
            return proposal

    def execute_emergency_action(self, proposal_id: str) -> None:
        """Execute an emergency action if threshold met (3 yes votes).

        Args:
            proposal_id: Emergency proposal identifier.

        Raises:
            EmergencyActionError: If conditions not met.
        """
        with self._lock:
            proposal = self._proposals.get(proposal_id)
            if proposal is None:
                raise EmergencyActionError(f"Proposal {proposal_id} not found")
            if proposal.status != ProposalStatus.EMERGENCY:
                raise EmergencyActionError(
                    f"Proposal {proposal_id} is not in emergency status"
                )
            for_votes = sum(
                1 for v in proposal.votes.values() if v == VoteCategory.FOR
            )
            if for_votes < EMERGENCY_THRESHOLD:
                raise EmergencyActionError(
                    f"Emergency action needs {EMERGENCY_THRESHOLD} yes votes, only {for_votes}"
                )
            proposal.emergency_executed = True
            proposal.status = ProposalStatus.RATIFIED
            _logger.info(
                "Emergency action %s executed with %d yes votes", proposal_id, for_votes
            )

    # --- Election ---
    def run_election(self) -> List[CouncilMember]:
        """Simulate an election by filling vacant seats with eligible candidates.

        In a full implementation, this would involve a ranked‑choice vote.
        Here we simply assign the most senior eligible candidate to each vacant seat.

        Returns:
            List of newly seated CouncilMembers.

        Raises:
            ElectionError: If no eligible candidates or council not initialized.
        """
        with self._lock:
            if not self._initialized:
                raise ElectionError("Council not initialized")
            if all(s is not None for s in self._seats):
                raise ElectionError("No vacant seats to fill")

            # Get eligible candidates not already seated
            candidates: List[CouncilMember] = []
            for wallet, member in self._members.items():
                if member.is_active:
                    continue  # already seated or active
                if member.meets_eligibility_criteria():
                    candidates.append(member)

            if not candidates:
                raise ElectionError("No eligible candidates available")

            # Sort by seniority (merged_prs + total_engagements descending)
            candidates.sort(
                key=lambda m: (
                    m.contribution.merged_prs + m.advocacy.total_engagements,
                    m.consecutive_terms,
                ),
                reverse=True,
            )

            newly_seated: List[CouncilMember] = []
            vacant_indices = self.get_vacant_seats()
            for idx, candidate in zip(vacant_indices, candidates):
                # Skip if already seated (race condition prevention)
                if candidate.seat_index is not None:
                    continue
                self._seats[idx] = candidate
                candidate.seat_index = idx
                candidate.increment_consecutive_terms()
                candidate.activate_term(
                    start=datetime.now(timezone.utc),
                    end=datetime.now(timezone.utc).replace(second=0, microsecond=0)
                    + timedelta(days=TERM_MONTHS * 30),
                )
                newly_seated.append(candidate)
                _logger.info(
                    "Election: %s seated at index %d (term %d)",
                    candidate.name,
                    idx,
                    candidate.consecutive_terms,
                )
            return newly_seated

    # --- Status reports ---
    def get_status_report(self) -> Dict[str, Any]:
        """Produce a comprehensive status report of the council.

        Returns:
            Dictionary with keys: initialized, total_seats, occupied_seats,
            vacant_seats, active_members, total_members_registered,
            treasury_balance, proposals_active, proposals_total.
        """
        with self._lock:
            active_members = self.get_active_members()
            return {
                "initialized": self._initialized,
                "total_seats": self._total_seats,
                "occupied_seats": len(active_members),
                "vacant_seats": self.get_vacant_seats(),
                "active_members": [m.wallet for m in active_members],
                "total_members_registered": len(self._members),
                "treasury_balance": self._treasury.balance,
                "proposals_active": len(
                    [p for p in self._proposals.values() if p.status in (ProposalStatus.ACTIVE, ProposalStatus.EMERGENCY)]
                ),
                "proposals_total": len(self._proposals),
            }