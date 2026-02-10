"""
Confidence Calibrator — Adjusts confidence based on evidence quality.

This module provides calibration functions that adjust raw confidence scores
based on evidence tiers and source quality. This ensures that:
- High-evidence claims (E1-E2) maintain their confidence
- Lower-evidence claims (E4-E5) have appropriately reduced confidence
- Claims with sources get a credibility bonus

The goal is to provide more accurate confidence estimates for downstream
decision-making and validation prioritization.

Calibration Formula:
    calibrated = raw_confidence * tier_weight + source_bonus
    where:
        - tier_weight is based on evidence tier (E1=1.0, E5=0.1)
        - source_bonus is 0.1 if a source URL is provided
"""

from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# TIER WEIGHTS FOR CONFIDENCE CALIBRATION
# ═══════════════════════════════════════════════════════════════════════════════

# These weights represent the reliability multiplier for each evidence tier
# Higher tiers (E1-E2) are more reliable, so they get higher weights
TIER_WEIGHTS: dict[str, float] = {
    "E1": 1.0,    # Primary research - highest reliability
    "E2": 0.85,   # Verified external source
    "E3": 0.6,    # Industry data (less verified)
    "E4": 0.3,    # Hypothesis (reasoned but unverified)
    "E5": 0.1,    # Assumption (unvalidated premise)
}

# Bonus for having a verifiable source
SOURCE_BONUS = 0.1

# Maximum and minimum confidence bounds
MAX_CONFIDENCE = 1.0
MIN_CONFIDENCE = 0.0


def calibrate_claim_confidence(claim: dict[str, Any]) -> float:
    """
    Calibrate confidence for a single claim based on evidence tier and source quality.

    The calibration formula:
        calibrated = raw_confidence * tier_weight + source_bonus

    This ensures that:
    - E1/E2 claims with sources can reach near 1.0 confidence
    - E4/E5 claims without sources stay below 0.4 confidence
    - The presence of a source always helps, but doesn't dominate

    Args:
        claim: Dictionary containing claim data with keys:
            - evidence_tier: E1-E5 tier string
            - confidence: Raw confidence value (0.0-1.0)
            - source: Optional URL or reference string

    Returns:
        Calibrated confidence value (0.0-1.0)
    """
    tier = claim.get("evidence_tier", "E5")
    raw_confidence = claim.get("confidence", 0.5)
    has_source = bool(claim.get("source"))

    # Get tier weight (default to E5 weight if unknown tier)
    tier_weight = TIER_WEIGHTS.get(tier, TIER_WEIGHTS["E5"])

    # Apply source bonus if source is provided
    source_bonus = SOURCE_BONUS if has_source else 0.0

    # Calculate calibrated confidence
    calibrated = raw_confidence * tier_weight + source_bonus

    # Clamp to valid range
    calibrated = max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, calibrated))

    return round(calibrated, 3)


def calibrate_section_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Calibrate all claims in a section.

    This function processes a list of claims, adding calibrated confidence
    scores while preserving the original raw confidence for reference.

    Args:
        claims: List of claim dictionaries

    Returns:
        List of claims with added 'raw_confidence' and updated 'confidence' fields
    """
    calibrated_claims = []

    for claim in claims:
        claim_copy = dict(claim)

        # Preserve original confidence as raw_confidence
        claim_copy["raw_confidence"] = claim.get("confidence", 0.5)

        # Calculate and set calibrated confidence
        claim_copy["confidence"] = calibrate_claim_confidence(claim)

        calibrated_claims.append(claim_copy)

    return calibrated_claims


def calibrate_cross_reference_index(
    cross_ref: dict[str, Any]
) -> dict[str, Any]:
    """
    Calibrate all claims in a cross-reference index.

    This updates the claims in place and recalculates the evidence score
    based on calibrated confidences.

    Args:
        cross_ref: Cross-reference index dictionary with 'claims' list

    Returns:
        Updated cross-reference index with calibrated confidence scores
    """
    if not cross_ref:
        return cross_ref

    claims = cross_ref.get("claims", [])
    if not claims:
        return cross_ref

    # Calibrate all claims
    calibrated_claims = calibrate_section_claims(claims)

    # Recalculate evidence score based on calibrated confidences
    total_calibrated = sum(c.get("confidence", 0) for c in calibrated_claims)
    avg_confidence = total_calibrated / len(calibrated_claims) if calibrated_claims else 0

    # Update the index
    cross_ref_copy = dict(cross_ref)
    cross_ref_copy["claims"] = calibrated_claims
    cross_ref_copy["calibrated_evidence_score"] = round(avg_confidence, 3)

    logger.info(
        "cross_reference_calibrated",
        total_claims=len(calibrated_claims),
        original_score=cross_ref.get("evidence_score", 0),
        calibrated_score=cross_ref_copy["calibrated_evidence_score"],
    )

    return cross_ref_copy


def get_confidence_distribution(claims: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Get distribution statistics for claim confidences.

    Useful for understanding the overall quality of evidence in a pack.

    Args:
        claims: List of claim dictionaries

    Returns:
        Dictionary with distribution statistics:
            - total: Total number of claims
            - by_tier: Count by evidence tier
            - avg_raw_confidence: Average raw confidence
            - avg_calibrated_confidence: Average calibrated confidence
            - high_confidence_count: Claims with calibrated confidence >= 0.7
            - low_confidence_count: Claims with calibrated confidence < 0.3
    """
    if not claims:
        return {
            "total": 0,
            "by_tier": {},
            "avg_raw_confidence": 0,
            "avg_calibrated_confidence": 0,
            "high_confidence_count": 0,
            "low_confidence_count": 0,
        }

    # Count by tier
    by_tier: dict[str, int] = {}
    raw_confidences = []
    calibrated_confidences = []

    for claim in claims:
        tier = claim.get("evidence_tier", "E5")
        by_tier[tier] = by_tier.get(tier, 0) + 1

        raw_conf = claim.get("raw_confidence", claim.get("confidence", 0.5))
        cal_conf = claim.get("confidence", calibrate_claim_confidence(claim))

        raw_confidences.append(raw_conf)
        calibrated_confidences.append(cal_conf)

    # Calculate statistics
    total = len(claims)
    avg_raw = sum(raw_confidences) / total if total else 0
    avg_calibrated = sum(calibrated_confidences) / total if total else 0
    high_count = sum(1 for c in calibrated_confidences if c >= 0.7)
    low_count = sum(1 for c in calibrated_confidences if c < 0.3)

    return {
        "total": total,
        "by_tier": by_tier,
        "avg_raw_confidence": round(avg_raw, 3),
        "avg_calibrated_confidence": round(avg_calibrated, 3),
        "high_confidence_count": high_count,
        "low_confidence_count": low_count,
    }


