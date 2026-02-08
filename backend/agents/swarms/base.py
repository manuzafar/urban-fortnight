"""
Base Swarm Class for Parallel Agent Execution.

Provides the foundation for swarm implementations with:
- Parallel agent execution using asyncio.gather
- State merging utilities
- Error handling with partial results
- Logging and metrics
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Coroutine

import structlog

from agents.state import DiscoveryState

logger = structlog.get_logger(__name__)


class BaseSwarm(ABC):
    """
    Abstract base class for agent swarms.

    A swarm is a group of agents that can run in parallel because
    they don't have sequential dependencies on each other.
    """

    # Subclasses define their agent list
    agent_names: list[str] = []

    # Display name for logging
    swarm_name: str = "BaseSwarm"

    def __init__(self):
        self.logger = structlog.get_logger(f"swarm.{self.swarm_name}")

    @abstractmethod
    def get_agent_tasks(
        self, state: DiscoveryState
    ) -> list[tuple[str, Coroutine[Any, Any, DiscoveryState]]]:
        """
        Get the list of agent coroutines to run in parallel.

        Args:
            state: Current discovery state.

        Returns:
            List of (agent_name, coroutine) tuples.
        """
        pass

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """
        Execute all agents in the swarm in parallel.

        Args:
            state: Current discovery state.

        Returns:
            DiscoveryState: Merged state with all agent outputs.
        """
        start_time = datetime.utcnow()

        self.logger.info(
            "swarm_start",
            swarm=self.swarm_name,
            session_id=state["session_id"],
            agent_count=len(self.agent_names),
        )

        # Get agent tasks
        agent_tasks = self.get_agent_tasks(state)

        if not agent_tasks:
            self.logger.warning(
                "swarm_no_tasks",
                swarm=self.swarm_name,
                session_id=state["session_id"],
            )
            return state

        # Run all agents in parallel
        agent_names = [name for name, _ in agent_tasks]
        coroutines = [coro for _, coro in agent_tasks]

        results = await asyncio.gather(
            *coroutines,
            return_exceptions=True,
        )

        # Merge results back into state
        merged_state = self._merge_results(state, agent_names, results)

        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()

        # Count successes and failures
        success_count = sum(
            1 for r in results if not isinstance(r, Exception)
        )
        failure_count = len(results) - success_count

        self.logger.info(
            "swarm_complete",
            swarm=self.swarm_name,
            session_id=state["session_id"],
            duration_seconds=round(duration, 2),
            success_count=success_count,
            failure_count=failure_count,
        )

        return merged_state

    def _merge_results(
        self,
        base_state: DiscoveryState,
        agent_names: list[str],
        results: list[DiscoveryState | Exception],
    ) -> DiscoveryState:
        """
        Merge results from parallel agent executions.

        Handles exceptions by logging them and continuing with
        partial results.

        Args:
            base_state: Original state before swarm execution.
            agent_names: Names of agents that ran.
            results: Results from each agent (or Exception if failed).

        Returns:
            DiscoveryState: Merged state.
        """
        merged = dict(base_state)

        for agent_name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                self.logger.error(
                    "swarm_agent_failed",
                    swarm=self.swarm_name,
                    agent=agent_name,
                    error=str(result),
                )
                # Add to errors list
                if "errors" not in merged:
                    merged["errors"] = []
                merged["errors"].append(f"{agent_name}: {str(result)}")
                continue

            # Merge successful result
            # Copy specific output fields from the result
            output_fields = self.get_output_fields(agent_name)
            for field in output_fields:
                if field in result and result[field] is not None:
                    merged[field] = result[field]

            # Merge cross_reference_index from all parallel agents
            if "cross_reference_index" in result and result["cross_reference_index"] is not None:
                merged["cross_reference_index"] = self._merge_cross_references(
                    merged.get("cross_reference_index"),
                    result["cross_reference_index"],
                )

            # Aggregate token usage
            merged["total_tokens_used"] = merged.get("total_tokens_used", 0) + result.get(
                "total_tokens_used", 0
            )
            merged["total_duration_seconds"] = merged.get("total_duration_seconds", 0.0) + result.get(
                "total_duration_seconds", 0.0
            )

            # Merge errors if any
            if result.get("errors"):
                if "errors" not in merged:
                    merged["errors"] = []
                merged["errors"].extend(result["errors"])

        merged["updated_at"] = datetime.utcnow().isoformat()
        return merged

    def get_output_fields(self, agent_name: str) -> list[str]:
        """
        Get the state fields that an agent outputs.

        Override in subclasses for custom field mappings.

        Args:
            agent_name: The agent's name.

        Returns:
            list[str]: Field names this agent writes to state.
        """
        # Default mapping based on common patterns
        field_mappings = {
            "customer_research": ["customer_research"],
            "competitive_intelligence": ["competitive_analysis"],
            "persona_development": ["detailed_personas"],
            "business_strategy": ["business_case"],
            "gtm_strategy": ["gtm_plan"],
            "financial_modeling": ["financial_model"],
            "product_requirements": ["product_requirements"],
            "technical_architect": ["technical_architecture"],
            "legal_regulatory": ["legal_regulatory_review"],
            "risk_assessment": ["risk_assessment"],
            "legal_preliminary": ["preliminary_legal_scan"],
        }
        return field_mappings.get(agent_name, [agent_name])

    def _merge_cross_references(
        self,
        current: dict | None,
        new: dict | None,
    ) -> dict | None:
        """
        Merge cross-reference indices from parallel agents.

        Combines claims, avoiding duplicates, and recalculates statistics.

        Args:
            current: Current cross_reference_index (or None)
            new: New cross_reference_index to merge (or None)

        Returns:
            Merged cross_reference_index dict
        """
        if current is None and new is None:
            return None
        if current is None:
            return new
        if new is None:
            return current

        # Merge claims, avoiding duplicates by claim_id
        current_claims = current.get("claims", [])
        new_claims = new.get("claims", [])

        existing_ids = {c.get("claim_id") for c in current_claims if c.get("claim_id")}
        merged_claims = list(current_claims)

        for claim in new_claims:
            if claim.get("claim_id") not in existing_ids:
                merged_claims.append(claim)
                existing_ids.add(claim.get("claim_id"))

        # Recalculate statistics
        tier_distribution: dict[str, int] = {}
        total_weighted = 0.0
        tier_weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}

        for claim in merged_claims:
            tier = claim.get("evidence_tier", "E5")
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            total_weighted += tier_weights.get(tier, 0.1)

        total_claims = len(merged_claims)
        evidence_score = total_weighted / total_claims if total_claims > 0 else 0.0

        return {
            "claims": merged_claims,
            "total_claims": total_claims,
            "tier_distribution": tier_distribution,
            "evidence_score": evidence_score,
            "unresolved_dependencies": current.get("unresolved_dependencies", [])
            + new.get("unresolved_dependencies", []),
        }
