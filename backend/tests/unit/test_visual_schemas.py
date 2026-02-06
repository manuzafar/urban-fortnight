"""
Tests for visual data schemas.
"""

import pytest
from pydantic import ValidationError

from models.visual_schemas import (
    CompetitorPosition,
    CompetitivePositioning,
    MonthlyProjection,
    FinancialProjection,
    LeanCanvasVisual,
    DecisionOption,
    KeyDecision,
    KeyDecisions,
    RiskMatrixItem,
    RiskMatrix,
    MilestoneItem,
    ProductRoadmap,
)


class TestCompetitivePositioning:
    """Tests for competitive positioning schemas."""

    def test_valid_competitor_position(self):
        """Should create valid competitor position."""
        pos = CompetitorPosition(
            name="Slack",
            x_score=7.5,
            y_score=8.0,
            description="Enterprise messaging leader",
            is_target_product=False,
        )

        assert pos.name == "Slack"
        assert pos.x_score == 7.5
        assert pos.y_score == 8.0

    def test_competitor_position_score_bounds(self):
        """Scores should be bounded 0-10."""
        with pytest.raises(ValidationError):
            CompetitorPosition(
                name="Test",
                x_score=15.0,  # Invalid - over 10
                y_score=5.0,
                description="Test",
            )

    def test_valid_competitive_positioning(self):
        """Should create valid competitive positioning."""
        positioning = CompetitivePositioning(
            competitors=[
                CompetitorPosition(
                    name="Slack", x_score=7.0, y_score=8.0, description="Leader"
                ),
                CompetitorPosition(
                    name="Teams", x_score=6.0, y_score=7.0, description="Challenger"
                ),
            ],
            x_axis_label="Price",
            y_axis_label="Features",
        )

        assert len(positioning.competitors) == 2
        assert positioning.x_axis_label == "Price"

    def test_competitive_positioning_requires_min_competitors(self):
        """Should require at least 2 competitors."""
        with pytest.raises(ValidationError):
            CompetitivePositioning(
                competitors=[
                    CompetitorPosition(
                        name="Only One", x_score=5.0, y_score=5.0, description="Test"
                    )
                ],
                x_axis_label="Price",
                y_axis_label="Features",
            )


class TestFinancialProjection:
    """Tests for financial projection schemas."""

    def test_valid_monthly_projection(self):
        """Should create valid monthly projection."""
        proj = MonthlyProjection(
            month=1,
            revenue=10000.0,
            costs=8000.0,
            profit=2000.0,
            users=100,
            mrr=10000.0,
        )

        assert proj.month == 1
        assert proj.profit == 2000.0

    def test_monthly_projection_month_bounds(self):
        """Month should be bounded 1-36."""
        with pytest.raises(ValidationError):
            MonthlyProjection(
                month=0,  # Invalid
                revenue=0,
                costs=0,
                profit=0,
                users=0,
                mrr=0,
            )

    def test_valid_financial_projection(self):
        """Should create valid financial projection."""
        proj = FinancialProjection(
            monthly_data=[
                MonthlyProjection(
                    month=1,
                    revenue=10000,
                    costs=8000,
                    profit=2000,
                    users=100,
                    mrr=10000,
                )
            ],
            year_1_revenue="$120,000",
            year_1_costs="$96,000",
            year_1_profit="$24,000",
            break_even_month=6,
        )

        assert proj.break_even_month == 6
        assert len(proj.monthly_data) == 1


class TestLeanCanvasVisual:
    """Tests for Lean Canvas visual schema."""

    def test_valid_lean_canvas(self):
        """Should create valid lean canvas."""
        canvas = LeanCanvasVisual(
            problem=["Problem 1", "Problem 2"],
            solution=["Solution 1"],
            key_metrics=["DAU", "Retention"],
            unique_value_proposition="The only tool that...",
            unfair_advantage="Proprietary AI",
            channels=["Direct sales", "SEO"],
            customer_segments=["SMBs"],
            cost_structure=["Hosting", "Salaries"],
            revenue_streams=["Subscriptions"],
        )

        assert len(canvas.problem) == 2
        assert canvas.unfair_advantage == "Proprietary AI"

    def test_lean_canvas_max_problems(self):
        """Should limit problems to 3."""
        with pytest.raises(ValidationError):
            LeanCanvasVisual(
                problem=["P1", "P2", "P3", "P4"],  # Too many
                solution=["S1"],
                key_metrics=["M1"],
                unique_value_proposition="UVP",
                unfair_advantage="UA",
                channels=["C1"],
                customer_segments=["CS1"],
                cost_structure=["Cost1"],
                revenue_streams=["Rev1"],
            )


