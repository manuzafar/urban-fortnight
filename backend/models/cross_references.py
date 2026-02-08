"""
Cross-Reference System — every claim gets a unique ID and evidence tier.

This module provides the backbone for tracking claims across all sections
of an inception pack, enabling evidence grading, dependency tracking,
and stakeholder-specific views.

Evidence Tiers:
    E1 (Primary Research): User-uploaded primary research data
    E2 (Verified Source): Search-grounded claims with citation URLs
    E3 (Industry Data): Published reports, analyst estimates
    E4 (Hypothesis): LLM inference without direct evidence
    E5 (Assumption): Structural assumptions underlying analysis
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EvidenceTier(str, Enum):
    """Evidence tier classification for claims."""

    E1_PRIMARY = "E1"       # User-uploaded primary research
    E2_VERIFIED = "E2"      # Search-grounded with citation URL
    E3_INDUSTRY = "E3"      # Published reports, analyst estimates
    E4_HYPOTHESIS = "E4"    # LLM inference without direct evidence
    E5_ASSUMPTION = "E5"    # Structural assumption underlying analysis


# Evidence tier weights for scoring
EVIDENCE_WEIGHTS: dict[str, float] = {
    "E1": 1.0,
    "E2": 0.85,
    "E3": 0.6,
    "E4": 0.3,
    "E5": 0.1,
}


# Section prefix mapping for claim IDs
SECTION_PREFIXES: dict[str, str] = {
    "Market Intelligence": "MI",
    "Competitive Landscape": "CL",
    "Customer Personas": "CP",
    "Business Case": "BC",
    "Go-to-Market": "GM",
    "Financial Model": "FM",
    "Product Requirements": "PR",
    "Technical Architecture": "TA",
    "Regulatory & Compliance": "RC",
    "Risk Assessment": "RM",
    "Executive Summary": "ES",
}


class Claim(BaseModel):
    """
    A single claim extracted from agent output.

    Each claim is uniquely identified and graded by evidence tier,
    with optional dependency tracking to other claims.

    Attributes:
        claim_id: Unique identifier ({section_prefix}-{number}, e.g., MI-1, BC-3)
        section: The section this claim belongs to
        statement: The actual claim text
        evidence_tier: Quality grade (E1-E5)
        confidence: Agent's confidence in the claim (0.0-1.0)
        source: Optional citation URL or reference
        depends_on: List of claim_ids this claim relies on
        supports: List of claim_ids that this claim supports
        validation_method: How to validate this claim
        validation_effort: Estimated effort (quick|moderate|significant)
    """

    claim_id: str = Field(
        ...,
        description="Unique claim identifier (e.g., MI-1, BC-3)",
        pattern=r"^[A-Z]{2}-\d+$",
    )
    section: str = Field(
        ...,
        description="Section this claim belongs to",
    )
    statement: str = Field(
        ...,
        description="The claim text",
        min_length=10,
    )
    evidence_tier: EvidenceTier = Field(
        ...,
        description="Evidence quality tier (E1-E5)",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Agent's confidence in this claim",
    )
    source: Optional[str] = Field(
        default=None,
        description="Citation URL or reference",
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="Claim IDs this claim depends on",
    )
    supports: list[str] = Field(
        default_factory=list,
        description="Claim IDs this claim supports",
    )
    validation_method: Optional[str] = Field(
        default=None,
        description="How to validate this claim",
    )
    validation_effort: Optional[str] = Field(
        default=None,
        description="Validation effort: quick|moderate|significant",
        pattern=r"^(quick|moderate|significant)$",
    )

    def get_weight(self) -> float:
        """Get the evidence weight for this claim's tier."""
        return EVIDENCE_WEIGHTS.get(self.evidence_tier.value, 0.3)


