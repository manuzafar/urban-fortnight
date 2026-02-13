"""
Contradiction Detector — Finds inconsistencies between sections.

Uses LLM to detect contradictions in:
- Market size claims
- Pricing statements
- Target customer definitions
- Timeline projections
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)

logger = structlog.get_logger(__name__)


CONTRADICTION_PROMPT = """You are a consistency checker for product discovery documents.

Analyze the following sections for contradictions and inconsistencies.

## SECTIONS TO ANALYZE

### Executive Summary
{executive_summary}

### Customer Research
{customer_research}

### Business Case
{business_case}

### Financial Model
{financial_model}

## CHECK FOR CONTRADICTIONS IN:

1. **Market Size** - Do TAM/SAM/SOM numbers match across sections?
2. **Pricing** - Is pricing consistent (executive summary vs business case vs financial model)?
3. **Target Customer** - Is the target customer described consistently?
4. **Timeline** - Do milestone dates and projections align?
5. **Funding** - Is the funding requirement consistent?
6. **Revenue Projections** - Do Year 1/Year 3 numbers match?

## OUTPUT FORMAT
Respond with valid JSON only:
{{
  "contradictions": [
    {{
      "type": "market_size|pricing|target_customer|timeline|funding|revenue",
      "sections_involved": ["section1", "section2"],
      "description": "What is contradictory",
      "severity": "critical|moderate|minor",
      "values_found": {{"section1": "value1", "section2": "value2"}}
    }}
  ],
  "consistency_score": 0.0,  // 0.0-1.0, where 1.0 is perfectly consistent
  "summary": "Brief summary of consistency analysis"
}}

If no contradictions found, return empty contradictions array and score of 1.0.
Be thorough but don't flag minor wording differences as contradictions.
"""


class ContradictionDetectorEval(BaseEval):
    """
    Detects contradictions between sections using LLM analysis.

    This is a cross-section eval that looks at the full state
    rather than individual agent outputs.
    """

    name = "contradiction_detector"
    eval_type = EvalType.CONSISTENCY
    description = "Detects contradictions between sections"
    severity = EvalSeverity.CRITICAL  # Contradictions are serious

    # Score threshold
    MIN_CONSISTENCY = 0.7

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Evaluate cross-section consistency.

        Note: This eval operates on the full state, not individual agent outputs.
        The agent_output param is used for per-agent scoring compatibility.

        Args:
            agent_output: The agent's output (not used directly)
            agent_name: Name of the agent
            context: Must contain 'full_state' for cross-section analysis

        Returns:
            EvalResult with contradiction analysis
        """
        # Get full state from context
        if not context or "full_state" not in context:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message="No full state available for cross-section analysis",
                agent_name=agent_name,
            )

        state = context["full_state"]

        # Extract sections for comparison
        executive_summary = json.dumps(
            state.get("executive_summary", {}),
            indent=2, default=str
        )[:3000]

        customer_research = json.dumps(
            state.get("customer_research", {}),
            indent=2, default=str
        )[:3000]

        business_case = json.dumps(
            state.get("business_case", {}),
            indent=2, default=str
        )[:3000]

        financial_model = json.dumps(
            state.get("financial_model", {}),
            indent=2, default=str
        )[:3000]

        # Build prompt
        prompt = CONTRADICTION_PROMPT.format(
            executive_summary=executive_summary,
            customer_research=customer_research,
            business_case=business_case,
            financial_model=financial_model,
        )

        # Call LLM
        try:
            result = await call_llm(
                prompt=prompt,
                agent_name=f"{self.name}_eval",
            )

            if not result.get("success"):
                logger.warning(
                    "contradiction_detector_failed",
                    error=result.get("error"),
                )
                return EvalResult(
                    eval_name=self.name,
                    eval_type=self.eval_type,
                    passed=True,
                    score=None,
                    severity=EvalSeverity.INFO,
                    message=f"Contradiction check unavailable: {result.get('error')}",
                    agent_name=agent_name,
                )

            # Parse response
            data = result.get("data", {})
            contradictions = data.get("contradictions", [])
            consistency_score = data.get("consistency_score", 1.0)
            summary = data.get("summary", "")

            # Normalize score
            consistency_score = max(0.0, min(1.0, float(consistency_score)))

            # Count severity
            critical_count = sum(
                1 for c in contradictions
                if c.get("severity") == "critical"
            )
            moderate_count = sum(
                1 for c in contradictions
                if c.get("severity") == "moderate"
            )

            # Determine pass/fail
            passed = consistency_score >= self.MIN_CONSISTENCY and critical_count == 0

            if critical_count > 0:
                message = f"Found {critical_count} critical contradiction(s)"
                severity = EvalSeverity.CRITICAL
            elif moderate_count > 0:
                message = f"Found {moderate_count} moderate inconsistency(ies)"
                severity = EvalSeverity.WARNING
            elif len(contradictions) > 0:
                message = f"Found {len(contradictions)} minor inconsistency(ies)"
                severity = EvalSeverity.INFO
            else:
                message = "No contradictions detected"
                severity = EvalSeverity.INFO

            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=passed,
                score=consistency_score,
                severity=severity,
                message=message,
                agent_name=agent_name,
                details={
                    "contradictions": contradictions,
                    "critical_count": critical_count,
                    "moderate_count": moderate_count,
                    "summary": summary,
                },
            )

        except Exception as e:
            logger.error("contradiction_detector_exception", error=str(e))
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message=f"Contradiction check error: {str(e)}",
                agent_name=agent_name,
            )


# Register the eval
EvalRegistry.register(ContradictionDetectorEval())
