"""
Facilitator Agent for Swarm Orchestration.

The Facilitator is the central intelligence that:
- Coordinates all swarms
- Detects contradictions between agent outputs
- Resolves conflicts by re-running specific agents
- Synthesizes final outputs
"""

from typing import Any

import structlog

from agents.planner import run_planner_agent
from agents.critique import run_critique_agent
from agents.state import DiscoveryState
from agents.swarms import DiscoverySwarm, StrategySwarm, DeliverySwarm
from models.schemas import SessionStatus

logger = structlog.get_logger(__name__)


class FacilitatorAgent:
    """
    Central intelligence coordinating all swarms.

    The Facilitator:
    1. Creates a research plan
    2. Dispatches swarms in dependency order
    3. Detects contradictions between outputs
    4. Resolves conflicts through targeted re-runs
    5. Synthesizes final outputs
    """

    def __init__(self):
        self.logger = structlog.get_logger("facilitator")
        self.discovery_swarm = DiscoverySwarm()
        self.strategy_swarm = StrategySwarm()
        self.delivery_swarm = DeliverySwarm()

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """
        Execute the complete swarm-based workflow.

        Args:
            state: Initial discovery state.

        Returns:
            DiscoveryState: Final state with all outputs.
        """
        self.logger.info(
            "facilitator_start",
            session_id=state["session_id"],
        )

        try:
            # Phase 1: Planning
            state = await self._run_planning_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Phase 2: Discovery Swarm
            state = await self._run_discovery_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Check for contradictions in discovery outputs
            contradictions = self.detect_contradictions(state, phase="discovery")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # Phase 3: Strategy Swarm (depends on Discovery)
            state = await self._run_strategy_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Check for contradictions between discovery and strategy
            contradictions = self.detect_contradictions(state, phase="strategy")
            if contradictions:
                state = await self._resolve_contradictions(state, contradictions)

            # Phase 4: Delivery Swarm (depends on Discovery + Strategy)
            state = await self._run_delivery_phase(state)
            if state.get("status") == SessionStatus.FAILED:
                return state

            # Phase 5: Quality Check
            state = await self._run_quality_check(state)

            # Phase 6: Executive Summary and Finalization
            state = await self._synthesize_outputs(state)

            self.logger.info(
                "facilitator_complete",
                session_id=state["session_id"],
                status=state.get("status"),
            )

            return state

        except Exception as e:
            self.logger.error(
                "facilitator_error",
                session_id=state["session_id"],
                error=str(e),
                exc_info=True,
            )
            state["status"] = SessionStatus.FAILED
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"Facilitator error: {str(e)}")
            return state

    async def _run_planning_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the planning agent."""
        self.logger.info("phase_start", phase="planning", session_id=state["session_id"])
        state = await run_planner_agent(state)
        return state

    async def _run_discovery_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the discovery swarm."""
        self.logger.info("phase_start", phase="discovery", session_id=state["session_id"])
        state = await self.discovery_swarm.run(state)
        return state

    async def _run_strategy_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the strategy swarm."""
        self.logger.info("phase_start", phase="strategy", session_id=state["session_id"])
        state = await self.strategy_swarm.run(state)
        return state

    async def _run_delivery_phase(self, state: DiscoveryState) -> DiscoveryState:
        """Run the delivery swarm."""
        self.logger.info("phase_start", phase="delivery", session_id=state["session_id"])
        state = await self.delivery_swarm.run(state)
        return state

    async def _run_quality_check(self, state: DiscoveryState) -> DiscoveryState:
        """Run the critique agent for quality assessment."""
        self.logger.info("phase_start", phase="quality_check", session_id=state["session_id"])
        state = await run_critique_agent(state)
        return state

    async def _synthesize_outputs(self, state: DiscoveryState) -> DiscoveryState:
        """Generate executive summary and finalize."""
        from agents.orchestrator import executive_summary_node, finalize_node

        self.logger.info("phase_start", phase="synthesis", session_id=state["session_id"])

        # Generate executive summary
        state = await executive_summary_node(state)

        # Finalize
        state = await finalize_node(state)

        return state

    def detect_contradictions(
        self, state: DiscoveryState, phase: str = "all"
    ) -> list[dict[str, Any]]:
        """
        Detect contradictions between agent outputs.

        Checks for inconsistencies in:
        - Market size estimates
        - Pricing assumptions
        - Target customer definitions
        - Technical feasibility vs business requirements

        Args:
            state: Current workflow state.
            phase: Which phase to check ("discovery", "strategy", or "all").

        Returns:
            list[dict]: List of detected contradictions.
        """
        contradictions = []

        # Get relevant outputs
        customer_research = state.get("customer_research", {})
        business_case = state.get("business_case", {})
        financial_model = state.get("financial_model", {})
        gtm_plan = state.get("gtm_plan", {})

        # Check 1: Market size consistency
        if customer_research and business_case:
            cr_tam = customer_research.get("market_context", {}).get("total_addressable_market", "")
            bc_tam = business_case.get("market_size", {}).get("tam", "")

            if cr_tam and bc_tam and self._values_differ_significantly(cr_tam, bc_tam):
                contradictions.append({
                    "type": "market_size",
                    "agents": ["customer_research", "business_strategy"],
                    "field": "TAM",
                    "values": {"customer_research": cr_tam, "business_case": bc_tam},
                    "severity": "medium",
                })

        # Check 2: Pricing consistency
        if business_case and financial_model:
            bc_pricing = business_case.get("revenue_streams", [])
            fm_pricing = financial_model.get("revenue_model", {}).get("primary_revenue_stream", {})

            if bc_pricing and fm_pricing:
                bc_price = self._extract_price(bc_pricing)
                fm_price = fm_pricing.get("pricing_tiers", [{}])[0].get("price_monthly", 0)

                if bc_price and fm_price and abs(bc_price - fm_price) / max(bc_price, fm_price) > 0.5:
                    contradictions.append({
                        "type": "pricing",
                        "agents": ["business_strategy", "financial_modeling"],
                        "field": "pricing",
                        "values": {"business_case": bc_price, "financial_model": fm_price},
                        "severity": "high",
                    })

        # Check 3: Target customer consistency
        if customer_research and gtm_plan:
            cr_segments = customer_research.get("market_context", {}).get("customer_segments", [])
            gtm_segment = gtm_plan.get("market_entry_strategy", {}).get("initial_segment", "")

            if cr_segments and gtm_segment:
                if not any(gtm_segment.lower() in str(seg).lower() for seg in cr_segments):
                    contradictions.append({
                        "type": "target_customer",
                        "agents": ["customer_research", "gtm_strategy"],
                        "field": "initial_segment",
                        "values": {"customer_research": cr_segments, "gtm_plan": gtm_segment},
                        "severity": "medium",
                    })

        if contradictions:
            self.logger.warning(
                "contradictions_detected",
                session_id=state["session_id"],
                phase=phase,
                count=len(contradictions),
                types=[c["type"] for c in contradictions],
            )

        return contradictions

    async def _resolve_contradictions(
        self,
        state: DiscoveryState,
        contradictions: list[dict[str, Any]],
    ) -> DiscoveryState:
        """
        Resolve contradictions by re-running specific agents with context.

        Args:
            state: Current workflow state.
            contradictions: List of detected contradictions.

        Returns:
            DiscoveryState: Updated state after resolution.
        """
        self.logger.info(
            "resolving_contradictions",
            session_id=state["session_id"],
            count=len(contradictions),
        )

        # For high-severity contradictions, re-run the affected agents
        high_severity = [c for c in contradictions if c.get("severity") == "high"]

        if not high_severity:
            # Just log medium severity and continue
            return state

        # Add contradiction context to state for agents to consider
        state["contradiction_context"] = {
            "contradictions": contradictions,
            "resolution_instruction": (
                "Previous outputs contained inconsistencies. "
                "Please review and ensure your output is consistent with other agents' findings. "
                "Contradictions detected: " + str([c["type"] for c in contradictions])
            ),
        }

        # Re-run the second agent in each contradiction (typically the one that should adjust)
        agents_to_rerun = set()
        for c in high_severity:
            agents_to_rerun.add(c["agents"][1])  # Re-run the second agent

        for agent in agents_to_rerun:
            self.logger.info(
                "rerunning_agent_for_resolution",
                session_id=state["session_id"],
                agent=agent,
            )

            if agent == "business_strategy":
                from agents.business_strategy import run_business_strategy_agent
                state = await run_business_strategy_agent(state)
            elif agent == "financial_modeling":
                from agents.swarms.strategy_swarm import run_financial_modeling
                state = await run_financial_modeling(state)
            elif agent == "gtm_strategy":
                from agents.swarms.strategy_swarm import run_gtm_strategy
                state = await run_gtm_strategy(state)

        # Clear contradiction context after resolution
        if "contradiction_context" in state:
            del state["contradiction_context"]

        return state

    def _values_differ_significantly(self, val1: str, val2: str) -> bool:
        """Check if two string values representing numbers differ significantly."""
        import re

        def extract_number(s: str) -> float | None:
            # Extract numeric value from strings like "$5B", "5 billion", etc.
            s = s.lower().replace(",", "").replace("$", "")
            multipliers = {"k": 1e3, "m": 1e6, "b": 1e9, "t": 1e12}

            match = re.search(r"(\d+(?:\.\d+)?)\s*(k|m|b|t|billion|million|thousand|trillion)?", s)
            if match:
                num = float(match.group(1))
                mult = match.group(2) or ""
                if mult.startswith("b"):
                    num *= 1e9
                elif mult.startswith("m"):
                    num *= 1e6
                elif mult.startswith("t"):
                    if "thousand" in mult:
                        num *= 1e3
                    else:
                        num *= 1e12
                elif mult.startswith("k"):
                    num *= 1e3
                elif mult in multipliers:
                    num *= multipliers[mult]
                return num
            return None

        n1 = extract_number(val1)
        n2 = extract_number(val2)

        if n1 is None or n2 is None:
            return False

        # Differ by more than 100%
        return abs(n1 - n2) / max(n1, n2) > 1.0

    def _extract_price(self, revenue_streams: list) -> float | None:
        """Extract a price from revenue streams list."""
        if not revenue_streams:
            return None

        for stream in revenue_streams:
            if isinstance(stream, dict):
                price = stream.get("price") or stream.get("pricing") or stream.get("monthly_price")
                if price:
                    if isinstance(price, (int, float)):
                        return float(price)
                    import re
                    match = re.search(r"(\d+(?:\.\d+)?)", str(price))
                    if match:
                        return float(match.group(1))
        return None


async def run_facilitator(state: DiscoveryState) -> DiscoveryState:
    """
    Run the Facilitator agent.

    This is the main entry point for swarm-based workflow execution.

    Args:
        state: Initial discovery state.

    Returns:
        DiscoveryState: Final state with all outputs.
    """
    facilitator = FacilitatorAgent()
    return await facilitator.run(state)
