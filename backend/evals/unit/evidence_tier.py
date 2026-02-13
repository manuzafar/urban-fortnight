"""
Evidence Tier Eval — Checks evidence tier distribution in claims.

This eval analyzes the evidence tiers (E1-E5) of claims across agent outputs
to ensure a healthy distribution with enough grounded evidence.

Thresholds:
- E1-E3 (grounded) claims >= 30%
- E1-E2 (verified) claims >= 10%
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)
from agents.confidence_calibrator import TIER_WEIGHTS


# Thresholds for evidence tier distribution
GROUNDED_THRESHOLD = 0.30  # E1-E3 should be >= 30%
VERIFIED_THRESHOLD = 0.10  # E1-E2 should be >= 10%


class EvidenceTierEval(BaseEval):
    """
    Evaluates evidence tier distribution in agent outputs.

    Checks that outputs have sufficient grounded evidence (E1-E3)
    and aren't overly reliant on hypotheses and assumptions (E4-E5).
    """

    name = "evidence_tier_distribution"
    eval_type = EvalType.UNIT
    description = "Checks evidence tier distribution meets quality thresholds"
    severity = EvalSeverity.WARNING

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Analyze evidence tier distribution.

        Args:
            agent_output: The agent's output dictionary
            agent_name: Name of the agent
            context: Should contain 'full_state' with cross_reference_index

        Returns:
            EvalResult with distribution analysis
        """
        # Get claims from cross-reference index
        claims = self._extract_claims(agent_output, agent_name, context)

        if not claims:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=1.0,
                severity=EvalSeverity.INFO,
                message="No claims found to analyze",
                agent_name=agent_name,
            )

        # Calculate tier distribution
        tier_counts = self._count_tiers(claims)
        total_claims = sum(tier_counts.values())

        # Calculate percentages
        grounded_count = tier_counts.get("E1", 0) + tier_counts.get("E2", 0) + tier_counts.get("E3", 0)
        verified_count = tier_counts.get("E1", 0) + tier_counts.get("E2", 0)

        grounded_pct = grounded_count / total_claims if total_claims > 0 else 0
        verified_pct = verified_count / total_claims if total_claims > 0 else 0

        # Calculate weighted evidence score
        weighted_sum = sum(
            count * TIER_WEIGHTS.get(tier, 0.1)
            for tier, count in tier_counts.items()
        )
        evidence_score = weighted_sum / total_claims if total_claims > 0 else 0

        # Check thresholds
        passes_grounded = grounded_pct >= GROUNDED_THRESHOLD
        passes_verified = verified_pct >= VERIFIED_THRESHOLD

        passed = passes_grounded and passes_verified

        # Build message
        if passed:
            message = f"Evidence distribution healthy: {grounded_pct:.1%} grounded, {verified_pct:.1%} verified"
        else:
            issues = []
            if not passes_grounded:
                issues.append(f"grounded claims {grounded_pct:.1%} < {GROUNDED_THRESHOLD:.0%}")
            if not passes_verified:
                issues.append(f"verified claims {verified_pct:.1%} < {VERIFIED_THRESHOLD:.0%}")
            message = f"Evidence distribution below threshold: {', '.join(issues)}"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=passed,
            score=evidence_score,
            severity=self.severity if not passed else EvalSeverity.INFO,
            message=message,
            agent_name=agent_name,
            details={
                "total_claims": total_claims,
                "tier_counts": tier_counts,
                "grounded_percentage": round(grounded_pct, 3),
                "verified_percentage": round(verified_pct, 3),
                "evidence_score": round(evidence_score, 3),
                "thresholds": {
                    "grounded_minimum": GROUNDED_THRESHOLD,
                    "verified_minimum": VERIFIED_THRESHOLD,
                },
            },
        )

    def _extract_claims(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Extract claims relevant to this agent."""
        claims = []

        # Try to get from cross-reference index in context
        if context and "full_state" in context:
            cross_ref = context["full_state"].get("cross_reference_index", {})
            all_claims = cross_ref.get("claims", [])

            # Filter to claims from this agent's section
            section_prefix = self._get_section_prefix(agent_name)
            if section_prefix:
                claims = [
                    c for c in all_claims
                    if c.get("claim_id", "").startswith(section_prefix)
                ]
            else:
                claims = all_claims

        # Also look for evidence_tier fields in the agent output itself
        claims.extend(self._extract_inline_evidence(agent_output))

        return claims

    def _extract_inline_evidence(
        self,
        data: Any,
        path: str = "",
    ) -> list[dict[str, Any]]:
        """Recursively extract evidence tiers from nested structures."""
        claims = []

        if isinstance(data, dict):
            # Check if this dict has an evidence_tier field
            if "evidence_tier" in data:
                claims.append({
                    "claim_id": f"inline-{path}",
                    "evidence_tier": data["evidence_tier"],
                    "statement": data.get("description", data.get("statement", data.get("insight", ""))),
                })

            # Recurse into nested dicts
            for key, value in data.items():
                claims.extend(self._extract_inline_evidence(value, f"{path}.{key}"))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                claims.extend(self._extract_inline_evidence(item, f"{path}[{i}]"))

        return claims

    def _count_tiers(self, claims: list[dict[str, Any]]) -> dict[str, int]:
        """Count claims by tier."""
        counts: dict[str, int] = {}
        for claim in claims:
            tier = claim.get("evidence_tier", "E5")
            # Normalize tier format (E1 or E1_PRIMARY -> E1)
            if isinstance(tier, str):
                tier = tier.split("_")[0].upper()
            counts[tier] = counts.get(tier, 0) + 1
        return counts

    def _get_section_prefix(self, agent_name: str) -> str | None:
        """Get the claim ID prefix for an agent's section."""
        prefix_map = {
            "customer_research": "MI",
            "competitive_intelligence": "CL",
            "persona_development": "CP",
            "business_strategy": "BC",
            "gtm_agent": "GM",
            "financial_model_agent": "FM",
            "product_requirements": "PR",
            "technical_architect": "TA",
            "legal_regulatory": "RC",
            "risk_assessment": "RM",
            "executive_summary": "ES",
        }
        return prefix_map.get(agent_name)


# Register the eval
EvalRegistry.register(EvidenceTierEval())
