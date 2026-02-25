"""
Tests for Discovery V4 Stages.

This module tests the V4 Discovery system including:
- Individual stage execution (problem_love, customer_truth, opportunity_mapping, solution_design, validation_plan)
- Stage state transitions
- Output schema validation
- Error handling
- Reflection loop behavior
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.discovery_v4.engine import DiscoveryEngineV4
from agents.discovery_v4.stages.problem_love import ProblemLoveStage
from agents.discovery_v4.stages.customer_truth import CustomerTruthStage
from agents.discovery_v4.stages.opportunity_mapping import OpportunityMappingStage
from agents.discovery_v4.stages.solution_design import SolutionDesignStage
from agents.discovery_v4.stages.validation_plan import ValidationPlanStage
from models.discovery_v4_schemas import (
    CustomerTruthOutput,
    DiscoveryMode,
    DiscoverySessionV4,
    EvidenceQuality,
    Interview,
    OpportunityMappingOutput,
    PatternSynthesis,
    ProblemLoveOutput,
    RealPerson,
    SolutionDesignOutput,
    StageState,
    StageStatus,
    TarpitAnalysis,
    ValidationPlanOutput,
)


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_session():
    """Create a mock V4 discovery session."""
    return DiscoverySessionV4(
        session_id="test-session-123",
        user_id="test-user-456",
        mode=DiscoveryMode.QUICK,
        product_idea="AI-powered task management for remote teams",
        industry="SaaS",
        target_market="Remote teams of 5-50 people",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )


@pytest.fixture
def mock_session_with_interviews():
    """Create a mock session with interviews."""
    session = DiscoverySessionV4(
        session_id="test-session-123",
        user_id="test-user-456",
        mode=DiscoveryMode.GUIDED,
        product_idea="AI-powered task management for remote teams",
        industry="SaaS",
        target_market="Remote teams of 5-50 people",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )

    # Add mock interviews
    session.interviews = [
        Interview(
            id="int-1",
            interviewee_name="John Doe",
            interviewee_role="Engineering Manager",
            company_type="Startup",
            company_size="11-50",
            interview_date=date.today(),
            story_raw="We struggle to keep track of tasks across our distributed team",
            key_quote="It's chaos trying to coordinate work across time zones",
            struggling_moment="Last week our sprint planning took 3 hours",
            emotions=["frustrated", "overwhelmed"],
            current_workaround="Using Slack + Google Sheets + Jira",
            desired_outcome="One place to see all team work",
            ai_pain_points=["Coordination overhead", "Tool sprawl"],
            ai_triggers=["Sprint planning", "Daily standups"],
            ai_goals=["Visibility", "Coordination"],
        ),
        Interview(
            id="int-2",
            interviewee_name="Jane Smith",
            interviewee_role="Product Manager",
            company_type="Startup",
            company_size="11-50",
            interview_date=date.today(),
            story_raw="We lose context switching between tools",
            key_quote="I spend more time updating tools than building product",
            struggling_moment="Missing a critical deadline because task was buried in Slack",
            emotions=["stressed", "anxious"],
            current_workaround="Manual daily updates in multiple tools",
            desired_outcome="Automated task tracking",
            ai_pain_points=["Context switching", "Manual updates"],
            ai_triggers=["Status updates", "Sprint reviews"],
            ai_goals=["Automation", "Context retention"],
        ),
    ]

    return session


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 1: PROBLEM LOVE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestProblemLoveStage:
    """Tests for Problem Love stage."""

    @pytest.mark.asyncio
    async def test_problem_love_generates_output(self, mock_session):
        """Should generate problem love analysis."""
        stage = ProblemLoveStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "problem_statement": "Remote teams struggle to coordinate work across time zones",
                "specificity_score": 8,
                "real_people": [
                    {
                        "name": "Alice",
                        "struggling_moment": "Missed deadline due to timezone confusion",
                    }
                ],
                "frequency": "daily",
                "frequency_analysis": "Happens during every standup and sprint planning",
                "current_alternatives": ["Slack", "Jira", "Email"],
                "alternatives_analysis": "Current tools are fragmented and require manual coordination",
                "tarpit_check": {
                    "is_tarpit": False,
                    "similarity_score": 0.3,
                    "similar_to": [],
                    "specific_concerns": [],
                },
                "overall_score": 8,
                "ai_coaching_notes": ["Strong problem validation"],
                "proceed_recommendation": True,
            },
        }

        mock_critique = {
            "overall_score": 8.0,
            "passes_threshold": True,
            "feedback": [],
        }

        with patch("agents.discovery_v4.stages.problem_love.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.problem_love.critique_stage_output", return_value=mock_critique):
                context = {
                    "product_idea": mock_session.product_idea,
                    "mode": "quick",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, ProblemLoveOutput)
                assert output.problem_statement == "Remote teams struggle to coordinate work across time zones"
                assert output.specificity_score == 8
                assert output.frequency == "daily"
                assert output.overall_score == 8
                assert output.proceed_recommendation is True

    @pytest.mark.asyncio
    async def test_problem_love_handles_llm_failure(self, mock_session):
        """Should handle LLM failure gracefully."""
        stage = ProblemLoveStage()

        mock_llm_response = {
            "success": False,
            "error": "API timeout",
        }

        with patch("agents.discovery_v4.stages.problem_love.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.problem_love.critique_stage_output", return_value={"overall_score": 1, "passes_threshold": False, "feedback": []}):
                context = {
                    "product_idea": mock_session.product_idea,
                    "mode": "quick",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, ProblemLoveOutput)
                assert output.specificity_score == 1
                assert output.overall_score == 1
                assert output.proceed_recommendation is False
                assert len(output.ai_coaching_notes) > 0

    @pytest.mark.asyncio
    async def test_problem_love_normalizes_frequency(self, mock_session):
        """Should normalize frequency values to valid enum."""
        stage = ProblemLoveStage()

        # Test various frequency formats
        test_cases = [
            ("DAILY", "daily"),
            ("every day", "daily"),
            ("Weekly basis", "weekly"),
            ("once a month", "monthly"),
            ("rarely happens", "rarely"),
            ("unknown", "weekly"),  # Default
        ]

        for raw_freq, expected_freq in test_cases:
            normalized = stage._normalize_frequency(raw_freq)
            assert normalized == expected_freq

    @pytest.mark.asyncio
    async def test_problem_love_reflection_loop(self, mock_session):
        """Should iterate through reflection loop until quality threshold met."""
        stage = ProblemLoveStage()

        # First iteration returns low score, second returns high score
        mock_llm_calls = 0

        def mock_llm_side_effect(*args, **kwargs):
            nonlocal mock_llm_calls
            mock_llm_calls += 1
            return {
                "success": True,
                "data": {
                    "problem_statement": "Remote teams struggle",
                    "specificity_score": 6,
                    "real_people": [],
                    "frequency": "daily",
                    "frequency_analysis": "Often",
                    "current_alternatives": ["Slack"],
                    "alternatives_analysis": "Not ideal",
                    "tarpit_check": {
                        "is_tarpit": False,
                        "similarity_score": 0.2,
                        "similar_to": [],
                        "specific_concerns": [],
                    },
                    "overall_score": 6 + mock_llm_calls,  # Increases each iteration
                    "ai_coaching_notes": [],
                    "proceed_recommendation": True,
                },
            }

        mock_critique_calls = 0

        def mock_critique_side_effect(*args, **kwargs):
            nonlocal mock_critique_calls
            mock_critique_calls += 1
            # First critique fails, second passes
            return {
                "overall_score": 6.0 if mock_critique_calls == 1 else 8.0,
                "passes_threshold": mock_critique_calls > 1,
                "feedback": ["Needs more specificity"],
                "suggested_improvements": {},
            }

        with patch("agents.discovery_v4.stages.problem_love.call_llm", side_effect=mock_llm_side_effect):
            with patch("agents.discovery_v4.stages.problem_love.critique_stage_output", side_effect=mock_critique_side_effect):
                context = {"product_idea": mock_session.product_idea, "mode": "quick"}
                output = await stage.run(mock_session, context)

                # Should have made 2 LLM calls (initial + 1 refinement)
                assert mock_llm_calls == 2
                assert mock_critique_calls == 2
                assert output.overall_score >= 7  # Should meet threshold

    @pytest.mark.asyncio
    async def test_tarpit_check(self):
        """Should check if idea is a tarpit."""
        stage = ProblemLoveStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "is_tarpit": True,
                "similarity_score": 0.8,
                "similar_to": ["TaskRabbit clone", "Uber for X"],
                "specific_concerns": ["Crowded market", "High CAC"],
            },
        }

        with patch("agents.discovery_v4.stages.problem_love.call_llm", return_value=mock_llm_response):
            result = await stage.check_tarpit("On-demand task marketplace")

            assert isinstance(result, TarpitAnalysis)
            assert result.is_tarpit is True
            assert result.similarity_score == 0.8
            assert "TaskRabbit clone" in result.similar_to


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 2: CUSTOMER TRUTH TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestCustomerTruthStage:
    """Tests for Customer Truth stage."""

    @pytest.mark.asyncio
    async def test_customer_truth_synthesizes_interviews(self, mock_session_with_interviews):
        """Should synthesize patterns from real interviews."""
        stage = CustomerTruthStage()

        mock_patterns_response = {
            "success": True,
            "data": {
                "pain_patterns": [
                    {
                        "description": "Coordination overhead across time zones",
                        "frequency": 2,
                        "evidence": [{"interview_id": "int-1", "quote": "chaos"}],
                        "severity": "high",
                    }
                ],
                "trigger_patterns": [
                    {
                        "description": "Sprint planning meetings",
                        "frequency": 2,
                        "evidence": [{"interview_id": "int-1", "quote": "3 hours"}],
                    }
                ],
                "outcome_patterns": [
                    {
                        "description": "Unified visibility",
                        "frequency": 2,
                        "evidence": [{"interview_id": "int-1", "quote": "one place"}],
                    }
                ],
                "contradictions": [],
                "interview_gaps": ["Need more enterprise users"],
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_patterns_response):
            context = {
                "product_idea": mock_session_with_interviews.product_idea,
                "mode": "guided",
            }

            output = await stage.run(mock_session_with_interviews, context)

            assert isinstance(output, CustomerTruthOutput)
            assert len(output.interviews) == 2
            assert output.patterns is not None
            assert len(output.patterns.pain_patterns) > 0
            assert output.readiness_score > 0

    @pytest.mark.asyncio
    async def test_customer_truth_generates_hypothetical_for_quick_mode(self, mock_session):
        """Should generate hypothetical insights for Quick mode."""
        stage = CustomerTruthStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "interviews": [],
                "patterns": {
                    "pain_patterns": [
                        {
                            "description": "Tool sprawl",
                            "frequency": 1,
                            "evidence": [],
                            "severity": "medium",
                        }
                    ],
                    "trigger_patterns": [],
                    "outcome_patterns": [],
                    "contradictions": [],
                    "interview_gaps": [],
                },
                "readiness_score": 4,
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.mini_critique.critique_stage_output") as mock_critique:
                mock_critique.return_value = {
                    "overall_score": 7.0,
                    "passes_threshold": True,
                    "feedback": [],
                }

                context = {
                    "product_idea": mock_session.product_idea,
                    "mode": "quick",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, CustomerTruthOutput)
                assert output.readiness_score >= 4

    @pytest.mark.asyncio
    async def test_customer_truth_deep_mode_requires_interviews(self, mock_session):
        """Deep mode should require real interviews."""
        stage = CustomerTruthStage()

        # Set to deep mode with no interviews
        mock_session.mode = DiscoveryMode.DEEP

        context = {
            "product_idea": mock_session.product_idea,
            "mode": "deep",
        }

        output = await stage.run(mock_session, context)

        assert isinstance(output, CustomerTruthOutput)
        assert output.readiness_score == 1
        assert output.interviews_completed == 0

    @pytest.mark.asyncio
    async def test_synthesize_patterns(self, mock_session_with_interviews):
        """Should synthesize patterns from interviews."""
        stage = CustomerTruthStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "pain_patterns": [
                    {
                        "description": "Coordination overhead",
                        "frequency": 2,
                        "evidence": [{"interview_id": "int-1", "quote": "chaos"}],
                        "severity": "high",
                    }
                ],
                "trigger_patterns": [],
                "outcome_patterns": [],
                "contradictions": [],
                "interview_gaps": [],
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            patterns = await stage.synthesize_patterns(mock_session_with_interviews.interviews)

            assert isinstance(patterns, PatternSynthesis)
            assert len(patterns.pain_patterns) > 0
            assert patterns.total_interviews == 2
            assert patterns.evidence_quality in [EvidenceQuality.E2, EvidenceQuality.E3]

    @pytest.mark.asyncio
    async def test_generate_interview_guide(self):
        """Should generate interview guide."""
        stage = CustomerTruthStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "interview_goal": "Understand coordination pain",
                "opening_script": "Thank you for your time...",
                "story_prompt": "Tell me about the last time...",
                "follow_up_questions": ["What happened?", "How did it feel?"],
                "deep_dive_areas": [],
                "things_to_listen_for": ["Emotional language"],
                "closing_script": "Thank you",
                "referral_ask": "Know anyone else?",
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            context = {"problem_statement": "Remote team coordination"}
            guide = await stage.generate_interview_guide(context)

            assert "interview_goal" in guide
            assert "story_prompt" in guide


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 3: OPPORTUNITY MAPPING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestOpportunityMappingStage:
    """Tests for Opportunity Mapping stage."""

    @pytest.mark.asyncio
    async def test_opportunity_mapping_generates_output(self, mock_session):
        """Should generate opportunity mapping with 4 Forces and Opportunity Tree."""
        stage = OpportunityMappingStage()

        mock_four_forces_response = {
            "success": True,
            "data": {
                "push": {"items": ["Manual coordination pain"], "evidence": [], "strength": 8},
                "pull": {"items": ["Automated workflow"], "evidence": [], "strength": 7},
                "anxiety": {"items": ["Learning curve"], "evidence": [], "strength": 4},
                "habit": {"items": ["Current tools"], "evidence": [], "strength": 5},
                "force_balance": 6,
                "change_likely": True,
                "key_insight": "Strong push from coordination pain",
            },
        }

        mock_opportunity_tree_response = {
            "success": True,
            "data": {
                "outcome": "Help teams coordinate better",
                "opportunities": [
                    {
                        "id": "opp-1",
                        "description": "Reduce coordination overhead",
                        "interview_count": 2,
                        "evidence": [],
                        "solutions": ["Automated task routing"],
                        "priority": 1,
                    }
                ],
            },
        }

        call_count = 0

        def mock_llm_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # First call for 4 forces, second for opportunity tree
            if call_count == 1:
                return mock_four_forces_response
            return mock_opportunity_tree_response

        with patch("agents.base_agent.call_llm", side_effect=mock_llm_side_effect):
            with patch("agents.discovery_v4.stages.mini_critique.critique_stage_output") as mock_critique:
                mock_critique.return_value = {
                    "overall_score": 8.0,
                    "passes_threshold": True,
                    "feedback": [],
                }

                context = {
                    "product_idea": mock_session.product_idea,
                    "problem_statement": "Remote teams struggle with coordination",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, OpportunityMappingOutput)
                assert output.four_forces is not None
                assert output.four_forces.change_likely is True
                assert output.opportunity_tree is not None
                assert len(output.opportunity_tree.opportunities) > 0
                assert output.primary_opportunity is not None

    @pytest.mark.asyncio
    async def test_four_forces_analysis(self, mock_session):
        """Should analyze 4 Forces Model."""
        stage = OpportunityMappingStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "push": {"items": ["Pain A"], "evidence": [], "strength": 7},
                "pull": {"items": ["Benefit B"], "evidence": [], "strength": 6},
                "anxiety": {"items": ["Fear C"], "evidence": [], "strength": 4},
                "habit": {"items": ["Status quo"], "evidence": [], "strength": 3},
                "force_balance": 6,
                "change_likely": True,
                "key_insight": "Net positive force",
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            context = {"product_idea": mock_session.product_idea}
            four_forces = await stage.generate_four_forces(mock_session, context)

            assert four_forces.push.strength == 7
            assert four_forces.force_balance == 6
            assert four_forces.change_likely is True

    @pytest.mark.asyncio
    async def test_opportunity_tree_generation(self, mock_session):
        """Should generate opportunity solution tree."""
        stage = OpportunityMappingStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "outcome": "Improve team productivity",
                "opportunities": [
                    {
                        "id": "opp-1",
                        "description": "Reduce context switching",
                        "interview_count": 3,
                        "evidence": [],
                        "solutions": ["Unified interface"],
                        "priority": 1,
                    },
                    {
                        "id": "opp-2",
                        "description": "Automate status updates",
                        "interview_count": 2,
                        "evidence": [],
                        "solutions": ["AI automation"],
                        "priority": 2,
                    },
                ],
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            context = {"product_idea": mock_session.product_idea}
            tree = await stage.generate_opportunity_tree(
                mock_session, "Improve team productivity", context
            )

            assert tree.outcome == "Improve team productivity"
            assert len(tree.opportunities) == 2
            # Should be sorted by priority
            assert tree.opportunities[0].priority <= tree.opportunities[1].priority


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 4: SOLUTION DESIGN TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSolutionDesignStage:
    """Tests for Solution Design stage."""

    @pytest.mark.asyncio
    async def test_solution_design_generates_output(self, mock_session):
        """Should generate solution design with DHM score and pre-mortem."""
        stage = SolutionDesignStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "solution_concept": "AI-powered task coordinator",
                "solution_description": "Automated task routing and status tracking",
                "key_features": ["Auto-routing", "Smart notifications", "Team analytics"],
                "dhm_score": {
                    "delight": 8,
                    "delight_reasoning": "Saves hours per week",
                    "hard_to_copy": 6,
                    "hard_to_copy_reasoning": "AI model requires data",
                    "margin": 7,
                    "margin_reasoning": "Low marginal cost",
                    "total": 21,
                    "passes_threshold": True,
                },
                "pre_mortem": {
                    "tigers": [{"description": "Market saturation"}],
                    "paper_tigers": [{"description": "Competition"}],
                    "elephants": [{"description": "Team expertise"}],
                },
                "value_proposition": "Save 5 hours/week on coordination",
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.mini_critique.critique_stage_output") as mock_critique:
                mock_critique.return_value = {
                    "overall_score": 8.0,
                    "passes_threshold": True,
                    "feedback": [],
                }

                context = {
                    "product_idea": mock_session.product_idea,
                    "problem_statement": "Remote teams struggle",
                    "primary_opportunity": "Reduce coordination overhead",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, SolutionDesignOutput)
                assert output.solution_concept == "AI-powered task coordinator"
                assert output.dhm_score.total == 21
                assert output.dhm_score.passes_threshold is True
                assert len(output.key_features) == 3

    @pytest.mark.asyncio
    async def test_dhm_analysis(self, mock_session):
        """Should perform DHM analysis."""
        stage = SolutionDesignStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "delight": 9,
                "delight_reasoning": "Huge time savings",
                "hard_to_copy": 5,
                "hard_to_copy_reasoning": "Network effects",
                "margin": 8,
                "margin_reasoning": "SaaS model",
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            context = {"primary_opportunity": "Test"}
            dhm = await stage.analyze_dhm(mock_session, "Test solution", context)

            assert dhm.delight == 9
            assert dhm.hard_to_copy == 5
            assert dhm.margin == 8
            assert dhm.total == 22
            assert dhm.passes_threshold is True  # >= 20

    @pytest.mark.asyncio
    async def test_pre_mortem_analysis(self, mock_session):
        """Should run pre-mortem analysis."""
        stage = SolutionDesignStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "tigers": [
                    {
                        "description": "No product-market fit",
                        "mitigation": "Run experiments",
                        "early_warning": "Low retention",
                    }
                ],
                "paper_tigers": [{"description": "Big tech competition"}],
                "elephants": [{"description": "Founder disagreement"}],
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            pre_mortem = await stage.run_pre_mortem(mock_session, "Test solution")

            assert len(pre_mortem.tigers) > 0
            assert pre_mortem.tigers[0].description == "No product-market fit"
            assert pre_mortem.tigers[0].mitigation == "Run experiments"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE 5: VALIDATION PLAN TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestValidationPlanStage:
    """Tests for Validation Plan stage."""

    @pytest.mark.asyncio
    async def test_validation_plan_generates_output(self, mock_session):
        """Should generate validation plan with experiments."""
        stage = ValidationPlanStage()

        mock_llm_response = {
            "success": True,
            "data": {
                "current_rung": 1,
                "experiments": [
                    {
                        "rung": 1,
                        "name": "Problem validation interviews",
                        "hypothesis": "7/10 teams have coordination pain",
                        "success_criteria": "7+ confirmations",
                        "failure_criteria": "<5 confirmations",
                        "target_participants": "10 remote teams",
                        "method": "Customer interviews",
                        "timeline": "2 weeks",
                        "status": "todo",
                    },
                    {
                        "rung": 2,
                        "name": "Landing page test",
                        "hypothesis": "5% conversion",
                        "success_criteria": ">5% conversion",
                        "failure_criteria": "<2% conversion",
                        "target_participants": "1000 visitors",
                        "method": "Landing page",
                        "timeline": "1 week",
                        "status": "todo",
                    },
                ],
                "validation_summary": "Start with problem validation",
            },
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.mini_critique.critique_stage_output") as mock_critique:
                mock_critique.return_value = {
                    "overall_score": 8.0,
                    "passes_threshold": True,
                    "feedback": [],
                }

                context = {
                    "product_idea": mock_session.product_idea,
                    "solution": "AI task coordinator",
                }

                output = await stage.run(mock_session, context)

                assert isinstance(output, ValidationPlanOutput)
                assert output.current_rung == 1
                assert len(output.experiments) == 2
                assert output.next_experiment is not None
                assert output.next_experiment.rung == 1

    @pytest.mark.asyncio
    async def test_validation_ladder_defaults(self, mock_session):
        """Should create default validation ladder when LLM fails."""
        stage = ValidationPlanStage()

        mock_llm_response = {
            "success": False,
            "error": "API error",
        }

        with patch("agents.base_agent.call_llm", return_value=mock_llm_response):
            with patch("agents.discovery_v4.stages.mini_critique.critique_stage_output") as mock_critique:
                mock_critique.return_value = {
                    "overall_score": 5.0,
                    "passes_threshold": False,
                    "feedback": [],
                }

                context = {"product_idea": mock_session.product_idea}
                output = await stage.run(mock_session, context)

                assert isinstance(output, ValidationPlanOutput)
                assert len(output.experiments) == 5  # All 5 rungs
                assert output.experiments[0].rung == 1
                assert output.experiments[-1].rung == 5

    @pytest.mark.asyncio
    async def test_status_normalization(self, mock_session):
        """Should normalize invalid experiment statuses."""
        stage = ValidationPlanStage()

        mock_data = {
            "current_rung": 1,
            "experiments": [
                {
                    "rung": 1,
                    "name": "Test",
                    "hypothesis": "H",
                    "success_criteria": "S",
                    "failure_criteria": "F",
                    "target_participants": "P",
                    "method": "M",
                    "timeline": "1 week",
                    "status": "planned",  # Invalid - should normalize to "todo"
                }
            ],
            "validation_summary": "Test",
        }

        output = stage._parse_output(mock_data, {})

        assert output.experiments[0].status == "todo"


# ═══════════════════════════════════════════════════════════════════════════
# DISCOVERY ENGINE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestDiscoveryEngineV4:
    """Tests for the Discovery Engine orchestrator."""

    @pytest.mark.asyncio
    async def test_engine_runs_quick_mode_stages(self, mock_session):
        """Should run all stages automatically in Quick mode."""
        engine = DiscoveryEngineV4()

        # Mock all stage runners
        with patch.object(engine, "stage_runners", {
            "problem_love": MagicMock(run=AsyncMock(return_value=MagicMock(
                model_dump=MagicMock(return_value={"overall_score": 8})
            ))),
            "customer_truth": MagicMock(run=AsyncMock(return_value=MagicMock(
                model_dump=MagicMock(return_value={"readiness_score": 7})
            ))),
            "opportunity_mapping": MagicMock(run=AsyncMock(return_value=MagicMock(
                model_dump=MagicMock(return_value={})
            ))),
            "solution_design": MagicMock(run=AsyncMock(return_value=MagicMock(
                model_dump=MagicMock(return_value={})
            ))),
            "validation_plan": MagicMock(run=AsyncMock(return_value=MagicMock(
                model_dump=MagicMock(return_value={})
            ))),
        }):
            with patch.object(engine, "_save_checkpoint", new_callable=AsyncMock):
                with patch("utils.db.SupabaseSessionStore") as MockStore:
                    mock_store = MockStore.return_value
                    mock_store.save_draft_state = MagicMock()
                    mock_store.update_status = MagicMock()

                    result = await engine.run_session(mock_session)

                    assert result.session_id == mock_session.session_id
                    # Quick mode runs all stages
                    for stage_name in ["problem_love", "customer_truth", "opportunity_mapping", "solution_design", "validation_plan"]:
                        assert engine.stage_runners[stage_name].run.called

    @pytest.mark.asyncio
    async def test_engine_handles_stage_failure(self, mock_session):
        """Should handle stage failures gracefully."""
        engine = DiscoveryEngineV4()

        # Mock stage that raises exception
        failing_stage = MagicMock()
        failing_stage.run = AsyncMock(side_effect=Exception("LLM timeout"))

        with patch.object(engine, "stage_runners", {"problem_love": failing_stage}):
            with pytest.raises(Exception, match="LLM timeout"):
                await engine.run_stage(mock_session, "problem_love")

            # Check that error was recorded in stage state
            assert mock_session.stages["problem_love"].status == StageStatus.NOT_STARTED
            assert mock_session.stages["problem_love"].error_message == "LLM timeout"
            assert len(mock_session.stages["problem_love"].coaching_messages) > 0

    @pytest.mark.asyncio
    async def test_quality_gate_blocks_low_score(self, mock_session):
        """Should block progression when quality gate fails."""
        engine = DiscoveryEngineV4()

        # Set up a stage with low score
        mock_session.stages["problem_love"].output = {
            "problem_statement": "Vague problem",
            "overall_score": 3,  # Below threshold
        }
        mock_session.stages["problem_love"].score = 3

        passed, blocked_reason, feedback = engine._check_quality_gate(mock_session, "problem_love")

        assert passed is False  # May pass if score check is lenient
        assert len(feedback) > 0  # Should have feedback

    @pytest.mark.asyncio
    async def test_evidence_tier_calculation(self, mock_session_with_interviews):
        """Should calculate evidence tier based on interviews."""
        engine = DiscoveryEngineV4()

        # 2 interviews should be E3
        tier = engine._calculate_evidence_tier(mock_session_with_interviews, "customer_truth")
        assert tier in [EvidenceQuality.E2, EvidenceQuality.E3]

        # Add more interviews for E1
        for i in range(5):
            mock_session_with_interviews.interviews.append(
                Interview(
                    id=f"int-{i+3}",
                    interviewee_name=f"User {i}",
                    interviewee_role="Manager",
                    company_type="Startup",
                    company_size="11-50",
                    interview_date=date.today(),
                    story_raw="Test story",
                    key_quote="Test quote",
                    struggling_moment="Test moment",
                    emotions=["frustrated"],
                    current_workaround="Manual process",
                    desired_outcome="Automation",
                )
            )

        tier = engine._calculate_evidence_tier(mock_session_with_interviews, "customer_truth")
        assert tier == EvidenceQuality.E1  # >= 5 interviews

    @pytest.mark.asyncio
    async def test_session_progress_calculation(self, mock_session):
        """Should calculate session progress correctly."""
        engine = DiscoveryEngineV4()

        # Complete 2 out of 5 stages
        mock_session.stages["problem_love"].status = StageStatus.COMPLETED
        mock_session.stages["problem_love"].score = 8
        mock_session.stages["customer_truth"].status = StageStatus.COMPLETED
        mock_session.stages["customer_truth"].score = 7

        with patch("utils.db.SupabaseSessionStore") as MockStore:
            mock_store = MockStore.return_value
            mock_store.update_status = MagicMock()

            result = engine._update_session_progress(mock_session)

            # Quality score should be average of completed stages
            assert result.quality_score > 0
            # Update status should be called with progress
            mock_store.update_status.assert_called()
