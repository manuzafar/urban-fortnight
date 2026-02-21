"""
Pydantic models for the Discovery V4 Hybrid System.

This module defines all data models for the V4 Discovery system including:
- Discovery modes (Quick, Guided, Deep)
- Stage outputs (Problem Love, Customer Truth, Opportunity Mapping, etc.)
- Interview data structures
- Pattern synthesis models
- Session state management
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class DiscoveryMode(str, Enum):
    """Discovery mode selection."""

    QUICK = "quick"  # AI generates everything automatically (~3-5 min)
    GUIDED = "guided"  # AI generates + optional checkpoints (~5-8 min)
    DEEP = "deep"  # User provides interviews, AI synthesizes (days-weeks)


class StageStatus(str, Enum):
    """Status of a discovery stage."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    SKIPPED = "skipped"


class EvidenceQuality(str, Enum):
    """Evidence quality tiers based on source."""

    E1 = "E1"  # Direct customer quotes/interviews
    E2 = "E2"  # Survey data, analytics
    E3 = "E3"  # Expert analysis, market research
    E4 = "E4"  # AI-generated hypotheses


class Severity(str, Enum):
    """Severity/priority levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PROBLEM LOVE
# Based on Uri Levine's frameworks
# ═══════════════════════════════════════════════════════════════════════════════


class RealPerson(BaseModel):
    """A real person experiencing the problem."""

    name: str = Field(..., description="Name or pseudonym")
    struggling_moment: str = Field(
        ..., description="Specific moment when they struggled with this problem"
    )
    how_you_know_them: Optional[str] = Field(
        default=None, description="How you know this person (friend, colleague, etc.)"
    )


class TarpitAnalysis(BaseModel):
    """Analysis of whether the idea is a tarpit (common trap)."""

    is_tarpit: bool = Field(
        ..., description="Whether this matches known tarpit patterns"
    )
    similarity_score: float = Field(
        ..., ge=0, le=1, description="How similar to known tarpits (0-1)"
    )
    similar_to: list[str] = Field(
        default_factory=list, description="Similar ideas that failed"
    )
    specific_concerns: list[str] = Field(
        default_factory=list, description="Specific concerns about this idea"
    )
    user_differentiation: Optional[str] = Field(
        default=None, description="How user claims to be different"
    )


class ProblemLoveOutput(BaseModel):
    """Output from Stage 1: Problem Love analysis."""

    # Problem statement
    problem_statement: str = Field(..., description="The original problem statement")
    problem_statement_refined: Optional[str] = Field(
        default=None, description="AI-refined version of the problem statement"
    )
    specificity_score: int = Field(
        ..., ge=1, le=10, description="How specific the problem is (1-10)"
    )

    # Real people validation
    real_people: list[RealPerson] = Field(
        default_factory=list, description="Real people experiencing this problem"
    )
    real_people_count: int = Field(
        default=0, ge=0, description="Number of real people identified"
    )

    # Frequency analysis
    frequency: Literal["daily", "weekly", "monthly", "rarely"] = Field(
        ..., description="How often the problem occurs"
    )
    frequency_analysis: str = Field(
        ..., description="Analysis of problem frequency implications"
    )

    # Alternatives analysis
    current_alternatives: list[str] = Field(
        default_factory=list, description="Current solutions people use"
    )
    alternatives_analysis: str = Field(
        ..., description="Analysis of why current alternatives are insufficient"
    )

    # Tarpit check
    tarpit_check: TarpitAnalysis = Field(
        ..., description="Tarpit pattern analysis"
    )

    # Overall assessment
    overall_score: int = Field(
        ..., ge=1, le=10, description="Overall problem love score (1-10)"
    )
    ai_coaching_notes: list[str] = Field(
        default_factory=list, description="AI coaching suggestions"
    )
    proceed_recommendation: bool = Field(
        ..., description="Whether to proceed with this problem"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: CUSTOMER TRUTH (Interviews)
# Based on Teresa Torres's Continuous Discovery methodology
# ═══════════════════════════════════════════════════════════════════════════════


class Interview(BaseModel):
    """Customer interview data."""

    id: Optional[str] = Field(default=None, description="Unique interview identifier")

    # Interviewee info
    interviewee_name: str = Field(..., description="Name of the person interviewed")
    interviewee_role: str = Field(..., description="Role/title of the interviewee")
    company_type: str = Field(
        ..., description="Type of company (startup, enterprise, etc.)"
    )
    company_size: str = Field(..., description="Size of company (1-10, 11-50, etc.)")
    interview_date: date = Field(..., description="Date of the interview")

    # The story
    story_raw: str = Field(
        ..., description="Raw interview notes/transcript"
    )
    key_quote: str = Field(
        ..., description="Most impactful quote from the interview"
    )

    # Analysis
    struggling_moment: str = Field(
        ..., description="The specific struggling moment identified"
    )
    emotions: list[str] = Field(
        default_factory=list, description="Emotions expressed during the interview"
    )
    current_workaround: str = Field(
        ..., description="How they currently solve/cope with the problem"
    )
    desired_outcome: str = Field(
        ..., description="What success would look like for them"
    )

    # AI-extracted insights
    ai_pain_points: list[str] = Field(
        default_factory=list, description="Pain points extracted by AI"
    )
    ai_triggers: list[str] = Field(
        default_factory=list, description="Trigger events identified by AI"
    )
    ai_goals: list[str] = Field(
        default_factory=list, description="Goals identified by AI"
    )


class Evidence(BaseModel):
    """Evidence linking a pattern to source interviews."""

    interview_id: str = Field(..., description="ID of the source interview")
    quote: str = Field(..., description="Supporting quote")


class PainPattern(BaseModel):
    """A pain pattern identified across interviews."""

    description: str = Field(..., description="Description of the pain pattern")
    frequency: int = Field(
        ..., ge=0, description="Number of interviews mentioning this"
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="Evidence from interviews"
    )
    severity: Severity = Field(..., description="Severity of this pain")


class TriggerPattern(BaseModel):
    """A trigger pattern identified across interviews."""

    description: str = Field(..., description="Description of the trigger")
    frequency: int = Field(
        ..., ge=0, description="Number of interviews mentioning this"
    )
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence")


class OutcomePattern(BaseModel):
    """A desired outcome pattern identified across interviews."""

    description: str = Field(..., description="Description of the desired outcome")
    frequency: int = Field(
        ..., ge=0, description="Number of interviews mentioning this"
    )
    evidence: list[Evidence] = Field(default_factory=list, description="Evidence")


class Contradiction(BaseModel):
    """A contradiction found between interviews."""

    description: str = Field(..., description="Description of the contradiction")
    interview_a: str = Field(..., description="First interview ID")
    interview_b: str = Field(..., description="Second interview ID")
    resolution_suggestion: Optional[str] = Field(
        default=None, description="Suggested resolution"
    )


class PatternSynthesis(BaseModel):
    """Synthesis of patterns across all interviews."""

    pain_patterns: list[PainPattern] = Field(
        default_factory=list, description="Identified pain patterns"
    )
    trigger_patterns: list[TriggerPattern] = Field(
        default_factory=list, description="Identified trigger patterns"
    )
    outcome_patterns: list[OutcomePattern] = Field(
        default_factory=list, description="Identified outcome patterns"
    )
    contradictions: list[Contradiction] = Field(
        default_factory=list, description="Contradictions found"
    )
    interview_gaps: list[str] = Field(
        default_factory=list, description="Areas needing more interview data"
    )
    total_interviews: int = Field(default=0, ge=0, description="Total interviews")
    evidence_quality: EvidenceQuality = Field(
        default=EvidenceQuality.E4, description="Evidence quality tier"
    )


class CustomerTruthOutput(BaseModel):
    """Output from Stage 2: Customer Truth."""

    interviews: list[Interview] = Field(
        default_factory=list, description="All interviews"
    )
    patterns: Optional[PatternSynthesis] = Field(
        default=None, description="Synthesized patterns"
    )
    interview_goal: int = Field(
        default=5, ge=1, description="Target number of interviews"
    )
    interviews_completed: int = Field(
        default=0, ge=0, description="Interviews completed"
    )
    readiness_score: int = Field(
        ..., ge=1, le=10, description="Readiness to proceed score (1-10)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: OPPORTUNITY MAPPING
# Based on Teresa Torres's Opportunity Solution Tree
# ═══════════════════════════════════════════════════════════════════════════════


class Force(BaseModel):
    """A force in the 4 Forces model."""

    items: list[str] = Field(default_factory=list, description="Force items")
    evidence: list[dict[str, Any]] = Field(
        default_factory=list, description="Evidence for each item"
    )
    strength: int = Field(
        ..., ge=1, le=10, description="Strength of this force (1-10)"
    )


class FourForcesModel(BaseModel):
    """The 4 Forces Model (Jobs to be Done)."""

    push: Force = Field(..., description="Push: What's broken/painful")
    pull: Force = Field(..., description="Pull: What's attractive about change")
    anxiety: Force = Field(
        ..., description="Anxiety: What scares them about changing"
    )
    habit: Force = Field(
        ..., description="Habit: What's comfortable about status quo"
    )

    force_balance: int = Field(
        ..., description="Net force: (push + pull) - (anxiety + habit)"
    )
    change_likely: bool = Field(
        ..., description="Whether change is likely given the forces"
    )
    key_insight: str = Field(..., description="Key insight from forces analysis")


class Opportunity(BaseModel):
    """An opportunity in the Opportunity Solution Tree."""

    id: str = Field(..., description="Unique opportunity identifier")
    description: str = Field(..., description="Opportunity description")
    interview_count: int = Field(
        ..., ge=0, description="Number of interviews supporting this"
    )
    evidence: list[dict[str, Any]] = Field(
        default_factory=list, description="Evidence from interviews"
    )
    solutions: list[str] = Field(
        default_factory=list, description="Potential solutions for this opportunity"
    )
    priority: int = Field(..., ge=1, le=5, description="Priority (1 = highest)")


class OpportunitySolutionTree(BaseModel):
    """Opportunity Solution Tree structure."""

    outcome: str = Field(..., description="Desired outcome")
    opportunities: list[Opportunity] = Field(
        default_factory=list, description="Opportunities to achieve outcome"
    )


class OpportunityMappingOutput(BaseModel):
    """Output from Stage 3: Opportunity Mapping."""

    four_forces: FourForcesModel = Field(..., description="4 Forces analysis")
    opportunity_tree: OpportunitySolutionTree = Field(
        ..., description="Opportunity Solution Tree"
    )
    primary_opportunity: str = Field(
        ..., description="Primary opportunity to pursue"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: SOLUTION DESIGN
# ═══════════════════════════════════════════════════════════════════════════════


class DHMScore(BaseModel):
    """Delight, Hard-to-copy, Margin scoring model."""

    delight: int = Field(..., ge=1, le=10, description="Delight score (1-10)")
    delight_reasoning: str = Field(..., description="Why this delights users")

    hard_to_copy: int = Field(
        ..., ge=1, le=10, description="Hard-to-copy score (1-10)"
    )
    hard_to_copy_reasoning: str = Field(
        ..., description="Why this is hard to copy"
    )
    moat_type: Optional[str] = Field(
        default=None, description="Type of competitive moat"
    )

    margin: int = Field(..., ge=1, le=10, description="Margin score (1-10)")
    margin_reasoning: str = Field(..., description="Margin potential reasoning")

    total: int = Field(..., ge=3, le=30, description="Total DHM score")
    passes_threshold: bool = Field(
        ..., description="Whether total >= 20 (threshold for good ideas)"
    )


class PreMortemItem(BaseModel):
    """An item in the pre-mortem analysis."""

    description: str = Field(..., description="What could go wrong")
    mitigation: Optional[str] = Field(
        default=None, description="How to mitigate this risk"
    )
    early_warning: Optional[str] = Field(
        default=None, description="Early warning signs to watch"
    )
    owner: Optional[str] = Field(
        default=None, description="Who should own this risk"
    )


class PreMortem(BaseModel):
    """Pre-mortem analysis."""

    tigers: list[PreMortemItem] = Field(
        default_factory=list, description="Real threats that could kill the product"
    )
    paper_tigers: list[PreMortemItem] = Field(
        default_factory=list, description="Seem scary but probably aren't"
    )
    elephants: list[PreMortemItem] = Field(
        default_factory=list, description="Things no one wants to talk about"
    )


class SolutionDesignOutput(BaseModel):
    """Output from Stage 4: Solution Design."""

    solution_concept: str = Field(..., description="The solution concept")
    solution_description: str = Field(
        ..., description="Detailed solution description"
    )
    key_features: list[str] = Field(
        default_factory=list, description="Key features of the solution"
    )
    dhm_score: DHMScore = Field(..., description="DHM score analysis")
    pre_mortem: PreMortem = Field(..., description="Pre-mortem analysis")
    value_proposition: str = Field(..., description="Clear value proposition")


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: VALIDATION PLAN
# Based on the Validation Ladder
# ═══════════════════════════════════════════════════════════════════════════════


class ValidationExperiment(BaseModel):
    """A validation experiment on the validation ladder."""

    rung: int = Field(..., ge=1, le=5, description="Validation ladder rung (1-5)")
    name: str = Field(..., description="Experiment name")
    hypothesis: str = Field(..., description="What we're testing")
    success_criteria: str = Field(..., description="What counts as success")
    failure_criteria: str = Field(..., description="What counts as failure")
    target_participants: str = Field(..., description="Who to test with")
    method: str = Field(..., description="How to run the experiment")
    timeline: str = Field(..., description="How long this takes")
    status: Literal["todo", "in_progress", "completed", "passed", "failed"] = Field(
        default="todo", description="Current status"
    )


class ValidationPlanOutput(BaseModel):
    """Output from Stage 5: Validation Plan."""

    current_rung: int = Field(
        ..., ge=0, le=5, description="Current rung on the validation ladder"
    )
    experiments: list[ValidationExperiment] = Field(
        default_factory=list, description="Planned experiments"
    )
    next_experiment: Optional[ValidationExperiment] = Field(
        default=None, description="Next experiment to run"
    )
    validation_summary: str = Field(
        ..., description="Summary of validation approach"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════


class StageState(BaseModel):
    """State of a single discovery stage."""

    status: StageStatus = Field(
        default=StageStatus.NOT_STARTED, description="Stage status"
    )
    output: Optional[dict[str, Any]] = Field(
        default=None, description="Stage output data"
    )
    output_source: Literal["ai_generated", "user_edited", "user_created"] = Field(
        default="ai_generated", description="Source of the output"
    )
    user_notes: Optional[str] = Field(
        default=None, description="User's notes for this stage"
    )
    coaching_messages: list[str] = Field(
        default_factory=list, description="AI coaching messages"
    )
    score: Optional[int] = Field(
        default=None, ge=1, le=10, description="Stage quality score"
    )
    started_at: Optional[str] = Field(
        default=None, description="When the stage started"
    )
    completed_at: Optional[str] = Field(
        default=None, description="When the stage completed"
    )
    approved_at: Optional[str] = Field(
        default=None, description="When the stage was approved"
    )
    # Error tracking for stuck stage detection
    error_message: Optional[str] = Field(
        default=None, description="Error message if stage failed"
    )
    last_error_at: Optional[str] = Field(
        default=None, description="When the last error occurred"
    )


class DiscoverySessionV4(BaseModel):
    """V4 Discovery session state."""

    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="Owner user ID")
    mode: DiscoveryMode = Field(..., description="Discovery mode")

    # Inputs
    product_idea: str = Field(..., description="The product idea")
    industry: Optional[str] = Field(default=None, description="Industry context")
    target_market: Optional[str] = Field(
        default=None, description="Target market"
    )

    # Stage states
    stages: dict[str, StageState] = Field(
        default_factory=lambda: {
            "problem_love": StageState(),
            "customer_truth": StageState(),
            "opportunity_mapping": StageState(),
            "solution_design": StageState(),
            "validation_plan": StageState(),
        },
        description="State of each stage",
    )

    # Cross-stage data
    interviews: list[Interview] = Field(
        default_factory=list, description="All interviews"
    )
    patterns: Optional[PatternSynthesis] = Field(
        default=None, description="Synthesized patterns"
    )
    four_forces: Optional[FourForcesModel] = Field(
        default=None, description="4 Forces analysis"
    )
    opportunity_tree: Optional[OpportunitySolutionTree] = Field(
        default=None, description="Opportunity Solution Tree"
    )

    # Quality tracking
    overall_evidence_quality: EvidenceQuality = Field(
        default=EvidenceQuality.E4, description="Overall evidence quality"
    )
    quality_score: int = Field(
        default=0, ge=0, le=100, description="Overall quality score"
    )

    # Metadata
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        use_enum_values = True


# ═══════════════════════════════════════════════════════════════════════════════
# API REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class CreateDiscoverySessionV4Request(BaseModel):
    """Request to create a V4 discovery session."""

    product_idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The product idea to analyze",
    )
    mode: DiscoveryMode = Field(
        default=DiscoveryMode.GUIDED,
        description="Discovery mode to use",
    )
    industry: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Industry context",
    )
    target_market: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Target market or customer segment",
    )


class CreateDiscoverySessionV4Response(BaseModel):
    """Response after creating a V4 discovery session."""

    session_id: str = Field(..., description="Unique session identifier")
    mode: DiscoveryMode = Field(..., description="Discovery mode")
    status: str = Field(default="created", description="Session status")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionStatusV4Response(BaseModel):
    """V4 session status response."""

    session_id: str = Field(..., description="Session identifier")
    mode: DiscoveryMode = Field(..., description="Discovery mode")
    current_stage: Optional[str] = Field(
        default=None, description="Currently active stage"
    )
    stages: dict[str, dict[str, Any]] = Field(
        ..., description="Status of each stage"
    )
    overall_progress: int = Field(
        ..., ge=0, le=100, description="Overall progress percentage"
    )
    evidence_quality: EvidenceQuality = Field(
        ..., description="Evidence quality tier"
    )
    quality_score: int = Field(..., ge=0, le=100, description="Quality score")


class RunStageRequest(BaseModel):
    """Request to run a specific stage."""

    force_regenerate: bool = Field(
        default=False,
        description="Force regeneration even if stage is complete",
    )
    user_context: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional user context for the stage",
    )


class AIAssistanceRequest(BaseModel):
    """Request for AI assistance within a stage."""

    assistance_type: Literal["coaching", "synthesis", "suggestions", "tarpit_check"] = Field(
        ..., description="Type of assistance needed"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context for the assistance",
    )


class SaveStageOutputRequest(BaseModel):
    """Request to save user's edits to a stage output."""

    output: dict[str, Any] = Field(..., description="The stage output to save")
    source: Literal["user_edited", "user_created"] = Field(
        default="user_edited",
        description="Source of the output",
    )
    notes: Optional[str] = Field(
        default=None,
        description="User notes about the changes",
    )
