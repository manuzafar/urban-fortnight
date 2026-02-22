"""
Stage 3: Opportunity Mapping

Based on Teresa Torres's Opportunity Solution Tree + Jobs to be Done 4 Forces.
This stage maps opportunities and analyzes forces affecting adoption.

Includes reflection loop: Generate -> Critique -> Refine (max 2 iterations)
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import (
    FOUR_FORCES_PROMPT,
    OPPORTUNITY_MAPPING_REFINE_PROMPT,
    OPPORTUNITY_TREE_PROMPT,
)
from agents.discovery_v4.stages.mini_critique import critique_stage_output
from models.discovery_v4_schemas import (
    DiscoverySessionV4,
    Force,
    FourForcesModel,
    Opportunity,
    OpportunityMappingOutput,
    OpportunitySolutionTree,
)

logger = structlog.get_logger(__name__)

# Reflection loop configuration
MAX_REFLECTION_ITERATIONS = 2
MIN_QUALITY_THRESHOLD = 7.0


class OpportunityMappingStage:
    """
    Stage 3: Opportunity Mapping

    Combines two frameworks:
    1. Jobs to be Done 4 Forces Model (Push, Pull, Anxiety, Habit)
    2. Teresa Torres's Opportunity Solution Tree
    """

    async def run(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> OpportunityMappingOutput:
        """Run opportunity mapping stage with reflection loop."""
        logger.info(
            "opportunity_mapping_stage_run",
            session_id=session.session_id,
            has_patterns=context.get("patterns") is not None,
        )

        return await self._generate_with_reflection(session, context)

    async def _generate_with_reflection(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> OpportunityMappingOutput:
        """Generate with reflection loop: Generate -> Critique -> Refine."""
        iteration = 0
        critique_feedback = None
        output = None

        while iteration < MAX_REFLECTION_ITERATIONS:
            logger.info(
                "opportunity_mapping_reflection_iteration",
                iteration=iteration + 1,
                max_iterations=MAX_REFLECTION_ITERATIONS,
                has_feedback=critique_feedback is not None,
            )

            # Generate (or refine based on feedback)
            if critique_feedback:
                output = await self._generate_with_feedback(session, context, critique_feedback)
            else:
                output = await self._generate_initial(session, context)

            # Critique the output
            critique = await critique_stage_output(
                "opportunity_mapping",
                output.model_dump(),
                evidence_tier="E4",
            )

            logger.info(
                "opportunity_mapping_critique_result",
                iteration=iteration + 1,
                overall_score=critique.get("overall_score"),
                passes_threshold=critique.get("passes_threshold"),
            )

            # Check quality gate
            if critique.get("overall_score", 0) >= MIN_QUALITY_THRESHOLD:
                logger.info(
                    "opportunity_mapping_quality_threshold_met",
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
                "opportunity_mapping_max_iterations_reached",
                final_score=critique.get("overall_score"),
            )

        return output

    async def _generate_initial(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
    ) -> OpportunityMappingOutput:
        """Generate initial opportunity mapping."""
        # Generate 4 Forces analysis
        four_forces = await self.generate_four_forces(session, context)

        # Generate Opportunity Tree
        outcome = context.get(
            "outcome",
            f"Help {context.get('target_market', 'users')} solve {context.get('problem_statement', context.get('product_idea', 'their problem'))}",
        )
        opportunity_tree = await self.generate_opportunity_tree(session, outcome, context)

        # Determine primary opportunity
        primary_opportunity = (
            opportunity_tree.opportunities[0].description
            if opportunity_tree.opportunities
            else "No clear opportunity identified"
        )

        return OpportunityMappingOutput(
            four_forces=four_forces,
            opportunity_tree=opportunity_tree,
            primary_opportunity=primary_opportunity,
        )

    async def _generate_with_feedback(
        self,
        session: DiscoverySessionV4,
        context: dict[str, Any],
        feedback: dict[str, Any],
    ) -> OpportunityMappingOutput:
        """Generate refined output incorporating critique feedback."""
        prompt = OPPORTUNITY_MAPPING_REFINE_PROMPT.format(
            original_output=json.dumps(feedback["previous_output"], indent=2, default=str),
            feedback="\n".join(f"- {f}" for f in feedback.get("feedback", [])),
        )

        logger.info("opportunity_mapping_refine_generation_start")

        result = await call_llm(prompt, "opportunity_mapping_refine")

        if result.get("success"):
            data = result["data"]
            output = self._parse_output(data)
            logger.info("opportunity_mapping_refine_generation_complete")
            return output
        else:
            logger.warning(
                "opportunity_mapping_refine_failed",
                error=result.get("error"),
            )
            # Return the previous output if refinement fails
            return self._parse_output(feedback["previous_output"])

    def _parse_output(self, data: dict[str, Any]) -> OpportunityMappingOutput:
        """Parse full opportunity mapping output."""
        four_forces = self._parse_four_forces(data.get("four_forces", {}))
        opportunity_tree = self._parse_opportunity_tree(
            data.get("opportunity_tree", {}),
            data.get("outcome", "")
        )
        primary_opportunity = data.get(
            "primary_opportunity",
            opportunity_tree.opportunities[0].description if opportunity_tree.opportunities else "No opportunity identified"
        )

        return OpportunityMappingOutput(
            four_forces=four_forces,
            opportunity_tree=opportunity_tree,
            primary_opportunity=primary_opportunity,
        )

    async def generate_four_forces(
        self,
        session: DiscoverySessionV4 | None = None,
        context: dict[str, Any] = None,
    ) -> FourForcesModel:
        """Generate 4 Forces Model analysis."""
        if context is None:
            context = {}

        prompt = FOUR_FORCES_PROMPT.format(
            product_idea=context.get("product_idea", ""),
            problem_statement=context.get("problem_statement", ""),
            patterns=json.dumps(context.get("patterns", {}), default=str),
        )

        result = await call_llm(prompt, "four_forces_analysis")

        if result.get("success"):
            data = result["data"]
            return self._parse_four_forces(data)
        else:
            logger.error(
                "four_forces_generation_failed",
                error=result.get("error"),
            )
            return self._default_four_forces()

    async def generate_opportunity_tree(
        self,
        session: DiscoverySessionV4 | None = None,
        outcome: str = "",
        context: dict[str, Any] = None,
    ) -> OpportunitySolutionTree:
        """Generate Opportunity Solution Tree."""
        if context is None:
            context = {}

        prompt = OPPORTUNITY_TREE_PROMPT.format(
            outcome=outcome,
            problem_statement=context.get("problem_statement", ""),
            patterns=json.dumps(context.get("patterns", {}), default=str),
            four_forces=json.dumps(context.get("four_forces", {}), default=str),
        )

        result = await call_llm(prompt, "opportunity_tree")

        if result.get("success"):
            data = result["data"]
            return self._parse_opportunity_tree(data, outcome)
        else:
            logger.error(
                "opportunity_tree_generation_failed",
                error=result.get("error"),
            )
            return OpportunitySolutionTree(
                outcome=outcome,
                opportunities=[],
            )

    def _parse_four_forces(self, data: dict[str, Any]) -> FourForcesModel:
        """Parse LLM output into FourForcesModel."""
        push = self._parse_force(data.get("push", {}))
        pull = self._parse_force(data.get("pull", {}))
        anxiety = self._parse_force(data.get("anxiety", {}))
        habit = self._parse_force(data.get("habit", {}))

        # Calculate force balance
        force_balance = (push.strength + pull.strength) - (
            anxiety.strength + habit.strength
        )

        return FourForcesModel(
            push=push,
            pull=pull,
            anxiety=anxiety,
            habit=habit,
            force_balance=data.get("force_balance", force_balance),
            change_likely=data.get("change_likely", force_balance > 0),
            key_insight=data.get("key_insight", "Analyze forces to understand adoption likelihood"),
        )

    def _parse_force(self, data: dict[str, Any]) -> Force:
        """Parse a single force."""
        return Force(
            items=data.get("items", []),
            evidence=data.get("evidence", []),
            strength=data.get("strength", 5),
        )

    def _default_four_forces(self) -> FourForcesModel:
        """Return default 4 forces when analysis fails."""
        return FourForcesModel(
            push=Force(items=["Unknown pains"], evidence=[], strength=5),
            pull=Force(items=["Unknown benefits"], evidence=[], strength=5),
            anxiety=Force(items=["Unknown concerns"], evidence=[], strength=5),
            habit=Force(items=["Current workflow"], evidence=[], strength=5),
            force_balance=0,
            change_likely=False,
            key_insight="Need more data to analyze forces",
        )

    def _parse_opportunity_tree(
        self, data: dict[str, Any], default_outcome: str
    ) -> OpportunitySolutionTree:
        """Parse LLM output into OpportunitySolutionTree."""
        opportunities = []
        for opp in data.get("opportunities", []):
            opportunities.append(
                Opportunity(
                    id=opp.get("id", f"opp_{len(opportunities)}"),
                    description=opp.get("description", ""),
                    interview_count=opp.get("interview_count", 0),
                    evidence=opp.get("evidence", []),
                    solutions=opp.get("solutions", []),
                    priority=opp.get("priority", len(opportunities) + 1),
                )
            )

        # Sort by priority
        opportunities.sort(key=lambda x: x.priority)

        return OpportunitySolutionTree(
            outcome=data.get("outcome", default_outcome),
            opportunities=opportunities,
        )

    async def get_suggestions(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Get suggestions for opportunity mapping."""
        has_patterns = context.get("patterns") is not None
        has_four_forces = context.get("four_forces") is not None

        suggestions = []

        if not has_patterns:
            suggestions.append("Complete customer interviews to build patterns")

        if not has_four_forces:
            suggestions.append("Run 4 Forces analysis to understand adoption barriers")
        else:
            four_forces = context.get("four_forces", {})
            balance = four_forces.get("force_balance", 0)
            if balance <= 0:
                suggestions.append("Force balance is negative - find ways to increase Push/Pull or reduce Anxiety/Habit")

        if not context.get("opportunity_tree"):
            suggestions.append("Build Opportunity Solution Tree to prioritize solutions")
        else:
            suggestions.append("Prioritize opportunities by interview frequency and severity")

        return {"suggestions": suggestions[:3]}
