"""
Business Case Eval — Specialized evaluation for business strategy outputs.

Criteria:
- Market sizing: TAM/SAM/SOM with methodology
- Revenue model: Clear monetization strategy
- Competitive moat: Defensibility explained
- Risk factors: Business risks identified
- Success metrics: KPIs defined with targets
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class BusinessCaseEval(BaseEval):
    """Evaluates business case output for strategic completeness."""

    name = "business_case_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks business case has required strategic elements"
    severity = EvalSeverity.WARNING
    applicable_agents = ["business_strategy"]

    MIN_REVENUE_STREAMS = 1
    MIN_RISKS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate business case output."""
        checks = []
        score_components = []

        # Check Lean Canvas
        lean_canvas = agent_output.get("lean_canvas", {})
        canvas_complete = all([
            lean_canvas.get("problem"),
            lean_canvas.get("solution"),
            lean_canvas.get("unique_value_proposition"),
            lean_canvas.get("customer_segments"),
            lean_canvas.get("revenue_streams"),
        ])
        checks.append({
            "name": "lean_canvas",
            "passed": canvas_complete,
            "actual": "complete" if canvas_complete else "incomplete",
            "required": "all core fields",
        })
        score_components.append(1.0 if canvas_complete else 0.5)

        # Check revenue streams
        revenue_streams = agent_output.get("revenue_streams", [])
        revenue_passed = len(revenue_streams) >= self.MIN_REVENUE_STREAMS
        has_pricing = any(r.get("pricing_model") for r in revenue_streams)
        checks.append({
            "name": "revenue_model",
            "passed": revenue_passed and has_pricing,
            "actual": f"{len(revenue_streams)} streams, pricing: {has_pricing}",
            "required": f">= {self.MIN_REVENUE_STREAMS} with pricing",
        })
        score_components.append(1.0 if revenue_passed and has_pricing else 0.5)

        # Check financial projections
        has_year1 = bool(agent_output.get("year_1_projection"))
        has_year3 = bool(agent_output.get("year_3_projection"))
        has_breakeven = bool(agent_output.get("break_even_analysis"))
        projections_passed = has_year1 and has_year3
        checks.append({
            "name": "financial_projections",
            "passed": projections_passed,
            "actual": f"Y1: {has_year1}, Y3: {has_year3}, breakeven: {has_breakeven}",
            "required": "Year 1 and Year 3 projections",
        })
        score_components.append(1.0 if projections_passed else 0.3)

        # Check funding requirement
        funding = agent_output.get("funding_requirement")
        has_funding = bool(funding) and len(str(funding)) > 5
        checks.append({
            "name": "funding_requirement",
            "passed": has_funding,
            "actual": "specified" if has_funding else "missing",
            "required": "funding amount specified",
        })
        score_components.append(1.0 if has_funding else 0.5)

        # Check ROI analysis
        roi = agent_output.get("roi_analysis")
        has_roi = bool(roi) and len(str(roi)) > 10
        checks.append({
            "name": "roi_analysis",
            "passed": has_roi,
            "actual": "present" if has_roi else "missing",
            "required": "ROI analysis",
        })
        score_components.append(1.0 if has_roi else 0.5)

        # Check risks and mitigations
        risks = agent_output.get("risks_and_mitigations", [])
        risks_passed = len(risks) >= self.MIN_RISKS
        has_mitigations = all(
            r.get("mitigation") or r.get("mitigations")
            for r in risks[:self.MIN_RISKS] if isinstance(r, dict)
        )
        checks.append({
            "name": "risk_analysis",
            "passed": risks_passed,
            "actual": f"{len(risks)} risks, mitigations: {has_mitigations}",
            "required": f">= {self.MIN_RISKS} with mitigations",
        })
        score_components.append(min(len(risks) / self.MIN_RISKS, 1.0))

        # Check GTM strategy
        gtm = agent_output.get("go_to_market_strategy")
        has_gtm = bool(gtm) and len(str(gtm)) > 20
        checks.append({
            "name": "gtm_strategy",
            "passed": has_gtm,
            "actual": "present" if has_gtm else "missing",
            "required": "GTM strategy overview",
        })
        score_components.append(1.0 if has_gtm else 0.5)

        # Check unit economics (if present)
        unit_economics = agent_output.get("unit_economics", {})
        if unit_economics:
            has_cac = "cac" in str(unit_economics).lower()
            has_ltv = "ltv" in str(unit_economics).lower()
            economics_complete = has_cac and has_ltv
            checks.append({
                "name": "unit_economics",
                "passed": economics_complete,
                "actual": f"CAC: {has_cac}, LTV: {has_ltv}",
                "required": "CAC and LTV defined",
            })
            score_components.append(1.0 if economics_complete else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = "Business case complete with all strategic elements"
        else:
            message = f"Business case missing: {', '.join(failed_checks)}"

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
                "revenue_stream_count": len(revenue_streams),
                "risk_count": len(risks),
                "has_unit_economics": bool(unit_economics),
            },
        )


# Register the eval
EvalRegistry.register(BusinessCaseEval())
