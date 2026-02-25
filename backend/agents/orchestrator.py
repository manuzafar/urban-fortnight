"""
LangGraph Orchestrator for the Product Discovery Multi-Agent System.

This module defines the workflow that coordinates all 6 agents:
1. Customer Research Agent
2. Business Strategy Agent
3. Product Requirements Agent
4. Technical Architect Agent
5. Legal & Regulatory Review Agent
6. Critique Agent

The workflow includes a conditional revision loop that can iterate
up to 3 times if quality thresholds are not met.

SSE streaming is supported via an optional event_emitter parameter
that broadcasts agent progress and insights in real-time.
"""

import asyncio
import json
from datetime import datetime
from typing import Literal, Optional, TYPE_CHECKING

import structlog
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from langgraph.graph import END, StateGraph

from agents.base_agent import call_llm, configure_gemini
from agents.critique import run_critique_agent, should_revise
from agents.customer_research import run_customer_research_agent
from agents.business_strategy import run_business_strategy_agent
from agents.prd_subgraph import run_prd_subworkflow
from agents.planner import run_planner_agent
from agents.prompts import EXECUTIVE_SUMMARY_PROMPT, format_prompt
from agents.state import DiscoveryState, create_initial_state, get_progress_percentage
from agents.technical_architect import run_technical_architect_agent
from agents.legal_regulatory import run_legal_regulatory_agent, run_legal_preliminary_scan
from config import settings
from models.schemas import ExecutiveSummary, SessionStatus
from utils.state_pruning import (
    prune_state,
    get_state_size,
    PruningConfig,
    default_pruning_config,
)

if TYPE_CHECKING:
    from utils.sse import SessionEventEmitter

logger = structlog.get_logger(__name__)

# Global reference to the current event emitter (set per workflow run)
_current_emitter: Optional["SessionEventEmitter"] = None


def get_current_emitter() -> Optional["SessionEventEmitter"]:
    """Get the current event emitter for the running workflow."""
    return _current_emitter


# ═══════════════════════════════════════════════════════════════════════════════
# NODE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


async def planner_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Planning Agent.

    The planner runs first to analyze the product idea and create
    a research plan that guides all subsequent agents.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with research_plan.
    """
    logger.info(
        "node_start",
        node="planner",
        session_id=state["session_id"],
    )

    # Emit agent start event
    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("planner")

    result = await run_planner_agent(state)

    # Emit insights and completion
    if emitter and result.get("research_plan"):
        plan = result["research_plan"]

        if plan.get("domain_type"):
            await emitter.emit_insight(
                "planner",
                "domain_type",
                f"Domain: {plan['domain_type']}",
            )

        if plan.get("competitors_to_analyze"):
            competitors = plan["competitors_to_analyze"]
            names = [c.get("name", "Unknown") for c in competitors[:3]]
            await emitter.emit_insight(
                "planner",
                "competitors",
                f"Competitors: {', '.join(names)}",
            )

        if plan.get("regulatory_domains"):
            regs = plan["regulatory_domains"]
            reg_names = [r.get("regulation", "Unknown") for r in regs[:3]]
            await emitter.emit_insight(
                "planner",
                "regulations",
                f"Regulations: {', '.join(reg_names)}",
            )

        await emitter.emit_agent_complete(
            "planner",
            "Research plan created",
            insights_count=3,
        )
        await emitter.emit_progress(5, "planner")

    return result


def parallel_dispatch(state: DiscoveryState) -> list[Send]:
    """
    Fan out to parallel tracks after planning.

    This dispatches customer research and legal preliminary scan
    to run concurrently, improving overall workflow speed.

    Args:
        state: Current workflow state after planning.

    Returns:
        list[Send]: List of Send objects for parallel node execution.
    """
    logger.info(
        "parallel_dispatch",
        session_id=state["session_id"],
        tracks=["customer_research", "legal_preliminary"],
    )

    return [
        Send("customer_research", state),
        Send("legal_preliminary", state),
    ]


async def legal_preliminary_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Legal Preliminary Scan.

    This lightweight legal scan runs in parallel with customer research
    to identify regulatory considerations early.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with preliminary_legal_scan.
    """
    logger.info(
        "node_start",
        node="legal_preliminary",
        session_id=state["session_id"],
    )

    # Emit agent start event
    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("legal_preliminary")

    result = await run_legal_preliminary_scan(state)

    # Emit insights and completion
    if emitter and result.get("preliminary_legal_scan"):
        scan = result["preliminary_legal_scan"]

        if scan.get("regulatory_domains"):
            domains = [d.get("name", "Unknown") for d in scan["regulatory_domains"][:3]]
            await emitter.emit_insight(
                "legal_preliminary",
                "domains",
                f"Regulations: {', '.join(domains)}",
            )

        if scan.get("initial_risk_level"):
            await emitter.emit_insight(
                "legal_preliminary",
                "risk_level",
                f"Initial risk: {scan['initial_risk_level']}",
            )

        if scan.get("blocking_issues") and len(scan["blocking_issues"]) > 0:
            await emitter.emit_insight(
                "legal_preliminary",
                "blockers",
                f"{len(scan['blocking_issues'])} potential blockers identified",
            )

        await emitter.emit_agent_complete(
            "legal_preliminary",
            "Preliminary legal scan complete",
            insights_count=3,
        )
        await emitter.emit_progress(10, "legal_preliminary")

    return result