def identify_weak_claims(
    claims: list[dict[str, Any]],
    threshold: float = 0.3,
) -> list[dict[str, Any]]:
    """
    Identify claims that need validation based on low calibrated confidence.

    These claims should be prioritized for validation experiments.

    Args:
        claims: List of claim dictionaries
        threshold: Confidence threshold below which claims are considered weak

    Returns:
        List of weak claims sorted by confidence (lowest first)
    """
    weak_claims = []

    for claim in claims:
        # Always calibrate to get the true confidence based on evidence tier
        calibrated_conf = calibrate_claim_confidence(claim)

        if calibrated_conf < threshold:
            weak_claim = dict(claim)
            weak_claim["calibrated_confidence"] = calibrated_conf
            weak_claims.append(weak_claim)

    # Sort by confidence (lowest first)
    weak_claims.sort(key=lambda c: c.get("calibrated_confidence", 0))

    return weak_claims


def identify_foundation_claims(
    claims: list[dict[str, Any]],
    threshold: float = 0.7,
) -> list[dict[str, Any]]:
    """
    Identify high-confidence claims that can serve as foundation.

    These claims are reliable enough to build upon and should be used
    as constraints for downstream agents.

    Args:
        claims: List of claim dictionaries
        threshold: Confidence threshold above which claims are strong

    Returns:
        List of strong claims sorted by confidence (highest first)
    """
    strong_claims = []

    for claim in claims:
        # Always calibrate to get the true confidence based on evidence tier
        calibrated_conf = calibrate_claim_confidence(claim)

        if calibrated_conf >= threshold:
            strong_claim = dict(claim)
            strong_claim["calibrated_confidence"] = calibrated_conf
            strong_claims.append(strong_claim)

    # Sort by confidence (highest first)
    strong_claims.sort(key=lambda c: c.get("calibrated_confidence", 0), reverse=True)

    return strong_claims


def calculate_section_quality_score(
    claims: list[dict[str, Any]],
    section_name: str,
) -> dict[str, Any]:
    """
    Calculate a quality score for a section based on its claims.

    The quality score considers:
    - Average calibrated confidence
    - Tier distribution (more E1-E2 is better)
    - Source coverage (percentage with sources)
    - Claim count adequacy

    Args:
        claims: List of claims for the section
        section_name: Name of the section for minimum requirements

    Returns:
        Dictionary with quality metrics:
            - score: Overall quality score (0.0-1.0)
            - avg_confidence: Average calibrated confidence
            - tier_score: Score based on tier distribution
            - source_coverage: Percentage of claims with sources
            - claim_adequacy: Whether minimum claims met
    """
    from agents.claim_extractor import MIN_CLAIMS_PER_SECTION

    if not claims:
        return {
            "score": 0.0,
            "avg_confidence": 0.0,
            "tier_score": 0.0,
            "source_coverage": 0.0,
            "claim_adequacy": False,
        }

    # Calculate average calibrated confidence
    confidences = [
        claim.get("confidence", calibrate_claim_confidence(claim))
        for claim in claims
    ]
    avg_confidence = sum(confidences) / len(confidences)

    # Calculate tier score (weighted by tier importance)
    tier_counts = {}
    for claim in claims:
        tier = claim.get("evidence_tier", "E5")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    tier_score_sum = sum(
        count * TIER_WEIGHTS.get(tier, 0.1)
        for tier, count in tier_counts.items()
    )
    max_tier_score = len(claims) * TIER_WEIGHTS["E1"]  # If all were E1
    tier_score = tier_score_sum / max_tier_score if max_tier_score > 0 else 0

    # Calculate source coverage
    with_source = sum(1 for c in claims if c.get("source"))
    source_coverage = with_source / len(claims)

    # Check claim adequacy
    min_required = MIN_CLAIMS_PER_SECTION.get(section_name, 3)
    claim_adequacy = len(claims) >= min_required

    # Calculate overall score (weighted combination)
    # 40% avg confidence + 30% tier score + 20% source coverage + 10% adequacy
    overall_score = (
        0.4 * avg_confidence +
        0.3 * tier_score +
        0.2 * source_coverage +
        0.1 * (1.0 if claim_adequacy else 0.5)
    )

    return {
        "score": round(overall_score, 3),
        "avg_confidence": round(avg_confidence, 3),
        "tier_score": round(tier_score, 3),
        "source_coverage": round(source_coverage, 3),
        "claim_adequacy": claim_adequacy,
        "claim_count": len(claims),
        "min_required": min_required,
    }
