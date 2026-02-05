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
"""

import json
from datetime import datetime
from typing import Literal

import structlog
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from agents.base_agent import call_llm, configure_gemini
from agents.critique import run_critique_agent, should_revise
from agents.customer_research import run_customer_research_agent
from agents.business_strategy import run_business_strategy_agent
from agents.prd_subgraph import run_prd_subworkflow
from agents.prompts import EXECUTIVE_SUMMARY_PROMPT, format_prompt
from agents.state import DiscoveryState, create_initial_state, get_progress_percentage
from agents.technical_architect import run_technical_architect_agent
from agents.legal_regulatory import run_legal_regulatory_agent
from config import settings
from models.schemas import ExecutiveSummary, SessionStatus

logger = structlog.get_logger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# NODE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


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
    return await run_customer_research_agent(state)


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
    return await run_business_strategy_agent(state)


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
    return await run_technical_architect_agent(state)


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
    return await run_legal_regulatory_agent(state)


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
    return await run_critique_agent(state)


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

    return state


async def prepare_revision_node(state: DiscoveryState) -> DiscoveryState:
    """
    Prepare state for a revision iteration.

    This node:
    - Increments the iteration counter
    - Clears previous agent outputs (keeping feedback)
    - Logs the revision event

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: State prepared for revision.
    """
    current_iteration = state.get("iteration", 1)
    new_iteration = current_iteration + 1

    logger.info(
        "revision_started",
        session_id=state["session_id"],
        previous_iteration=current_iteration,
        new_iteration=new_iteration,
        quality_score=(state.get("quality_assessment") or {}).get("overall_score"),
    )

    # Increment iteration
    state["iteration"] = new_iteration
    state["updated_at"] = datetime.utcnow().isoformat()

    # Clear previous outputs but keep the feedback
    # Agents will use the feedback to improve their outputs
    state["customer_research"] = None
    state["business_case"] = None
    state["product_requirements"] = None
    state["technical_architecture"] = None
    state["legal_regulatory_review"] = None
    # Keep quality_assessment for reference
    # Keep critique_feedback for agents to use

    return state


async def finalize_node(state: DiscoveryState) -> DiscoveryState:
    """
    Finalize the workflow and mark as completed.

    Args:
        state: Current workflow state.

    Returns:
        DiscoveryState: Finalized state.
    """
    state["status"] = SessionStatus.COMPLETED
    state["current_agent"] = "Complete"
    state["updated_at"] = datetime.utcnow().isoformat()

    logger.info(
        "workflow_completed",
        session_id=state["session_id"],
        iteration=state.get("iteration", 1),
        total_tokens=state.get("total_tokens_used", 0),
        total_duration=round(state.get("total_duration_seconds", 0), 2),
        quality_score=(state.get("quality_assessment") or {}).get("overall_score"),
        quality_passed=state.get("quality_passed", False),
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


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def build_discovery_graph() -> StateGraph:
    """
    Build the LangGraph workflow for product discovery.

    The workflow follows this pattern:
    1. Customer Research → Business Strategy → Product Requirements → Technical Architect → Legal & Regulatory Review
    2. Critique evaluates all outputs
    3. If quality < threshold and iterations < max: loop back to step 1
    4. Otherwise: generate executive summary and finalize

    Returns:
        StateGraph: Compiled workflow graph.
    """
    # Create the graph with our state type
    workflow = StateGraph(DiscoveryState)

    # Add all nodes
    workflow.add_node("customer_research", customer_research_node)
    workflow.add_node("business_strategy", business_strategy_node)
    workflow.add_node("product_requirements", product_requirements_node)
    workflow.add_node("technical_architect", technical_architect_node)
    workflow.add_node("legal_regulatory", legal_regulatory_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("prepare_revision", prepare_revision_node)
    workflow.add_node("executive_summary", executive_summary_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point
    workflow.set_entry_point("customer_research")

    # Add sequential edges for main flow
    workflow.add_edge("customer_research", "business_strategy")
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

    # Revision loops back to customer research
    workflow.add_edge("prepare_revision", "customer_research")

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

    Returns:
        DiscoveryState: Final state with complete inception pack.

    Raises:
        Exception: If workflow execution fails.
    """
    logger.info(
        "workflow_start",
        session_id=session_id,
        product_idea=product_idea[:100],
        industry=industry,
        target_market=target_market,
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

    # Create workflow
    workflow = create_discovery_workflow()

    # Configuration for this run
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    try:
        # Execute workflow
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

        # Return state with error
        initial_state["status"] = SessionStatus.FAILED
        initial_state["errors"] = initial_state.get("errors", []) + [str(e)]
        initial_state["updated_at"] = datetime.utcnow().isoformat()

        return initial_state


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
