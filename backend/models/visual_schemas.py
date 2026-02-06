"""
Visual data schemas for rich output in inception packs.

This module defines Pydantic models for structured visual data that can be
rendered as charts, diagrams, and interactive visualizations in the frontend.

These schemas support:
- Competitive positioning quadrants
- Financial projections (revenue, costs, MRR)
- Lean Canvas visualizations
- Key decision frameworks
"""

from typing import Optional
from pydantic import BaseModel, Field


# =====================================================================
# COMPETITIVE POSITIONING
# =====================================================================


class CompetitorPosition(BaseModel):
    """A competitor's position on a 2D competitive map."""

    name: str = Field(..., description="Competitor name")
    x_score: float = Field(
        ..., ge=0.0, le=10.0, description="Position on X-axis (0-10)"
    )
    y_score: float = Field(
        ..., ge=0.0, le=10.0, description="Position on Y-axis (0-10)"
    )
    description: str = Field(..., description="Brief description of positioning")
    market_share: Optional[str] = Field(
        default=None, description="Estimated market share if known"
    )
    funding: Optional[str] = Field(
        default=None, description="Funding raised if known"
    )
    is_target_product: bool = Field(
        default=False, description="True if this represents our product"
    )


class CompetitivePositioning(BaseModel):
    """
    Competitive positioning data for a quadrant visualization.

    The axes can represent any strategic dimensions:
    - Price vs Features
    - Enterprise vs Consumer focus
    - Innovation vs Stability
    - etc.
    """

    competitors: list[CompetitorPosition] = Field(
        ..., min_length=2, description="List of competitors with positions"
    )
    x_axis_label: str = Field(..., description="Label for X-axis (e.g., 'Price')")
    y_axis_label: str = Field(
        ..., description="Label for Y-axis (e.g., 'Feature Completeness')"
    )
    x_axis_low: str = Field(
        default="Low", description="Label for low end of X-axis"
    )
    x_axis_high: str = Field(
        default="High", description="Label for high end of X-axis"
    )
    y_axis_low: str = Field(
        default="Low", description="Label for low end of Y-axis"
    )
    y_axis_high: str = Field(
        default="High", description="Label for high end of Y-axis"
    )
    insight: Optional[str] = Field(
        default=None,
        description="Key insight from the competitive positioning analysis",
    )


# =====================================================================
# FINANCIAL PROJECTIONS
# =====================================================================


class MonthlyProjection(BaseModel):
    """Financial data for a single month."""

    month: int = Field(..., ge=1, le=36, description="Month number (1-36)")
    revenue: float = Field(..., ge=0, description="Monthly revenue in dollars")
    costs: float = Field(..., ge=0, description="Monthly costs in dollars")
    profit: float = Field(..., description="Monthly profit (revenue - costs)")
    users: int = Field(..., ge=0, description="Active users at end of month")
    mrr: float = Field(..., ge=0, description="Monthly Recurring Revenue")
    arr: Optional[float] = Field(
        default=None, description="Annual Recurring Revenue (MRR * 12)"
    )


class FinancialProjection(BaseModel):
    """
    Financial projections for visualization.

    Supports time-series data for revenue, costs, users, and MRR
    that can be rendered as line charts, area charts, or tables.
    """

    monthly_data: list[MonthlyProjection] = Field(
        ..., min_length=1, description="Monthly projection data"
    )
    break_even_month: Optional[int] = Field(
        default=None, description="Month when profit first turns positive"
    )
    year_1_revenue: str = Field(..., description="Total Year 1 revenue")
    year_1_costs: str = Field(..., description="Total Year 1 costs")
    year_1_profit: str = Field(..., description="Year 1 profit/loss")
    year_3_revenue: Optional[str] = Field(
        default=None, description="Projected Year 3 revenue"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Key assumptions behind projections"
    )
    sensitivity_notes: Optional[str] = Field(
        default=None, description="Notes on projection sensitivity"
    )


# =====================================================================
# LEAN CANVAS VISUAL
# =====================================================================


class LeanCanvasVisual(BaseModel):
    """
    Lean Canvas data structured for visual rendering.

    Each section is limited to encourage concise, actionable content
    that fits well in a visual canvas layout.
    """

    problem: list[str] = Field(
        ..., min_length=1, max_length=3, description="Top 3 problems"
    )
    solution: list[str] = Field(
        ..., min_length=1, max_length=3, description="Top 3 solutions"
    )
    key_metrics: list[str] = Field(
        ..., min_length=1, max_length=5, description="Key metrics to track"
    )
    unique_value_proposition: str = Field(
        ..., max_length=200, description="Single compelling value statement"
    )
    unfair_advantage: str = Field(
        ..., max_length=150, description="What cannot be easily copied"
    )
    channels: list[str] = Field(
        ..., min_length=1, max_length=4, description="Customer acquisition channels"
    )
    customer_segments: list[str] = Field(
        ..., min_length=1, max_length=3, description="Target customer segments"
    )
    cost_structure: list[str] = Field(
        ..., min_length=1, max_length=4, description="Main cost categories"
    )
    revenue_streams: list[str] = Field(
        ..., min_length=1, max_length=3, description="Revenue model components"
    )


