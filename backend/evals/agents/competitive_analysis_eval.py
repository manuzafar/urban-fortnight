"""
Competitive Analysis Eval — Specialized evaluation for competitive intelligence.

Criteria:
- Real competitors: Names are verifiable companies (not invented)
- Feature comparison: Structured feature matrix exists
- Pricing data: At least 2 competitors have pricing info
- Differentiation: Clear differentiation strategy identified
- Market gaps: Identifies specific gaps to exploit
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class CompetitiveAnalysisEval(BaseEval):
    """Evaluates competitive analysis output for completeness and realism."""

    name = "competitive_analysis_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks competitive analysis has real data and insights"
    severity = EvalSeverity.WARNING
    applicable_agents = ["competitive_intelligence", "customer_research"]

    MIN_COMPETITORS = 2
    MIN_WITH_PRICING = 2

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate competitive analysis output."""
        checks = []
        score_components = []

        # Get competitive landscape (may be in customer_research or separate)
        landscape = agent_output.get("competitive_landscape", agent_output)

        # Check competitor count
        direct_competitors = landscape.get("direct_competitors", [])
        legacy_competitors = landscape.get("competitors", [])
        all_competitors = direct_competitors or legacy_competitors
        competitor_count = len(all_competitors)

        competitors_passed = competitor_count >= self.MIN_COMPETITORS
        checks.append({
            "name": "competitor_count",
            "passed": competitors_passed,
            "actual": competitor_count,
            "required": self.MIN_COMPETITORS,
        })
        score_components.append(min(competitor_count / self.MIN_COMPETITORS, 1.0))

        # Check for pricing data
        with_pricing = sum(
            1 for c in all_competitors
            if c.get("pricing") or c.get("pricing_model")
        )
        pricing_passed = with_pricing >= min(self.MIN_WITH_PRICING, competitor_count)
        checks.append({
            "name": "pricing_data",
            "passed": pricing_passed,
            "actual": with_pricing,
            "required": self.MIN_WITH_PRICING,
        })
        score_components.append(min(with_pricing / max(self.MIN_WITH_PRICING, 1), 1.0))

        # Check for differentiation thesis
        differentiation = landscape.get("differentiation_thesis") or landscape.get("market_position")
        has_differentiation = bool(differentiation and len(str(differentiation)) > 20)
        checks.append({
            "name": "differentiation_strategy",
            "passed": has_differentiation,
            "actual": "present" if has_differentiation else "missing",
            "required": "clear differentiation thesis",
        })
        score_components.append(1.0 if has_differentiation else 0.3)

        # Check for market gaps
        gaps = landscape.get("competitive_gaps", [])
        has_gaps = len(gaps) > 0
        checks.append({
            "name": "market_gaps",
            "passed": has_gaps,
            "actual": len(gaps),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_gaps else 0.5)

        # Check for positioning map
        positioning_map = landscape.get("positioning_map")
        has_positioning = positioning_map is not None and len(positioning_map.get("positions", [])) > 0
        checks.append({
            "name": "positioning_map",
            "passed": has_positioning,
            "actual": "present" if has_positioning else "missing",
            "required": "positioning map with positions",
        })
        score_components.append(1.0 if has_positioning else 0.5)

        # Check competitor profiles have strengths/weaknesses
        detailed_profiles = sum(
            1 for c in all_competitors
            if c.get("strengths") and c.get("weaknesses")
        )
        detailed_passed = detailed_profiles >= min(2, competitor_count)
        checks.append({
            "name": "detailed_profiles",
            "passed": detailed_passed,
            "actual": detailed_profiles,
            "required": ">=2 with strengths/weaknesses",
        })
        score_components.append(min(detailed_profiles / max(2, 1), 1.0))

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Competitive analysis complete with {competitor_count} competitors"
        else:
            message = f"Competitive analysis missing: {', '.join(failed_checks)}"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=all_passed,
            score=round(score, 3),
            severity=self.severity if not all_passed else EvalSeverity.INFO,
            message=message,
            agent_name=agent_name,
            details={
                "checks": checks,
                "competitor_count": competitor_count,
                "with_pricing": with_pricing,
                "has_differentiation": has_differentiation,
                "gap_count": len(gaps),
            },
        )


# Register the eval
EvalRegistry.register(CompetitiveAnalysisEval())
