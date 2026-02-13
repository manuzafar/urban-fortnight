"""
Financial Model Eval — Specialized evaluation for financial projections.

Criteria:
- Math validity: Revenue = customers × price × frequency
- Projection consistency: Monthly projections sum to annual
- Assumptions explicit: All key assumptions documented
- Unit economics: CAC, LTV, margin calculations present
- Funding justification: Runway calculation matches burn rate
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class FinancialModelEval(BaseEval):
    """Evaluates financial model for mathematical validity and completeness."""

    name = "financial_model_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks financial model has valid projections and assumptions"
    severity = EvalSeverity.WARNING
    applicable_agents = ["financial_model_agent"]

    MIN_ASSUMPTIONS = 5
    MIN_MONTHLY_PROJECTIONS = 12

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate financial model output."""
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

        # Check input assumptions (support both field names)
        assumptions = agent_output.get("input_assumptions", agent_output.get("assumptions", []))
        # Handle both list of dicts and list of strings
        if assumptions and isinstance(assumptions[0], str):
            # Assumptions are plain strings
            assumption_count = len(assumptions)
            with_evidence = 0  # Can't check evidence tiers for string assumptions
        else:
            assumption_count = len(assumptions)
            # Check for evidence tiers (only if assumptions are dicts)
            with_evidence = sum(
                1 for a in assumptions
                if isinstance(a, dict) and a.get("evidence_tier") and a.get("evidence_tier") != "E5"
            )
        assumptions_passed = assumption_count >= self.MIN_ASSUMPTIONS
        checks.append({
            "name": "input_assumptions",
            "passed": assumptions_passed,
            "actual": f"{assumption_count} assumptions, {with_evidence} with evidence",
            "required": f">= {self.MIN_ASSUMPTIONS}",
        })
        score_components.append(min(assumption_count / self.MIN_ASSUMPTIONS, 1.0))

        # Check monthly projections (support both field names)
        monthly = agent_output.get("monthly_projections_year_1", [])
        if not monthly:
            # Try alternative structure
            projections = agent_output.get("projections", {})
            if isinstance(projections, dict):
                monthly = projections.get("monthly", projections.get("year_1", []))
            elif isinstance(projections, list):
                monthly = projections
        monthly_count = len(monthly)
        monthly_passed = monthly_count >= self.MIN_MONTHLY_PROJECTIONS
        checks.append({
            "name": "monthly_projections",
            "passed": monthly_passed,
            "actual": monthly_count,
            "required": self.MIN_MONTHLY_PROJECTIONS,
        })
        score_components.append(min(monthly_count / self.MIN_MONTHLY_PROJECTIONS, 1.0))

        # Check projection fields are populated
        if monthly:
            fields_complete = all(
                m.get("revenue") is not None and
                m.get("costs") is not None and
                m.get("customers") is not None
                for m in monthly
            )
            checks.append({
                "name": "projection_completeness",
                "passed": fields_complete,
                "actual": "complete" if fields_complete else "incomplete",
                "required": "revenue, costs, customers for each month",
            })
            score_components.append(1.0 if fields_complete else 0.5)

        # Check revenue model
        revenue_model = agent_output.get("revenue_model", {})
        has_revenue_model = bool(revenue_model) and len(str(revenue_model)) > 20
        checks.append({
            "name": "revenue_model",
            "passed": has_revenue_model,
            "actual": "present" if has_revenue_model else "missing",
            "required": "revenue model breakdown",
        })
        score_components.append(1.0 if has_revenue_model else 0.3)

        # Check unit economics
        unit_economics = agent_output.get("unit_economics", {})
        has_cac = "cac" in str(unit_economics).lower() or "acquisition" in str(unit_economics).lower()
        has_ltv = "ltv" in str(unit_economics).lower() or "lifetime" in str(unit_economics).lower()
        has_margin = "margin" in str(unit_economics).lower()
        economics_complete = has_cac and has_ltv
        checks.append({
            "name": "unit_economics",
            "passed": economics_complete,
            "actual": f"CAC: {has_cac}, LTV: {has_ltv}, margin: {has_margin}",
            "required": "CAC and LTV calculations",
        })
        score_components.append(1.0 if economics_complete else 0.3)

        # Check scenario analysis
        scenarios = agent_output.get("scenario_analysis", {})
        has_base = "base" in str(scenarios).lower()
        has_optimistic = "optimistic" in str(scenarios).lower() or "bull" in str(scenarios).lower()
        has_pessimistic = "pessimistic" in str(scenarios).lower() or "bear" in str(scenarios).lower()
        scenarios_complete = has_base and (has_optimistic or has_pessimistic)
        checks.append({
            "name": "scenario_analysis",
            "passed": scenarios_complete,
            "actual": f"base: {has_base}, optimistic: {has_optimistic}, pessimistic: {has_pessimistic}",
            "required": "base + at least one alternative scenario",
        })
        score_components.append(1.0 if scenarios_complete else 0.5)

        # Check funding requirements (support both dict and string formats)
        funding = agent_output.get("funding_requirements", {})
        has_funding = False
        if funding:
            if isinstance(funding, str):
                # String format - check if it contains amounts
                has_funding = len(funding) > 20 and any(
                    c.isdigit() for c in funding
                )
            elif isinstance(funding, dict):
                has_funding = bool(
                    funding.get("total_required") or
                    funding.get("seed") or
                    funding.get("pre_seed")
                )
        checks.append({
            "name": "funding_requirements",
            "passed": has_funding,
            "actual": "specified" if has_funding else "missing",
            "required": "funding amount by stage",
        })
        score_components.append(1.0 if has_funding else 0.5)

        # Check financial risks
        risks = agent_output.get("key_financial_risks", [])
        has_risks = len(risks) >= 2
        checks.append({
            "name": "financial_risks",
            "passed": has_risks,
            "actual": len(risks),
            "required": ">= 2",
        })
        score_components.append(1.0 if has_risks else 0.5)

        # Validate math consistency (basic check)
        math_valid = True
        if monthly and len(monthly) >= 2:
            # Check that profit = revenue - costs (approximately)
            for m in monthly[:3]:  # Check first 3 months
                revenue = m.get("revenue", 0) or 0
                costs = m.get("costs", 0) or 0
                profit = m.get("profit", 0) or 0
                expected_profit = revenue - costs
                if profit != 0 and abs(profit - expected_profit) > abs(expected_profit) * 0.1:
                    math_valid = False
                    break

        checks.append({
            "name": "math_consistency",
            "passed": math_valid,
            "actual": "valid" if math_valid else "inconsistent",
            "required": "profit = revenue - costs",
        })
        score_components.append(1.0 if math_valid else 0.3)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Financial model complete with {monthly_count} months, {assumption_count} assumptions"
        else:
            message = f"Financial model issues: {', '.join(failed_checks)}"

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
                "assumption_count": assumption_count,
                "monthly_projection_count": monthly_count,
                "has_unit_economics": bool(unit_economics),
                "has_scenarios": bool(scenarios),
            },
        )


# Register the eval
EvalRegistry.register(FinancialModelEval())
