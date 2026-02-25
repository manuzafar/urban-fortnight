"""
State pruning utilities for managing unbounded fields in DiscoveryState.

This module provides functions to prune large state fields like revision_history,
errors, and cross_reference_index to prevent memory issues in long-running
workflows.

The pruning strategy:
1. Keep recent entries in memory for active use
2. Archive old entries to database for audit/debugging
3. Log state size before and after pruning for monitoring
"""

import json
import sys
from datetime import datetime
from typing import Any, Optional

import structlog

from config import settings

logger = structlog.get_logger(__name__)


# ===============================================================================
# CONFIGURATION
# ===============================================================================

# Default pruning thresholds (can be overridden via config)
DEFAULT_MAX_REVISION_HISTORY = 5
DEFAULT_MAX_ERRORS = 20
DEFAULT_MAX_CLAIMS = 100

# State size warning threshold (1MB)
STATE_SIZE_WARNING_THRESHOLD = 1_000_000


# ===============================================================================
# STATE SIZE CALCULATION
# ===============================================================================


def get_state_size(state: dict) -> int:
    """
    Calculate approximate state size in bytes.

    Uses JSON serialization to estimate size, which closely matches
    how the state is stored/transmitted.

    Args:
        state: The state dictionary to measure.

    Returns:
        int: Approximate size in bytes.
    """
    try:
        # Use JSON serialization for accurate size estimation
        json_str = json.dumps(state, default=str)
        return len(json_str.encode("utf-8"))
    except (TypeError, ValueError) as e:
        # Fallback to sys.getsizeof for complex objects
        logger.warning("state_size_json_failed", error=str(e))
        return _recursive_sizeof(state)