class CrossReferenceIndex(BaseModel):
    """
    Index of all claims across the inception pack.

    Provides aggregate statistics, evidence scoring, and utilities
    for analyzing claim quality and dependencies.

    Attributes:
        claims: List of all extracted claims
        total_claims: Count of claims
        tier_distribution: Count per evidence tier
        evidence_score: Weighted average score (0.0-1.0)
        unresolved_dependencies: Claims with missing dependencies
    """

    claims: list[Claim] = Field(default_factory=list)
    total_claims: int = 0
    tier_distribution: dict[str, int] = Field(default_factory=dict)
    evidence_score: float = 0.0
    unresolved_dependencies: list[str] = Field(default_factory=list)

    def add_claims(self, new_claims: list[Claim]) -> None:
        """
        Add new claims to the index and recalculate statistics.

        Args:
            new_claims: List of claims to add
        """
        self.claims.extend(new_claims)
        self._recalculate_statistics()

    def _recalculate_statistics(self) -> None:
        """Recalculate all aggregate statistics."""
        self.total_claims = len(self.claims)

        # Calculate tier distribution
        self.tier_distribution = {}
        for claim in self.claims:
            tier = claim.evidence_tier.value
            self.tier_distribution[tier] = self.tier_distribution.get(tier, 0) + 1

        # Calculate weighted evidence score
        if self.claims:
            total_weight = sum(claim.get_weight() for claim in self.claims)
            self.evidence_score = total_weight / len(self.claims)
        else:
            self.evidence_score = 0.0

        # Find unresolved dependencies
        all_claim_ids = {claim.claim_id for claim in self.claims}
        self.unresolved_dependencies = []
        for claim in self.claims:
            for dep_id in claim.depends_on:
                if dep_id not in all_claim_ids and dep_id not in self.unresolved_dependencies:
                    self.unresolved_dependencies.append(dep_id)

    def get_claims_by_section(self, section_prefix: str) -> list[Claim]:
        """
        Get all claims for a specific section.

        Args:
            section_prefix: Two-letter section prefix (e.g., "MI", "BC")

        Returns:
            List of claims for that section
        """
        return [c for c in self.claims if c.claim_id.startswith(section_prefix)]

    def get_claims_by_tier(self, tier: EvidenceTier) -> list[Claim]:
        """
        Get all claims with a specific evidence tier.

        Args:
            tier: Evidence tier to filter by

        Returns:
            List of claims with that tier
        """
        return [c for c in self.claims if c.evidence_tier == tier]

    def get_validation_priorities(self) -> list[Claim]:
        """
        Get claims prioritized for validation.

        Returns E4 and E5 claims sorted by number of dependents,
        so validating them would upgrade the most other claims.

        Returns:
            List of claims prioritized for validation
        """
        # Find E4 and E5 claims
        hypothesis_claims = [
            c for c in self.claims
            if c.evidence_tier in (EvidenceTier.E4_HYPOTHESIS, EvidenceTier.E5_ASSUMPTION)
        ]

        # Count how many claims depend on each
        def count_dependents(claim: Claim) -> int:
            return sum(
                1 for c in self.claims
                if claim.claim_id in c.depends_on
            )

        # Sort by number of dependents (descending) then confidence (ascending)
        return sorted(
            hypothesis_claims,
            key=lambda c: (-count_dependents(c), c.confidence),
        )

    def get_dependency_chain(self, claim_id: str) -> list[str]:
        """
        Get the full dependency chain for a claim.

        Args:
            claim_id: The claim to trace dependencies for

        Returns:
            List of claim IDs in dependency order
        """
        chain: list[str] = []
        visited: set[str] = set()

        def trace(cid: str) -> None:
            if cid in visited:
                return
            visited.add(cid)

            claim = next((c for c in self.claims if c.claim_id == cid), None)
            if claim:
                for dep_id in claim.depends_on:
                    trace(dep_id)
                chain.append(cid)

        trace(claim_id)
        return chain

    def to_summary(self, max_claims: int = 20) -> dict:
        """
        Generate a summary suitable for prompt injection.

        Args:
            max_claims: Maximum number of claims to include

        Returns:
            Summary dict with key statistics
        """
        # Get highest-impact claims across sections
        priority_claims = self.get_validation_priorities()[:max_claims]

        return {
            "total_claims": self.total_claims,
            "evidence_score": round(self.evidence_score, 2),
            "tier_distribution": self.tier_distribution,
            "unresolved_count": len(self.unresolved_dependencies),
            "validation_priorities": [
                {
                    "claim_id": c.claim_id,
                    "statement": c.statement[:100] + "..." if len(c.statement) > 100 else c.statement,
                    "tier": c.evidence_tier.value,
                    "validation_method": c.validation_method,
                }
                for c in priority_claims
            ],
        }


def merge_cross_reference_indices(
    current: CrossReferenceIndex | None,
    new: CrossReferenceIndex | None,
) -> CrossReferenceIndex:
    """
    Merge two cross-reference indices (reducer for parallel state merging).

    Args:
        current: Existing index (may be None)
        new: New index to merge (may be None)

    Returns:
        Merged index with all claims
    """
    if current is None and new is None:
        return CrossReferenceIndex()
    if current is None:
        return new if new else CrossReferenceIndex()
    if new is None:
        return current

    # Merge claims, avoiding duplicates by claim_id
    existing_ids = {c.claim_id for c in current.claims}
    merged_claims = current.claims.copy()

    for claim in new.claims:
        if claim.claim_id not in existing_ids:
            merged_claims.append(claim)
            existing_ids.add(claim.claim_id)

    merged = CrossReferenceIndex(claims=merged_claims)
    merged._recalculate_statistics()
    return merged