class TestKeyDecisions:
    """Tests for key decision schemas."""

    def test_valid_decision_option(self):
        """Should create valid decision option."""
        option = DecisionOption(
            name="Option A",
            description="First option",
            pros=["Fast", "Cheap"],
            cons=["Limited features"],
        )

        assert option.name == "Option A"
        assert len(option.pros) == 2

    def test_valid_key_decision(self):
        """Should create valid key decision."""
        decision = KeyDecision(
            id="DEC-001",
            title="Pricing Model",
            context="Need to decide on pricing",
            category="strategy",
            options=[
                DecisionOption(
                    name="Freemium",
                    description="Free tier with paid upgrades",
                    pros=["Growth"],
                    cons=["Revenue delay"],
                ),
                DecisionOption(
                    name="Paid only",
                    description="No free tier",
                    pros=["Revenue"],
                    cons=["Slow growth"],
                ),
            ],
            recommendation="Freemium for market entry",
            confidence="high",
            impact_if_delayed="Blocks launch",
        )

        assert decision.id == "DEC-001"
        assert len(decision.options) == 2

    def test_key_decision_id_format(self):
        """Decision ID should match pattern DEC-XXX."""
        with pytest.raises(ValidationError):
            KeyDecision(
                id="INVALID",  # Wrong format
                title="Test",
                context="Test",
                category="strategy",
                options=[
                    DecisionOption(
                        name="A", description="A", pros=["a"], cons=["b"]
                    ),
                    DecisionOption(
                        name="B", description="B", pros=["a"], cons=["b"]
                    ),
                ],
                recommendation="A",
                confidence="high",
                impact_if_delayed="Test",
            )


class TestRiskMatrix:
    """Tests for risk matrix schemas."""

    def test_valid_risk_matrix_item(self):
        """Should create valid risk matrix item."""
        risk = RiskMatrixItem(
            id="RISK-001",
            name="Market Risk",
            description="Market may not adopt",
            likelihood=3,
            impact=4,
            risk_score=12,
            category="market",
            mitigation="Early customer validation",
        )

        assert risk.likelihood == 3
        assert risk.impact == 4
        assert risk.risk_score == 12

    def test_risk_likelihood_bounds(self):
        """Likelihood should be 1-5."""
        with pytest.raises(ValidationError):
            RiskMatrixItem(
                id="R1",
                name="Test",
                description="Test",
                likelihood=6,  # Invalid
                impact=3,
                risk_score=18,
                category="market",
                mitigation="Test",
            )

    def test_valid_risk_matrix(self):
        """Should create valid risk matrix."""
        matrix = RiskMatrix(
            risks=[
                RiskMatrixItem(
                    id="R1",
                    name="Risk 1",
                    description="Desc",
                    likelihood=4,
                    impact=4,
                    risk_score=16,
                    category="market",
                    mitigation="Mit",
                )
            ],
            high_priority_count=1,
            overall_risk_level="high",
        )

        assert matrix.high_priority_count == 1


class TestProductRoadmap:
    """Tests for product roadmap schemas."""

    def test_valid_milestone(self):
        """Should create valid milestone."""
        milestone = MilestoneItem(
            id="M1",
            title="MVP Launch",
            description="Launch minimum viable product",
            target_date="Q1 2025",
            category="development",
        )

        assert milestone.title == "MVP Launch"
        assert milestone.status == "planned"

    def test_valid_roadmap(self):
        """Should create valid roadmap."""
        roadmap = ProductRoadmap(
            milestones=[
                MilestoneItem(
                    id="M1",
                    title="MVP",
                    description="MVP launch",
                    target_date="Q1 2025",
                    category="development",
                )
            ],
            phases=[{"name": "Phase 1", "start": "Jan 2025", "end": "Mar 2025"}],
        )

        assert len(roadmap.milestones) == 1
        assert len(roadmap.phases) == 1