async def convergence_node(state: DiscoveryState) -> DiscoveryState:
    """
    Merge results from parallel tracks.

    This node:
    - Combines customer_research output with preliminary_legal_scan
    - Enriches context for downstream agents
    - Logs the convergence event

    Args:
        state: Current workflow state with parallel outputs.

    Returns:
        DiscoveryState: State ready for business_strategy.
    """
    logger.info(
        "convergence_node",
        session_id=state["session_id"],
        has_customer_research=state.get("customer_research") is not None,
        has_preliminary_legal=state.get("preliminary_legal_scan") is not None,
    )

    # Update state to show convergence
    state["current_agent"] = "Convergence"
    state["updated_at"] = datetime.utcnow().isoformat()

    # Log the merge
    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_progress(18, "convergence")

    return state


async def customer_research_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Customer Research Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state after agent execution.
    """
    logger.info(
        "node_start",
        node="customer_research",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    # Emit agent start event
    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("customer_research")

    result = await run_customer_research_agent(state)

    # Emit insights and completion
    if emitter and result.get("customer_research"):
        cr = result["customer_research"]

        # Emit key insights
        if cr.get("pain_signals"):
            await emitter.emit_insight(
                "customer_research",
                "pain_signals",
                f"Found {len(cr['pain_signals'])} pain points",
                cr["pain_signals"][0] if cr["pain_signals"] else None,
            )

        if cr.get("personas"):
            await emitter.emit_insight(
                "customer_research",
                "personas",
                f"Identified {len(cr['personas'])} personas",
            )

        if cr.get("market_context", {}).get("total_addressable_market"):
            tam = cr["market_context"]["total_addressable_market"]
            await emitter.emit_insight(
                "customer_research",
                "market_size",
                f"TAM: {tam}",
            )

        await emitter.emit_agent_complete(
            "customer_research",
            "Market research and personas identified",
            insights_count=3,
        )
        await emitter.emit_progress(15, "customer_research")

    return result


async def business_strategy_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Business Strategy Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state after agent execution.
    """
    logger.info(
        "node_start",
        node="business_strategy",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("business_strategy")

    result = await run_business_strategy_agent(state)

    if emitter and result.get("business_case"):
        bc = result["business_case"]

        if bc.get("revenue_streams"):
            await emitter.emit_insight(
                "business_strategy",
                "revenue_streams",
                f"{len(bc['revenue_streams'])} revenue streams defined",
            )

        if bc.get("lean_canvas", {}).get("unique_value_proposition"):
            await emitter.emit_insight(
                "business_strategy",
                "value_proposition",
                "Value proposition defined",
            )

        if bc.get("go_to_market", {}).get("channels"):
            channels = bc["go_to_market"]["channels"]
            await emitter.emit_insight(
                "business_strategy",
                "channels",
                f"{len(channels)} GTM channels identified",
            )

        await emitter.emit_agent_complete(
            "business_strategy",
            "Business model and revenue strategy complete",
            insights_count=3,
        )
        await emitter.emit_progress(30, "business_strategy")

    return result


async def product_requirements_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Product Requirements Sub-Workflow.

    This node runs the PRD sub-graph which includes:
    1. PRD Generator - Creates/refines the PRD
    2. PRD Critic - Evaluates quality and provides feedback
    3. (Loop) - Iterates until quality threshold is met or max iterations reached
    4. PRD Formatter - Formats and validates the final PRD

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state with product_requirements.
    """
    logger.info(
        "node_start",
        node="product_requirements_subgraph",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("product_requirements")

    # Initialize PRD sub-workflow state fields
    state["prd_iteration"] = 0
    state["prd_draft"] = None
    state["prd_critic_feedback"] = None
    state["prd_critic_score"] = None
    state["prd_quality_passed"] = False

    # Run the PRD sub-workflow
    updated_state = await run_prd_subworkflow(state)

    logger.info(
        "node_complete",
        node="product_requirements_subgraph",
        session_id=state["session_id"],
        prd_iterations=updated_state.get("prd_iteration"),
        prd_score=updated_state.get("prd_critic_score"),
        has_product_requirements=updated_state.get("product_requirements") is not None,
    )

    if emitter and updated_state.get("product_requirements"):
        prd = updated_state["product_requirements"]

        if prd.get("epics"):
            await emitter.emit_insight(
                "product_requirements",
                "epics",
                f"{len(prd['epics'])} epics defined",
            )

        total_stories = sum(
            len(epic.get("user_stories", [])) for epic in prd.get("epics", [])
        )
        if total_stories:
            await emitter.emit_insight(
                "product_requirements",
                "user_stories",
                f"{total_stories} user stories created",
            )

        if prd.get("functional_requirements"):
            await emitter.emit_insight(
                "product_requirements",
                "requirements",
                f"{len(prd['functional_requirements'])} functional requirements",
            )

        await emitter.emit_agent_complete(
            "product_requirements",
            f"PRD complete after {updated_state.get('prd_iteration', 1)} iterations",
            insights_count=3,
        )
        await emitter.emit_progress(50, "product_requirements")

    return updated_state


async def technical_architect_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Technical Architect Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state after agent execution.
    """
    logger.info(
        "node_start",
        node="technical_architect",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("technical_architect")

    result = await run_technical_architect_agent(state)

    if emitter and result.get("technical_architecture"):
        ta = result["technical_architecture"]

        if ta.get("tech_stack"):
            stack = ta["tech_stack"]
            techs = []
            if stack.get("frontend"):
                techs.append(stack["frontend"])
            if stack.get("backend"):
                techs.append(stack["backend"])
            if techs:
                await emitter.emit_insight(
                    "technical_architect",
                    "tech_stack",
                    f"Stack: {', '.join(techs[:3])}",
                )

        if ta.get("system_components"):
            await emitter.emit_insight(
                "technical_architect",
                "components",
                f"{len(ta['system_components'])} system components",
            )

        if ta.get("security_architecture"):
            await emitter.emit_insight(
                "technical_architect",
                "security",
                "Security architecture defined",
            )

        await emitter.emit_agent_complete(
            "technical_architect",
            "System architecture designed",
            insights_count=3,
        )
        await emitter.emit_progress(65, "technical_architect")

    return result


async def legal_regulatory_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Legal & Regulatory Review Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state after agent execution.
    """
    logger.info(
        "node_start",
        node="legal_regulatory",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("legal_regulatory")

    result = await run_legal_regulatory_agent(state)

    if emitter and result.get("legal_regulatory_review"):
        lr = result["legal_regulatory_review"]

        if lr.get("applicable_regulations"):
            await emitter.emit_insight(
                "legal_regulatory",
                "regulations",
                f"{len(lr['applicable_regulations'])} regulations identified",
            )

        if lr.get("data_protection"):
            await emitter.emit_insight(
                "legal_regulatory",
                "data_protection",
                "Data protection requirements defined",
            )

        if lr.get("overall_risk_assessment", {}).get("risk_level"):
            risk = lr["overall_risk_assessment"]["risk_level"]
            await emitter.emit_insight(
                "legal_regulatory",
                "risk_level",
                f"Risk level: {risk}",
            )

        await emitter.emit_agent_complete(
            "legal_regulatory",
            "Compliance review complete",
            insights_count=3,
        )
        await emitter.emit_progress(85, "legal_regulatory")

    return result


async def critique_node(state: DiscoveryState) -> DiscoveryState:
    """
    Node wrapper for Critique Agent.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Updated state after agent execution.
    """
    logger.info(
        "node_start",
        node="critique",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("critique")

    result = await run_critique_agent(state)

    if emitter and result.get("quality_assessment"):
        qa = result["quality_assessment"]

        if qa.get("overall_score") is not None:
            score = qa["overall_score"]
            await emitter.emit_insight(
                "critique",
                "quality_score",
                f"Quality score: {int(score * 100)}%",
            )

        if qa.get("strengths"):
            await emitter.emit_insight(
                "critique",
                "strengths",
                f"{len(qa['strengths'])} strengths identified",
            )

        if qa.get("areas_for_improvement"):
            await emitter.emit_insight(
                "critique",
                "improvements",
                f"{len(qa['areas_for_improvement'])} areas for improvement",
            )

        await emitter.emit_agent_complete(
            "critique",
            f"Quality assessment: {int((qa.get('overall_score') or 0) * 100)}%",
            insights_count=3,
        )
        await emitter.emit_progress(95, "critique")

    return result


async def executive_summary_node(state: DiscoveryState) -> DiscoveryState:
    """
    Generate the executive summary from all agent outputs.

    This node synthesizes the complete inception pack into a
    concise executive summary.

    Args:
        state: Current workflow state with all agent outputs.

    Returns:
        DiscoveryState: Updated state with executive summary.
    """
    logger.info(
        "node_start",
        node="executive_summary",
        session_id=state["session_id"],
    )

    emitter = get_current_emitter()
    if emitter:
        await emitter.emit_agent_start("executive_summary")

    state["current_agent"] = "Executive Summary Generator"
    state["updated_at"] = datetime.utcnow().isoformat()

    # Format the synthesis prompt
    prompt = format_prompt(
        template=EXECUTIVE_SUMMARY_PROMPT,
        product_idea=state["product_idea"],
        customer_research=json.dumps(state.get("customer_research", {}), indent=2),
        business_case=json.dumps(state.get("business_case", {}), indent=2),
        product_requirements=json.dumps(state.get("product_requirements", {}), indent=2),
        technical_architecture=json.dumps(state.get("technical_architecture", {}), indent=2),
        legal_regulatory_review=json.dumps(state.get("legal_regulatory_review", {}), indent=2),
    )

    # Call LLM for synthesis
    result = await call_llm(prompt, "Executive Summary Generator")

    # Update tracking
    state["total_tokens_used"] = state.get("total_tokens_used", 0) + result.get("tokens_used", 0)
    state["total_duration_seconds"] = state.get("total_duration_seconds", 0.0) + result.get(
        "duration_seconds", 0.0
    )

    if result["success"]:
        try:
            validated_data = ExecutiveSummary.model_validate(result["data"])
            state["executive_summary"] = validated_data.model_dump()
            logger.info(
                "executive_summary_generated",
                session_id=state["session_id"],
                product_name=validated_data.product_name,
            )

            # Emit executive summary insights
            if emitter:
                await emitter.emit_insight(
                    "executive_summary",
                    "product_name",
                    f"Product: {validated_data.product_name}",
                )
                if validated_data.recommendation:
                    await emitter.emit_insight(
                        "executive_summary",
                        "recommendation",
                        validated_data.recommendation[:100],
                    )

        except Exception as e:
            logger.error(
                "executive_summary_validation_error",
                session_id=state["session_id"],
                error=str(e),
            )
            state["executive_summary"] = result["data"]
    else:
        logger.error(
            "executive_summary_failed",
            session_id=state["session_id"],
            error=result.get("error"),
        )
        # Create a minimal executive summary from available data
        state["executive_summary"] = _create_fallback_summary(state)

    if emitter:
        await emitter.emit_agent_complete(
            "executive_summary",
            "Executive summary generated",
            insights_count=2,
        )
        await emitter.emit_progress(100, "executive_summary")

    return state


async def prepare_revision_node(state: DiscoveryState) -> DiscoveryState:
    """
    Prepare state for a revision iteration.

    This node:
    - Increments the iteration counter
    - Clears outputs from the failing agent onwards (targeted revision)
    - Preserves outputs from earlier agents that passed
    - Prunes unbounded state fields to manage memory
    - Logs the revision event

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: State prepared for revision.
    """
    current_iteration = state.get("iteration", 1)
    new_iteration = current_iteration + 1

    # Determine which agent to start from based on quality scores
    target_agent = route_revision(state)

    # Agent execution order for determining what to clear
    agent_order = [
        "customer_research",
        "business_strategy",  # maps to business_case
        "product_requirements",
        "technical_architect",  # maps to technical_architecture
        "legal_regulatory",  # maps to legal_regulatory_review
    ]

    # State keys for each agent
    agent_to_state_key = {
        "customer_research": "customer_research",
        "business_strategy": "business_case",
        "product_requirements": "product_requirements",
        "technical_architect": "technical_architecture",
        "legal_regulatory": "legal_regulatory_review",
    }

    # Find the index of the target agent
    try:
        start_index = agent_order.index(target_agent)
    except ValueError:
        start_index = 0  # Fallback to clearing everything

    # Determine what to clear (from target agent onwards)
    agents_to_clear = agent_order[start_index:]
    agents_preserved = agent_order[:start_index]

    # Log state size before pruning
    size_before = get_state_size(state)

    logger.info(
        "revision_started",
        session_id=state["session_id"],
        previous_iteration=current_iteration,
        new_iteration=new_iteration,
        quality_score=(state.get("quality_assessment") or {}).get("overall_score"),
        target_agent=target_agent,
        agents_to_clear=agents_to_clear,
        agents_preserved=agents_preserved,
        state_size_before=size_before,
    )

    # Increment iteration
    state["iteration"] = new_iteration
    state["updated_at"] = datetime.utcnow().isoformat()

    # Only clear outputs from the failing agent onwards
    # This preserves work from earlier agents that passed quality checks
    for agent in agents_to_clear:
        state_key = agent_to_state_key.get(agent)
        if state_key:
            state[state_key] = None

    # Keep quality_assessment for reference
    # Keep critique_feedback for agents to use

    # Prune unbounded state fields after revision loop
    pruning_config = PruningConfig.from_settings()
    if pruning_config.prune_after_revision:
        state = await prune_state(
            state,
            max_revision_history=pruning_config.max_revision_history,
            max_errors=pruning_config.max_errors,
            max_claims=pruning_config.max_claims,
            archive_revisions=pruning_config.archive_revisions,
        )

        size_after = get_state_size(state)
        logger.info(
            "revision_state_pruned",
            session_id=state["session_id"],
            size_before=size_before,
            size_after=size_after,
        )

    return state


async def finalize_node(state: DiscoveryState) -> DiscoveryState:
    """
    Finalize the workflow and mark as completed.

    Also:
    - Prunes unbounded state fields to reduce storage size
    - Stores high-quality outputs as memories for future runs (cross-run learning)

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Finalized state.
    """
    state["status"] = SessionStatus.COMPLETED
    state["current_agent"] = "Complete"
    state["updated_at"] = datetime.utcnow().isoformat()

    quality_score = (state.get("quality_assessment") or {}).get("overall_score")

    # Log state size before finalization
    size_before = get_state_size(state)

    logger.info(
        "workflow_completed",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
        total_tokens=state.get("total_tokens_used", 0),
        total_duration=round(state.get("total_duration_seconds", 0), 2),
        quality_score=quality_score,
        quality_passed=state.get("quality_passed", False),
        state_size_before_finalize=size_before,
    )

    # Prune unbounded state fields before final storage
    pruning_config = PruningConfig.from_settings()
    if pruning_config.prune_on_finalize:
        state = await prune_state(
            state,
            max_revision_history=pruning_config.max_revision_history,
            max_errors=pruning_config.max_errors,
            max_claims=pruning_config.max_claims,
            archive_revisions=pruning_config.archive_revisions,
        )

        size_after = get_state_size(state)
        logger.info(
            "finalize_state_pruned",
            session_id=state["session_id"],
            size_before=size_before,
            size_after=size_after,
            reduction_bytes=size_before - size_after,
        )

    # Store memories for cross-run learning (non-blocking)
    try:
        from services.memory_pipeline import store_successful_run

        # Get user_id from state if available
        user_id = state.get("user_id")

        if user_id and quality_score and quality_score >= 0.8:
            # Run memory storage asynchronously (don't wait for it)
            asyncio.create_task(
                store_successful_run(
                    session_id=state["session_id"],
                    user_id=user_id,
                    state=state,
                )
            )
            logger.info(
                "memory_storage_initiated",
                session_id=state["session_id"],
            )
    except ImportError:
        # Memory services not available
        pass
    except Exception as e:
        # Non-blocking - log and continue
        logger.warning(
            "memory_storage_failed",
            session_id=state["session_id"],
            error=str(e),
        )

    return state


# ═══════════════════════════════════════════════════════════════════════════════
# CONDITIONAL EDGES
# ═══════════════════════════════════════════════════════════════════════════════


def should_revise_condition(state: DiscoveryState) -> Literal["revise", "finalize"]:
    """
    Determine whether to revise or finalize based on quality assessment.

    Args:
        state: Current workflow state.

    Returns:
        str: "revise" to start another iteration, "finalize" to complete.
    """
    # Safely get quality score, handling None case
    quality_assessment = state.get("quality_assessment")
    quality_score = quality_assessment.get("overall_score") if quality_assessment else None

    if should_revise(state):
        logger.info(
            "revision_decision",
            session_id=state["session_id"],
            decision="revise",
            iteration=state.get("iteration", 1),
            quality_score=quality_score,
        )
        return "revise"
    else:
        logger.info(
            "revision_decision",
            session_id=state["session_id"],
            decision="finalize",
            iteration=state.get("iteration", 1),
            quality_score=quality_score,
        )
        return "finalize"


def route_revision(
    state: DiscoveryState,
) -> Literal[
    "customer_research",
    "business_strategy",
    "product_requirements",
    "technical_architect",
    "legal_regulatory",
]:
    """
    Route to the first failing agent instead of always customer_research.

    Analyzes section_scores from quality_assessment to find the first section
    that scored below the threshold (0.7), then routes to that agent.

    Args:
        state: Current workflow state with quality_assessment.

    Returns:
        str: The agent node name to route to for revision.
    """
    quality_assessment = state.get("quality_assessment") or {}
    section_scores = quality_assessment.get("section_scores", []) or []

    # Map section names (from critique) to agent node names
    section_to_agent = {
        "customer research": "customer_research",
        "business case": "business_strategy",
        "product requirements": "product_requirements",
        "technical architecture": "technical_architect",
        "legal": "legal_regulatory",
        "cross-section consistency": "customer_research",  # Full re-run for consistency issues
    }

    # Find first section below threshold (0.7)
    threshold = settings.min_quality_score
    for section in section_scores:
        score = section.get("score", 1.0)
        section_name = section.get("section", "").lower()

        if score < threshold:
            # Find matching agent
            for key, agent in section_to_agent.items():
                if key in section_name:
                    logger.info(
                        "targeted_revision_routing",
                        session_id=state["session_id"],
                        failing_section=section_name,
                        score=score,
                        routed_to=agent,
                    )
                    return agent

    # Fallback to full re-run if no specific failing section found
    logger.info(
        "targeted_revision_routing",
        session_id=state["session_id"],
        decision="fallback_to_customer_research",
        reason="no_specific_failing_section",
    )
    return "customer_research"


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_discovery_graph() -> StateGraph:
    """
    Build the LangGraph workflow for product discovery.

    The workflow follows this pattern:
    1. Planner → [Parallel: Customer Research + Legal Preliminary] → Convergence
    2. Convergence → Business Strategy → Product Requirements → Technical Architect → Legal & Regulatory Review
    3. Critique evaluates all outputs
    4. If quality < threshold and iterations < max: loop back to failing agent (targeted revision)
    5. Otherwise: generate executive summary and finalize

    Parallel execution improves speed by running customer research and
    preliminary legal scan concurrently after planning.

    Returns:
        StateGraph: Compiled workflow graph.
    """
    # Create the graph with our state type
    workflow = StateGraph(DiscoveryState)

    # Add all nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("customer_research", customer_research_node)
    workflow.add_node("legal_preliminary", legal_preliminary_node)
    workflow.add_node("convergence", convergence_node)
    workflow.add_node("business_strategy", business_strategy_node)
    workflow.add_node("product_requirements", product_requirements_node)
    workflow.add_node("technical_architect", technical_architect_node)
    workflow.add_node("legal_regulatory", legal_regulatory_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("prepare_revision", prepare_revision_node)
    workflow.add_node("executive_summary", executive_summary_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point - planner runs first
    workflow.set_entry_point("planner")

    # Planner fans out to parallel tracks
    workflow.add_conditional_edges(
        "planner",
        parallel_dispatch,
        ["customer_research", "legal_preliminary"],
    )

    # Parallel tracks converge
    workflow.add_edge("customer_research", "convergence")
    workflow.add_edge("legal_preliminary", "convergence")

    # Convergence leads to business strategy
    workflow.add_edge("convergence", "business_strategy")

    # Add sequential edges for main flow
    workflow.add_edge("business_strategy", "product_requirements")
    workflow.add_edge("product_requirements", "technical_architect")
    workflow.add_edge("technical_architect", "legal_regulatory")
    workflow.add_edge("legal_regulatory", "critique")

    # Add conditional edge after critique
    workflow.add_conditional_edges(
        "critique",
        should_revise_condition,
        {
            "revise": "prepare_revision",
            "finalize": "executive_summary",
        },
    )

    # Revision routes to the first failing agent (targeted revision)
    workflow.add_conditional_edges(
        "prepare_revision",
        route_revision,
        {
            "customer_research": "customer_research",
            "business_strategy": "business_strategy",
            "product_requirements": "product_requirements",
            "technical_architect": "technical_architect",
            "legal_regulatory": "legal_regulatory",
        },
    )

    # Executive summary leads to finalize
    workflow.add_edge("executive_summary", "finalize")

    # Finalize is the end
    workflow.add_edge("finalize", END)

    return workflow


def create_discovery_workflow():
    """
    Create a compiled workflow with memory checkpointing.

    Returns:
        Compiled LangGraph workflow ready for execution.
    """
    # Build the graph
    graph = build_discovery_graph()

    # Create memory checkpointer for state persistence
    checkpointer = MemorySaver()

    # Compile with checkpointing
    return graph.compile(checkpointer=checkpointer)


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════


async def run_discovery_workflow(
    session_id: str,
    product_idea: str,
    industry: str | None = None,
    target_market: str | None = None,
    constraints: list[str] | None = None,
    additional_context: str | None = None,
    event_emitter: Optional["SessionEventEmitter"] = None,
    use_v3_facilitator: bool = True,
) -> DiscoveryState:
    """
    Execute the complete product discovery workflow.

    This is the main entry point for running a discovery session.
    It initializes state, configures the LLM, and runs the workflow.

    Args:
        session_id: Unique session identifier.
        product_idea: The product idea to analyze.
        industry: Optional industry context.
        target_market: Optional target market specification.
        constraints: Optional business/technical constraints.
        additional_context: Any additional context.
        event_emitter: Optional SSE event emitter for real-time streaming.
        use_v3_facilitator: If True, use the v3.0 7-phase facilitator pipeline.

    Returns:
        DiscoveryState: Final state with complete inception pack.

    Raises:
        Exception: If workflow execution fails.
    """
    global _current_emitter
    _current_emitter = event_emitter

    logger.info(
        "workflow_start",
        session_id=session_id,
        product_idea=product_idea[:100],
        industry=industry,
        target_market=target_market,
        has_emitter=event_emitter is not None,
        use_v3_facilitator=use_v3_facilitator,
    )

    # Configure Gemini API
    configure_gemini()

    # Create initial state
    initial_state = create_initial_state(
        session_id=session_id,
        product_idea=product_idea,
        industry=industry,
        target_market=target_market,
        constraints=constraints,
        additional_context=additional_context,
    )

    try:
        if use_v3_facilitator:
            # Use v3.0 7-phase facilitator pipeline
            from agents.facilitator import run_facilitator

            logger.info(
                "using_v3_facilitator",
                session_id=session_id,
            )

            final_state = await run_facilitator(initial_state)
        else:
            # Use legacy LangGraph workflow
            workflow = create_discovery_workflow()
            config = {
                "configurable": {
                    "thread_id": session_id,
                }
            }
            final_state = await workflow.ainvoke(initial_state, config)

        logger.info(
            "workflow_success",
            session_id=session_id,
            status=final_state.get("status"),
            iterations=final_state.get("iteration", 1),
        )

        return final_state

    except Exception as e:
        logger.error(
            "workflow_error",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )

        # Emit error if emitter available
        if event_emitter:
            await event_emitter.emit_error(str(e))

        # Return state with error
        initial_state["status"] = SessionStatus.FAILED
        initial_state["errors"] = initial_state.get("errors", []) + [str(e)]
        initial_state["updated_at"] = datetime.utcnow().isoformat()

        return initial_state

    finally:
        # Clear the global emitter reference
        _current_emitter = None


async def get_workflow_state(session_id: str) -> DiscoveryState | None:
    """
    Get the current state of a workflow by session ID.

    Args:
        session_id: The session ID to look up.

    Returns:
        DiscoveryState | None: Current state or None if not found.
    """
    workflow = create_discovery_workflow()
    config = {"configurable": {"thread_id": session_id}}

    try:
        state = await workflow.aget_state(config)
        return state.values if state else None
    except Exception as e:
        logger.error(
            "get_state_error",
            session_id=session_id,
            error=str(e),
        )
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _create_fallback_summary(state: DiscoveryState) -> dict:
    """
    Create a fallback executive summary when LLM synthesis fails.

    Extracts available data from other agent outputs to provide
    a meaningful summary even when synthesis fails.

    Args:
        state: Current workflow state.

    Returns:
        dict: Executive summary with available data.
    """
    product_idea = state.get("product_idea", "Unknown Product")

    # Extract from customer research
    customer_research = state.get("customer_research") or {}
    job_to_be_done = customer_research.get("job_to_be_done") or {}
    market_context = customer_research.get("market_context") or {}
    competitive_landscape = customer_research.get("competitive_landscape") or {}
    pain_signals = customer_research.get("pain_signals") or []

    # Extract from business case
    business_case = state.get("business_case") or {}
    lean_canvas = business_case.get("lean_canvas") or {}
    revenue_streams = business_case.get("revenue_streams") or []
    risks = business_case.get("risks_and_mitigations") or []

    # Extract from legal review
    legal_review = state.get("legal_regulatory_review") or {}
    risk_assessment = legal_review.get("overall_risk_assessment") or {}
    regulations = legal_review.get("applicable_regulations") or []

    # Build target users from research
    research_scope = customer_research.get("research_scope") or {}
    segments = research_scope.get("segments_examined") or []
    target_users = segments if segments else [job_to_be_done.get("underlying_goal", "Target market segment")]

    # Build competitors list
    competitors = competitive_landscape.get("competitors") or []
    competitor_names = [c.get("name", "Competitor") for c in competitors[:3]]
    competitive_summary = f"Competing against {', '.join(competitor_names)}" if competitor_names else "Competitive analysis pending"

    # Build financial summary
    funding = business_case.get("funding_requirement") or "Funding requirements to be determined"
    roi = business_case.get("roi_analysis") or "ROI analysis pending"
    break_even = business_case.get("break_even_analysis") or "Break-even analysis pending"

    # Build risk summary
    top_risks = [f"Risk: {r.get('risk', 'Unknown')} | Mitigation: {r.get('mitigation', 'TBD')}" for r in risks[:3]]
    if not top_risks:
        top_risks = ["Risk assessment pending"]

    # Build regulatory summary
    reg_names = [r.get("name", "Unknown") for r in regulations[:3]]
    regulatory_summary = f"Key regulations: {', '.join(reg_names)}" if reg_names else "Regulatory review pending"

    return {
        "product_name": product_idea.split()[0] if product_idea else "Product",
        "tagline": f"Innovative solution for {product_idea[:100]}",
        "problem_statement": lean_canvas.get("problem", ["Problem to be defined"])[0] if lean_canvas.get("problem") else "Problem to be defined",
        "solution_overview": lean_canvas.get("solution", ["Solution to be defined"])[0] if lean_canvas.get("solution") else "Solution to be defined",
        "value_proposition": lean_canvas.get("unique_value_proposition") or "Value proposition to be defined",
        "target_users": target_users if target_users else ["Target users to be identified"],
        "target_market_size": f"TAM: {market_context.get('total_addressable_market', 'TBD')}, SAM: {market_context.get('serviceable_addressable_market', 'TBD')}, SOM: {market_context.get('serviceable_obtainable_market', 'TBD')}",
        "key_differentiators": lean_canvas.get("unfair_advantage", "To be determined").split(", ") if isinstance(lean_canvas.get("unfair_advantage"), str) else ["Differentiation to be defined"],
        "competitive_landscape": competitive_summary,
        "funding_required": funding,
        "revenue_model": revenue_streams[0].get("pricing_model", "Revenue model TBD") if revenue_streams else "Revenue model TBD",
        "financial_projections": f"Year 1: {business_case.get('year_1_projection', 'TBD')} | Year 3: {business_case.get('year_3_projection', 'TBD')}",
        "break_even_timeline": break_even,
        "expected_roi": roi,
        "top_risks": top_risks,
        "regulatory_summary": regulatory_summary,
        "gtm_strategy": business_case.get("go_to_market_strategy") or "GTM strategy to be defined",
        "key_milestones": ["Q1: MVP development", "Q2: Beta launch", "Q3-Q4: Market expansion"],
        "success_metrics": lean_canvas.get("key_metrics", ["Metrics to be defined"]) if lean_canvas.get("key_metrics") else ["Metrics to be defined"],
        "recommendation": f"PROCEED WITH CONDITIONS - Complete analysis required. Risk level: {risk_assessment.get('risk_level', 'Unknown')}",
    }
