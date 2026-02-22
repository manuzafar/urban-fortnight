"""
Stage 1: Problem Love

Based on Uri Levine's "Fall in Love with the Problem" methodology.
This stage validates that the problem is worth solving.

Includes reflection loop: Generate -> Critique -> Refine (max 2 iterations)
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import (
    PROBLEM_LOVE_COACHING_PROMPT,
    PROBLEM_LOVE_GENERATION_PROMPT,
    PROBLEM_LOVE_REFINE_PROMPT,
    TARPIT_CHECK_PROMPT,
)
from agents.discovery_v4.stages.mini_critique import critique_stage_output
from models.discovery_v4_schemas import (
    DiscoveryMode,
    DiscoverySessionV4,
    ProblemLoveOutput,
    RealPerson,
    TarpitAnalysis,
)

logger = structlog.get_logger(__name__)

# Reflection loop configuration
MAX_REFLECTION_ITERATIONS = 2
MIN_QUALITY_THRESHOLD = 7.0


class ProblemLoveStage:
    """
    Stage 1: Problem Love

    Based on Uri Levine's frameworks:
    - Fall in love with the PROBLEM, not the solution
    - Real people must be experiencing this RIGHT NOW
    - The problem must occur FREQUENTLY
    - Current alternatives must be inadequate
    - Beware of TARPITS
    """

    async def run(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> ProblemLoveOutput:
        """
        Generate or coach problem love analysis with reflection loop.

        Implements: Generate -> Critique -> Refine (max 2 iterations)
        """
        logger.info(
            "problem_love_stage_run",
            session_id=session.session_id,
            mode=context.get("mode"),
        )

        if context.get("mode") == "deep":
            # Deep mode: Coaching only (user provides interviews)
            return await self._coach(context)
        else:
            # Quick/Guided modes: Full AI generation with reflection loop
            return await self._generate_with_reflection(context)

    async def _generate_with_reflection(
        self, context: dict[str, Any]
    ) -> ProblemLoveOutput:
        """
        AI generates with reflection loop.

        Pattern: Generate -> Critique -> Refine (max iterations)
        """
        iteration = 0
        critique_feedback = None
        output = None

        while iteration < MAX_REFLECTION_ITERATIONS:
            logger.info(
                "problem_love_reflection_iteration",
                iteration=iteration + 1,
                max_iterations=MAX_REFLECTION_ITERATIONS,
                has_feedback=critique_feedback is not None,
            )

            # Generate (or refine based on feedback)
            if critique_feedback:
                output = await self._generate_with_feedback(context, critique_feedback)
            else:
                output = await self._generate_full(context)

            # Critique the output
            critique = await critique_stage_output(
                "problem_love",
                output.model_dump(),
                evidence_tier="E4",  # Quick mode is E4
            )

            logger.info(
                "problem_love_critique_result",
                iteration=iteration + 1,
                overall_score=critique.get("overall_score"),
                passes_threshold=critique.get("passes_threshold"),
            )

            # Check quality gate
            if critique.get("overall_score", 0) >= MIN_QUALITY_THRESHOLD:
                # Quality threshold met - add coaching notes and exit
                output.ai_coaching_notes = critique.get("feedback", [])
                output.overall_score = int(critique.get("overall_score", 7))
                output.proceed_recommendation = True
                logger.info(
                    "problem_love_quality_threshold_met",
                    score=output.overall_score,
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

        # If max iterations reached, include coaching notes but allow progression
        if iteration >= MAX_REFLECTION_ITERATIONS:
            output.ai_coaching_notes = critique.get("feedback", [])
            output.proceed_recommendation = critique.get("overall_score", 5) >= 6.0
            logger.info(
                "problem_love_max_iterations_reached",
                final_score=critique.get("overall_score"),
                proceed=output.proceed_recommendation,
            )

        return output

    async def _generate_with_feedback(
        self, context: dict[str, Any], feedback: dict[str, Any]
    ) -> ProblemLoveOutput:
        """Generate refined output incorporating critique feedback."""
        prompt = PROBLEM_LOVE_REFINE_PROMPT.format(
            original_output=json.dumps(feedback["previous_output"], indent=2, default=str),
            feedback="\n".join(f"- {f}" for f in feedback.get("feedback", [])),
            suggested_improvements=json.dumps(
                feedback.get("suggested_improvements", {}), indent=2, default=str
            ),
            product_idea=context.get("product_idea", ""),
            industry=context.get("industry", "Not specified"),
            target_market=context.get("target_market", "Not specified"),
        )

        logger.info("problem_love_refine_generation_start")

        result = await call_llm(prompt, "problem_love_refine")

        if result.get("success"):
            data = result["data"]
            output = self._parse_output(data)
            logger.info(
                "problem_love_refine_generation_complete",
                score=output.overall_score,
            )
            return output
        else:
            logger.warning(
                "problem_love_refine_failed",
                error=result.get("error"),
            )
            # Return the previous output if refinement fails
            return self._parse_output(feedback["previous_output"])

    async def _generate_full(
        self, context: dict[str, Any]
    ) -> ProblemLoveOutput:
        """AI generates complete problem love analysis."""
        prompt = PROBLEM_LOVE_GENERATION_PROMPT.format(
            product_idea=context.get("product_idea", ""),
            industry=context.get("industry", "Not specified"),
            target_market=context.get("target_market", "Not specified"),
        )

        result = await call_llm(prompt, "problem_love_generation")

        if result.get("success"):
            data = result["data"]
            return self._parse_output(data)
        else:
            logger.error(
                "problem_love_generation_failed",
                error=result.get("error"),
            )
            # Return a default output with error coaching
            return ProblemLoveOutput(
                problem_statement=context.get("product_idea", ""),
                specificity_score=1,
                real_people=[],
                real_people_count=0,
                frequency="rarely",
                frequency_analysis="Unable to analyze - please try again",
                current_alternatives=[],
                alternatives_analysis="Unable to analyze",
                tarpit_check=TarpitAnalysis(
                    is_tarpit=False,
                    similarity_score=0,
                    similar_to=[],
                    specific_concerns=["Analysis failed - please retry"],
                ),
                overall_score=1,
                ai_coaching_notes=["Error during analysis. Please try again."],
                proceed_recommendation=False,
            )

    async def _coach(self, context: dict[str, Any]) -> ProblemLoveOutput:
        """Provide coaching feedback on user's problem statement."""
        # Get existing problem statement from context or use product idea
        problem_statement = context.get(
            "problem_statement", context.get("product_idea", "")
        )

        prompt = PROBLEM_LOVE_COACHING_PROMPT.format(
            problem_statement=problem_statement,
            product_idea=context.get("product_idea", ""),
            industry=context.get("industry", "Not specified"),
            target_market=context.get("target_market", "Not specified"),
        )

        result = await call_llm(prompt, "problem_love_coaching")

        if result.get("success"):
            data = result["data"]

            # Convert coaching response to ProblemLoveOutput format
            return ProblemLoveOutput(
                problem_statement=problem_statement,
                problem_statement_refined=data.get("refined_statement"),
                specificity_score=data.get("current_score", 5),
                real_people=[],
                real_people_count=0,
                frequency="weekly",  # Default assumption
                frequency_analysis="Provide more details about frequency",
                current_alternatives=[],
                alternatives_analysis="Identify current alternatives",
                tarpit_check=TarpitAnalysis(
                    is_tarpit=False,
                    similarity_score=0,
                    similar_to=[],
                    specific_concerns=[],
                ),
                overall_score=data.get("current_score", 5),
                ai_coaching_notes=(
                    data.get("weaknesses", [])
                    + data.get("clarifying_questions", [])
                    + ([data.get("coaching_message")] if data.get("coaching_message") else [])
                ),
                proceed_recommendation=data.get("current_score", 5) >= 6,
            )
        else:
            # Fallback - return basic coaching
            return await self._generate_full(context)

    async def check_tarpit(
        self, problem: str, solution: str | None = None
    ) -> TarpitAnalysis:
        """Check if idea matches known tarpit patterns."""
        prompt = TARPIT_CHECK_PROMPT.format(
            problem_statement=problem,
            solution_concept=solution or "Not specified",
        )

        result = await call_llm(prompt, "tarpit_check")

        if result.get("success"):
            data = result["data"]
            return TarpitAnalysis(
                is_tarpit=data.get("is_tarpit", False),
                similarity_score=data.get("similarity_score", 0),
                similar_to=data.get("similar_to", []),
                specific_concerns=data.get("specific_concerns", []),
                user_differentiation=data.get("user_differentiation"),
            )
        else:
            return TarpitAnalysis(
                is_tarpit=False,
                similarity_score=0,
                similar_to=[],
                specific_concerns=["Unable to check - please try again"],
            )

    def _normalize_frequency(self, raw_frequency: str) -> str:
        """Normalize frequency to valid enum value."""
        valid_frequencies = {"daily", "weekly", "monthly", "rarely"}
        freq_lower = raw_frequency.lower().strip()

        # Direct match
        if freq_lower in valid_frequencies:
            return freq_lower

        # Handle common variations
        if "daily" in freq_lower or "day" in freq_lower:
            return "daily"
        if "weekly" in freq_lower or "week" in freq_lower:
            return "weekly"
        if "monthly" in freq_lower or "month" in freq_lower:
            return "monthly"
        if "rarely" in freq_lower or "rare" in freq_lower or "never" in freq_lower:
            return "rarely"

        # Default to weekly if unrecognized
        return "weekly"

    def _parse_output(self, data: dict[str, Any]) -> ProblemLoveOutput:
        """Parse LLM output into ProblemLoveOutput model."""
        # Parse real people
        real_people = []
        for person in data.get("real_people", []):
            real_people.append(
                RealPerson(
                    name=person.get("name", "Unknown"),
                    struggling_moment=person.get("struggling_moment", ""),
                    how_you_know_them=person.get("how_you_know_them"),
                )
            )

        # Parse tarpit check
        tarpit_data = data.get("tarpit_check", {})
        tarpit_check = TarpitAnalysis(
            is_tarpit=tarpit_data.get("is_tarpit", False),
            similarity_score=tarpit_data.get("similarity_score", 0),
            similar_to=tarpit_data.get("similar_to", []),
            specific_concerns=tarpit_data.get("specific_concerns", []),
            user_differentiation=tarpit_data.get("user_differentiation"),
        )

        # Normalize frequency to valid enum value
        raw_frequency = data.get("frequency", "weekly")
        frequency = self._normalize_frequency(raw_frequency)

        return ProblemLoveOutput(
            problem_statement=data.get("problem_statement", ""),
            problem_statement_refined=data.get("problem_statement_refined"),
            specificity_score=data.get("specificity_score", 5),
            real_people=real_people,
            real_people_count=len(real_people),
            frequency=frequency,
            frequency_analysis=data.get("frequency_analysis", ""),
            current_alternatives=data.get("current_alternatives", []),
            alternatives_analysis=data.get("alternatives_analysis", ""),
            tarpit_check=tarpit_check,
            overall_score=data.get("overall_score", 5),
            ai_coaching_notes=data.get("ai_coaching_notes", []),
            proceed_recommendation=data.get("proceed_recommendation", True),
        )

    async def get_suggestions(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get suggestions for improving the problem statement."""
        suggestions = [
            "Make the problem more specific - who exactly has this problem?",
            "Add frequency - how often does this problem occur?",
            "Identify real people - can you name 3 people with this problem?",
            "Check alternatives - what do people use today?",
            "Validate urgency - is this a 'hair on fire' problem?",
        ]

        # Filter based on what's already present
        if context.get("problem_love_output"):
            output = context["problem_love_output"]
            if output.get("specificity_score", 0) >= 7:
                suggestions = [s for s in suggestions if "specific" not in s.lower()]
            if output.get("real_people_count", 0) >= 3:
                suggestions = [s for s in suggestions if "real people" not in s.lower()]

        return {"suggestions": suggestions[:3]}
