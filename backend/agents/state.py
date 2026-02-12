"""
LangGraph state definition for the Product Discovery workflow.

This module defines the shared state that flows through all agents
in the discovery pipeline. Each agent reads from and writes to
specific fields in this state.

The state follows LangGraph's TypedDict pattern for type safety
and checkpoint serialization support.

For parallel execution support, we use Annotated types with reducers
to handle state merging when parallel branches converge.
"""

from datetime import datetime
from operator import add
from typing import Annotated, Any, Optional, TypedDict

from models.schemas import (
    ExecutiveSummary,
    CustomerResearch,
    BusinessCase,
    ProductRequirementsDocument,
    TechnicalArchitecture,
    LegalRegulatoryReview,
    QualityAssessment,
    SessionStatus,
)


# ═══════════════════════════════════════════════════════════════════════════════
# REDUCERS FOR PARALLEL STATE MERGING
# ═══════════════════════════════════════════════════════════════════════════════


def keep_last(current: Any, new: Any) -> Any:
    """Keep the last non-None value (for immutable fields like session_id)."""
    return new if new is not None else current


def keep_first_non_none(current: Any, new: Any) -> Any:
    """Keep the first non-None value."""
    return current if current is not None else new


def merge_errors(current: list[str], new: list[str]) -> list[str]:
    """Merge error lists from parallel branches."""
    if current is None:
        current = []
    if new is None:
        new = []
    # Use set to avoid duplicates, then convert back to list
    return list(set(current + new))


