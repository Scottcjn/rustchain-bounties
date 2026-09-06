"""Validator for Issue #16863 contributor feedback micro-bounty submissions."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


class FeedbackValidationError(ValueError):
    """Raised when feedback submission fails validation against issue requirements."""
    pass


class FeedbackValidator:
    """Validates feedback submissions against all criteria in Issue #16863."""

    MIN_SENTENCES: int = 2
    MAX_SENTENCES: int = 6

    AGENT_PATTERNS: List[re.Pattern] = [
        re.compile(r"\b(?:autonomous|coding|ai|software)?\s*agent\b", re.IGNORECASE),
        re.compile(r"\boperating on behalf of\b", re.IGNORECASE),
        re.compile(r"\bautomated\b", re.IGNORECASE),
    ]

    REPO_PATTERNS: List[re.Pattern] = [
        re.compile(r"\brustchain\b", re.IGNORECASE),
        re.compile(r"\bbottube\b", re.IGNORECASE),
        re.compile(r"\belyan\b", re.IGNORECASE),
        re.compile(r"#\d+\b"),
    ]

    FRICTION_PATTERNS: List[re.Pattern] = [
        re.compile(r"\b(?:nearly|almost)?\s*(?:left|abandoned|quit|stopped)\b", re.IGNORECASE),
        re.compile(r"\bfriction\b", re.IGNORECASE),
        re.compile(r"\blatency\b", re.IGNORECASE),
        re.compile(r"\blimbo\b", re.IGNORECASE),
        re.compile(r"\bbottleneck\b", re.IGNORECASE),
        re.compile(r"\bsparse\b", re.IGNORECASE),
        re.compile(r"\bcomplexity\b", re.IGNORECASE),
    ]

    IMPROVEMENT_PATTERNS: List[re.Pattern] = [
        re.compile(r"\b(?:change|improve|add|introducing|provide|support|endpoint|webhook|status)\b", re.IGNORECASE),
        re.compile(r"\bwould have made\b", re.IGNORECASE),
        re.compile(r"\baccelerate\b", re.IGNORECASE),
    ]

    BANNED_PRAISE_PATTERNS: List[re.Pattern] = [
        re.compile(r"^great project!?$", re.IGNORECASE),
        re.compile(r"^nice work!?$", re.IGNORECASE),
        re.compile(r"^looks good!?$", re.IGNORECASE),
        re.compile(r"^awesome repo!?$", re.IGNORECASE),
        re.compile(r"^i love this project!?$", re.IGNORECASE),
    ]

    RTC_WALLET_PATTERN: re.Pattern = re.compile(r"\bRTC[a-fA-F0-9]{40}\b")
    EVM_WALLET_PATTERN: re.Pattern = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
    GITHUB_HANDLE_PATTERN: re.Pattern = re.compile(r"(?:@|handle:\s*`?)([a-zA-Z0-9_-]+)`?")

    def split_into_sentences(self, text: str) -> List[str]:
        """Split raw text into clean individual sentences.

        Parameters
        ----------
        text : str
            Input text containing feedback.

        Returns
        -------
        List[str]
            List of non-empty stripped sentences.
        """
        raw_sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in raw_sentences if s.strip()]

    def validate_sentence_count(self, text: str) -> int:
        """Validate that text consists of between 2 and 6 sentences inclusive.

        Parameters
        ----------
        text : str
            Input text to evaluate.

        Returns
        -------
        int
            The number of validated sentences.

        Raises
        ------
        FeedbackValidationError
            If the sentence count is strictly outside [2, 6].
        """
        sentences = self.split_into_sentences(text)
        count = len(sentences)
        if count < self.MIN_SENTENCES or count > self.MAX_SENTENCES:
            raise FeedbackValidationError(
                f"Sentence count must be between {self.MIN_SENTENCES} and {self.MAX_SENTENCES}. Found {count}."
            )
        return count

    def validate_agent_disclosure(self, text: str, is_agent: bool) -> bool:
        """Validate that agent submissions explicitly disclose agent identity.

        Parameters
        ----------
        text : str
            Submission text.
        is_agent : bool
            Whether the submitter operates as an AI/automated agent.

        Returns
        -------
        bool
            True if disclosure is present or not required.

        Raises
        ------
        FeedbackValidationError
            If submitter is an agent but failed to disclose.
        """
        if not is_agent:
            return True

        if any(p.search(text) for p in self.AGENT_PATTERNS):
            return True

        raise FeedbackValidationError("Agent submissions must disclose agent identity in the text.")

    def validate_starting_context(self, text: str) -> bool:
        """Validate that the text names a starting repository, bounty, or issue.

        Parameters
        ----------
        text : str
            Submission text.

        Returns
        -------
        bool
            True if starting context is identified.

        Raises
        ------
        FeedbackValidationError
            If no starting repo or bounty identifier is found.
        """
        if any(p.search(text) for p in self.REPO_PATTERNS):
            return True

        raise FeedbackValidationError("Submission must mention which repo or bounty you started with.")

    def validate_friction_point(self, text: str) -> bool:
        """Validate that the text describes what nearly caused the contributor to leave.

        Parameters
        ----------
        text : str
            Submission text.

        Returns
        -------
        bool
            True if friction point is present.

        Raises
        ------
        FeedbackValidationError
            If no friction point or near-quit moment is described.
        """
        if any(p.search(text) for p in self.FRICTION_PATTERNS):
            return True

        raise FeedbackValidationError("Submission must explain what nearly made you leave.")

    def validate_improvement_suggestion(self, text: str) -> bool:
        """Validate that the text suggests a concrete improvement.

        Parameters
        ----------
        text : str
            Submission text.

        Returns
        -------
        bool
            True if an improvement suggestion is present.

        Raises
        ------
        FeedbackValidationError
            If no improvement suggestion is identified.
        """
        if any(p.search(text) for p in self.IMPROVEMENT_PATTERNS):
            return True

        raise FeedbackValidationError("Submission must suggest one thing to change that would drive more work.")

    def validate_anti_boilerplate(self, text: str) -> bool:
        """Validate that the text is substantive and not low-effort praise or copy-paste.

        Parameters
        ----------
        text : str
            Submission text.

        Returns
        -------
        bool
            True if text is substantive.

        Raises
        ------
        FeedbackValidationError
            If text matches known spam or generic praise templates.
        """
        stripped = text.strip().lower()
        for p in self.BANNED_PRAISE_PATTERNS:
            if p.match(stripped):
                raise FeedbackValidationError("Generic praise and copy-paste answers are not eligible for payment.")

        if len(stripped.split()) < 15:
            raise FeedbackValidationError("Submission is too brief to satisfy substantive feedback criteria.")

        return True

    def extract_payout_identifier(self, text: str, fallback_handle: Optional[str] = None) -> Dict[str, Optional[str]]:
        """Extract RTC wallet address, EVM address, or GitHub handle from submission text.

        Parameters
        ----------
        text : str
            Submission text.
        fallback_handle : Optional[str]
            Fallback GitHub handle if not present in body.

        Returns
        -------
        Dict[str, Optional[str]]
            Extracted identifiers with keys 'rtc_wallet', 'evm_wallet', and 'github_handle'.

        Raises
        ------
        FeedbackValidationError
            If neither a valid wallet nor a GitHub handle can be determined.
        """
        rtc_match = self.RTC_WALLET_PATTERN.search(text)
        evm_match = self.EVM_WALLET_PATTERN.search(text)
        handle_match = self.GITHUB_HANDLE_PATTERN.search(text)

        rtc_wallet = rtc_match.group(0) if rtc_match else None
        evm_wallet = evm_match.group(0) if evm_match else None
        github_handle = handle_match.group(1) if handle_match else fallback_handle

        if not rtc_wallet and not evm_wallet and not github_handle:
            raise FeedbackValidationError("Submission must provide an RTC wallet, EVM address, or GitHub handle.")

        return {
            "rtc_wallet": rtc_wallet,
            "evm_wallet": evm_wallet,
            "github_handle": github_handle,
        }

    def validate_submission(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a full submission dictionary against all Issue #16863 criteria.

        Parameters
        ----------
        submission : Dict[str, Any]
            Submission payload containing response_text, is_agent, claimant, etc.

        Returns
        -------
        Dict[str, Any]
            Validated submission summary with check results.
        """
        text = submission.get("response_text", "")
        is_agent = submission.get("is_agent", False)
        claimant = submission.get("claimant")

        sentence_count = self.validate_sentence_count(text)
        self.validate_agent_disclosure(text, is_agent)
        self.validate_starting_context(text)
        self.validate_friction_point(text)
        self.validate_improvement_suggestion(text)
        self.validate_anti_boilerplate(text)
        identifiers = self.extract_payout_identifier(text, fallback_handle=claimant)

        return {
            "valid": True,
            "sentence_count": sentence_count,
            "is_agent": is_agent,
            "identifiers": identifiers,
            "checks_passed": [
                "sentence_count_bounds",
                "agent_identity_disclosure",
                "starting_repo_context",
                "near_quit_friction_point",
                "improvement_suggestion",
                "anti_boilerplate_substance",
                "payout_identifier_resolved",
            ],
        }
