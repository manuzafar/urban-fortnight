"""
Stage 3: Opportunity Mapping

Based on Teresa Torres's Opportunity Solution Tree + Jobs to be Done 4 Forces.
This stage maps opportunities and analyzes forces affecting adoption.
"""

import json
from typing import Any

import structlog

from agents.base_agent import call_llm
from agents.discovery_v4.prompts import (
    FOUR_FORCES_PROMPT,
    OPPORTUNITY_TREE_PROMPT,
)
from models.discovery_v4_schemas import (
    DiscoverySessionV4,
    Force,
    FourForcesModel,
    Opportunity,
    OpportunityMappingOutput,
    OpportunitySolutionTree,
)

logger = structlog.get_logger(__name__)


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
        """Run opportunity mapping stage."""
        logger.info(
            "opportunity_mapping_stage_run",
            session_id=session.session_id,
            has_patterns=context.get("patterns") is not None,
        )

        # Generate 4 Forces analysis
        four_forces = await self.generate_four_forces(session, context)

        # Generate Opportunity Tree
        # Use product idea as outcome if not specified
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