# =====================================================================
# KEY DECISIONS FRAMEWORK
# =====================================================================


class DecisionOption(BaseModel):
    """An option within a key decision."""

    name: str = Field(..., description="Option name")
    description: str = Field(..., description="Brief description of this option")
    pros: list[str] = Field(..., min_length=1, description="Advantages of this option")
    cons: list[str] = Field(..., min_length=1, description="Disadvantages of this option")
    estimated_cost: Optional[str] = Field(
        default=None, description="Cost estimate if applicable"
    )
    estimated_timeline: Optional[str] = Field(
        default=None, description="Timeline estimate if applicable"
    )


class KeyDecision(BaseModel):
    """
    A key decision that stakeholders need to make.

    Extracted from the analysis to highlight critical go/no-go
    points and strategic choices.
    """

    id: str = Field(..., pattern=r"^DEC-\d{3}$", description="Decision ID (e.g., DEC-001)")
    title: str = Field(..., max_length=100, description="Decision title")
    context: str = Field(..., description="Why this decision matters")
    category: str = Field(
        ...,
        description="Category: strategy, technology, legal, financial, go-to-market",
    )
    options: list[DecisionOption] = Field(
        ..., min_length=2, max_length=4, description="Available options"
    )
    recommendation: str = Field(
        ..., description="Recommended option with brief rationale"
    )
    confidence: str = Field(
        ..., description="Confidence level: high, medium, low"
    )
    impact_if_delayed: str = Field(
        ..., description="Consequence of not deciding soon"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Other decisions this depends on"
    )


class KeyDecisions(BaseModel):
    """Collection of key decisions for executive review."""

    decisions: list[KeyDecision] = Field(
        ..., min_length=1, max_length=7, description="Key decisions requiring attention"
    )
    summary: str = Field(
        ..., description="Brief summary of the decision landscape"
    )
    most_critical: str = Field(
        ..., description="ID of the most critical decision to address first"
    )


# =====================================================================
# RISK MATRIX
# =====================================================================


class RiskMatrixItem(BaseModel):
    """A risk positioned on likelihood/impact matrix."""

    id: str = Field(..., description="Risk identifier")
    name: str = Field(..., description="Risk name")
    description: str = Field(..., description="Risk description")
    likelihood: int = Field(
        ..., ge=1, le=5, description="Likelihood score (1-5)"
    )
    impact: int = Field(..., ge=1, le=5, description="Impact score (1-5)")
    risk_score: int = Field(
        ..., ge=1, le=25, description="Combined score (likelihood * impact)"
    )
    category: str = Field(
        ..., description="Category: market, technical, legal, financial, operational"
    )
    mitigation: str = Field(..., description="Mitigation strategy")
    owner: Optional[str] = Field(
        default=None, description="Who owns mitigating this risk"
    )


class RiskMatrix(BaseModel):
    """Risk matrix data for visualization."""

    risks: list[RiskMatrixItem] = Field(
        ..., min_length=1, description="Risks positioned on the matrix"
    )
    high_priority_count: int = Field(
        ..., ge=0, description="Count of high-priority risks (score >= 15)"
    )
    overall_risk_level: str = Field(
        ..., description="Overall risk level: low, medium, high, critical"
    )


# =====================================================================
# TIMELINE / ROADMAP
# =====================================================================


class MilestoneItem(BaseModel):
    """A milestone on the product roadmap."""

    id: str = Field(..., description="Milestone ID")
    title: str = Field(..., description="Milestone title")
    description: str = Field(..., description="What this milestone achieves")
    target_date: str = Field(
        ..., description="Target completion (e.g., 'Q1 2025', 'Month 3')"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Milestone IDs this depends on"
    )
    category: str = Field(
        ..., description="Category: development, marketing, legal, operations"
    )
    status: str = Field(
        default="planned", description="Status: planned, in_progress, completed, at_risk"
    )


class ProductRoadmap(BaseModel):
    """Product roadmap for Gantt-style visualization."""

    milestones: list[MilestoneItem] = Field(
        ..., min_length=1, description="Roadmap milestones"
    )
    phases: list[dict[str, str]] = Field(
        ...,
        min_length=1,
        description="Phase definitions with name, start, end",
    )
    critical_path: list[str] = Field(
        default_factory=list, description="Milestone IDs on the critical path"
    )
