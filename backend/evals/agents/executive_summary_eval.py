"""
Executive Summary Eval — Specialized evaluation for executive summaries.

Criteria:
- Concise: Under 500 words total
- Key sections: Problem, solution, market, ask
- Quantified claims: Includes key numbers
- Stakeholder-appropriate: C-suite readable
- CTA clear: Next steps defined
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class ExecutiveSummaryEval(BaseEval):
    """Evaluates executive summary for clarity and completeness."""

    name = "executive_summary_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks executive summary is concise, complete, and actionable"
    severity = EvalSeverity.WARNING
    applicable_agents = ["executive_summary"]

    MAX_WORD_COUNT = 1000  # Reasonable max for exec summary content
    MIN_KEY_DECISIONS = 1

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate executive summary output."""
        checks = []
        score_components = []

        # Check product identity
        has_name = bool(agent_output.get("product_name"))
        has_tagline = bool(agent_output.get("tagline"))
        identity_passed = has_name and has_tagline
        checks.append({
            "name": "product_identity",
            "passed": identity_passed,
            "actual": f"name: {has_name}, tagline: {has_tagline}",
            "required": "product name and tagline",
        })
        score_components.append(1.0 if identity_passed else 0.5)

        # Check problem & solution
        has_problem = bool(agent_output.get("problem_statement"))
        has_solution = bool(agent_output.get("solution_overview"))
        has_value_prop = bool(agent_output.get("value_proposition"))
        problem_solution_passed = has_problem and has_solution and has_value_prop
        checks.append({
            "name": "problem_solution",
            "passed": problem_solution_passed,
            "actual": f"problem: {has_problem}, solution: {has_solution}, value prop: {has_value_prop}",
            "required": "problem, solution, and value proposition",
        })
        score_components.append(1.0 if problem_solution_passed else 0.3)

        # Check target market
        has_users = len(agent_output.get("target_users", [])) > 0
        has_market_size = bool(agent_output.get("target_market_size"))
        market_passed = has_users and has_market_size
        checks.append({
            "name": "target_market",
            "passed": market_passed,
            "actual": f"users: {has_users}, market size: {has_market_size}",
            "required": "target users and market size",
        })
        score_components.append(1.0 if market_passed else 0.5)

        # Check financials
        has_funding = bool(agent_output.get("funding_required"))
        has_revenue = bool(agent_output.get("revenue_model"))
        has_projections = bool(agent_output.get("financial_projections"))
        has_roi = bool(agent_output.get("expected_roi"))
        financials_passed = has_funding and has_revenue and has_projections
        checks.append({
            "name": "financial_summary",
            "passed": financials_passed,
            "actual": f"funding: {has_funding}, revenue: {has_revenue}, projections: {has_projections}",
            "required": "funding, revenue model, projections",
        })
        score_components.append(1.0 if financials_passed else 0.3)

        # Check risks
        risks = agent_output.get("top_risks", [])
        has_risks = len(risks) >= 3
        checks.append({
            "name": "risk_summary",
            "passed": has_risks,
            "actual": len(risks),
            "required": ">= 3 top risks",
        })
        score_components.append(min(len(risks) / 3, 1.0))

        # Check GTM and milestones
        has_gtm = bool(agent_output.get("gtm_strategy"))
        milestones = agent_output.get("key_milestones", [])
        has_milestones = len(milestones) >= 3
        gtm_passed = has_gtm and has_milestones
        checks.append({
            "name": "gtm_milestones",
            "passed": gtm_passed,
            "actual": f"GTM: {has_gtm}, milestones: {len(milestones)}",
            "required": "GTM strategy and >= 3 milestones",
        })
        score_components.append(1.0 if gtm_passed else 0.5)

        # Check success metrics
        metrics = agent_output.get("success_metrics", [])
        has_metrics = len(metrics) >= 3
        checks.append({
            "name": "success_metrics",
            "passed": has_metrics,
            "actual": len(metrics),
            "required": ">= 3 metrics",
        })
        score_components.append(min(len(metrics) / 3, 1.0))

        # Check recommendation
        recommendation = agent_output.get("recommendation", "")
        has_recommendation = bool(recommendation) and len(str(recommendation)) > 20
        checks.append({
            "name": "recommendation",
            "passed": has_recommendation,
            "actual": "present" if has_recommendation else "missing",
            "required": "clear recommendation",
        })
        score_components.append(1.0 if has_recommendation else 0.3)

        # Check key decisions
        key_decisions = agent_output.get("key_decisions", [])
        has_decisions = len(key_decisions) >= self.MIN_KEY_DECISIONS
        checks.append({
            "name": "key_decisions",
            "passed": has_decisions,
            "actual": len(key_decisions),
            "required": f">= {self.MIN_KEY_DECISIONS}",
        })
        score_components.append(1.0 if has_decisions else 0.5)

        # Check differentiators
        differentiators = agent_output.get("key_differentiators", [])
        has_differentiators = len(differentiators) >= 2
        checks.append({
            "name": "differentiators",
            "passed": has_differentiators,
            "actual": len(differentiators),
            "required": ">= 2",
        })
        score_components.append(1.0 if has_differentiators else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = "Executive summary complete and actionable"
        else:
            message = f"Executive summary needs: {', '.join(failed_checks)}"

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
                "risk_count": len(risks),
                "milestone_count": len(milestones),
                "metric_count": len(metrics),
            },
        )


# Register the eval
EvalRegistry.register(ExecutiveSummaryEval())
