"""Core webhook handler for comment moderation.

Implements payload validation, error handling with proper status codes,
and separation of user-facing vs. internal exception details.
"""

import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, request, Response

# --------------------------------------------------------------------------- #
# Custom exceptions
# --------------------------------------------------------------------------- #


class ValidationError(Exception):
    """Raised when the incoming payload is malformed or fails schema validation.

    Attributes:
        message: Human-readable summary.
        details: Mapping from field name to specific error description.
    """

    def __init__(self, message: str, details: Optional[Dict[str, str]] = None) -> None:
        self.message = message
        self.details: Dict[str, str] = details or {}
        super().__init__(message)


class ProcessingError(Exception):
    """Raised when an internal processing step fails (not user-caused).

    Attributes:
        message: Generic message for external consumers.
        original: The underlying exception (used for audit logging).
    """

    def __init__(self, message: str, original: Optional[Exception] = None) -> None:
        self.message = message
        self.original = original
        super().__init__(message)


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

REQUIRED_FIELDS: Tuple[str, ...] = ("comment", "author", "moderation_action")
NESTED_REQUIRED_FIELDS: Tuple[str, ...] = ("text", "id")
MAX_PAYLOAD_SIZE_BYTES: int = 1_000_000  # 1 MB

# Retained for potential use in security validation (e.g., allowed action types)
ALLOWED_MODERATION_ACTIONS: Tuple[str, ...] = ("approve", "reject", "flag", "review")

# Webhook secret used for HMAC signature verification
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

# --------------------------------------------------------------------------- #
# Logger
# --------------------------------------------------------------------------- #

logger: logging.Logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Public validation & processing
# --------------------------------------------------------------------------- #


def validate_payload(payload: object) -> None:
    """Validate the structure and required fields of a webhook payload.

    Args:
        payload: The parsed JSON payload (expected to be a ``dict``).

    Raises:
        ValidationError: If the payload is not a ``dict``, is missing required
            keys, or contains invalid field types/contents.
    """
    if not isinstance(payload, dict):
        raise ValidationError("Payload must be a JSON object.", details={"payload": "expected object"})

    # Validate top-level required fields
    for field in REQUIRED_FIELDS:
        if field not in payload:
            raise ValidationError(f"Missing required field: '{field}'.", details={field: "field is required"})

    # Validate ``comment`` is a dict
    comment = payload.get("comment")
    if not isinstance(comment, dict):
        raise ValidationError(
            "Field 'comment' must be a JSON object.",
            details={"comment": "expected object"},
        )

    # Validate nested required fields
    for field in NESTED_REQUIRED_FIELDS:
        if field not in comment:
            raise ValidationError(
                f"Missing nested field 'comment.{field}'.",
                details={f"comment.{field}": "field is required"},
            )

    # Validate ``comment.text`` is a non-empty string
    comment_text = comment.get("text")
    if not isinstance(comment_text, str) or not comment_text.strip():
        raise ValidationError(
            "Field 'comment.text' must be a non-empty string.",
            details={"comment.text": "expected non-empty string"},
        )

    # Validate ``author`` is a non-empty string (optional refinement)
    author = payload.get("author")
    if not isinstance(author, str) or not author.strip():
        raise ValidationError(
            "Field 'author' must be a non-empty string.",
            details={"author": "expected non-empty string"},
        )

    # Validate ``moderation_action`` is one of the allowed values
    action = payload.get("moderation_action")
    if action not in ALLOWED_MODERATION_ACTIONS:
        allowed = ", ".join(repr(a) for a in ALLOWED_MODERATION_ACTIONS)
        raise ValidationError(
            f"Field 'moderation_action' must be one of {allowed}.",
            details={"moderation_action": f"expected one of {allowed}, got {action!r}"},
        )


def verify_signature(payload_body: bytes, signature_header: Optional[str]) -> None:
    """Verify the HMAC-SHA256 signature of the webhook payload.

    Args:
        payload_body: Raw bytes of the request body.
        signature_header: Value of the ``X-Hub-Signature-256`` header.

    Raises:
        ValidationError: If the signature is missing, invalid, or does not match.
    """
    if not WEBHOOK_SECRET:
        logger.warning("WEBHOOK_SECRET not set; skipping signature verification")
        return

    if not signature_header:
        raise ValidationError(
            "Missing signature header 'X-Hub-Signature-256'.",
            details={"signature": "header required when secret is configured"},
        )

    expected_prefix = "sha256="
    if not signature_header.startswith(expected_prefix):
        raise ValidationError(
            "Invalid signature format; expected 'sha256=...'.",
            details={"signature": "invalid format"},
        )

    received_sig = signature_header[len(expected_prefix):]

    # Compute expected signature using HMAC-SHA256
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        payload_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, received_sig):
        raise ValidationError(
            "Signature mismatch; payload may have been tampered with.",
            details={"signature": "mismatch"},
        )

    logger.info("Webhook signature verified successfully.")


