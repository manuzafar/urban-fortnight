"""
Planner Eval — Specialized evaluation for planner/orchestrator outputs.

Criteria:
- Research questions: >= 5 critical questions identified
- Competitor targets: Specific competitors to analyze
- Domain classification: Industry/domain type determined
- Search strategy: Key search terms defined
- Constraint identification: Initial constraints recognized
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class PlannerEval(BaseEval):
    """Evaluates planner output for research direction quality."""

    name = "planner_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks planner identifies key research questions and strategy"
    severity = EvalSeverity.WARNING
    applicable_agents = ["planner"]

    MIN_RESEARCH_QUESTIONS = 3
    MIN_SEARCH_TERMS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate planner output."""
        checks = []
        score_components = []

        # Check research questions
        questions = agent_output.get("research_questions", agent_output.get("critical_questions", []))
        question_count = len(questions)
        questions_passed = question_count >= self.MIN_RESEARCH_QUESTIONS
        checks.append({
            "name": "research_questions",
            "passed": questions_passed,
            "actual": question_count,
            "required": self.MIN_RESEARCH_QUESTIONS,
        })
        score_components.append(min(question_count / self.MIN_RESEARCH_QUESTIONS, 1.0))

        # Check competitor targets
        competitors = agent_output.get("competitor_targets", agent_output.get("competitors_to_analyze", []))
        has_competitors = len(competitors) >= 2
        checks.append({
            "name": "competitor_targets",
            "passed": has_competitors,
            "actual": len(competitors),
            "required": ">= 2",
        })
        score_components.append(1.0 if has_competitors else 0.5)

        # Check domain classification
        domain = agent_output.get("domain_type", agent_output.get("industry_classification", ""))
        has_domain = bool(domain) and len(str(domain)) > 3
        checks.append({
            "name": "domain_classification",
            "passed": has_domain,
            "actual": domain if has_domain else "missing",
            "required": "domain/industry type",
        })
        score_components.append(1.0 if has_domain else 0.5)

        # Check search terms
        search_terms = agent_output.get("search_terms", agent_output.get("key_search_queries", []))
        search_count = len(search_terms)
        search_passed = search_count >= self.MIN_SEARCH_TERMS
        checks.append({
            "name": "search_strategy",
            "passed": search_passed,
            "actual": search_count,
            "required": self.MIN_SEARCH_TERMS,
        })
        score_components.append(min(search_count / self.MIN_SEARCH_TERMS, 1.0))

        # Check constraints
        constraints = agent_output.get("constraints", agent_output.get("identified_constraints", []))
        has_constraints = len(constraints) >= 1
        checks.append({
            "name": "constraint_identification",
            "passed": has_constraints,
            "actual": len(constraints),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_constraints else 0.5)

        # Check target market
        target_market = agent_output.get("target_market", agent_output.get("market_focus", ""))
        has_market = bool(target_market) and len(str(target_market)) > 10
        checks.append({
            "name": "target_market",
            "passed": has_market,
            "actual": "defined" if has_market else "missing",
            "required": "target market identified",
        })
        score_components.append(1.0 if has_market else 0.5)

        # Check agent routing (if present)
        agent_priority = agent_output.get("agent_priority", agent_output.get("swarm_order", []))
        has_routing = len(agent_priority) >= 1
        checks.append({
            "name": "agent_routing",
            "passed": has_routing,
            "actual": len(agent_priority) if has_routing else 0,
            "required": "agent execution order",
        })
        score_components.append(1.0 if has_routing else 0.5)

        # Check product idea clarity
        product_summary = agent_output.get("product_idea_summary", agent_output.get("idea_analysis", ""))
        has_summary = bool(product_summary) and len(str(product_summary)) > 30
        checks.append({
            "name": "product_idea_analysis",
            "passed": has_summary,
            "actual": "analyzed" if has_summary else "missing",
            "required": "product idea analysis",
        })
        score_components.append(1.0 if has_summary else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Planner complete: {question_count} questions, {search_count} search terms"
        else:
            message = f"Planner needs: {', '.join(failed_checks)}"

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
                "question_count": question_count,
                "search_term_count": search_count,
            },
        )


# Register the eval
EvalRegistry.register(PlannerEval())
