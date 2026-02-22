"""
Stage 4: Solution Design

Based on DHM (Delight, Hard-to-copy, Margin) framework + Pre-mortem analysis.
This stage designs and evaluates solution concepts.

Includes reflection loop: Generate -> Critique -> Refine (max 2 iterations)
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import (
    DHM_ANALYSIS_PROMPT,
    PRE_MORTEM_PROMPT,
    SOLUTION_DESIGN_FULL_PROMPT,
    SOLUTION_DESIGN_REFINE_PROMPT,
)
from agents.discovery_v4.stages.mini_critique import critique_stage_output
from models.discovery_v4_schemas import (
    DHMScore,
    DiscoverySessionV4,
    PreMortem,
    PreMortemItem,
    SolutionDesignOutput,
)

logger = structlog.get_logger(__name__)

# Reflection loop configuration
MAX_REFLECTION_ITERATIONS = 2
MIN_QUALITY_THRESHOLD = 7.0


class SolutionDesignStage:
    """
    Stage 4: Solution Design

    Uses two frameworks:
    1. DHM (Delight, Hard-to-copy, Margin) for solution evaluation
    2. Pre-mortem analysis for risk identification
    """

    async def run(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> SolutionDesignOutput:
        """Run solution design stage with reflection loop."""
        logger.info(
            "solution_design_stage_run",
            session_id=session.session_id,
            has_opportunity=context.get("primary_opportunity") is not None,
        )

        return await self._generate_with_reflection(context)

    async def _generate_with_reflection(
        self, context: dict[str, Any]
    ) -> SolutionDesignOutput:
        """Generate with reflection loop: Generate -> Critique -> Refine."""
        iteration = 0
        critique_feedback = None
        output = None

        while iteration < MAX_REFLECTION_ITERATIONS:
            logger.info(
                "solution_design_reflection_iteration",
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
                "solution_design",
                output.model_dump(),
                evidence_tier="E4",
            )

            logger.info(
                "solution_design_critique_result",
                iteration=iteration + 1,
                overall_score=critique.get("overall_score"),
                passes_threshold=critique.get("passes_threshold"),
            )

            # Check quality gate
            if critique.get("overall_score", 0) >= MIN_QUALITY_THRESHOLD:
                logger.info(
                    "solution_design_quality_threshold_met",
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
                "solution_design_max_iterations_reached",
                final_score=critique.get("overall_score"),
            )

        return output

    async def _generate_initial(self, context: dict[str, Any]) -> SolutionDesignOutput:
        """Generate initial solution design."""
        prompt = SOLUTION_DESIGN_FULL_PROMPT.format(
            product_idea=context.get("product_idea", ""),
            problem_statement=context.get("problem_statement", ""),
            primary_opportunity=context.get("primary_opportunity", ""),
            patterns=json.dumps(context.get("patterns", {}), default=str),
            four_forces=json.dumps(context.get("four_forces", {}), default=str),
            target_market=context.get("target_market", "Not specified"),
        )

        result = await call_llm(prompt, "solution_design_full")

        if result.get("success"):
            data = result["data"]
            # Handle case where data is a JSON string instead of dict
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    logger.warning("solution_design_parse_failed", raw_data=data[:200])
                    return self._default_output(context)
            return self._parse_output(data)
        else:
            logger.error(
                "solution_design_failed",
                error=result.get("error"),
            )
            return self._default_output(context)

    async def _generate_with_feedback(
        self, context: dict[str, Any], feedback: dict[str, Any]
    ) -> SolutionDesignOutput:
        """Generate refined output incorporating critique feedback."""
        prompt = SOLUTION_DESIGN_REFINE_PROMPT.format(
            original_output=json.dumps(feedback["previous_output"], indent=2, default=str),
            feedback="\n".join(f"- {f}" for f in feedback.get("feedback", [])),
        )

        logger.info("solution_design_refine_generation_start")

        result = await call_llm(prompt, "solution_design_refine")

        if result.get("success"):
            data = result["data"]
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return self._parse_output(feedback["previous_output"])
            output = self._parse_output(data)
            logger.info("solution_design_refine_generation_complete")
            return output
        else:
            logger.warning(
                "solution_design_refine_failed",
                error=result.get("error"),
            )
            # Return the previous output if refinement fails
            return self._parse_output(feedback["previous_output"])

    async def analyze_dhm(
        self,
        session: DiscoverySessionV4,
        solution: str,
        context: dict[str, Any] = None,
    ) -> DHMScore:
        """Perform DHM analysis on a solution."""
        if context is None:
            context = {}

        prompt = DHM_ANALYSIS_PROMPT.format(
            solution=solution,
            opportunity=context.get("primary_opportunity", "Not specified"),
            target_market=context.get("target_market", "Not specified"),
            patterns=json.dumps(context.get("patterns", {}), default=str),
        )

        result = await call_llm(prompt, "dhm_analysis")

        if result.get("success"):
            data = result["data"]
            return self._parse_dhm(data)
        else:
            logger.error("dhm_analysis_failed", error=result.get("error"))
            return self._default_dhm()

    async def run_pre_mortem(
        self,
        session: DiscoverySessionV4,
        solution: str,
        dhm_score: DHMScore | None = None,
        context: dict[str, Any] = None,
    ) -> PreMortem:
        """Run pre-mortem analysis."""
        if context is None:
            context = {}

        prompt = PRE_MORTEM_PROMPT.format(
            solution=solution,
            dhm_score=json.dumps(
                dhm_score.model_dump() if dhm_score else {}, default=str
            ),
            target_market=context.get("target_market", "Not specified"),
            four_forces=json.dumps(context.get("four_forces", {}), default=str),
        )

        result = await call_llm(prompt, "pre_mortem")

        if result.get("success"):
            data = result["data"]
            return self._parse_pre_mortem(data)
        else:
            logger.error("pre_mortem_failed", error=result.get("error"))
            return self._default_pre_mortem()

    def _parse_output(self, data: dict[str, Any]) -> SolutionDesignOutput:
        """Parse full solution design output."""
        dhm_score = self._parse_dhm(data.get("dhm_score", {}))
        pre_mortem = self._parse_pre_mortem(data.get("pre_mortem", {}))

        return SolutionDesignOutput(
            solution_concept=data.get("solution_concept", ""),
            solution_description=data.get("solution_description", ""),
            key_features=data.get("key_features", []),
            dhm_score=dhm_score,
            pre_mortem=pre_mortem,
            value_proposition=data.get("value_proposition", ""),
        )

    def _parse_dhm(self, data: dict[str, Any]) -> DHMScore:
        """Parse DHM score from data."""
        delight = data.get("delight", 5)
        hard_to_copy = data.get("hard_to_copy", 5)
        margin = data.get("margin", 5)
        total = delight + hard_to_copy + margin

        return DHMScore(
            delight=delight,
            delight_reasoning=data.get(
                "delight_reasoning", "Needs analysis"
            ),
            hard_to_copy=hard_to_copy,
            hard_to_copy_reasoning=data.get(
                "hard_to_copy_reasoning", "Needs analysis"
            ),
            moat_type=data.get("moat_type"),
            margin=margin,
            margin_reasoning=data.get("margin_reasoning", "Needs analysis"),
            total=total,
            passes_threshold=total >= 20,
        )

    def _parse_pre_mortem(self, data: dict[str, Any]) -> PreMortem:
        """Parse pre-mortem analysis."""
        def parse_item(t: Any) -> PreMortemItem:
            """Parse a single pre-mortem item, handling both dict and string formats."""
            if isinstance(t, str):
                return PreMortemItem(description=t)
            elif isinstance(t, dict):
                return PreMortemItem(
                    description=t.get("description", ""),
                    mitigation=t.get("mitigation"),
                    early_warning=t.get("early_warning"),
                    owner=t.get("owner"),
                )
            else:
                return PreMortemItem(description=str(t))

        tigers = [parse_item(t) for t in data.get("tigers", [])]
        paper_tigers = [parse_item(t) for t in data.get("paper_tigers", [])]
        elephants = [parse_item(t) for t in data.get("elephants", [])]

        return PreMortem(
            tigers=tigers,
            paper_tigers=paper_tigers,
            elephants=elephants,
        )

    def _default_output(self, context: dict[str, Any]) -> SolutionDesignOutput:
        """Return default output when generation fails."""
        return SolutionDesignOutput(
            solution_concept=context.get("product_idea", "Solution concept needed"),
            solution_description="Design a solution based on the opportunity mapping",
            key_features=[],
            dhm_score=self._default_dhm(),
            pre_mortem=self._default_pre_mortem(),
            value_proposition="Define value proposition based on customer needs",
        )

    def _default_dhm(self) -> DHMScore:
        """Return default DHM score."""
        return DHMScore(
            delight=5,
            delight_reasoning="Needs analysis",
            hard_to_copy=5,
            hard_to_copy_reasoning="Needs analysis",
            moat_type=None,
            margin=5,
            margin_reasoning="Needs analysis",
            total=15,
            passes_threshold=False,
        )

    def _default_pre_mortem(self) -> PreMortem:
        """Return default pre-mortem."""
        return PreMortem(
            tigers=[
                PreMortemItem(
                    description="Market risk - need to validate demand",
                    mitigation="Run validation experiments",
                )
            ],
            paper_tigers=[],
            elephants=[
                PreMortemItem(
                    description="Founder assumptions may be wrong",
                    mitigation="Stay close to customers",
                )
            ],
        )

    async def get_suggestions(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get suggestions for solution design."""
        suggestions = []

        dhm = context.get("dhm_score", {})
        total = dhm.get("total", 0)

        if total < 20:
            if dhm.get("delight", 5) < 7:
                suggestions.append("Focus on increasing delight - what would make users love this?")
            if dhm.get("hard_to_copy", 5) < 7:
                suggestions.append("Build defensibility - what moat can you create?")
            if dhm.get("margin", 5) < 7:
                suggestions.append("Improve unit economics - how can this be profitable?")

        if not context.get("pre_mortem"):
            suggestions.append("Run pre-mortem to identify risks early")

        if not suggestions:
            suggestions = [
                "Review DHM score breakdown for areas to improve",
                "Address the tigers in your pre-mortem",
                "Consider if there are elephants in the room",
            ]

        return {"suggestions": suggestions[:3]}