def merge_cross_references(
    current: dict[str, Any] | None,
    new: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Merge cross-reference indices from parallel agents.

    This reducer combines claims from parallel branches, avoiding duplicates
    and recalculating aggregate statistics.
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
    merged_claims = current_claims.copy()

    for claim in new_claims:
        if claim.get("claim_id") not in existing_ids:
            merged_claims.append(claim)
            existing_ids.add(claim.get("claim_id"))

    # Recalculate statistics
    tier_distribution: dict[str, int] = {}
    for claim in merged_claims:
        tier = claim.get("evidence_tier", "E4")
        if isinstance(tier, str):
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1

    # Calculate evidence score
    weights = {"E1": 1.0, "E2": 0.85, "E3": 0.6, "E4": 0.3, "E5": 0.1}
    if merged_claims:
        total_weight = sum(
            weights.get(c.get("evidence_tier", "E4"), 0.3)
            for c in merged_claims
        )
        evidence_score = total_weight / len(merged_claims)
    else:
        evidence_score = 0.0

    # Find unresolved dependencies
    all_claim_ids = {c.get("claim_id") for c in merged_claims if c.get("claim_id")}
    unresolved = []
    for claim in merged_claims:
        for dep_id in claim.get("depends_on", []):
            if dep_id not in all_claim_ids and dep_id not in unresolved:
                unresolved.append(dep_id)

    return {
        "claims": merged_claims,
        "total_claims": len(merged_claims),
        "tier_distribution": tier_distribution,
        "evidence_score": round(evidence_score, 3),
        "unresolved_dependencies": unresolved,
    }


class AgentOutput(TypedDict, total=False):
    """
    Output structure from an individual agent.

    Attributes:
        success: Whether the agent completed successfully.
        data: The structured data output from the agent.
        raw_response: Raw LLM response for debugging.
        error: Error message if the agent failed.
        tokens_used: Token count for this agent call.
        duration_seconds: Time taken by this agent.
    """

    success: bool
    data: dict[str, Any]
    raw_response: str
    error: str
    tokens_used: int
    duration_seconds: float


class CritiqueFeedback(TypedDict, total=False):
    """
    Feedback from the critique agent for refinement.

    Attributes:
        customer_research_feedback: Feedback for customer research agent.
        business_strategy_feedback: Feedback for business strategy agent.
        product_requirements_feedback: Feedback for PRD agent.
        technical_architecture_feedback: Feedback for technical architect agent.
        legal_regulatory_feedback: Feedback for legal & regulatory review agent.
        priority_improvements: Ordered list of most important improvements.
    """

    customer_research_feedback: list[str]
    business_strategy_feedback: list[str]
    product_requirements_feedback: list[str]
    technical_architecture_feedback: list[str]
    legal_regulatory_feedback: list[str]
    priority_improvements: list[str]


class DiscoveryState(TypedDict, total=False):
    """
    Shared state for the product discovery workflow.

    This TypedDict defines all fields that flow through the LangGraph
    workflow. Each agent reads the inputs it needs and writes its outputs.

    For parallel execution, fields use Annotated types with reducers:
    - keep_last: For fields that should use the latest value
    - keep_first_non_none: For fields set once and shouldn't change
    - merge_errors: For error lists that should be combined

    Input Fields (set at start):
        session_id: Unique identifier for this discovery session.
        product_idea: The product idea to analyze.
        industry: Optional industry context.
        target_market: Optional target market specification.
        constraints: Optional business/technical constraints.
        additional_context: Any additional context provided.

    Processing Fields (updated during workflow):
        status: Current session status.
        current_agent: Name of the currently executing agent.
        iteration: Current revision iteration (1-based).
        started_at: Workflow start timestamp.
        updated_at: Last update timestamp.

    Agent Outputs (populated by respective agents):
        executive_summary: Output from synthesis (built from other outputs).
        customer_research: Output from Customer Research Agent.
        business_case: Output from Business Strategy Agent.
        product_requirements: Output from Product Requirements Agent.
        technical_architecture: Output from Technical Architect Agent.
        legal_regulatory_review: Output from Legal & Regulatory Review Agent.
        quality_assessment: Output from Critique Agent.

    Feedback Fields (for revision loops):
        critique_feedback: Detailed feedback for each agent.
        quality_passed: Whether quality threshold was met.
        requires_revision: Whether another iteration is needed.

    Tracking Fields:
        agent_outputs: Raw outputs from each agent for debugging.
        errors: Any errors encountered during processing.
        total_tokens_used: Total token count across all agents.
        total_duration_seconds: Total processing time.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # INPUT FIELDS (immutable - use keep_last reducer for parallel safety)
    # ═══════════════════════════════════════════════════════════════════════════

    session_id: Annotated[str, keep_last]
    product_idea: Annotated[str, keep_last]
    industry: Annotated[Optional[str], keep_last]
    target_market: Annotated[Optional[str], keep_last]
    constraints: Annotated[Optional[list[str]], keep_last]
    additional_context: Annotated[Optional[str], keep_last]

    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESSING FIELDS (use keep_last for parallel merging)
    # ═══════════════════════════════════════════════════════════════════════════

    status: Annotated[SessionStatus, keep_last]
    current_agent: Annotated[str, keep_last]
    iteration: Annotated[int, keep_last]
    started_at: Annotated[str, keep_last]  # ISO format datetime string
    updated_at: Annotated[str, keep_last]  # ISO format datetime string

    # ═══════════════════════════════════════════════════════════════════════════
    # PLANNING AGENT OUTPUT
    # ═══════════════════════════════════════════════════════════════════════════

    research_plan: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════════════════════
    # PARALLEL EXECUTION OUTPUTS (from parallel tracks after planner)
    # ═══════════════════════════════════════════════════════════════════════════

    preliminary_legal_scan: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT OUTPUTS (Validated Pydantic Models serialized to dict)
    # ═══════════════════════════════════════════════════════════════════════════

    executive_summary: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    customer_research: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    business_case: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    product_requirements: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    technical_architecture: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    legal_regulatory_review: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    quality_assessment: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════════════════════
    # SWARM AGENT OUTPUTS (from parallel swarm execution)
    # ═══════════════════════════════════════════════════════════════════════════

    # Discovery Swarm outputs
    competitive_analysis: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    detailed_personas: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # Strategy Swarm outputs
    gtm_plan: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    financial_model: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # Delivery Swarm outputs
    risk_assessment: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # Facilitator context
    contradiction_context: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════════════════════
    # QUALITY IMPROVEMENT SYSTEM FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    # Active constraints for the current phase (from constraint_broadcaster)
    active_constraints: Annotated[Optional[list[dict[str, Any]]], keep_last]
    # Formatted constraints prompt for injection into agent prompts
    constraints_prompt: Annotated[Optional[str], keep_last]
    # Revision history for tracking what was tried before
    revision_history: Annotated[list[dict[str, Any]], add]  # Append reducer

    # ═══════════════════════════════════════════════════════════════════════════
    # V3.0 CROSS-REFERENCE AND SYNTHESIS OUTPUTS
    # ═══════════════════════════════════════════════════════════════════════════

    # Cross-reference index for claim tracking
    cross_reference_index: Annotated[Optional[dict[str, Any]], merge_cross_references]

    # Design agents output
    wireframes: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    prototype: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # Synthesis agents output
    stakeholder_views: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    validation_playbook: Annotated[Optional[dict[str, Any]], keep_first_non_none]

    # ═══════════════════════════════════════════════════════════════════════════
    # PRD SUB-WORKFLOW FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    prd_iteration: Annotated[int, keep_last]
    prd_draft: Annotated[Optional[dict[str, Any]], keep_first_non_none]
    prd_critic_feedback: Annotated[Optional[list[str]], keep_first_non_none]
    prd_critic_score: Annotated[Optional[float], keep_first_non_none]
    prd_quality_passed: Annotated[bool, keep_last]

    # ═══════════════════════════════════════════════════════════════════════════
    # FEEDBACK FIELDS (for revision loops)
    # ═══════════════════════════════════════════════════════════════════════════

    critique_feedback: Annotated[Optional[CritiqueFeedback], keep_first_non_none]
    quality_passed: Annotated[bool, keep_last]
    requires_revision: Annotated[bool, keep_last]

    # ═══════════════════════════════════════════════════════════════════════════
    # TRACKING FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    agent_outputs: Annotated[dict[str, AgentOutput], keep_last]
    errors: Annotated[list[str], merge_errors]
    total_tokens_used: Annotated[int, keep_last]
    total_duration_seconds: Annotated[float, keep_last]

    # Critique retry tracking
    critique_attempt: Annotated[int, keep_last]


def create_initial_state(
    session_id: str,
    product_idea: str,
    industry: Optional[str] = None,
    target_market: Optional[str] = None,
    constraints: Optional[list[str]] = None,
    additional_context: Optional[str] = None,
) -> DiscoveryState:
    """
    Create the initial state for a new discovery session.

    Args:
        session_id: Unique session identifier.
        product_idea: The product idea to analyze.
        industry: Optional industry context.
        target_market: Optional target market specification.
        constraints: Optional business/technical constraints.
        additional_context: Any additional context.

    Returns:
        DiscoveryState: Initialized state ready for the workflow.
    """
    now = datetime.utcnow().isoformat()

    return DiscoveryState(
        # Input fields
        session_id=session_id,
        product_idea=product_idea,
        industry=industry,
        target_market=target_market,
        constraints=constraints,
        additional_context=additional_context,
        # Processing fields
        status=SessionStatus.PENDING,
        current_agent="",
        iteration=1,
        started_at=now,
        updated_at=now,
        # Planning agent output
        research_plan=None,
        # Parallel execution outputs
        preliminary_legal_scan=None,
        # Agent outputs (initially None)
        executive_summary=None,
        customer_research=None,
        business_case=None,
        product_requirements=None,
        technical_architecture=None,
        legal_regulatory_review=None,
        quality_assessment=None,
        # Swarm agent outputs
        competitive_analysis=None,
        detailed_personas=None,
        gtm_plan=None,
        financial_model=None,
        risk_assessment=None,
        contradiction_context=None,
        # V3.0 cross-reference and synthesis
        cross_reference_index=None,
        wireframes=None,
        prototype=None,
        stakeholder_views=None,
        validation_playbook=None,
        # Quality improvement system fields
        active_constraints=None,
        constraints_prompt=None,
        revision_history=[],
        # PRD sub-workflow fields
        prd_iteration=0,
        prd_draft=None,
        prd_critic_feedback=None,
        prd_critic_score=None,
        prd_quality_passed=False,
        # Feedback fields
        critique_feedback=None,
        quality_passed=False,
        requires_revision=False,
        # Tracking fields
        agent_outputs={},
        errors=[],
        total_tokens_used=0,
        total_duration_seconds=0.0,
        # Critique retry tracking
        critique_attempt=1,
    )


def get_progress_percentage(state: DiscoveryState) -> int:
    """
    Calculate the progress percentage based on completed agents.

    Args:
        state: Current discovery state.

    Returns:
        int: Progress percentage (0-100).
    """
    agent_weights = {
        "customer_research": 15,
        "business_case": 15,
        "product_requirements": 20,  # PRD is weighted higher
        "technical_architecture": 15,
        "legal_regulatory_review": 20,  # Legal review is critical
        "quality_assessment": 15,
    }

    completed = 0
    for agent, weight in agent_weights.items():
        if state.get(agent) is not None:
            completed += weight

    return min(completed, 100)


def get_current_agent_name(state: DiscoveryState) -> str:
    """
    Determine which agent should run next based on state.

    Args:
        state: Current discovery state.

    Returns:
        str: Name of the next agent to run.
    """
    if state.get("customer_research") is None:
        return "Customer Research Agent"
    elif state.get("business_case") is None:
        return "Business Strategy Agent"
    elif state.get("product_requirements") is None:
        return "Product Requirements Agent"
    elif state.get("technical_architecture") is None:
        return "Technical Architect Agent"
    elif state.get("legal_regulatory_review") is None:
        return "Legal & Regulatory Review Agent"
    elif state.get("quality_assessment") is None:
        return "Critique Agent"
    else:
        return "Complete"
