"""
LangGraph state definition for the Product Discovery workflow.

This module defines the shared state that flows through all agents
in the discovery pipeline. Each agent reads from and writes to
specific fields in this state.

The state follows LangGraph's TypedDict pattern for type safety
and checkpoint serialization support.
"""

from datetime import datetime
from typing import Any, Optional, TypedDict

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
    # INPUT FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    session_id: str
    product_idea: str
    industry: Optional[str]
    target_market: Optional[str]
    constraints: Optional[list[str]]
    additional_context: Optional[str]

    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESSING FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    status: SessionStatus
    current_agent: str
    iteration: int
    started_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string

    # ═══════════════════════════════════════════════════════════════════════════
    # AGENT OUTPUTS (Validated Pydantic Models serialized to dict)
    # ═══════════════════════════════════════════════════════════════════════════

    executive_summary: Optional[dict[str, Any]]  # ExecutiveSummary
    customer_research: Optional[dict[str, Any]]  # CustomerResearch
    business_case: Optional[dict[str, Any]]  # BusinessCase
    product_requirements: Optional[dict[str, Any]]  # ProductRequirementsDocument
    technical_architecture: Optional[dict[str, Any]]  # TechnicalArchitecture
    legal_regulatory_review: Optional[dict[str, Any]]  # LegalRegulatoryReview
    quality_assessment: Optional[dict[str, Any]]  # QualityAssessment

    # ═══════════════════════════════════════════════════════════════════════════
    # PRD SUB-WORKFLOW FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    prd_iteration: int  # Current iteration within PRD loop (1-3)
    prd_draft: Optional[dict[str, Any]]  # Current PRD draft being refined
    prd_critic_feedback: Optional[list[str]]  # Feedback from PRD critic
    prd_critic_score: Optional[float]  # Latest PRD critic score (0.0-1.0)
    prd_quality_passed: bool  # Whether PRD passed quality threshold

    # ═══════════════════════════════════════════════════════════════════════════
    # FEEDBACK FIELDS (for revision loops)
    # ═══════════════════════════════════════════════════════════════════════════

    critique_feedback: Optional[CritiqueFeedback]
    quality_passed: bool
    requires_revision: bool

    # ═══════════════════════════════════════════════════════════════════════════
    # TRACKING FIELDS
    # ═══════════════════════════════════════════════════════════════════════════

    agent_outputs: dict[str, AgentOutput]  # Keyed by agent name
    errors: list[str]
    total_tokens_used: int
    total_duration_seconds: float


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
        # Agent outputs (initially None)
        executive_summary=None,
        customer_research=None,
        business_case=None,
        product_requirements=None,
        technical_architecture=None,
        legal_regulatory_review=None,
        quality_assessment=None,
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
