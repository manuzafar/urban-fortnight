"""
Risk Assessment Eval — Specialized evaluation for risk assessment outputs.

Criteria:
- Risk categories: Market, technical, financial, operational covered
- Probability/impact: Each risk rated on likelihood and severity
- Mitigation strategies: Specific mitigations per risk
- Risk matrix: Visual/tabular risk prioritization
- Monitoring plan: How risks will be tracked
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


EXPECTED_RISK_CATEGORIES = {"market", "technical", "financial", "operational", "regulatory", "competitive"}


class RiskAssessmentEval(BaseEval):
    """Evaluates risk assessment for coverage and actionability."""

    name = "risk_assessment_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks risk assessment covers key categories with mitigations"
    severity = EvalSeverity.WARNING
    applicable_agents = ["risk_assessment"]

    MIN_RISKS = 5
    MIN_CATEGORIES = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate risk assessment output."""
        # Handle non-dict outputs
        if not isinstance(agent_output, dict):
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=False,
                score=0.0,
                severity=self.severity,
                message=f"Invalid output type: expected dict, got {type(agent_output).__name__}",
                agent_name=agent_name,
            )

        checks = []
        score_components = []

        # Get risks (may be in different formats)
        risks = agent_output.get("risks", [])
        if not risks:
            risks = agent_output.get("risk_items", [])
        if not risks:
            risks = agent_output.get("top_3_risks", [])
        if not risks and "risk_matrix" in agent_output:
            matrix = agent_output.get("risk_matrix", {})
            if isinstance(matrix, dict):
                risks = matrix.get("risks", [])
            elif isinstance(matrix, list):
                risks = matrix

        risk_count = len(risks)

        # Check risk count
        count_passed = risk_count >= self.MIN_RISKS
        checks.append({
            "name": "risk_count",
            "passed": count_passed,
            "actual": risk_count,
            "required": self.MIN_RISKS,
        })
        score_components.append(min(risk_count / self.MIN_RISKS, 1.0))

        # Check category coverage
        categories_found = set()
        for risk in risks:
            category = str(risk.get("category", risk.get("risk_category", ""))).lower()
            for expected in EXPECTED_RISK_CATEGORIES:
                if expected in category:
                    categories_found.add(expected)

        category_count = len(categories_found)
        categories_passed = category_count >= self.MIN_CATEGORIES
        checks.append({
            "name": "category_coverage",
            "passed": categories_passed,
            "actual": f"{category_count} categories: {', '.join(categories_found)}",
            "required": f">= {self.MIN_CATEGORIES} categories",
        })
        score_components.append(min(category_count / self.MIN_CATEGORIES, 1.0))

        # Check probability/impact ratings
        risks_with_ratings = sum(
            1 for r in risks
            if (r.get("likelihood") or r.get("probability")) and
               (r.get("impact") or r.get("severity"))
        )
        rating_rate = risks_with_ratings / max(risk_count, 1)
        ratings_passed = rating_rate >= 0.8 or risk_count == 0
        checks.append({
            "name": "probability_impact_ratings",
            "passed": ratings_passed,
            "actual": f"{risks_with_ratings}/{risk_count} have ratings",
            "required": "80% with likelihood/impact",
        })
        score_components.append(rating_rate if risk_count else 1.0)

        # Check mitigations
        risks_with_mitigations = sum(
            1 for r in risks
            if r.get("mitigation") or r.get("mitigation_strategy") or r.get("mitigations")
        )
        mitigation_rate = risks_with_mitigations / max(risk_count, 1)
        mitigations_passed = mitigation_rate >= 0.8 or risk_count == 0
        checks.append({
            "name": "mitigation_strategies",
            "passed": mitigations_passed,
            "actual": f"{risks_with_mitigations}/{risk_count} have mitigations",
            "required": "80% with mitigations",
        })
        score_components.append(mitigation_rate if risk_count else 1.0)

        # Check risk matrix
        risk_matrix = agent_output.get("risk_matrix")
        has_matrix = False
        if risk_matrix:
            if isinstance(risk_matrix, list):
                has_matrix = len(risk_matrix) > 0
            elif isinstance(risk_matrix, dict):
                has_matrix = bool(
                    risk_matrix.get("risks") or
                    risk_matrix.get("high") or
                    risk_matrix.get("matrix_data")
                )
        checks.append({
            "name": "risk_matrix",
            "passed": has_matrix,
            "actual": "present" if has_matrix else "missing",
            "required": "risk prioritization matrix",
        })
        score_components.append(1.0 if has_matrix else 0.5)

        # Check monitoring plan
        monitoring = agent_output.get("monitoring_plan", agent_output.get("monitoring"))
        has_monitoring = bool(monitoring)
        if not has_monitoring:
            # Check if risks have monitoring indicators
            risks_with_monitoring = sum(
                1 for r in risks
                if r.get("monitoring") or r.get("indicators") or r.get("warning_signs")
            )
            has_monitoring = risks_with_monitoring >= risk_count * 0.5
        checks.append({
            "name": "monitoring_plan",
            "passed": has_monitoring,
            "actual": "present" if has_monitoring else "missing",
            "required": "monitoring approach",
        })
        score_components.append(1.0 if has_monitoring else 0.5)

        # Check overall risk score/summary
        has_summary = bool(agent_output.get("overall_risk_level")) or \
                      bool(agent_output.get("risk_summary")) or \
                      bool(agent_output.get("executive_summary"))
        checks.append({
            "name": "risk_summary",
            "passed": has_summary,
            "actual": "present" if has_summary else "missing",
            "required": "overall risk summary",
        })
        score_components.append(1.0 if has_summary else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Risk assessment complete: {risk_count} risks across {category_count} categories"
        else:
            message = f"Risk assessment needs: {', '.join(failed_checks)}"

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
                "risk_count": risk_count,
                "category_count": category_count,
                "categories_found": list(categories_found),
            },
        )


# Register the eval
EvalRegistry.register(RiskAssessmentEval())
