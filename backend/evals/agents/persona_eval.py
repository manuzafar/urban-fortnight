"""
Persona Eval — Specialized evaluation for persona development.

Criteria:
- Distinct personas: >= 2 differentiated personas
- Demographics: Age, role, context specified
- Goals & frustrations: Clear motivations documented
- Behavioral patterns: Decision-making process described
- Quote from persona: Representative voice/quote
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class PersonaEval(BaseEval):
    """Evaluates persona development for depth and differentiation."""

    name = "persona_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks personas are well-developed and differentiated"
    severity = EvalSeverity.WARNING
    applicable_agents = ["persona_development"]

    MIN_PERSONAS = 2

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate persona output."""
        checks = []
        score_components = []

        # Get personas
        personas = agent_output.get("personas", [])
        if not personas and isinstance(agent_output, list):
            personas = agent_output

        persona_count = len(personas)

        # Check persona count
        count_passed = persona_count >= self.MIN_PERSONAS
        checks.append({
            "name": "persona_count",
            "passed": count_passed,
            "actual": persona_count,
            "required": self.MIN_PERSONAS,
        })
        score_components.append(min(persona_count / self.MIN_PERSONAS, 1.0))

        # Check each persona for required fields
        complete_personas = 0
        with_demographics = 0
        with_goals = 0
        with_frustrations = 0
        with_behaviors = 0
        with_quotes = 0

        for persona in personas:
            has_name = bool(persona.get("name"))
            has_role = bool(persona.get("role"))
            has_demographics = bool(persona.get("demographics"))
            has_goals = bool(persona.get("goals")) and len(persona.get("goals", [])) > 0
            has_frustrations = bool(persona.get("frustrations")) and len(persona.get("frustrations", [])) > 0
            has_behaviors = bool(persona.get("behaviors")) and len(persona.get("behaviors", [])) > 0
            has_quote = bool(persona.get("quote"))

            if has_demographics:
                with_demographics += 1
            if has_goals:
                with_goals += 1
            if has_frustrations:
                with_frustrations += 1
            if has_behaviors:
                with_behaviors += 1
            if has_quote:
                with_quotes += 1

            if all([has_name, has_role, has_demographics, has_goals, has_frustrations]):
                complete_personas += 1

        # Check completeness
        completeness_passed = complete_personas >= min(self.MIN_PERSONAS, persona_count)
        checks.append({
            "name": "persona_completeness",
            "passed": completeness_passed,
            "actual": complete_personas,
            "required": f"{min(self.MIN_PERSONAS, persona_count)} complete",
        })
        score_components.append(complete_personas / max(persona_count, 1))

        # Check demographics
        demographics_passed = with_demographics >= persona_count * 0.8
        checks.append({
            "name": "demographics",
            "passed": demographics_passed,
            "actual": with_demographics,
            "required": "80% of personas",
        })
        score_components.append(with_demographics / max(persona_count, 1))

        # Check goals
        goals_passed = with_goals >= persona_count * 0.8
        checks.append({
            "name": "goals_defined",
            "passed": goals_passed,
            "actual": with_goals,
            "required": "80% of personas",
        })
        score_components.append(with_goals / max(persona_count, 1))

        # Check frustrations
        frustrations_passed = with_frustrations >= persona_count * 0.8
        checks.append({
            "name": "frustrations_defined",
            "passed": frustrations_passed,
            "actual": with_frustrations,
            "required": "80% of personas",
        })
        score_components.append(with_frustrations / max(persona_count, 1))

        # Check behaviors
        behaviors_passed = with_behaviors >= persona_count * 0.5
        checks.append({
            "name": "behavioral_patterns",
            "passed": behaviors_passed,
            "actual": with_behaviors,
            "required": "50% of personas",
        })
        score_components.append(with_behaviors / max(persona_count, 1))

        # Check quotes
        quotes_passed = with_quotes >= persona_count * 0.5
        checks.append({
            "name": "representative_quotes",
            "passed": quotes_passed,
            "actual": with_quotes,
            "required": "50% of personas",
        })
        score_components.append(with_quotes / max(persona_count, 1))

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components) if score_components else 0

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Personas well-developed: {persona_count} distinct personas"
        else:
            message = f"Persona development needs: {', '.join(failed_checks)}"

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
                "persona_count": persona_count,
                "complete_personas": complete_personas,
            },
        )


# Register the eval
EvalRegistry.register(PersonaEval())