def handle_webhook(
    request_data: Dict[str, Any],
    event_type: Optional[str] = None,
) -> Tuple[Dict[str, Any], int]:
    """Process an incoming comment moderation webhook payload.

    The function performs payload validation, applies moderation rules based on
    the event type, and returns a JSON response with the appropriate HTTP status code.

    Args:
        request_data: Parsed request body (must be a ``dict``).
        event_type: GitHub event type from the ``X-GitHub-Event`` header
            (e.g., "issue_comment", "pull_request_review_comment").

    Returns:
        A tuple ``(response_dict, status_code)`` where ``response_dict``
        contains at least a ``"detail"`` key and optionally a
        ``"validation_errors"`` key.

    Raises:
        ValidationError: If the payload is malformed (handled upstream).
        ProcessingError: If an internal processing step fails (handled upstream).
    """
    try:
        validate_payload(request_data)

        # --- Determine event-specific handling ---
        comment_text: str = request_data["comment"]["text"]
        author: str = request_data["author"]
        action: str = request_data["moderation_action"]

        logger.info(
            "Processing %s event: comment by '%s' with action '%s': %.50s...",
            event_type or "unknown",
            author,
            action,
            comment_text,
        )

        # Mock moderation logic – in production, this would call an external API
        # or apply custom rules.
        if action == "reject" and "spam" in comment_text.lower():
            logger.info("Comment flagged as spam; rejecting.")
            return {
                "detail": "Comment rejected due to spam detection.",
                "moderation_result": "rejected",
            }, 200

        # For all other cases, approve or apply the requested action
        # Extend with additional business logic as needed.
        return {
            "detail": f"Comment processed successfully with action: {action}.",
            "moderation_result": action,
        }, 200

    except ValidationError:
        # Re-raise to let the caller format the response (keeps concerns separated)
        raise
    except ProcessingError:
        # Should not happen in this simple example, but re-raise if it does
        logger.exception("ProcessingError raised unexpectedly in handle_webhook")
        raise
    except Exception as exc:
        logger.exception("Unexpected processing failure")
        raise ProcessingError("Internal server error.", original=exc) from exc


def webhook_handler() -> Tuple[Response, int]:
    """Flask route handler for the ``/webhook`` endpoint.

    Parses the JSON request body, verifies the HMAC signature, calls
    :func:`handle_webhook`, and returns a proper HTTP response.

    Returns:
        A Flask response object and an HTTP status code.

    Notes:
        - Validates JSON content length before parsing.
        - Verifies the GitHub signature header.
        - Catches :class:`ValidationError` and returns a 400 response with
          field‑specific details.
        - Catches :class:`ProcessingError` and returns a 500 response with
          a generic message (the original exception is logged internally).
        - Any other unexpected error results in a 500 response.
    """
    # Security: reject oversized payloads before parsing
    if request.content_length and request.content_length > MAX_PAYLOAD_SIZE_BYTES:
        logger.warning("Payload exceeds maximum allowed size")
        return jsonify({"detail": "Payload too large."}), 413

    # Read raw body for signature verification
    try:
        raw_body: bytes = request.get_data()
    except Exception as exc:
        logger.exception("Failed to read request body")
        return jsonify({"detail": "Internal server error."}), 500

    # Verify HMAC signature
    try:
        signature = request.headers.get("X-Hub-Signature-256")
        verify_signature(raw_body, signature)
    except ValidationError as exc:
        logger.warning("Signature validation failed: %s", exc.message)
        return jsonify({"detail": exc.message, "validation_errors": exc.details}), 400
    except Exception as exc:
        logger.exception("Unexpected error during signature verification")
        return jsonify({"detail": "Internal server error."}), 500

    # Parse JSON
    try:
        payload: object = request.get_json(force=True, silent=False)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON payload: %s", exc)
        return jsonify({"detail": "Invalid JSON payload.", "validation_errors": {"_json": str(exc)}}), 400
    except Exception as exc:
        logger.exception("Request parsing failed unexpectedly")
        return jsonify({"detail": "Internal server error."}), 500

    # Extract event type from header
    event_type: Optional[str] = request.headers.get("X-GitHub-Event")

    # Process the payload
    try:
        response, status = handle_webhook(payload, event_type=event_type)  # type: ignore[arg-type]
        return jsonify(response), status
    except ValidationError as exc:
        logger.info("Validation failed: %s (details: %s)", exc.message, exc.details)
        return jsonify({"detail": exc.message, "validation_errors": exc.details}), 400
    except ProcessingError as exc:
        # Log the full context (original exception) but return a generic message
        logger.error("Processing error: %s | original: %s", exc.message, exc.original)
        return jsonify({"detail": "Internal server error."}), 500
    except Exception as exc:
        # Catch-all for any other unexpected error
        logger.exception("Unhandled exception in webhook_handler")
        return jsonify({"detail": "Internal server error."}), 500


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A configured Flask app instance.
    """
    app: Flask = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook() -> Tuple[Response, int]:
        return webhook_handler()

    return app


# --------------------------------------------------------------------------- #
# Main entry point (development only)
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app = create_app()
    app.run(host="0.0.0.0", port=8080, debug=False)