def _recursive_sizeof(obj: Any, seen: Optional[set] = None) -> int:
    """
    Recursively calculate object size including nested objects.

    Args:
        obj: Object to measure.
        seen: Set of already-seen object ids to prevent infinite loops.

    Returns:
        int: Approximate size in bytes.
    """
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    seen.add(obj_id)
    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(_recursive_sizeof(k, seen) + _recursive_sizeof(v, seen)
                   for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(_recursive_sizeof(item, seen) for item in obj)

    return size


def get_field_sizes(state: dict) -> dict[str, int]:
    """
    Get sizes of individual state fields.

    Useful for identifying which fields are consuming the most memory.

    Args:
        state: The state dictionary to analyze.

    Returns:
        dict: Map of field names to their sizes in bytes.
    """
    sizes = {}
    for key, value in state.items():
        if value is not None:
            try:
                sizes[key] = len(json.dumps(value, default=str).encode("utf-8"))
            except (TypeError, ValueError):
                sizes[key] = _recursive_sizeof(value)
    return sizes


# ===============================================================================
# REVISION HISTORY PRUNING
# ===============================================================================


async def prune_revision_history(
    state: dict,
    max_entries: int = DEFAULT_MAX_REVISION_HISTORY,
    archive: bool = True,
) -> dict:
    """
    Keep only recent revision history, optionally archiving old entries.

    Revision history tracks each iteration's changes and quality scores.
    Keeping unbounded history can grow large in complex sessions.

    Args:
        state: The state dictionary to prune.
        max_entries: Maximum number of recent entries to keep.
        archive: If True, archive old entries to database before pruning.

    Returns:
        dict: Updated state with pruned revision_history.
    """
    revision_history = state.get("revision_history", [])

    if len(revision_history) <= max_entries:
        return state

    session_id = state.get("session_id", "unknown")
    entries_to_archive = revision_history[:-max_entries]
    entries_to_keep = revision_history[-max_entries:]

    logger.info(
        "pruning_revision_history",
        session_id=session_id,
        total_entries=len(revision_history),
        archiving=len(entries_to_archive),
        keeping=len(entries_to_keep),
    )

    # Archive old entries if requested
    if archive and entries_to_archive:
        try:
            await archive_old_revisions(session_id, entries_to_archive)
        except Exception as e:
            logger.warning(
                "revision_archive_failed",
                session_id=session_id,
                error=str(e),
            )
            # Continue with pruning even if archive fails

    # Update state with pruned history
    state["revision_history"] = entries_to_keep

    return state


async def archive_old_revisions(session_id: str, revisions: list) -> None:
    """
    Archive old revisions to separate database storage.

    This allows historical revision data to be preserved for debugging
    and analysis without bloating the active state.

    Args:
        session_id: The session ID these revisions belong to.
        revisions: List of revision entries to archive.
    """
    try:
        from utils.supabase_client import get_supabase_client

        client = get_supabase_client()

        # Batch insert all revisions
        rows = []
        for i, revision in enumerate(revisions):
            rows.append({
                "session_id": session_id,
                "revision_index": i,
                "revision_data": revision,
                "archived_at": datetime.utcnow().isoformat(),
            })

        if rows:
            client.table("revision_archive").insert(rows).execute()
            logger.info(
                "revisions_archived",
                session_id=session_id,
                count=len(rows),
            )

    except ImportError:
        logger.warning(
            "archive_skipped_no_supabase",
            session_id=session_id,
        )
    except Exception as e:
        logger.error(
            "archive_failed",
            session_id=session_id,
            error=str(e),
        )
        raise


# ===============================================================================
# ERRORS PRUNING
# ===============================================================================


async def prune_errors(
    state: dict,
    max_entries: int = DEFAULT_MAX_ERRORS,
) -> dict:
    """
    Keep only recent errors, discarding old ones.

    Error logs can accumulate in long-running or retried workflows.
    This keeps the most recent errors which are most relevant for debugging.

    Args:
        state: The state dictionary to prune.
        max_entries: Maximum number of recent errors to keep.

    Returns:
        dict: Updated state with pruned errors.
    """
    errors = state.get("errors", [])

    if len(errors) <= max_entries:
        return state

    session_id = state.get("session_id", "unknown")
    original_count = len(errors)

    # Keep the most recent errors
    state["errors"] = errors[-max_entries:]

    logger.info(
        "pruning_errors",
        session_id=session_id,
        original_count=original_count,
        pruned_to=len(state["errors"]),
        discarded=original_count - max_entries,
    )

    return state


# ===============================================================================
# CROSS-REFERENCE INDEX PRUNING
# ===============================================================================


async def prune_cross_reference_index(
    state: dict,
    max_claims: int = DEFAULT_MAX_CLAIMS,
) -> dict:
    """
    Prune the cross-reference index to limit claim accumulation.

    The cross-reference index tracks claims across sections with evidence
    tiers. In complex products, this can grow very large.

    Pruning strategy:
    1. Keep all E1-E2 tier claims (highest evidence quality)
    2. Keep recent E3-E4 claims up to the limit
    3. Recalculate statistics after pruning

    Args:
        state: The state dictionary to prune.
        max_claims: Maximum number of claims to keep.

    Returns:
        dict: Updated state with pruned cross_reference_index.
    """
    cross_ref = state.get("cross_reference_index")

    if not cross_ref or not isinstance(cross_ref, dict):
        return state

    claims = cross_ref.get("claims", [])

    if len(claims) <= max_claims:
        return state

    session_id = state.get("session_id", "unknown")

    # Separate claims by evidence tier
    high_evidence_claims = []  # E1, E2
    other_claims = []  # E3, E4, E5

    for claim in claims:
        tier = claim.get("evidence_tier", "E4")
        if tier in ("E1", "E2"):
            high_evidence_claims.append(claim)
        else:
            other_claims.append(claim)

    # Calculate how many other claims we can keep
    remaining_slots = max_claims - len(high_evidence_claims)

    if remaining_slots > 0:
        # Keep the most recent other claims
        pruned_claims = high_evidence_claims + other_claims[-remaining_slots:]
    else:
        # Only keep high evidence claims, truncated if necessary
        pruned_claims = high_evidence_claims[-max_claims:]

    logger.info(
        "pruning_cross_reference_index",
        session_id=session_id,
        original_claims=len(claims),
        high_evidence_kept=min(len(high_evidence_claims), max_claims),
        other_kept=max(0, remaining_slots),
        final_count=len(pruned_claims),
    )

    # Recalculate statistics
    tier_distribution: dict[str, int] = {}
    for claim in pruned_claims:
        tier = claim.get("evidence_tier", "E4")
        tier_distribution[tier] = tier_distribution.get(tier, 0) + 1

    weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
    if pruned_claims:
        total_weight = sum(
            weights.get(c.get("evidence_tier", "E4"), 0.3)
            for c in pruned_claims
        )
        evidence_score = total_weight / len(pruned_claims)
    else:
        evidence_score = 0.0

    state["cross_reference_index"] = {
        "claims": pruned_claims,
        "total_claims": len(pruned_claims),
        "tier_distribution": tier_distribution,
        "evidence_score": round(evidence_score, 3),
        "unresolved_dependencies": cross_ref.get("unresolved_dependencies", []),
        "pruned": True,
        "original_claim_count": len(claims),
    }

    return state


# ===============================================================================
# COMPREHENSIVE STATE PRUNING
# ===============================================================================


async def prune_state(
    state: dict,
    max_revision_history: int = DEFAULT_MAX_REVISION_HISTORY,
    max_errors: int = DEFAULT_MAX_ERRORS,
    max_claims: int = DEFAULT_MAX_CLAIMS,
    archive_revisions: bool = True,
) -> dict:
    """
    Prune all unbounded fields in the state.

    This is the main entry point for state pruning, typically called
    after revision loops complete or before persisting state.

    Args:
        state: The state dictionary to prune.
        max_revision_history: Maximum revision history entries to keep.
        max_errors: Maximum error entries to keep.
        max_claims: Maximum claims to keep in cross-reference index.
        archive_revisions: Whether to archive old revisions to database.

    Returns:
        dict: Pruned state with reduced memory footprint.
    """
    session_id = state.get("session_id", "unknown")

    # Calculate size before pruning
    size_before = get_state_size(state)

    # Log field sizes for debugging
    if size_before > STATE_SIZE_WARNING_THRESHOLD:
        field_sizes = get_field_sizes(state)
        largest_fields = sorted(
            field_sizes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        logger.warning(
            "state_size_large",
            session_id=session_id,
            size_bytes=size_before,
            largest_fields=dict(largest_fields),
        )

    # Prune each unbounded field
    state = await prune_revision_history(
        state,
        max_entries=max_revision_history,
        archive=archive_revisions,
    )

    state = await prune_errors(state, max_entries=max_errors)

    state = await prune_cross_reference_index(state, max_claims=max_claims)

    # Calculate size after pruning
    size_after = get_state_size(state)
    reduction = size_before - size_after
    reduction_pct = (reduction / size_before * 100) if size_before > 0 else 0

    logger.info(
        "state_pruned",
        session_id=session_id,
        size_before=size_before,
        size_after=size_after,
        reduction_bytes=reduction,
        reduction_pct=round(reduction_pct, 1),
    )

    return state


# ===============================================================================
# PRUNING CONFIGURATION
# ===============================================================================


class PruningConfig:
    """
    Configuration for state pruning thresholds.

    Can be customized based on environment or workflow requirements.
    """

    def __init__(
        self,
        max_revision_history: int = DEFAULT_MAX_REVISION_HISTORY,
        max_errors: int = DEFAULT_MAX_ERRORS,
        max_claims: int = DEFAULT_MAX_CLAIMS,
        archive_revisions: bool = True,
        prune_on_finalize: bool = True,
        prune_after_revision: bool = True,
    ):
        self.max_revision_history = max_revision_history
        self.max_errors = max_errors
        self.max_claims = max_claims
        self.archive_revisions = archive_revisions
        self.prune_on_finalize = prune_on_finalize
        self.prune_after_revision = prune_after_revision

    @classmethod
    def from_settings(cls) -> "PruningConfig":
        """
        Create pruning config from application settings.

        Returns:
            PruningConfig with values from settings (using defaults if not configured).
        """
        return cls(
            max_revision_history=getattr(
                settings, "pruning_max_revision_history", DEFAULT_MAX_REVISION_HISTORY
            ),
            max_errors=getattr(
                settings, "pruning_max_errors", DEFAULT_MAX_ERRORS
            ),
            max_claims=getattr(
                settings, "pruning_max_claims", DEFAULT_MAX_CLAIMS
            ),
            archive_revisions=getattr(
                settings, "pruning_archive_revisions", True
            ),
            prune_on_finalize=getattr(
                settings, "pruning_on_finalize", True
            ),
            prune_after_revision=getattr(
                settings, "pruning_after_revision", True
            ),
        )


# Default pruning config instance
default_pruning_config = PruningConfig()
