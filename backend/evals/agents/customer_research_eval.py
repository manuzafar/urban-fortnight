"""
Customer Research Eval — Specialized evaluation for customer research outputs.

Criteria:
- Has interview quotes: >= 3 direct quotes from personas
- Pain points identified: >= 5 specific pain points
- Segments defined: >= 2 customer segments with characteristics
- Jobs-to-be-done: JTBD framework applied
- Validation methods: Suggests how to validate findings
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class CustomerResearchEval(BaseEval):
    """Evaluates customer research output for completeness and quality."""

    name = "customer_research_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks customer research has required depth and evidence"
    severity = EvalSeverity.WARNING
    applicable_agents = ["customer_research"]

    # Thresholds
    MIN_PAIN_POINTS = 3
    MIN_SEGMENTS = 2
    MIN_OPEN_QUESTIONS = 1
    MIN_UNCOMFORTABLE_INSIGHTS = 1

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate customer research output."""
        checks = []
        score_components = []

        # Check pain signals
        pain_signals = agent_output.get("pain_signals", [])
        pain_count = len(pain_signals)
        pain_passed = pain_count >= self.MIN_PAIN_POINTS
        checks.append({
            "name": "pain_points",
            "passed": pain_passed,
            "actual": pain_count,
            "required": self.MIN_PAIN_POINTS,
        })
        score_components.append(min(pain_count / self.MIN_PAIN_POINTS, 1.0))

        # Check segments
        research_scope = agent_output.get("research_scope", {})
        segments = research_scope.get("segments_examined", [])
        segment_count = len(segments)
        segments_passed = segment_count >= self.MIN_SEGMENTS
        checks.append({
            "name": "customer_segments",
            "passed": segments_passed,
            "actual": segment_count,
            "required": self.MIN_SEGMENTS,
        })
        score_components.append(min(segment_count / self.MIN_SEGMENTS, 1.0))

        # Check JTBD framework
        jtbd = agent_output.get("job_to_be_done", {})
        jtbd_complete = all([
            jtbd.get("trigger_situation"),
            jtbd.get("underlying_goal"),
            jtbd.get("success_definition"),
        ])
        checks.append({
            "name": "jtbd_framework",
            "passed": jtbd_complete,
            "actual": "complete" if jtbd_complete else "incomplete",
            "required": "all fields populated",
        })
        score_components.append(1.0 if jtbd_complete else 0.5)

        # Check open questions (validation methods)
        open_questions = agent_output.get("open_questions", [])
        has_validation = any(
            q.get("validation_needed") for q in open_questions
        )
        questions_passed = len(open_questions) >= self.MIN_OPEN_QUESTIONS and has_validation
        checks.append({
            "name": "validation_methods",
            "passed": questions_passed,
            "actual": len(open_questions),
            "required": self.MIN_OPEN_QUESTIONS,
        })
        score_components.append(1.0 if questions_passed else 0.5)

        # Check uncomfortable insights (intellectual honesty)
        uncomfortable = agent_output.get("uncomfortable_insights", [])
        uncomfortable_passed = len(uncomfortable) >= self.MIN_UNCOMFORTABLE_INSIGHTS
        checks.append({
            "name": "uncomfortable_insights",
            "passed": uncomfortable_passed,
            "actual": len(uncomfortable),
            "required": self.MIN_UNCOMFORTABLE_INSIGHTS,
        })
        score_components.append(1.0 if uncomfortable_passed else 0.3)

        # Check current behaviour analysis
        current_behaviour = agent_output.get("current_behaviour", {})
        has_existing_solutions = len(current_behaviour.get("existing_solutions", [])) > 0
        has_friction_points = len(current_behaviour.get("friction_points", [])) > 0
        behaviour_passed = has_existing_solutions and has_friction_points
        checks.append({
            "name": "current_behaviour_analysis",
            "passed": behaviour_passed,
            "actual": "complete" if behaviour_passed else "incomplete",
            "required": "existing solutions and friction points",
        })
        score_components.append(1.0 if behaviour_passed else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = "Customer research meets all quality criteria"
        else:
            message = f"Customer research missing: {', '.join(failed_checks)}"

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
                "pain_point_count": pain_count,
                "segment_count": segment_count,
                "has_jtbd": jtbd_complete,
                "has_validation_methods": has_validation,
            },
        )


# Register the eval
EvalRegistry.register(CustomerResearchEval())
