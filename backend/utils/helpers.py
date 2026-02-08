"""
Helper utilities for the Product Discovery Multi-Agent System.

This module provides:
- Session ID generation
- Logging configuration
- Input sanitization
- Inception pack building
"""

import logging
import re
import sys
import uuid
from datetime import datetime
from typing import Any

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
    Supports both V1.0 (7 sections) and V3.0 (16 sections) formats.

    Args:
        state: Completed workflow state.

    Returns:
        dict: Complete InceptionPack structure.
    """
    pack = {
        # Core sections (V1.0)
        "executive_summary": state.get("executive_summary", {}),
        "customer_research": state.get("customer_research", {}),
        "business_case": state.get("business_case", {}),
        "product_requirements_document": state.get("product_requirements", {}),
        "technical_architecture": state.get("technical_architecture", {}),
        "legal_regulatory_review": state.get("legal_regulatory_review", {}),
        "quality_assessment": state.get("quality_assessment") or {},
        # V3.0 Discovery sections
        "competitive_analysis": state.get("competitive_analysis"),
        "detailed_personas": state.get("detailed_personas"),
        # V3.0 Strategy sections
        "gtm_strategy": state.get("gtm_plan"),  # Backend uses gtm_plan, frontend expects gtm_strategy
        "financial_model": state.get("financial_model"),
        # V3.0 Delivery sections
        "risk_assessment": state.get("risk_assessment"),
        # V3.0 Design sections
        "wireframes": state.get("wireframes"),
        "prototype": state.get("prototype"),
        # V3.0 Synthesis sections
        "stakeholder_views": state.get("stakeholder_views"),
        "validation_playbook": state.get("validation_playbook"),
        # V3.0 Cross-reference index (from claim extractor)
        "cross_reference_index": state.get("cross_reference_index"),
        # Metadata
        "metadata": {
            "session_id": state.get("session_id", "unknown"),
            "generated_at": datetime.utcnow().isoformat(),
            "version": "3.0",
            "generator": "Product Discovery Multi-Agent System",
            "iterations": str(state.get("iteration", 1)),
            "total_tokens_used": str(state.get("total_tokens_used", 0)),
            "total_duration_seconds": str(round(state.get("total_duration_seconds", 0) or 0, 2)),
            "quality_score": str((state.get("quality_assessment") or {}).get("overall_score", 0.0)),
            "quality_passed": str(state.get("quality_passed", False)),
        },
    }

    # Remove None values to keep response clean
    return {k: v for k, v in pack.items() if v is not None}
