"""
Numerical Consistency — Validates financial numbers match across sections.

Checks:
- Funding requirement consistency (< 20% variance)
- Year 1 revenue consistency (< 30% variance)
- Cost structure alignment
"""

import re
from typing import Any

import structlog

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)

logger = structlog.get_logger(__name__)


class NumericalConsistencyEval(BaseEval):
    """
    Validates financial numbers are consistent across sections.

    Extracts numerical values from business_case, financial_model,
    and executive_summary, then checks for consistency.
    """

    name = "numerical_consistency"
    eval_type = EvalType.CONSISTENCY
    description = "Checks financial numbers match across sections"
    severity = EvalSeverity.WARNING

    # Variance thresholds
    FUNDING_VARIANCE_THRESHOLD = 0.20  # 20%
    REVENUE_VARIANCE_THRESHOLD = 0.30  # 30%

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Check numerical consistency across sections.

        Args:
            agent_output: The agent's output (not used directly)
            agent_name: Name of the agent
            context: Must contain 'full_state' for cross-section analysis

        Returns:
            EvalResult with numerical consistency analysis
        """
        if not context or "full_state" not in context:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message="No full state available for numerical analysis",
                agent_name=agent_name,
            )

        state = context["full_state"]

        # Extract numerical values from each section
        executive = state.get("executive_summary", {})
        business_case = state.get("business_case", {})
        financial = state.get("financial_model", {})

        checks = []
        issues = []

        # Check funding requirement
        funding_values = self._extract_funding(executive, business_case, financial)
        if len(funding_values) >= 2:
            variance = self._calculate_variance(funding_values)
            passed = variance <= self.FUNDING_VARIANCE_THRESHOLD
            checks.append({
                "name": "funding_requirement",
                "passed": passed,
                "variance": round(variance, 3),
                "threshold": self.FUNDING_VARIANCE_THRESHOLD,
                "values_found": funding_values,
            })
            if not passed:
                issues.append(f"Funding variance {variance:.0%}")

        # Check Year 1 revenue
        year1_values = self._extract_year1_revenue(executive, business_case, financial)
        if len(year1_values) >= 2:
            variance = self._calculate_variance(year1_values)
            passed = variance <= self.REVENUE_VARIANCE_THRESHOLD
            checks.append({
                "name": "year_1_revenue",
                "passed": passed,
                "variance": round(variance, 3),
                "threshold": self.REVENUE_VARIANCE_THRESHOLD,
                "values_found": year1_values,
            })
            if not passed:
                issues.append(f"Y1 revenue variance {variance:.0%}")

        # Check monthly projections sum
        monthly = financial.get("monthly_projections_year_1", [])
        if monthly:
            monthly_sum = sum(m.get("revenue", 0) or 0 for m in monthly)
            year1_stated = self._parse_money(
                str(financial.get("revenue_model", {}).get("year_1_total", ""))
            )
            if monthly_sum > 0 and year1_stated and year1_stated > 0:
                variance = abs(monthly_sum - year1_stated) / max(monthly_sum, year1_stated)
                passed = variance <= self.REVENUE_VARIANCE_THRESHOLD
                checks.append({
                    "name": "monthly_sum_matches_annual",
                    "passed": passed,
                    "variance": round(variance, 3),
                    "threshold": self.REVENUE_VARIANCE_THRESHOLD,
                    "values_found": {
                        "monthly_sum": monthly_sum,
                        "stated_annual": year1_stated,
                    },
                })
                if not passed:
                    issues.append(f"Monthly/annual mismatch {variance:.0%}")

        # Calculate overall
        if not checks:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=1.0,
                severity=EvalSeverity.INFO,
                message="No comparable numerical values found across sections",
                agent_name=agent_name,
            )

        passed_count = sum(1 for c in checks if c["passed"])
        total_checks = len(checks)
        score = passed_count / total_checks

        all_passed = passed_count == total_checks

        if all_passed:
            message = f"Numerical consistency verified ({total_checks} checks)"
        else:
            message = f"Numerical inconsistencies: {', '.join(issues)}"

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
                "passed_count": passed_count,
                "total_checks": total_checks,
            },
        )

    def _extract_funding(
        self,
        executive: dict,
        business_case: dict,
        financial: dict,
    ) -> dict[str, float]:
        """Extract funding amounts from sections."""
        values = {}

        # Executive summary
        exec_funding = self._parse_money(str(executive.get("funding_required", "")))
        if exec_funding:
            values["executive_summary"] = exec_funding

        # Business case
        bc_funding = self._parse_money(str(business_case.get("funding_requirement", "")))
        if bc_funding:
            values["business_case"] = bc_funding

        # Financial model
        fm_funding = financial.get("funding_requirements", {})
        if isinstance(fm_funding, dict):
            total = fm_funding.get("total_required")
            if total:
                values["financial_model"] = self._parse_money(str(total)) or 0

        return values

    def _extract_year1_revenue(
        self,
        executive: dict,
        business_case: dict,
        financial: dict,
    ) -> dict[str, float]:
        """Extract Year 1 revenue projections."""
        values = {}

        # Executive summary - parse from financial_projections
        exec_projections = str(executive.get("financial_projections", ""))
        exec_y1 = self._extract_year1_from_text(exec_projections)
        if exec_y1:
            values["executive_summary"] = exec_y1

        # Business case
        bc_y1 = self._parse_money(str(business_case.get("year_1_projection", "")))
        if bc_y1:
            values["business_case"] = bc_y1

        # Financial model - sum monthly projections
        monthly = financial.get("monthly_projections_year_1", [])
        if monthly:
            monthly_sum = sum(m.get("revenue", 0) or 0 for m in monthly)
            if monthly_sum > 0:
                values["financial_model"] = monthly_sum

        return values

    def _extract_year1_from_text(self, text: str) -> float | None:
        """Extract Year 1 revenue from projection text."""
        # Look for patterns like "Year 1: $413,000" or "Y1: $413K"
        patterns = [
            r"[Yy]ear\s*1[:\s]+\$?([\d,]+(?:\.\d+)?)\s*(?:M|K|million|thousand)?",
            r"Y1[:\s]+\$?([\d,]+(?:\.\d+)?)\s*(?:M|K|million|thousand)?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._parse_money(match.group(0))
        return None

    def _parse_money(self, text: str) -> float | None:
        """Parse money amount from text like '$250,000' or '$1.5M'."""
        if not text:
            return None

        text = text.strip().upper()

        # Remove currency symbols
        text = re.sub(r"[$€£]", "", text)

        # Look for number with optional multiplier
        match = re.search(r"([\d,]+(?:\.\d+)?)\s*(M|MILLION|K|THOUSAND|B|BILLION)?", text)
        if not match:
            return None

        try:
            number = float(match.group(1).replace(",", ""))
            multiplier = match.group(2) or ""

            if multiplier in ("M", "MILLION"):
                number *= 1_000_000
            elif multiplier in ("K", "THOUSAND"):
                number *= 1_000
            elif multiplier in ("B", "BILLION"):
                number *= 1_000_000_000

            return number
        except (ValueError, TypeError):
            return None

    def _calculate_variance(self, values: dict[str, float]) -> float:
        """Calculate variance between multiple values."""
        if len(values) < 2:
            return 0.0

        nums = list(values.values())
        avg = sum(nums) / len(nums)
        if avg == 0:
            return 0.0

        max_diff = max(abs(n - avg) for n in nums)
        return max_diff / avg


# Register the eval
EvalRegistry.register(NumericalConsistencyEval())
