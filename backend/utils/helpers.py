"""
Helper utilities for the Product Discovery Multi-Agent System.

This module provides:
- Session ID generation
- Logging configuration
- Input sanitization
- Inception pack building
- In-memory session storage
"""

import logging
import re
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

import structlog

from config import settings


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION ID GENERATION
# ═══════════════════════════════════════════════════════════════════════════════


def generate_session_id() -> str:
    """
    Generate a unique session ID.

    Format: disc_{timestamp}_{uuid}
    Example: disc_20240115_a1b2c3d4

    Returns:
        str: Unique session identifier.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8]
    return f"disc_{timestamp}_{unique_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════


def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up structlog with appropriate processors for either
    JSON output (production) or console output (development).
    """
    # Determine log level from settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Common processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ExtraAdder(),
    ]

    if settings.log_json_format:
        # JSON format for production
        structlog.configure(
            processors=shared_processors
            + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Pretty console output for development
        structlog.configure(
            processors=shared_processors
            + [
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Also configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SANITIZATION
# ═══════════════════════════════════════════════════════════════════════════════


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input text.

    - Strips leading/trailing whitespace
    - Removes control characters
    - Truncates to max length
    - Normalizes whitespace

    Args:
        text: Input text to sanitize.
        max_length: Maximum allowed length.

    Returns:
        str: Sanitized text.
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove control characters (except newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    # Normalize whitespace (multiple spaces to single)
    text = re.sub(r" +", " ", text)

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_constraints(constraints: list[str] | None) -> list[str] | None:
    """
    Sanitize a list of constraint strings.

    Args:
        constraints: List of constraints to sanitize.

    Returns:
        list[str] | None: Sanitized constraints or None.
    """
    if not constraints:
        return None

    sanitized = [sanitize_input(c, max_length=500) for c in constraints]
    return [c for c in sanitized if c]  # Remove empty strings


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATTING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        str: Formatted duration (e.g., "2m 30s", "45s").
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# ═══════════════════════════════════════════════════════════════════════════════
# INCEPTION PACK BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_inception_pack(state: dict[str, Any]) -> dict[str, Any]:
    """
    Build the final InceptionPack from workflow state.

    Assembles all agent outputs into the final deliverable format.

    Args:
        state: Completed workflow state.

    Returns:
        dict: Complete InceptionPack structure.
    """
    return {
        "executive_summary": state.get("executive_summary", {}),
        "customer_research": state.get("customer_research", {}),
        "business_case": state.get("business_case", {}),
        "product_requirements_document": state.get("product_requirements", {}),
        "technical_architecture": state.get("technical_architecture", {}),
        "quality_assessment": state.get("quality_assessment") or {},
        "metadata": {
            "session_id": state.get("session_id", "unknown"),
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "generator": "Product Discovery Multi-Agent System",
            "iterations": state.get("iteration", 1),
            "total_tokens_used": state.get("total_tokens_used", 0),
            "total_duration_seconds": round(state.get("total_duration_seconds", 0) or 0, 2),
            "quality_score": (state.get("quality_assessment") or {}).get("overall_score"),
            "quality_passed": state.get("quality_passed", False),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# IN-MEMORY SESSION STORAGE
# ═══════════════════════════════════════════════════════════════════════════════


class SessionStore:
    """
    In-memory session storage for MVP.

    Stores session state with automatic expiration.
    For production, replace with Redis or database storage.

    Attributes:
        _sessions: Dictionary of session data.
        _expiry: Session expiry time in seconds.
    """

    def __init__(self, expiry_seconds: int | None = None):
        """
        Initialize the session store.

        Args:
            expiry_seconds: Session expiry time. Defaults to settings value.
        """
        self._sessions: dict[str, dict[str, Any]] = {}
        self._expiry = expiry_seconds or settings.session_expiry_seconds

    def create(self, session_id: str, initial_data: dict[str, Any]) -> None:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier.
            initial_data: Initial session data.
        """
        self._sessions[session_id] = {
            "data": initial_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self._expiry),
        }
        self._cleanup_expired()

    def get(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        Get session data by ID.

        Args:
            session_id: Session identifier.

        Returns:
            dict | None: Session data or None if not found/expired.
        """
        self._cleanup_expired()

        session = self._sessions.get(session_id)
        if not session:
            return None

        if datetime.utcnow() > session["expires_at"]:
            del self._sessions[session_id]
            return None

        return session["data"]

    def update(self, session_id: str, data: dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier.
            data: Updated session data.

        Returns:
            bool: True if updated, False if session not found.
        """
        if session_id not in self._sessions:
            return False

        self._sessions[session_id]["data"] = data
        self._sessions[session_id]["updated_at"] = datetime.utcnow()
        # Extend expiry on update
        self._sessions[session_id]["expires_at"] = datetime.utcnow() + timedelta(
            seconds=self._expiry
        )
        return True

    def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier.

        Returns:
            bool: True if deleted, False if not found.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def exists(self, session_id: str) -> bool:
        """
        Check if a session exists and is not expired.

        Args:
            session_id: Session identifier.

        Returns:
            bool: True if session exists and is valid.
        """
        return self.get(session_id) is not None

    def count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            int: Number of non-expired sessions.
        """
        self._cleanup_expired()
        return len(self._sessions)

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        now = datetime.utcnow()
        expired = [
            sid
            for sid, session in self._sessions.items()
            if now > session["expires_at"]
        ]
        for sid in expired:
            del self._sessions[sid]

    def get_all_session_ids(self) -> list[str]:
        """
        Get all active session IDs.

        Returns:
            list[str]: List of active session IDs.
        """
        self._cleanup_expired()
        return list(self._sessions.keys())
