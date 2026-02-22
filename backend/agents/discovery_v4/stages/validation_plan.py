"""
Stage 5: Validation Plan

Based on the Validation Ladder methodology.
This stage creates a plan for validating the solution.

Includes reflection loop: Generate -> Critique -> Refine (max 2 iterations)
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import VALIDATION_PLAN_PROMPT, VALIDATION_PLAN_REFINE_PROMPT
from agents.discovery_v4.stages.mini_critique import critique_stage_output
from models.discovery_v4_schemas import (
    DiscoverySessionV4,
    ValidationExperiment,
    ValidationPlanOutput,
)

logger = structlog.get_logger(__name__)

# Reflection loop configuration
MAX_REFLECTION_ITERATIONS = 2
MIN_QUALITY_THRESHOLD = 7.0


class ValidationPlanStage:
    """
    Stage 5: Validation Plan

    Uses the Validation Ladder methodology:
    1. Exploration - Do people have this problem?
    2. Pitch - Do they want a solution like this?
    3. Concierge - Can we deliver value manually?
    4. Wizard of Oz - Does the concept work?
    5. MVP - Does the full product work?
    """

    VALIDATION_LADDER = {
        1: {
            "name": "Exploration",
            "goal": "Validate the problem exists",
            "methods": ["Customer interviews", "Survey research", "Desk research"],
        },
        2: {
            "name": "Pitch",
            "goal": "Validate interest in solution",
            "methods": ["Landing page test", "Concierge MVP", "Fake door test"],
        },
        3: {
            "name": "Concierge",
            "goal": "Validate we can deliver value manually",
            "methods": ["Manual service delivery", "White glove onboarding"],
        },
        4: {
            "name": "Wizard of Oz",
            "goal": "Validate the concept works",
            "methods": [
                "Automated front-end, manual back-end",
                "User experience testing",
            ],
        },
        5: {
            "name": "MVP",
            "goal": "Validate full product works",
            "methods": ["Minimal full solution", "Real users, real payment"],
        },
    }

    async def run(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> ValidationPlanOutput:
        """Run validation plan stage with reflection loop."""
        logger.info(
            "validation_plan_stage_run",
            session_id=session.session_id,
            has_solution=context.get("solution") is not None,
        )

        return await self._generate_with_reflection(context)

    async def _generate_with_reflection(
        self, context: dict[str, Any]
    ) -> ValidationPlanOutput:
        """Generate with reflection loop: Generate -> Critique -> Refine."""
        iteration = 0
        critique_feedback = None
        output = None

        while iteration < MAX_REFLECTION_ITERATIONS:
            logger.info(
                "validation_plan_reflection_iteration",
                iteration=iteration + 1,
                max_iterations=MAX_REFLECTION_ITERATIONS,
                has_feedback=critique_feedback is not None,
            )

            # Generate (or refine based on feedback)
            if critique_feedback:
                output = await self._generate_with_feedback(context, critique_feedback)
            else:
                output = await self._generate_initial(context)

            # Critique the output
            critique = await critique_stage_output(
                "validation_plan",
                output.model_dump(),
                evidence_tier="E4",
            )

            logger.info(
                "validation_plan_critique_result",
                iteration=iteration + 1,
                overall_score=critique.get("overall_score"),
                passes_threshold=critique.get("passes_threshold"),
            )

            # Check quality gate
            if critique.get("overall_score", 0) >= MIN_QUALITY_THRESHOLD:
                logger.info(
                    "validation_plan_quality_threshold_met",
                    score=critique.get("overall_score"),
                    iteration=iteration + 1,
                )
                break

            # Prepare feedback for next iteration
            critique_feedback = {
                "feedback": critique.get("feedback", []),
                "suggested_improvements": critique.get("suggested_improvements", {}),
                "previous_output": output.model_dump(),
                "dimension_scores": critique.get("dimension_scores", {}),
            }
            iteration += 1

        # If max iterations reached, log and return best effort
        if iteration >= MAX_REFLECTION_ITERATIONS:
            logger.info(
                "validation_plan_max_iterations_reached",
                final_score=critique.get("overall_score"),
            )

        return output

    async def _generate_initial(self, context: dict[str, Any]) -> ValidationPlanOutput:
        """Generate initial validation plan."""
        # Extract key risk from pre-mortem
        primary_risk = "Need to validate market demand"
        solution_output = context.get("solution_design_output", {})
        pre_mortem = solution_output.get("pre_mortem", {})
        tigers = pre_mortem.get("tigers", [])
        if tigers:
            primary_risk = tigers[0].get("description", primary_risk)

        prompt = VALIDATION_PLAN_PROMPT.format(
            solution=context.get("solution", context.get("product_idea", "")),
            dhm_score=json.dumps(context.get("dhm_score", {}), default=str),
            primary_risk=primary_risk,
            target_market=context.get("target_market", "Not specified"),
        )

        result = await call_llm(prompt, "validation_plan")

        if result.get("success"):
            data = result["data"]
            return self._parse_output(data, context)
        else:
            logger.error(
                "validation_plan_failed",
                error=result.get("error"),
            )
            return self._default_output(context)

    async def _generate_with_feedback(
        self, context: dict[str, Any], feedback: dict[str, Any]
    ) -> ValidationPlanOutput:
        """Generate refined output incorporating critique feedback."""
        prompt = VALIDATION_PLAN_REFINE_PROMPT.format(
            original_output=json.dumps(feedback["previous_output"], indent=2, default=str),
            feedback="\n".join(f"- {f}" for f in feedback.get("feedback", [])),
        )

        logger.info("validation_plan_refine_generation_start")

        result = await call_llm(prompt, "validation_plan_refine")

        if result.get("success"):
            data = result["data"]
            output = self._parse_output(data, context)
            logger.info("validation_plan_refine_generation_complete")
            return output
        else:
            logger.warning(
                "validation_plan_refine_failed",
                error=result.get("error"),
            )
            # Return the previous output if refinement fails
            return self._parse_output(feedback["previous_output"], context)

    def _parse_output(
        self, data: dict[str, Any], context: dict[str, Any]
    ) -> ValidationPlanOutput:
        """Parse validation plan output."""
        # Map invalid statuses to valid ones
        status_map = {
            "planned": "todo",
            "pending": "todo",
            "not_started": "todo",
            "running": "in_progress",
            "active": "in_progress",
            "done": "completed",
            "finished": "completed",
            "success": "passed",
            "succeeded": "passed",
            "failure": "failed",
            "failed": "failed",
        }

        experiments = []
        for exp in data.get("experiments", []):
            raw_status = exp.get("status", "todo")
            # Normalize status to valid value
            normalized_status = status_map.get(raw_status.lower(), "todo") if raw_status else "todo"
            if normalized_status not in ["todo", "in_progress", "completed", "passed", "failed"]:
                normalized_status = "todo"

            experiments.append(
                ValidationExperiment(
                    rung=exp.get("rung", 1),
                    name=exp.get("name", "Experiment"),
                    hypothesis=exp.get("hypothesis", ""),
                    success_criteria=exp.get("success_criteria", ""),
                    failure_criteria=exp.get("failure_criteria", ""),
                    target_participants=exp.get("target_participants", ""),
                    method=exp.get("method", ""),
                    timeline=exp.get("timeline", "1 week"),
                    status=normalized_status,
                )
            )

        # Sort experiments by rung
        experiments.sort(key=lambda x: x.rung)

        # Determine next experiment
        next_experiment = None
        for exp in experiments:
            if exp.status == "todo":
                next_experiment = exp
                break

        return ValidationPlanOutput(
            current_rung=data.get("current_rung", 1),
            experiments=experiments,
            next_experiment=next_experiment,
            validation_summary=data.get(
                "validation_summary",
                "Start with problem validation interviews before building anything",
            ),
        )

    def _default_output(self, context: dict[str, Any]) -> ValidationPlanOutput:
        """Return default validation plan."""
        target_market = context.get("target_market", "target users")
        problem = context.get("problem_statement", context.get("product_idea", "the problem"))

        experiments = [
            ValidationExperiment(
                rung=1,
                name="Problem Validation Interviews",
                hypothesis=f"At least 7/10 {target_market} experience {problem} weekly",
                success_criteria="7+ users confirm the problem",
                failure_criteria="< 5 users confirm",
                target_participants=f"10 {target_market}",
                method="30-minute interviews using Teresa Torres methodology",
                timeline="2 weeks",
                status="todo",
            ),
            ValidationExperiment(
                rung=2,
                name="Solution Interest Test",
                hypothesis="At least 5% of visitors will sign up for waitlist",
                success_criteria=">5% conversion rate",
                failure_criteria="<2% conversion rate",
                target_participants="1000 visitors from target audience",
                method="Landing page with clear value proposition",
                timeline="1 week",
                status="todo",
            ),
            ValidationExperiment(
                rung=3,
                name="Concierge MVP",
                hypothesis="Can deliver value manually to 5 users",
                success_criteria="5 users achieve desired outcome",
                failure_criteria="<3 users achieve outcome",
                target_participants="5 early adopters from waitlist",
                method="Manual service delivery with high-touch support",
                timeline="2 weeks",
                status="todo",
            ),
            ValidationExperiment(
                rung=4,
                name="Wizard of Oz Test",
                hypothesis="Users engage with product experience",
                success_criteria="70%+ weekly retention",
                failure_criteria="<50% retention",
                target_participants="20 users",
                method="Automated UI, manual backend processing",
                timeline="4 weeks",
                status="todo",
            ),
            ValidationExperiment(
                rung=5,
                name="Beta MVP",
                hypothesis="Users will pay for this solution",
                success_criteria="10 paying customers",
                failure_criteria="<5 paying customers",
                target_participants="100 users",
                method="Minimal full product with payment",
                timeline="8 weeks",
                status="todo",
            ),
        ]

        return ValidationPlanOutput(
            current_rung=1,
            experiments=experiments,
            next_experiment=experiments[0],
            validation_summary="Start with problem validation before building. Move up the ladder only when you have confidence at each rung.",
        )

    async def get_suggestions(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get suggestions for validation planning."""
        current_rung = 1

        # Determine current rung based on what's been done
        has_interviews = context.get("interview_count", 0) >= 5
        if has_interviews:
            current_rung = 2

        suggestions_by_rung = {
            1: [
                "Start with 10 customer interviews to validate the problem",
                "Focus on understanding the pain, not pitching your solution",
                "Use 'Tell me about the last time...' to get real stories",
            ],
            2: [
                "Create a landing page to test solution interest",
                "Run a concierge test - solve the problem manually first",
                "Consider a fake door test to measure demand",
            ],
            3: [
                "Deliver value manually to 5 early users",
                "Document the process to understand edge cases",
                "Validate willingness to pay",
            ],
            4: [
                "Build automated front-end with manual backend",
                "Test the user experience and retention",
                "Identify what needs to be automated",
            ],
            5: [
                "Build the minimal full solution",
                "Focus on core value, skip nice-to-haves",
                "Get real paying customers",
            ],
        }

        return {
            "current_rung": current_rung,
            "suggestions": suggestions_by_rung.get(current_rung, suggestions_by_rung[1]),
        }
