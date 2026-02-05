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

from pydantic import BaseModel, Field


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


class CompetitiveLandscape(BaseModel):
    """Competitive landscape reality check."""

    competitors: list[CompetitorReality] = Field(default_factory=list, description="Competitor analysis")
    market_position: str = Field(..., description="Overall competitive assessment")


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

    risk_level: RiskLevel = Field(..., description="Overall risk level")
    key_concerns: list[str] = Field(..., min_length=1, description="Top legal concerns")
    blocking_issues: list[str] = Field(
        default_factory=list, description="Issues that could block product launch"
    )
    recommended_timeline_buffer: str = Field(
        ..., description="Additional timeline buffer for legal compliance"
    )
    recommended_budget_allocation: str = Field(
        ..., description="Recommended budget for legal/compliance"
    )


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
        ..., description="High-level summary of legal/regulatory landscape"
    )
    applicable_regulations: list[Regulation] = Field(
        ..., min_length=0, description="Applicable regulations"
    )
    licensing_requirements: list[LicenseRequirement] = Field(
        default_factory=list, description="Required licenses and certifications"
    )
    data_protection_requirements: list[DataProtectionRequirement] = Field(
        default_factory=list, description="Data protection requirements"
    )
    legal_risks: list[LegalRisk] = Field(..., min_length=1, description="Legal risks identified")
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
        ..., description="Recommended business legal structure"
    )
    ongoing_compliance_requirements: list[str] = Field(
        ..., min_length=1, description="Ongoing compliance obligations"
    )
    overall_risk_assessment: OverallRiskAssessment = Field(..., description="Overall risk assessment")
    next_steps: list[str] = Field(..., min_length=3, description="Recommended next steps")


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
# INCEPTION PACK (Complete Output)
# ═══════════════════════════════════════════════════════════════════════════════


class InceptionPack(BaseModel):
    """
    Complete inception pack - the final deliverable.

    This model represents the complete output of the discovery process,
    combining all agent outputs into a cohesive document.

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

    executive_summary: ExecutiveSummary = Field(..., description="Executive summary")
    customer_research: CustomerResearch = Field(..., description="Customer research")
    business_case: BusinessCase = Field(..., description="Business case")
    product_requirements_document: ProductRequirementsDocument = Field(..., description="PRD")
    technical_architecture: TechnicalArchitecture = Field(..., description="Technical architecture")
    legal_regulatory_review: LegalRegulatoryReview = Field(
        ..., description="Legal and regulatory review"
    )
    quality_assessment: QualityAssessment = Field(..., description="Quality assessment")
    metadata: dict[str, str] = Field(
        default_factory=lambda: {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0",
            "generator": "Product Discovery Multi-Agent System",
        },
        description="Generation metadata",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL REBUILDS (for forward references)
# ═══════════════════════════════════════════════════════════════════════════════

# Rebuild models that use forward references
SessionStatusResponse.model_rebuild()
CustomerResearch.model_rebuild()
