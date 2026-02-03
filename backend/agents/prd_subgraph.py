"""
PRD Sub-Graph for the Product Discovery Multi-Agent System.

This module defines a sub-workflow that orchestrates the PRD generation loop:
1. PRD Generator - Creates/refines the PRD
2. PRD Critic - Evaluates quality and provides feedback
3. (Loop) - If quality < threshold and iterations < max, go back to Generator
4. PRD Formatter - Formats and validates the final PRD

The sub-graph is integrated into the main orchestrator between
Business Strategy and Technical Architect agents.
"""

from typing import Literal

import structlog
from langgraph.graph import END, StateGraph

from agents.prd_generator import run_prd_generator
from agents.prd_critic import run_prd_critic
from agents.prd_formatter import run_prd_formatter
from agents.state import DiscoveryState
from config import settings

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NODE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def prd_generator_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for PRD Generator Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with PRD draft.
    """
    logger.info(
        "prd_subgraph_node_start",
        node="prd_generator",
        session_id=state.get("session_id"),
        prd_iteration=state.get("prd_iteration", 0) + 1,
    )

    updates = await run_prd_generator(state)

    # Merge updates into state
    for key, value in updates.items():
        state[key] = value

    return state


async def prd_critic_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for PRD Critic Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with quality assessment.
    """
    logger.info(
        "prd_subgraph_node_start",
        node="prd_critic",
        session_id=state.get("session_id"),
        prd_iteration=state.get("prd_iteration", 1),
    )

    updates = await run_prd_critic(state)

    # Merge updates into state
    for key, value in updates.items():
        state[key] = value

    return state


async def prd_formatter_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for PRD Formatter Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with formatted PRD.
    """
    logger.info(
        "prd_subgraph_node_start",
        node="prd_formatter",
        session_id=state.get("session_id"),
        prd_iteration=state.get("prd_iteration", 1),
    )

    updates = await run_prd_formatter(state)

    # Merge updates into state
    for key, value in updates.items():
        state[key] = value

    return state


# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONAL EDGES
# ═══════════════════════════════════════════════════════════════════════════════


def should_continue_prd_loop(state: DiscoveryState) -> Literal["continue", "format"]:
    """
    Determine whether to continue the PRD loop or proceed to formatting.

    Args:
        state: Current workflow state.

    Returns:
        str: "continue" to iterate again, "format" to proceed to formatter.
    """
    prd_quality_passed = state.get("prd_quality_passed", False)
    prd_iteration = state.get("prd_iteration", 1)
    max_iterations = settings.prd_max_iterations
    prd_score = state.get("prd_critic_score", 0.0)

    if prd_quality_passed:
        logger.info(
            "prd_loop_decision",
            session_id=state.get("session_id"),
            decision="format",
            reason="quality_passed",
            prd_iteration=prd_iteration,
            prd_score=prd_score,
        )
        return "format"

    if prd_iteration >= max_iterations:
        logger.warning(
            "prd_loop_decision",
            session_id=state.get("session_id"),
            decision="format",
            reason="max_iterations_reached",
            prd_iteration=prd_iteration,
            prd_score=prd_score,
        )
        return "format"

    logger.info(
        "prd_loop_decision",
        session_id=state.get("session_id"),
        decision="continue",
        reason="quality_not_passed",
        prd_iteration=prd_iteration,
        prd_score=prd_score,
        threshold=settings.prd_quality_threshold,
    )
    return "continue"


# ═══════════════════════════════════════════════════════════════════════════════
# SUB-GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_prd_subgraph() -> StateGraph:
    """
    Build the PRD sub-workflow graph.

    The workflow follows this pattern:
    1. Generator creates/refines PRD draft
    2. Critic evaluates and scores the draft
    3. If quality < threshold and iterations < max: loop back to Generator
    4. Otherwise: Formatter validates and outputs final PRD

    Returns:
        StateGraph: The PRD sub-workflow graph (not compiled).
    """
    # Create the sub-graph with our state type
    subgraph = StateGraph(DiscoveryState)

    # Add nodes
    subgraph.add_node("prd_generator", prd_generator_node)
    subgraph.add_node("prd_critic", prd_critic_node)
    subgraph.add_node("prd_formatter", prd_formatter_node)

    # Set entry point
    subgraph.set_entry_point("prd_generator")

    # Generator -> Critic
    subgraph.add_edge("prd_generator", "prd_critic")

    # Conditional edge from Critic
    subgraph.add_conditional_edges(
        "prd_critic",
        should_continue_prd_loop,
        {
            "continue": "prd_generator",  # Loop back for another iteration
            "format": "prd_formatter",     # Proceed to formatting
        },
    )

    # Formatter is the exit point
    subgraph.add_edge("prd_formatter", END)

    return subgraph


def create_prd_subworkflow():
    """
    Create a compiled PRD sub-workflow.

    Returns:
        Compiled LangGraph sub-workflow ready for integration.
    """
    subgraph = build_prd_subgraph()
    return subgraph.compile()


# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION (for testing)
# ═══════════════════════════════════════════════════════════════════════════════


async def run_prd_subworkflow(state: DiscoveryState) -> DiscoveryState:
    """
    Execute the PRD sub-workflow standalone.

    This is useful for testing or when running the PRD generation
    independently of the main discovery workflow.

    Args:
        state: Discovery state with customer_research and business_case.

    Returns:
        DiscoveryState: Updated state with product_requirements.
    """
    logger.info(
        "prd_subworkflow_start",
        session_id=state.get("session_id"),
    )

    # Initialize PRD-specific state fields if not present
    if state.get("prd_iteration") is None:
        state["prd_iteration"] = 0
    if state.get("prd_draft") is None:
        state["prd_draft"] = None
    if state.get("prd_critic_feedback") is None:
        state["prd_critic_feedback"] = None
    if state.get("prd_critic_score") is None:
        state["prd_critic_score"] = None
    if state.get("prd_quality_passed") is None:
        state["prd_quality_passed"] = False

    # Create and run the sub-workflow
    workflow = create_prd_subworkflow()

    try:
        final_state = await workflow.ainvoke(state)

        logger.info(
            "prd_subworkflow_complete",
            session_id=state.get("session_id"),
            prd_iterations=final_state.get("prd_iteration"),
            prd_score=final_state.get("prd_critic_score"),
            has_product_requirements=final_state.get("product_requirements") is not None,
        )

        return final_state

    except Exception as e:
        logger.error(
            "prd_subworkflow_error",
            session_id=state.get("session_id"),
            error=str(e),
            exc_info=True,
        )
        raise
