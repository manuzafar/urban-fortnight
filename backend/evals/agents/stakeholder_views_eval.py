"""
Stakeholder Views Eval — Specialized evaluation for stakeholder-specific views.

Criteria:
- Role-specific: CFO, CTO, Product, Legal views differ
- Relevant sections: Each role gets relevant sections surfaced
- Concerns addressed: Role-specific concerns answered
- Action items: Each stakeholder has clear action items
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


EXPECTED_STAKEHOLDERS = {"cfo", "cto", "ciso", "vp product", "product", "legal", "arb", "engineering"}


class StakeholderViewsEval(BaseEval):
    """Evaluates stakeholder views for role-specific content."""

    name = "stakeholder_views_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks stakeholder views are role-appropriate and actionable"
    severity = EvalSeverity.WARNING
    applicable_agents = ["stakeholder_views"]

    MIN_STAKEHOLDERS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate stakeholder views output."""
        checks = []
        score_components = []

        # Get views
        views = agent_output.get("views", [])
        view_count = len(views)

        # Check stakeholder count
        count_passed = view_count >= self.MIN_STAKEHOLDERS
        checks.append({
            "name": "stakeholder_count",
            "passed": count_passed,
            "actual": view_count,
            "required": self.MIN_STAKEHOLDERS,
        })
        score_components.append(min(view_count / self.MIN_STAKEHOLDERS, 1.0))

        # Check for role diversity
        roles_found = set()
        for view in views:
            role = str(view.get("stakeholder_role", "")).lower()
            for expected in EXPECTED_STAKEHOLDERS:
                if expected in role:
                    roles_found.add(expected)

        diversity_passed = len(roles_found) >= min(self.MIN_STAKEHOLDERS, view_count)
        checks.append({
            "name": "role_diversity",
            "passed": diversity_passed,
            "actual": f"{len(roles_found)} distinct: {', '.join(roles_found)}",
            "required": "different stakeholder roles",
        })
        score_components.append(len(roles_found) / max(view_count, 1))

        # Check tailored summaries
        views_with_summary = sum(
            1 for v in views
            if v.get("tailored_summary") and len(str(v.get("tailored_summary", ""))) > 50
        )
        summary_rate = views_with_summary / max(view_count, 1)
        summaries_passed = summary_rate >= 0.8 or view_count == 0
        checks.append({
            "name": "tailored_summaries",
            "passed": summaries_passed,
            "actual": f"{views_with_summary}/{view_count} have summaries",
            "required": "80% with tailored summaries",
        })
        score_components.append(summary_rate if view_count else 1.0)

        # Check objections addressed
        views_with_objections = sum(
            1 for v in views
            if len(v.get("anticipated_objections", [])) >= 1
        )
        objections_rate = views_with_objections / max(view_count, 1)
        objections_passed = objections_rate >= 0.7 or view_count == 0
        checks.append({
            "name": "objections_addressed",
            "passed": objections_passed,
            "actual": f"{views_with_objections}/{view_count} have objections",
            "required": "70% with anticipated objections",
        })
        score_components.append(objections_rate if view_count else 1.0)

        # Check recommendations
        views_with_recommendations = sum(
            1 for v in views
            if v.get("decision_recommendation") and len(str(v.get("decision_recommendation", ""))) > 20
        )
        recommendation_rate = views_with_recommendations / max(view_count, 1)
        recommendations_passed = recommendation_rate >= 0.7 or view_count == 0
        checks.append({
            "name": "recommendations",
            "passed": recommendations_passed,
            "actual": f"{views_with_recommendations}/{view_count} have recommendations",
            "required": "70% with recommendations",
        })
        score_components.append(recommendation_rate if view_count else 1.0)

        # Check key questions answered
        views_with_questions = sum(
            1 for v in views
            if len(v.get("key_questions_answered", [])) >= 2
        )
        questions_rate = views_with_questions / max(view_count, 1)
        questions_passed = questions_rate >= 0.7 or view_count == 0
        checks.append({
            "name": "questions_answered",
            "passed": questions_passed,
            "actual": f"{views_with_questions}/{view_count} address key questions",
            "required": "70% with >= 2 questions answered",
        })
        score_components.append(questions_rate if view_count else 1.0)

        # Check common concerns
        common_concerns = agent_output.get("common_concerns", [])
        has_common = len(common_concerns) >= 1
        checks.append({
            "name": "common_concerns",
            "passed": has_common,
            "actual": len(common_concerns),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_common else 0.5)

        # Check alignment opportunities
        alignment = agent_output.get("alignment_opportunities", [])
        has_alignment = len(alignment) >= 1
        checks.append({
            "name": "alignment_opportunities",
            "passed": has_alignment,
            "actual": len(alignment),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_alignment else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Stakeholder views complete: {view_count} roles covered"
        else:
            message = f"Stakeholder views needs: {', '.join(failed_checks)}"

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
                "view_count": view_count,
                "roles_found": list(roles_found),
            },
        )


# Register the eval
EvalRegistry.register(StakeholderViewsEval())
