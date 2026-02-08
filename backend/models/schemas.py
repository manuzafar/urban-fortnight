"""
Pydantic models for the Product Discovery Multi-Agent System.

This module defines all data models for:
- API requests and responses
- Inception pack sections (Executive Summary, PRD, etc.)
- Nested structures (User Stories, Epics, Requirements, etc.)

All models use Pydantic v2 with strict validation and JSON serialization support.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

# Import visual schemas for use in agent outputs
from models.visual_schemas import (
    CompetitivePositioning,
    FinancialProjection,
    LeanCanvasVisual,
    KeyDecision,
    KeyDecisions,
    RiskMatrix,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class SessionStatus(str, Enum):
    """Status of a discovery session."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(str, Enum):
    """Priority levels for requirements and stories."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class StorySize(str, Enum):
    """T-shirt sizing for user stories."""

    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class RiskLevel(str, Enum):
    """Risk severity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ═══════════════════════════════════════════════════════════════════════════════
# API REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class DiscoveryRequest(BaseModel):
    """
    Request payload to start a product discovery session.

    Attributes:
        product_idea: The product idea or concept to analyze.
        industry: Optional industry context for better analysis.
        target_market: Optional target market specification.
        constraints: Optional business or technical constraints.
        additional_context: Any additional context to guide the analysis.
    """

    product_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The product idea to analyze",
        json_schema_extra={"example": "AI-powered meeting room booking system for enterprise offices"},
    )

    industry: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Industry context (e.g., Healthcare, FinTech, SaaS)",
    )

    target_market: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Target market or customer segment",
    )

    constraints: Optional[list[str]] = Field(
        default=None,
        max_length=10,
        description="Business or technical constraints",
    )

    additional_context: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional context or requirements",
    )


class DiscoveryResponse(BaseModel):
    """
    Response after initiating a discovery session.

    Attributes:
        session_id: Unique identifier for the session.
        status: Current status of the session.
        message: Human-readable status message.
        created_at: Timestamp when session was created.
    """

    session_id: str = Field(..., description="Unique session identifier")
    status: SessionStatus = Field(..., description="Current session status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionStatusResponse(BaseModel):
    """
    Response for session status queries.

    Attributes:
        session_id: Unique identifier for the session.
        status: Current status of the session.
        current_agent: Which agent is currently processing (if in progress).
        iteration: Current revision iteration number.
        progress_percentage: Estimated progress (0-100).
        inception_pack: The completed inception pack (if completed).
        error_message: Error details (if failed).
        created_at: Session creation timestamp.
        updated_at: Last update timestamp.
    """

    session_id: str = Field(..., description="Unique session identifier")
    status: SessionStatus = Field(..., description="Current session status")
    current_agent: Optional[str] = Field(default=None, description="Currently active agent")
    iteration: int = Field(default=1, ge=1, le=5, description="Current iteration")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    inception_pack: Optional[dict[str, Any]] = Field(default=None, description="Completed inception pack")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════


class ExecutiveSummary(BaseModel):
    """
    Comprehensive executive summary with data points senior executives need.

    This summary synthesizes all agent outputs into a decision-ready brief
    that covers market opportunity, financials, risks, and strategic positioning.
    """

    # Product Identity
    product_name: str = Field(..., description="Proposed product name")
    tagline: str = Field(..., max_length=150, description="One-line product description")

    # Problem & Solution
    problem_statement: str = Field(..., description="The problem being solved")
    solution_overview: str = Field(..., description="High-level solution description")
    value_proposition: str = Field(..., description="Core value proposition")

    # Target Market
    target_users: list[str] = Field(..., min_length=1, description="Specific target user segments with descriptions")
    target_market_size: str = Field(..., description="TAM/SAM/SOM summary with numbers")

    # Competitive Position
    key_differentiators: list[str] = Field(..., min_length=1, description="Unique differentiators vs competition")
    competitive_landscape: str = Field(..., description="Key competitors and our positioning")

    # Financial Summary
    funding_required: str = Field(..., description="Initial investment required")
    revenue_model: str = Field(..., description="How the product will make money")
    financial_projections: str = Field(..., description="Year 1 and Year 3 revenue/profit projections")
    break_even_timeline: str = Field(..., description="Expected break-even point")
    expected_roi: str = Field(..., description="3-year ROI projection")

    # Risk & Compliance
    top_risks: list[str] = Field(..., min_length=1, max_length=5, description="Top 3-5 risks with brief mitigations")
    regulatory_summary: str = Field(..., description="Key compliance requirements and timeline")

    # Go-to-Market
    gtm_strategy: str = Field(..., description="Go-to-market approach summary")
    key_milestones: list[str] = Field(..., min_length=1, description="Critical milestones for first 12 months")

    # Success Metrics
    success_metrics: list[str] = Field(..., min_length=1, description="Key KPIs to track")

    # Recommendation
    recommendation: str = Field(..., description="Clear recommendation: proceed, pivot, or stop - with rationale")

    # Key Decisions (extracted for executive action)
    key_decisions: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="3-5 critical decisions requiring executive attention",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOMER RESEARCH (Evidence-Based Reality Investigation)
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceTier(str, Enum):
    """Evidence quality tiers for research insights."""

    E1 = "E1"  # Direct evidence (quotes, transcripts, logs)
    E2 = "E2"  # Observed behaviour (drop-offs, workarounds, patterns)
    E3 = "E3"  # Market/industry data (benchmarks, reports)
    E4 = "E4"  # Hypothesis/assumption (unproven)


class ResearchScope(BaseModel):
    """Research scope and limitations - be honest about gaps."""

    segments_examined: list[str] = Field(..., description="Customer segments examined")
    observation_context: str = Field(..., description="How this research was conducted")
    known_gaps: list[str] = Field(..., description="Known blind spots or limitations")
    confidence_level: str = Field(..., description="Overall confidence: high/medium/low")


class JobToBeDone(BaseModel):
    """Contextual job-to-be-done - avoid feature language."""

    trigger_situation: str = Field(..., description="What situation triggers the need")
    underlying_goal: str = Field(..., description="What customer is really trying to achieve")
    success_definition: str = Field(..., description="What success looks like to the customer")


class CurrentBehaviour(BaseModel):
    """What customers actually do today - not what they say they want."""

    existing_solutions: list[str] = Field(..., description="How they solve it today")
    tools_and_workarounds: list[str] = Field(..., description="Specific tools/workarounds used")
    friction_points: list[str] = Field(..., description="Where friction/delay/anxiety occurs")
    why_problem_persists: str = Field(..., description="Why this hasn't been solved")


class PainSignal(BaseModel):
    """Evidence-tagged pain signal with severity."""

    description: str = Field(..., description="Detailed pain description")
    evidence_tier: str = Field(..., description="Evidence tier: E1/E2/E3/E4")
    evidence_detail: str = Field(..., description="Specific evidence supporting this")
    impact: str = Field(..., description="Why this matters (time/money/risk/emotion)")
    severity: Priority = Field(..., description="Severity: critical/high/medium/low")
    challenges_solution: bool = Field(default=False, description="Does this contradict the proposed solution?")


class UncomfortableInsight(BaseModel):
    """Insights that challenge assumptions - required for honest research."""

    insight: str = Field(..., description="The uncomfortable truth")
    evidence_tier: str = Field(..., description="Evidence tier: E1/E2/E3/E4")
    implication: str = Field(..., description="What this means for the product idea")


class CustomerIndifference(BaseModel):
    """What customers don't actually care about - critical for scope."""

    assumed_need: str = Field(..., description="What we thought they wanted")
    reality: str = Field(..., description="What they actually think/do")
    evidence_tier: str = Field(..., description="Evidence tier: E1/E2/E3/E4")


class OpenQuestion(BaseModel):
    """Unresolved questions requiring validation."""

    question: str = Field(..., description="What we don't know")
    why_it_matters: str = Field(..., description="Impact on product decisions")
    validation_needed: str = Field(..., description="How to validate this")


class CompetitorReality(BaseModel):
    """Reality-check competitor analysis."""

    name: str = Field(..., description="Competitor name")
    how_they_solve_it: str = Field(..., description="Their approach to the problem")
    why_they_havent_won: str = Field(..., description="Their limitations")
    switching_barriers: str = Field(..., description="What makes switching hard")


class CompetitorProfile(BaseModel):
    """Enhanced competitor profile with evidence."""

    name: str = Field(..., description="Exact company name")
    website: Optional[str] = Field(default=None, description="Company URL")
    one_liner: Optional[str] = Field(default=None, description="What they do in one sentence")
    founded: Optional[str] = Field(default=None, description="Year founded")
    funding: Optional[str] = Field(default=None, description="Funding amount and round")
    funding_evidence_tier: str = Field(default="E4", description="Evidence tier for funding")
    target_customer: Optional[str] = Field(default=None, description="Who they sell to")
    pricing: Optional[dict[str, Any]] = Field(default=None, description="Pricing tiers with evidence")
    key_features: list[str] = Field(default_factory=list, description="Key features")
    strengths: list[str] = Field(default_factory=list, description="Specific strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Specific weaknesses")
    threat_level: str = Field(default="moderate", description="existential|significant|moderate|low")
    threat_rationale: Optional[str] = Field(default=None, description="Why this threat level")


class PositioningMapPosition(BaseModel):
    """A position on the competitive positioning map."""

    name: str = Field(..., description="Competitor or Our Product")
    x_score: float = Field(..., ge=0, le=10, description="Position on X axis")
    y_score: float = Field(..., ge=0, le=10, description="Position on Y axis")
    is_target_product: bool = Field(default=False, description="True if this is our product")
    rationale: Optional[str] = Field(default=None, description="Why this position")


class PositioningMap(BaseModel):
    """Competitive positioning map."""

    x_axis: str = Field(..., description="X axis label (meaningful to this market)")
    y_axis: str = Field(..., description="Y axis label (meaningful to this market)")
    positions: list[PositioningMapPosition] = Field(default_factory=list, description="Competitor positions")
    white_space: Optional[str] = Field(default=None, description="Where no one is positioned")


class MoatAnalysis(BaseModel):
    """Analysis of competitive moat."""

    defensible: list[str] = Field(default_factory=list, description="Advantages hard to replicate")
    not_defensible: list[str] = Field(default_factory=list, description="Advantages that could be copied")
    moat_building_strategy: Optional[str] = Field(default=None, description="How moat deepens over time")


class CompetitiveLandscape(BaseModel):
    """Competitive landscape reality check."""

    competitors: list[CompetitorReality] = Field(default_factory=list, description="Legacy competitor analysis")
    market_position: str = Field(default="", description="Overall competitive assessment")
    # Enhanced fields from Prompt Library
    direct_competitors: list[CompetitorProfile] = Field(default_factory=list, description="Direct competitors with evidence")
    indirect_competitors: list[dict[str, Any]] = Field(default_factory=list, description="Indirect competitors")
    potential_entrants: list[dict[str, Any]] = Field(default_factory=list, description="Potential future entrants")
    positioning_map: Optional[PositioningMap] = Field(default=None, description="Competitive positioning map")
    competitive_gaps: list[dict[str, Any]] = Field(default_factory=list, description="Underserved gaps")
    differentiation_thesis: Optional[str] = Field(default=None, description="Why we win - must be 10x better")
    moat_analysis: Optional[MoatAnalysis] = Field(default=None, description="Moat analysis")
    competitive_risks: list[dict[str, Any]] = Field(default_factory=list, description="Competitive risks")


class MarketTrend(BaseModel):
    """Evidence-tagged market trend."""

    trend: str = Field(..., description="Trend description")
    helps_or_hurts: str = Field(..., description="helps/hurts/neutral")
    evidence_tier: str = Field(..., description="Evidence tier: E1/E2/E3/E4")


class MarketContext(BaseModel):
    """Market sizing with uncertainty acknowledgment."""

    total_addressable_market: str = Field(..., description="TAM with methodology")
    serviceable_addressable_market: str = Field(..., description="SAM with methodology")
    serviceable_obtainable_market: str = Field(..., description="SOM with methodology")
    uncertainty_factors: list[str] = Field(..., description="What could make these wrong")
    market_trends: list[MarketTrend] = Field(default_factory=list, description="Market trends")


class ResearchQualityCheck(BaseModel):
    """Self-critique of research quality."""

    could_kill_idea: bool = Field(..., description="Could this research kill the idea?")
    skeptic_would_trust: bool = Field(..., description="Would a skeptic trust this?")
    assumptions_separated: bool = Field(..., description="Are assumptions clearly separated?")
    self_critique: str = Field(..., description="Honest assessment of this research")


class CustomerResearch(BaseModel):
    """
    AI-generated market hypotheses designed to surface uncomfortable questions.

    IMPORTANT: These are hypotheses requiring validation through customer interviews.
    This is NOT validated research. This is hypothesis generation for testing.
    The goal is to identify assumptions that need customer confirmation.
    """

    research_scope: ResearchScope = Field(..., description="Scope and limitations")
    job_to_be_done: JobToBeDone = Field(..., description="Contextual JTBD")
    current_behaviour: CurrentBehaviour = Field(..., description="What customers do today")
    pain_signals: list[PainSignal] = Field(..., min_length=3, description="Evidence-tagged pain signals")
    uncomfortable_insights: list[UncomfortableInsight] = Field(..., min_length=1, description="Challenging insights")
    what_customers_dont_care_about: list[CustomerIndifference] = Field(..., min_length=1, description="Low-priority assumed needs")
    open_questions: list[OpenQuestion] = Field(..., min_length=1, description="Unresolved questions")
    competitive_landscape: CompetitiveLandscape = Field(..., description="Competitive reality check")
    market_context: MarketContext = Field(..., description="Market sizing with uncertainty")
    research_quality_check: ResearchQualityCheck = Field(..., description="Self-critique")
    validation_reminder: str = Field(
        default="These findings are AI-generated hypotheses. Schedule customer interviews to validate.",
        description="Reminder that these are hypotheses requiring customer validation"
    )
    # Visual data for frontend rendering
    competitive_positioning: Optional[dict[str, Any]] = Field(
        default=None,
        description="Structured competitive positioning data for quadrant visualization",
    )


# Legacy models for backward compatibility
class PainPoint(BaseModel):
    """A specific customer pain point (legacy format)."""

    description: str = Field(..., description="Pain point description")
    severity: Priority = Field(..., description="Severity of the pain point")
    current_workaround: Optional[str] = Field(default=None, description="How users currently handle this")


class MarketSegment(BaseModel):
    """A target market segment (legacy format)."""

    name: str = Field(..., description="Segment name")
    size_estimate: str = Field(..., description="Estimated market size")
    characteristics: list[str] = Field(..., description="Key characteristics")
    willingness_to_pay: str = Field(..., description="Expected price sensitivity")


class Competitor(BaseModel):
    """Competitive analysis entry (legacy format)."""

    name: str = Field(..., description="Competitor name")
    strengths: list[str] = Field(..., description="Competitor strengths")
    weaknesses: list[str] = Field(..., description="Competitor weaknesses")
    market_position: str = Field(..., description="Market positioning")
    pricing_model: Optional[str] = Field(default=None, description="Pricing approach")


class UserPersona(BaseModel):
    """
    Detailed user persona for product design (legacy format).
    Note: New research format uses behavior-based insights instead of personas.
    """

    name: str = Field(..., description="Persona name")
    role: str = Field(..., description="Job title or role")
    demographics: str = Field(..., description="Demographic summary")
    goals: list[str] = Field(..., min_length=1, description="User goals")
    frustrations: list[str] = Field(..., min_length=1, description="Pain points and frustrations")
    behaviors: list[str] = Field(..., min_length=1, description="Key behaviors")
    tech_savviness: str = Field(..., description="Technology comfort level")
    quote: str = Field(..., description="Representative user quote")


# ═══════════════════════════════════════════════════════════════════════════════
# BUSINESS CASE
# ═══════════════════════════════════════════════════════════════════════════════


class RevenueStream(BaseModel):
    """A revenue stream in the business model."""

    name: str = Field(..., description="Revenue stream name")
    description: str = Field(..., description="How this generates revenue")
    pricing_model: str = Field(..., description="Pricing approach")
    estimated_contribution: str = Field(..., description="Percentage of total revenue")


class CostStructure(BaseModel):
    """Cost structure breakdown."""

    category: str = Field(..., description="Cost category")
    description: str = Field(..., description="Cost description")
    estimated_amount: str = Field(..., description="Estimated cost")
    frequency: str = Field(..., description="One-time, monthly, annual, etc.")


class LeanCanvasBlock(BaseModel):
    """A block in the Lean Canvas."""

    problem: list[str] = Field(..., description="Top 3 problems")
    solution: list[str] = Field(..., description="Top 3 solutions")
    unique_value_proposition: str = Field(..., description="Single clear message")
    unfair_advantage: str = Field(..., description="What can't be copied")
    customer_segments: list[str] = Field(..., description="Target customers")
    key_metrics: list[str] = Field(..., description="Key activities to measure")
    channels: list[str] = Field(..., description="Path to customers")
    cost_structure: list[str] = Field(..., description="Customer acquisition, hosting, etc.")
    revenue_streams: list[str] = Field(..., description="Revenue model")


class BusinessCase(BaseModel):
    """
    Business case and financial analysis.

    Attributes:
        lean_canvas: Lean Canvas model.
        revenue_streams: Identified revenue streams.
        cost_structure: Cost breakdown.
        break_even_analysis: Break-even point estimate.
        year_1_projection: Year 1 financial projection.
        year_3_projection: Year 3 financial projection.
        funding_requirement: Initial funding needed.
        roi_analysis: Return on investment analysis.
        go_to_market_strategy: GTM strategy summary.
        key_partnerships: Strategic partnerships needed.
        risks_and_mitigations: Business risks and mitigations.
    """

    lean_canvas: LeanCanvasBlock = Field(..., description="Lean Canvas")
    revenue_streams: list[RevenueStream] = Field(..., min_length=1, description="Revenue streams")
    cost_structure: list[CostStructure] = Field(..., min_length=1, description="Cost breakdown")
    break_even_analysis: str = Field(..., description="Break-even estimate")
    year_1_projection: str = Field(..., description="Year 1 projection")
    year_3_projection: str = Field(..., description="Year 3 projection")
    funding_requirement: str = Field(..., description="Initial funding needed")
    roi_analysis: str = Field(..., description="ROI analysis")
    go_to_market_strategy: str = Field(..., description="GTM strategy")
    key_partnerships: list[str] = Field(default_factory=list, description="Key partnerships")
    risks_and_mitigations: list[dict[str, str]] = Field(..., description="Risk/mitigation pairs")
    # Enhanced unit economics from Prompt Library
    unit_economics: Optional[dict[str, Any]] = Field(
        default=None,
        description="Detailed unit economics with CAC, LTV, ARPU, margins, and derivations",
    )
    sensitivity_analysis: Optional[dict[str, Any]] = Field(
        default=None,
        description="Base/optimistic/pessimistic scenarios with kill conditions",
    )
    # Visual data for frontend rendering
    financial_projection: Optional[dict[str, Any]] = Field(
        default=None,
        description="Structured monthly projection data for charts",
    )
    lean_canvas_visual: Optional[dict[str, Any]] = Field(
        default=None,
        description="Structured lean canvas data for visual rendering",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT REQUIREMENTS DOCUMENT (PRD)
# ═══════════════════════════════════════════════════════════════════════════════


class AcceptanceCriteria(BaseModel):
    """Acceptance criteria for a user story."""

    given: str = Field(..., description="Given (precondition)")
    when: str = Field(..., description="When (action)")
    then: str = Field(..., description="Then (expected result)")


class UserStory(BaseModel):
    """
    User story following the standard format.

    Attributes:
        id: Unique story identifier (e.g., US-001).
        epic_id: Parent epic identifier.
        title: Brief story title.
        as_a: User role (As a...).
        i_want: Desired action (I want...).
        so_that: Business value (So that...).
        acceptance_criteria: List of acceptance criteria.
        priority: Story priority.
        size: T-shirt size estimate.
        dependencies: Story dependencies.
        notes: Additional notes.
    """

    id: str = Field(..., pattern=r"^US-\d{3}$", description="Story ID (e.g., US-001)")
    epic_id: str = Field(..., pattern=r"^EP-\d{2}$", description="Parent epic ID")
    title: str = Field(..., max_length=100, description="Story title")
    as_a: str = Field(..., description="User role")
    i_want: str = Field(..., description="Desired action")
    so_that: str = Field(..., description="Business value")
    acceptance_criteria: list[AcceptanceCriteria] = Field(
        ..., min_length=1, description="Acceptance criteria"
    )
    priority: Priority = Field(..., description="Story priority")
    size: StorySize = Field(..., description="T-shirt size")
    dependencies: list[str] = Field(default_factory=list, description="Dependencies")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class Epic(BaseModel):
    """
    Epic grouping related user stories.

    Attributes:
        id: Unique epic identifier (e.g., EP-01).
        title: Epic title.
        description: Epic description.
        business_value: Why this epic matters.
        stories: User stories in this epic.
    """

    id: str = Field(..., pattern=r"^EP-\d{2}$", description="Epic ID (e.g., EP-01)")
    title: str = Field(..., max_length=100, description="Epic title")
    description: str = Field(..., description="Epic description")
    business_value: str = Field(..., description="Business value")
    stories: list[UserStory] = Field(..., min_length=1, description="User stories")


class FunctionalRequirement(BaseModel):
    """
    Functional requirement specification.

    Attributes:
        id: Unique requirement ID (e.g., FR-001).
        title: Requirement title.
        description: Detailed description.
        priority: Requirement priority.
        rationale: Why this requirement exists.
        acceptance_criteria: How to verify this requirement.
    """

    id: str = Field(..., pattern=r"^FR-\d{3}$", description="Requirement ID")
    title: str = Field(..., max_length=100, description="Requirement title")
    description: str = Field(..., description="Detailed description")
    priority: Priority = Field(..., description="Priority level")
    rationale: str = Field(..., description="Business rationale")
    acceptance_criteria: list[str] = Field(..., min_length=1, description="Acceptance criteria")


class NonFunctionalRequirement(BaseModel):
    """
    Non-functional requirement specification.

    Attributes:
        id: Unique requirement ID (e.g., NFR-001).
        category: Category (Performance, Security, Scalability, etc.).
        title: Requirement title.
        description: Detailed description.
        metric: How this will be measured.
        target: Target value/threshold.
        priority: Requirement priority.
    """

    id: str = Field(..., pattern=r"^NFR-\d{3}$", description="Requirement ID")
    category: str = Field(..., description="NFR category")
    title: str = Field(..., max_length=100, description="Requirement title")
    description: str = Field(..., description="Detailed description")
    metric: str = Field(..., description="Measurement metric")
    target: str = Field(..., description="Target value")
    priority: Priority = Field(..., description="Priority level")


class DataEntity(BaseModel):
    """A data entity in the data model."""

    name: str = Field(..., description="Entity name")
    description: str = Field(..., description="Entity description")
    attributes: list[dict[str, str]] = Field(..., description="Entity attributes")
    relationships: list[str] = Field(default_factory=list, description="Relationships to other entities")


class DataModel(BaseModel):
    """
    Data model specification.

    Attributes:
        entities: Data entities.
        description: Overall data model description.
    """

    entities: list[DataEntity] = Field(..., min_length=1, description="Data entities")
    description: str = Field(..., description="Data model overview")


class ReleasePhase(BaseModel):
    """A release phase in the roadmap."""

    phase: str = Field(..., description="Phase name (e.g., MVP, v1.0)")
    description: str = Field(..., description="Phase description")
    features: list[str] = Field(..., min_length=1, description="Features in this phase")
    success_criteria: list[str] = Field(..., min_length=1, description="Success criteria")


class Risk(BaseModel):
    """A product risk."""

    id: str = Field(..., pattern=r"^RISK-\d{3}$", description="Risk ID")
    description: str = Field(..., description="Risk description")
    likelihood: RiskLevel = Field(..., description="Likelihood of occurrence")
    impact: RiskLevel = Field(..., description="Impact if it occurs")
    mitigation: str = Field(..., description="Mitigation strategy")


class ProductRequirementsDocument(BaseModel):
    """
    Complete Product Requirements Document (PRD).

    This is the core deliverable containing all product specifications.

    Attributes:
        version: PRD version number.
        last_updated: Last update timestamp.
        overview: Product overview.
        objectives: Product objectives.
        scope_in: What's in scope.
        scope_out: What's explicitly out of scope.
        user_personas: Referenced user personas.
        epics: Feature epics with user stories.
        functional_requirements: Functional requirements.
        non_functional_requirements: Non-functional requirements.
        data_model: Data model specification.
        integration_requirements: Integration points.
        constraints: Technical and business constraints.
        assumptions: Key assumptions.
        release_plan: Phased release plan.
        risks: Identified risks.
        open_questions: Questions requiring answers.
        glossary: Term definitions.
    """

    version: str = Field(default="1.0", description="PRD version")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update")
    overview: str = Field(..., description="Product overview")
    objectives: list[str] = Field(..., min_length=1, description="Product objectives")
    scope_in: list[str] = Field(..., min_length=1, description="In-scope items")
    scope_out: list[str] = Field(..., min_length=1, description="Out-of-scope items")
    user_personas: list[str] = Field(..., min_length=1, description="Referenced persona names")
    epics: list[Epic] = Field(..., min_length=3, max_length=7, description="Feature epics")
    functional_requirements: list[FunctionalRequirement] = Field(
        ..., min_length=8, max_length=15, description="Functional requirements"
    )
    non_functional_requirements: list[NonFunctionalRequirement] = Field(
        ..., min_length=5, max_length=12, description="Non-functional requirements"
    )
    data_model: DataModel = Field(..., description="Data model")
    integration_requirements: list[str] = Field(..., min_length=1, description="Integration points")
    constraints: list[str] = Field(..., min_length=1, description="Constraints")
    assumptions: list[str] = Field(..., min_length=1, description="Assumptions")
    release_plan: list[ReleasePhase] = Field(..., min_length=2, description="Release phases")
    risks: list[Risk] = Field(..., min_length=3, description="Product risks")
    open_questions: list[str] = Field(default_factory=list, description="Open questions")
    glossary: dict[str, str] = Field(default_factory=dict, description="Term definitions")


# ═══════════════════════════════════════════════════════════════════════════════
# TECHNICAL ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════


class TechnologyChoice(BaseModel):
    """A technology selection with rationale."""

    category: str = Field(..., description="Category (Frontend, Backend, Database, etc.)")
    technology: str = Field(..., description="Selected technology")
    rationale: str = Field(..., description="Why this choice")
    alternatives_considered: list[str] = Field(default_factory=list, description="Alternatives")


class SystemComponent(BaseModel):
    """A system component in the architecture."""

    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    responsibilities: list[str] = Field(..., min_length=1, description="Responsibilities")
    technologies: list[str] = Field(..., min_length=1, description="Technologies used")
    interfaces: list[str] = Field(default_factory=list, description="Interfaces exposed")


class IntegrationPoint(BaseModel):
    """An external integration point."""

    name: str = Field(..., description="Integration name")
    type: str = Field(..., description="Integration type (API, Webhook, SDK, etc.)")
    description: str = Field(..., description="Integration description")
    authentication: str = Field(..., description="Auth mechanism")
    data_flow: str = Field(..., description="Data flow direction and format")


class TechnicalArchitecture(BaseModel):
    """
    Technical architecture specification.

    Attributes:
        architecture_style: Architecture pattern (Microservices, Monolith, etc.).
        architecture_diagram_description: Text description of architecture.
        technology_stack: Technology selections.
        system_components: System components.
        integration_points: External integrations.
        data_storage: Data storage strategy.
        security_architecture: Security approach.
        scalability_approach: Scalability strategy.
        deployment_strategy: Deployment approach.
        infrastructure_requirements: Infrastructure needs.
        development_approach: Development methodology.
        technical_risks: Technical risks and mitigations.
    """

    architecture_style: str = Field(..., description="Architecture pattern")
    architecture_diagram_description: str = Field(..., description="Architecture description")
    architecture_diagram_mermaid: str = Field(
        default="",
        description="Mermaid.js diagram syntax for the system architecture"
    )
    sequence_diagram_mermaid: str = Field(
        default="",
        description="Mermaid.js sequence diagram showing key user flow interactions"
    )
    technology_stack: list[TechnologyChoice] = Field(..., min_length=3, description="Tech stack")
    system_components: list[SystemComponent] = Field(..., min_length=2, description="Components")
    integration_points: list[IntegrationPoint] = Field(default_factory=list, description="Integrations")
    data_storage: str = Field(..., description="Data storage strategy")
    security_architecture: str = Field(..., description="Security approach")
    scalability_approach: str = Field(..., description="Scalability strategy")
    deployment_strategy: str = Field(..., description="Deployment approach")
    infrastructure_requirements: list[str] = Field(..., min_length=1, description="Infrastructure needs")
    development_approach: str = Field(..., description="Development methodology")
    technical_risks: list[dict[str, str]] = Field(..., description="Risk/mitigation pairs")


# ═══════════════════════════════════════════════════════════════════════════════
# LEGAL & REGULATORY REVIEW
# ═══════════════════════════════════════════════════════════════════════════════


class Regulation(BaseModel):
    """A specific regulation or legal requirement."""

    name: str = Field(..., description="Regulation name (e.g., GDPR, HIPAA, SOC 2)")
    description: str = Field(..., description="What this regulation requires")
    applicability: str = Field(..., description="Why this applies to the product")
    compliance_requirements: list[str] = Field(
        ..., min_length=1, description="Specific compliance requirements"
    )
    impact_level: RiskLevel = Field(..., description="Impact on product development")
    estimated_compliance_timeline: str = Field(
        ..., description="Time needed to achieve compliance"
    )
    estimated_compliance_cost: str = Field(..., description="Estimated cost range")


class LicenseRequirement(BaseModel):
    """Licensing or certification requirement."""

    license_type: str = Field(..., description="Type of license or certification")
    issuing_authority: str = Field(..., description="Who issues this license")
    requirements: list[str] = Field(..., min_length=1, description="Requirements to obtain")
    timeline: str = Field(..., description="Time to obtain")
    cost: str = Field(..., description="Estimated cost")
    renewal_requirements: str = Field(..., description="Renewal process and frequency")


class LegalRisk(BaseModel):
    """Identified legal risk."""

    risk_category: str = Field(..., description="Category (e.g., Liability, IP, Privacy)")
    description: str = Field(..., description="Description of the legal risk")
    severity: RiskLevel = Field(..., description="Risk severity")
    likelihood: str = Field(..., description="Likelihood (High/Medium/Low)")
    mitigation_strategies: list[str] = Field(
        ..., min_length=1, description="How to mitigate this risk"
    )
    legal_counsel_recommended: bool = Field(
        ..., description="Whether specialized legal counsel is recommended"
    )


class DataProtectionRequirement(BaseModel):
    """Data protection and privacy requirement."""

    regulation: str = Field(..., description="Regulation name (GDPR, CCPA, etc.)")
    data_types_covered: list[str] = Field(..., min_length=1, description="Types of data covered")
    key_obligations: list[str] = Field(..., min_length=1, description="Key obligations")
    user_rights: list[str] = Field(..., min_length=1, description="User rights that must be supported")
    penalties_for_non_compliance: str = Field(..., description="Potential penalties")
    implementation_requirements: list[str] = Field(
        ..., min_length=1, description="Implementation requirements"
    )


class IntellectualPropertyConsideration(BaseModel):
    """Intellectual property considerations."""

    ip_type: str = Field(..., description="Type (Patent, Trademark, Copyright, Trade Secret)")
    description: str = Field(..., description="Description of IP consideration")
    action_required: str = Field(..., description="Required action")
    priority: Priority = Field(..., description="Priority level")
    estimated_cost: str = Field(..., description="Estimated cost")


class OverallRiskAssessment(BaseModel):
    """Overall legal and regulatory risk assessment."""

    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM, description="Overall risk level")
    key_concerns: list[str] = Field(default_factory=list, description="Top legal concerns")
    blocking_issues: list[str] = Field(
        default_factory=list, description="Issues that could block product launch"
    )
    recommended_timeline_buffer: str = Field(
        default="3-6 months", description="Additional timeline buffer for legal compliance"
    )
    recommended_budget_allocation: str = Field(
        default="10-15% of project budget", description="Recommended budget for legal/compliance"
    )

    @field_validator("risk_level", mode="before")
    @classmethod
    def normalize_risk_level(cls, v):
        """Normalize risk level values like 'medium-high' to valid enum values."""
        if isinstance(v, str):
            v_lower = v.lower().strip()
            # Map variations to valid enum values
            if v_lower in ("high", "critical", "severe"):
                return RiskLevel.HIGH
            elif v_lower in ("medium-high", "moderate-high"):
                return RiskLevel.HIGH
            elif v_lower in ("medium", "moderate"):
                return RiskLevel.MEDIUM
            elif v_lower in ("medium-low", "moderate-low"):
                return RiskLevel.LOW
            elif v_lower in ("low", "minimal"):
                return RiskLevel.LOW
        return v


class LegalRegulatoryReview(BaseModel):
    """
    Legal and regulatory review of the product idea.

    This comprehensive analysis stress tests the product against legal and
    regulatory requirements, helping teams understand compliance obligations
    and potential legal risks before building.

    Attributes:
        executive_summary: High-level summary of legal/regulatory landscape.
        applicable_regulations: Regulations that apply to this product.
        licensing_requirements: Required licenses and certifications.
        data_protection_requirements: Data protection and privacy requirements.
        legal_risks: Identified legal risks and mitigations.
        intellectual_property: IP considerations and recommendations.
        industry_specific_considerations: Industry-specific legal notes.
        international_considerations: Cross-border legal considerations.
        recommended_legal_structure: Recommended business legal structure.
        ongoing_compliance_requirements: Ongoing compliance obligations.
        overall_risk_assessment: Overall risk assessment.
        next_steps: Recommended next steps for legal compliance.
    """

    executive_summary: str = Field(
        default="", description="High-level summary of legal/regulatory landscape"
    )
    applicable_regulations: list[Regulation] = Field(
        default_factory=list, description="Applicable regulations"
    )
    licensing_requirements: list[LicenseRequirement] = Field(
        default_factory=list, description="Required licenses and certifications"
    )
    data_protection_requirements: list[DataProtectionRequirement] = Field(
        default_factory=list, description="Data protection requirements"
    )
    legal_risks: list[LegalRisk] = Field(default_factory=list, description="Legal risks identified")
    intellectual_property: list[IntellectualPropertyConsideration] = Field(
        default_factory=list, description="IP considerations"
    )
    industry_specific_considerations: list[str] = Field(
        default_factory=list, description="Industry-specific legal notes"
    )
    international_considerations: list[str] = Field(
        default_factory=list, description="Cross-border legal considerations"
    )
    recommended_legal_structure: str = Field(
        default="", description="Recommended business legal structure"
    )
    ongoing_compliance_requirements: list[str] = Field(
        default_factory=list, description="Ongoing compliance obligations"
    )
    overall_risk_assessment: OverallRiskAssessment = Field(
        default_factory=OverallRiskAssessment, description="Overall risk assessment"
    )
    next_steps: list[str] = Field(default_factory=list, description="Recommended next steps")


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════════


class SectionScore(BaseModel):
    """Quality score for a specific section."""

    section: str = Field(..., description="Section name")
    score: float = Field(..., ge=0.0, le=1.0, description="Score (0.0-1.0)")
    feedback: str = Field(..., description="Feedback on this section")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")


class QualityAssessment(BaseModel):
    """
    Quality assessment from the critique agent.

    Attributes:
        overall_score: Overall quality score (0.0-1.0).
        passed: Whether quality threshold was met.
        iteration: Which iteration this assessment is for.
        section_scores: Scores for each section.
        strengths: What was done well.
        weaknesses: Areas needing improvement.
        critical_gaps: Critical gaps that must be addressed.
        recommendations: Specific recommendations.
        ready_for_delivery: Whether the pack is ready for delivery.
    """

    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall score")
    passed: bool = Field(..., description="Whether quality check passed")
    iteration: int = Field(..., ge=1, le=5, description="Assessment iteration")
    section_scores: list[SectionScore] = Field(..., min_length=1, description="Section scores")
    strengths: list[str] = Field(..., min_length=1, description="Strengths identified")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses found")
    critical_gaps: list[str] = Field(default_factory=list, description="Critical gaps")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    ready_for_delivery: bool = Field(..., description="Ready for delivery")


# ═══════════════════════════════════════════════════════════════════════════════
# V3.0 GO-TO-MARKET STRATEGY
# ═══════════════════════════════════════════════════════════════════════════════


class ChannelStrategy(BaseModel):
    """A channel in the GTM strategy."""

    channel: str = Field(..., description="Channel name")
    role: str = Field(..., description="Role: acquisition|activation|retention|revenue|referral")
    expected_cac: Optional[str] = Field(default=None, description="Estimated CAC")
    time_to_scale: Optional[str] = Field(default=None, description="Time to scale this channel")
    priority: int = Field(default=1, ge=1, le=10, description="Priority rank")


class PhaseTactic(BaseModel):
    """A specific tactic within a launch phase."""

    tactic: str = Field(..., description="Specific tactic description")
    channel: str = Field(default="", description="Specific channel")
    budget: Optional[str] = Field(default=None, description="Monthly cost")
    expected_result: Optional[str] = Field(default=None, description="Expected measurable result")
    measurement: Optional[str] = Field(default=None, description="How to measure")
    timeline: Optional[str] = Field(default=None, description="When to execute")
    evidence_tier: str = Field(default="E4", description="Evidence tier: E2-E5")


class LaunchPhase(BaseModel):
    """A phase in the launch plan."""

    phase: str = Field(..., description="Phase name")
    duration: str = Field(..., description="Timeline/duration")
    objective: Optional[str] = Field(default=None, description="What success looks like at end of phase")
    goals: list[str] = Field(default_factory=list, description="Phase goals")
    tactics: list[dict[str, Any]] = Field(default_factory=list, description="Specific executable tactics")
    key_activities: list[str] = Field(default_factory=list, description="Key activities")
    success_metrics: list[str] = Field(default_factory=list, description="Success metrics")
    total_phase_budget: Optional[str] = Field(default=None, description="Total budget for phase")
    phase_success_criteria: Optional[str] = Field(default=None, description="Gate for next phase")


class PersonaMessaging(BaseModel):
    """Messaging tailored for a specific persona."""

    persona_name: str = Field(..., description="Target persona name")
    headline: str = Field(..., description="Primary headline")
    value_proposition: str = Field(..., description="Tailored value prop")
    key_benefits: list[str] = Field(default_factory=list, description="Key benefits to highlight")
    objection_handling: list[str] = Field(default_factory=list, description="Common objections and responses")


class MetricTarget(BaseModel):
    """A metric with targets over time."""

    metric: str = Field(..., description="Metric name")
    target_month_3: Optional[str] = Field(default=None, description="3-month target")
    target_month_6: Optional[str] = Field(default=None, description="6-month target")
    target_month_12: Optional[str] = Field(default=None, description="12-month target")


class GoToMarket(BaseModel):
    """
    Go-to-Market Strategy — executable launch playbook.

    Provides detailed GTM strategy including market entry approach,
    channel strategy, launch phases, and growth tactics.
    """

    positioning_statement: str = Field(..., description="Core positioning statement")
    messaging_by_persona: list[PersonaMessaging] = Field(
        default_factory=list, description="Tailored messaging per persona"
    )
    market_entry_strategy: Optional[dict[str, Any]] = Field(
        default=None, description="Market entry approach details"
    )
    launch_phases: list[LaunchPhase] = Field(
        default_factory=list, description="Phased launch plan"
    )
    channel_strategy: list[ChannelStrategy] = Field(
        default_factory=list, description="Channel mix strategy"
    )
    growth_tactics: list[dict[str, Any]] = Field(
        default_factory=list, description="Growth tactics with priority"
    )
    partnership_opportunities: list[dict[str, Any]] = Field(
        default_factory=list, description="Strategic partnership opportunities"
    )
    metrics_dashboard: list[MetricTarget] = Field(
        default_factory=list, description="Key metrics to track"
    )
    gtm_risks: list[dict[str, str]] = Field(
        default_factory=list, description="GTM risks and mitigations"
    )
    competitive_response_plan: Optional[dict[str, Any]] = Field(
        default=None, description="Plan for responding to competitive moves"
    )
    total_gtm_budget_estimate: Optional[str] = Field(
        default=None, description="Estimated total GTM budget for first 12 months"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V3.0 FINANCIAL MODEL
# ═══════════════════════════════════════════════════════════════════════════════


class InputAssumption(BaseModel):
    """An input assumption for the financial model."""

    name: str = Field(..., description="Assumption name")
    value: str = Field(..., description="Assumed value")
    evidence_tier: str = Field(default="E4", description="Evidence tier: E1-E5")
    source: Optional[str] = Field(default=None, description="Source for this assumption")
    sensitivity: str = Field(default="medium", description="Sensitivity: high|medium|low")


class MonthlyProjection(BaseModel):
    """Monthly financial projection."""

    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    revenue: float = Field(default=0, description="Monthly revenue")
    costs: float = Field(default=0, description="Monthly costs")
    profit: float = Field(default=0, description="Monthly profit/loss")
    customers: int = Field(default=0, description="Customer count")
    mrr: float = Field(default=0, description="Monthly recurring revenue")


class QuarterlyProjection(BaseModel):
    """Quarterly financial projection."""

    quarter: str = Field(..., description="Quarter label (e.g., Y2Q1)")
    revenue: float = Field(default=0, description="Quarterly revenue")
    costs: float = Field(default=0, description="Quarterly costs")
    profit: float = Field(default=0, description="Quarterly profit/loss")
    customers: int = Field(default=0, description="Customer count")
    arr: float = Field(default=0, description="Annual recurring revenue run rate")


class FundingRequirements(BaseModel):
    """Funding requirements by stage."""

    pre_seed: Optional[dict[str, Any]] = Field(default=None, description="Pre-seed requirements")
    seed: Optional[dict[str, Any]] = Field(default=None, description="Seed requirements")
    series_a: Optional[dict[str, Any]] = Field(default=None, description="Series A requirements")
    total_required: Optional[str] = Field(default=None, description="Total funding required")


class FinancialModel(BaseModel):
    """
    Financial Model — detailed projections with scenarios.

    Provides comprehensive financial projections including revenue model,
    cost structure, unit economics, and scenario analysis.
    """

    input_assumptions: list[InputAssumption] = Field(
        default_factory=list, description="Key input assumptions"
    )
    revenue_model: Optional[dict[str, Any]] = Field(
        default=None, description="Revenue model breakdown"
    )
    cost_structure: Optional[dict[str, Any]] = Field(
        default=None, description="Cost structure details"
    )
    unit_economics: Optional[dict[str, Any]] = Field(
        default=None, description="LTV, CAC, margins, etc."
    )
    monthly_projections_year_1: list[MonthlyProjection] = Field(
        default_factory=list, description="12-month Year 1 projections"
    )
    quarterly_projections_year_2_3: list[QuarterlyProjection] = Field(
        default_factory=list, description="Year 2-3 quarterly projections"
    )
    scenario_analysis: Optional[dict[str, Any]] = Field(
        default=None, description="Base, optimistic, pessimistic scenarios"
    )
    funding_requirements: Optional[FundingRequirements] = Field(
        default=None, description="Funding requirements by stage"
    )
    key_financial_risks: list[dict[str, str]] = Field(
        default_factory=list, description="Financial risks and mitigations"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V3.0 STAKEHOLDER VIEWS
# ═══════════════════════════════════════════════════════════════════════════════


class Objection(BaseModel):
    """An anticipated objection from a stakeholder."""

    objection: str = Field(..., description="The objection/concern")
    response: str = Field(..., description="How to address it")
    supporting_claim_ids: list[str] = Field(
        default_factory=list, description="Claim IDs that support the response"
    )


class StakeholderView(BaseModel):
    """
    Stakeholder-specific view of the inception pack.

    Tailored summary for a specific stakeholder role (CFO, CISO, ARB, VP Product)
    with anticipated objections and evidence confidence.
    """

    stakeholder_role: str = Field(..., description="Role: CFO|CISO|ARB|VP Product|etc.")
    tailored_summary: str = Field(..., description="Summary tailored to this stakeholder")
    key_questions_answered: list[str] = Field(
        default_factory=list, description="Key questions this pack answers for them"
    )
    anticipated_objections: list[Objection] = Field(
        default_factory=list, description="Likely objections and responses"
    )
    evidence_confidence: str = Field(
        default="medium", description="Confidence level: high|medium|low"
    )
    decision_recommendation: str = Field(
        default="", description="Specific recommendation for this stakeholder"
    )
    key_metrics_for_role: list[str] = Field(
        default_factory=list, description="Metrics most relevant to this role"
    )


class StakeholderViews(BaseModel):
    """Collection of stakeholder-specific views."""

    views: list[StakeholderView] = Field(
        default_factory=list, description="Individual stakeholder views"
    )
    common_concerns: list[str] = Field(
        default_factory=list, description="Concerns shared across stakeholders"
    )
    alignment_opportunities: list[str] = Field(
        default_factory=list, description="Areas where stakeholders align"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V3.0 VALIDATION PLAYBOOK
# ═══════════════════════════════════════════════════════════════════════════════


class Experiment(BaseModel):
    """A validation experiment for testing hypotheses."""

    experiment_id: str = Field(..., description="Unique experiment ID (EXP-1, EXP-2, etc.)")
    hypothesis_claim_id: str = Field(..., description="Claim ID being tested")
    experiment_name: str = Field(..., description="Name of the experiment")
    target_profile: str = Field(..., description="Who to test with")
    experiment_type: str = Field(
        default="interview",
        description="Type: interview|survey|landing_page|prototype|concierge|smoke_test"
    )
    specific_instructions: str = Field(..., description="Detailed instructions to run")
    sample_size: Optional[str] = Field(default=None, description="Target sample size")
    success_criteria: str = Field(..., description="What defines success")
    failure_criteria: str = Field(..., description="What defines failure")
    expected_duration: str = Field(default="1 week", description="Expected time to complete")
    cost_estimate: Optional[str] = Field(default=None, description="Cost estimate")
    upgrade_path: list[str] = Field(
        default_factory=list, description="Claim IDs that upgrade if validated"
    )
    risk_if_skipped: str = Field(
        default="", description="Risk of not running this experiment"
    )
    effort_level: str = Field(
        default="moderate", description="Effort required: quick|moderate|significant"
    )
    priority: str = Field(
        default="medium", description="Priority level: critical|high|medium|low"
    )
    timeline: Optional[str] = Field(default=None, description="Specific timeline for the experiment")


class ValidationPlaybook(BaseModel):
    """
    Validation Playbook — experiments for testing assumptions.

    Provides 5-8 specific experiments to validate E4/E5 claims,
    prioritized by impact and with clear success/failure criteria.
    """

    experiments: list[Experiment] = Field(
        default_factory=list, description="Ordered list of experiments"
    )
    validation_priorities: list[dict[str, Any]] = Field(
        default_factory=list, description="Prioritized claims to validate"
    )
    total_validation_budget: Optional[str] = Field(
        default=None, description="Estimated budget for all experiments"
    )
    total_validation_timeline: Optional[str] = Field(
        default=None, description="Estimated timeline to complete all"
    )
    critical_path_experiments: list[str] = Field(
        default_factory=list, description="Experiment IDs on critical path"
    )
    validation_dashboard: Optional[dict[str, Any]] = Field(
        default=None, description="Tracking dashboard structure"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V3.0 WIREFRAMES AND PROTOTYPE
# ═══════════════════════════════════════════════════════════════════════════════


class WireframeScreen(BaseModel):
    """A wireframe screen definition."""

    screen_id: str = Field(..., description="Screen ID (S1, S2, etc.)")
    screen_name: str = Field(..., description="Screen name")
    purpose: str = Field(..., description="Purpose of this screen")
    user_stories_covered: list[str] = Field(
        default_factory=list, description="User story IDs covered"
    )
    key_components: list[str] = Field(
        default_factory=list, description="Key UI components"
    )
    navigation_to: list[str] = Field(
        default_factory=list, description="Screen IDs this navigates to"
    )
    react_code: str = Field(default="", description="React component code")
    notes: str = Field(default="", description="Design decisions and notes")


class UserFlow(BaseModel):
    """A user flow diagram for a specific journey."""

    flow_name: str = Field(..., description="Name of the user flow")
    persona: str = Field(default="", description="Persona this flow follows")
    mermaid_code: str = Field(default="", description="Mermaid flowchart code")
    screens_referenced: list[str] = Field(
        default_factory=list, description="Screen IDs referenced in this flow"
    )
    notes: str = Field(default="", description="Notes about this flow")


class Wireframes(BaseModel):
    """Collection of wireframe screens."""

    screens: list[WireframeScreen] = Field(
        default_factory=list, description="Wireframe screens"
    )
    user_flows: list[UserFlow] = Field(
        default_factory=list, description="User flow diagrams"
    )
    user_flow_description: str = Field(
        default="", description="Overall user flow description"
    )
    user_flow_mermaid: str = Field(
        default="", description="Mermaid diagram of user flow"
    )
    design_system_notes: list[str] = Field(
        default_factory=list, description="Design system guidelines"
    )
    responsive_notes: str = Field(
        default="", description="Notes on responsive/mobile adaptation"
    )


class ColorPalette(BaseModel):
    """Color palette for prototype styling."""

    primary: str = Field(..., description="Primary color (hex or Tailwind class)")
    secondary: str = Field(default="", description="Secondary color")
    accent: str = Field(default="", description="Accent color")
    background: str = Field(default="", description="Background color")
    text: str = Field(default="", description="Text color")


class Prototype(BaseModel):
    """Interactive prototype definition."""

    prototype_name: str = Field(..., description="Prototype name")
    primary_persona: str = Field(..., description="Primary persona this serves")
    key_user_story: str = Field(..., description="Main user story demonstrated")
    react_component_code: str = Field(..., description="Full React component code")
    css_code: str = Field(default="", description="Additional CSS if needed")
    state_management_notes: str = Field(
        default="", description="Notes on state management"
    )
    interactivity_notes: list[str] = Field(
        default_factory=list, description="Interactivity implementation notes"
    )
    screens_included: list[str] = Field(
        default_factory=list, description="Screen IDs included"
    )
    color_palette: Optional[dict[str, Any]] = Field(
        default=None, description="Color palette with primary, secondary, accent, background, text"
    )
    demo_scenario: str = Field(default="", description="Step-by-step demo script")
    design_notes: str = Field(default="", description="Key design decisions and rationale")
    story_summary: str = Field(default="", description="What story does this prototype tell and what's the aha moment")


# ═══════════════════════════════════════════════════════════════════════════════
# INCEPTION PACK (Complete Output)
# ═══════════════════════════════════════════════════════════════════════════════


class InceptionPack(BaseModel):
    """
    Complete inception pack - the final deliverable.

    This model represents the complete output of the discovery process,
    combining all agent outputs into a cohesive document.

    V3.0 adds: cross_reference_index, gtm_strategy, financial_model,
    stakeholder_views, validation_playbook, wireframes, prototype.

    Attributes:
        executive_summary: High-level product summary.
        customer_research: Market and customer research.
        business_case: Business case and financials.
        product_requirements_document: Complete PRD.
        technical_architecture: Technical architecture.
        legal_regulatory_review: Legal and regulatory compliance review.
        quality_assessment: Quality assessment.
        metadata: Generation metadata.
    """

    # Core sections
    executive_summary: ExecutiveSummary = Field(..., description="Executive summary")
    customer_research: CustomerResearch = Field(..., description="Customer research")
    business_case: BusinessCase = Field(..., description="Business case")
    product_requirements_document: ProductRequirementsDocument = Field(..., description="PRD")
    technical_architecture: TechnicalArchitecture = Field(..., description="Technical architecture")
    legal_regulatory_review: LegalRegulatoryReview = Field(
        ..., description="Legal and regulatory review"
    )
    quality_assessment: QualityAssessment = Field(..., description="Quality assessment")

    # V3.0 additions
    cross_reference_index: Optional[dict[str, Any]] = Field(
        default=None, description="Cross-reference index with all claims"
    )
    competitive_analysis: Optional[dict[str, Any]] = Field(
        default=None, description="Detailed competitive analysis"
    )
    detailed_personas: Optional[dict[str, Any]] = Field(
        default=None, description="Detailed customer personas"
    )
    gtm_strategy: Optional[GoToMarket] = Field(
        default=None, description="Go-to-market strategy"
    )
    financial_model: Optional[FinancialModel] = Field(
        default=None, description="Detailed financial model"
    )
    risk_assessment: Optional[dict[str, Any]] = Field(
        default=None, description="Comprehensive risk assessment"
    )
    stakeholder_views: Optional[StakeholderViews] = Field(
        default=None, description="Stakeholder-specific views"
    )
    validation_playbook: Optional[ValidationPlaybook] = Field(
        default=None, description="Validation experiments playbook"
    )
    wireframes: Optional[Wireframes] = Field(
        default=None, description="UI wireframe screens"
    )
    prototype: Optional[Prototype] = Field(
        default=None, description="Interactive prototype"
    )

    metadata: dict[str, str] = Field(
        default_factory=lambda: {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "3.0",
            "generator": "Seedcraft v3.0 Multi-Agent System",
        },
        description="Generation metadata",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL REBUILDS (for forward references)
# ═══════════════════════════════════════════════════════════════════════════════

# Rebuild models that use forward references
SessionStatusResponse.model_rebuild()
CustomerResearch.model_rebuild()
InceptionPack.model_rebuild()
GoToMarket.model_rebuild()
FinancialModel.model_rebuild()
StakeholderViews.model_rebuild()
ValidationPlaybook.model_rebuild()
