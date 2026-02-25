"""
Tests for Discovery V4 Engine - Core orchestration tests.

This module tests the DiscoveryEngineV4 orchestrator including:
- Stage execution
- State transitions
- Quality gates
- Evidence tier calculation
- Session progress tracking
"""

from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.discovery_v4.engine import DiscoveryEngineV4
from models.discovery_v4_schemas import (
    DiscoveryMode,
    DiscoverySessionV4,
    EvidenceQuality,
    Interview,
    StageState,
    StageStatus,
)


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
    for i in range(5):
        session.interviews.append(
            Interview(
                id=f"int-{i}",
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

    return session


class TestDiscoveryEngineV4:
    """Tests for the Discovery Engine orchestrator."""

    def test_mode_config_exists(self):
        """Should have configuration for all three modes."""
        engine = DiscoveryEngineV4()

        assert "quick" in engine.MODE_CONFIG
        assert "guided" in engine.MODE_CONFIG
        assert "deep" in engine.MODE_CONFIG

        # Quick mode should auto-run all stages
        assert len(engine.MODE_CONFIG["quick"]["auto_run_stages"]) == 5

        # Deep mode should require interviews
        assert engine.MODE_CONFIG["deep"]["interviews_required"] >= 3

    def test_stage_runners_lazy_load(self):
        """Should lazy load stage runners."""
        engine = DiscoveryEngineV4()

        # Should be None initially
        assert engine._stage_runners is None

        # Should load on first access
        runners = engine.stage_runners
        assert runners is not None
        assert "problem_love" in runners
        assert "customer_truth" in runners
        assert "opportunity_mapping" in runners
        assert "solution_design" in runners
        assert "validation_plan" in runners

    @pytest.mark.asyncio
    async def test_run_stage_updates_status(self, mock_session):
        """Should update stage status during execution."""
        engine = DiscoveryEngineV4()

        # Mock a stage runner
        mock_output = MagicMock()
        mock_output.model_dump.return_value = {"test": "data", "overall_score": 8}
        mock_output.overall_score = 8

        mock_runner = MagicMock()
        mock_runner.run = AsyncMock(return_value=mock_output)

        # Patch the _stage_runners private attribute instead of the property
        engine._stage_runners = {"problem_love": mock_runner}

        with patch("utils.db.SupabaseSessionStore") as MockStore:
            mock_store = MockStore.return_value
            mock_store.save_draft_state = MagicMock()

            result = await engine.run_stage(mock_session, "problem_love")

            # Should mark as completed
            assert result.stages["problem_love"].status == StageStatus.COMPLETED
            assert result.stages["problem_love"].output is not None
            assert result.stages["problem_love"].score == 8

    @pytest.mark.asyncio
    async def test_run_stage_handles_errors(self, mock_session):
        """Should handle stage errors gracefully."""
        engine = DiscoveryEngineV4()

        # Mock a failing stage
        mock_runner = MagicMock()
        mock_runner.run = AsyncMock(side_effect=Exception("LLM timeout"))

        # Patch the _stage_runners private attribute
        engine._stage_runners = {"problem_love": mock_runner}

        with pytest.raises(Exception, match="LLM timeout"):
            await engine.run_stage(mock_session, "problem_love")

        # Should record error
        assert mock_session.stages["problem_love"].status == StageStatus.NOT_STARTED
        assert mock_session.stages["problem_love"].error_message == "LLM timeout"
        assert len(mock_session.stages["problem_love"].coaching_messages) > 0

    def test_build_stage_context(self, mock_session):
        """Should build context from previous stages."""
        engine = DiscoveryEngineV4()

        # Add some outputs
        mock_session.stages["problem_love"].output = {
            "problem_statement": "Remote teams struggle",
            "problem_statement_refined": "Teams struggle with async work",
        }

        context = engine._build_stage_context(mock_session, "customer_truth")

        assert "product_idea" in context
        assert "mode" in context
        assert context["problem_statement"] == "Teams struggle with async work"

    def test_build_stage_context_with_interviews(self, mock_session_with_interviews):
        """Should include interviews in context."""
        engine = DiscoveryEngineV4()

        context = engine._build_stage_context(mock_session_with_interviews, "opportunity_mapping")

        assert "interviews" in context
        assert context["interview_count"] == 5
        assert len(context["interviews"]) == 5

    def test_quality_gate_requires_output(self, mock_session):
        """Should fail quality gate when no output."""
        engine = DiscoveryEngineV4()

        passed, blocked_reason, feedback = engine._check_quality_gate(mock_session, "problem_love")

        assert passed is False
        assert blocked_reason == "No output generated"
        assert "failed to generate output" in feedback[0].lower()

    def test_quality_gate_checks_score(self, mock_session):
        """Should check minimum score threshold."""
        engine = DiscoveryEngineV4()

        # Set low score
        mock_session.stages["problem_love"].output = {
            "problem_statement": "Vague problem",
            "frequency": "rarely",
            "overall_score": 3,
        }
        mock_session.stages["problem_love"].score = 3

        passed, blocked_reason, feedback = engine._check_quality_gate(mock_session, "problem_love")

        # Should have feedback about low score
        assert any("score" in f.lower() for f in feedback)

    def test_quality_gate_checks_required_fields(self, mock_session):
        """Should check for required fields."""
        engine = DiscoveryEngineV4()

        # Missing required field
        mock_session.stages["problem_love"].output = {
            # Missing problem_statement
            "overall_score": 8,
        }
        mock_session.stages["problem_love"].score = 8

        passed, blocked_reason, feedback = engine._check_quality_gate(mock_session, "problem_love")

        # Should have feedback about missing field
        assert any("missing" in f.lower() for f in feedback)

    def test_evidence_tier_calculation_no_interviews(self, mock_session):
        """Should return E4 with no interviews."""
        engine = DiscoveryEngineV4()

        tier = engine._calculate_evidence_tier(mock_session, "customer_truth")

        assert tier == EvidenceQuality.E4

    def test_evidence_tier_calculation_with_interviews(self, mock_session_with_interviews):
        """Should calculate tier based on interview count."""
        engine = DiscoveryEngineV4()

        # 5 interviews = E1
        tier = engine._calculate_evidence_tier(mock_session_with_interviews, "customer_truth")
        assert tier == EvidenceQuality.E1

        # Remove to get 3 interviews = E2
        mock_session_with_interviews.interviews = mock_session_with_interviews.interviews[:3]
        tier = engine._calculate_evidence_tier(mock_session_with_interviews, "customer_truth")
        assert tier == EvidenceQuality.E2

        # Remove to get 1 interview = E3
        mock_session_with_interviews.interviews = mock_session_with_interviews.interviews[:1]
        tier = engine._calculate_evidence_tier(mock_session_with_interviews, "customer_truth")
        assert tier == EvidenceQuality.E3

    def test_update_session_progress(self, mock_session):
        """Should calculate session progress correctly."""
        engine = DiscoveryEngineV4()

        # Complete 2 out of 5 stages
        mock_session.stages["problem_love"].status = StageStatus.COMPLETED
        mock_session.stages["problem_love"].score = 8
        mock_session.stages["customer_truth"].status = StageStatus.COMPLETED
        mock_session.stages["customer_truth"].score = 7

        with patch("agents.discovery_v4.engine.session_store") as mock_store:
            mock_store.update_status = MagicMock()

            result = engine._update_session_progress(mock_session)

            # Quality score should be average of completed stages
            assert result.quality_score > 0
            assert result.quality_score == int((8 + 7) / 2 * 10)

            # Update status should be called
            mock_store.update_status.assert_called_once()

            # Check call args
            call_args = mock_store.update_status.call_args[0]
            assert call_args[0] == mock_session.session_id
            assert call_args[1]["progress_percentage"] == 40  # 2/5 = 40%
            assert call_args[1]["status"] == "in_progress"

    def test_update_session_progress_all_complete(self, mock_session):
        """Should mark session as completed when all stages done."""
        engine = DiscoveryEngineV4()

        # Complete all stages
        for stage_name in mock_session.stages:
            mock_session.stages[stage_name].status = StageStatus.COMPLETED
            mock_session.stages[stage_name].score = 8

        with patch("agents.discovery_v4.engine.session_store") as mock_store:
            mock_store.update_status = MagicMock()

            engine._update_session_progress(mock_session)

            # Should mark as completed
            call_args = mock_store.update_status.call_args[0]
            assert call_args[1]["progress_percentage"] == 100
            assert call_args[1]["status"] == "completed"

    def test_update_cross_stage_data_customer_truth(self, mock_session):
        """Should update patterns from customer truth stage."""
        engine = DiscoveryEngineV4()

        mock_output = MagicMock()
        mock_output.patterns = MagicMock()
        mock_output.interviews = [MagicMock()]

        result = engine._update_cross_stage_data(mock_session, "customer_truth", mock_output)

        assert result.patterns is not None
        assert len(result.interviews) == 1

    def test_update_cross_stage_data_opportunity_mapping(self, mock_session):
        """Should update four_forces and opportunity_tree."""
        engine = DiscoveryEngineV4()

        mock_output = MagicMock()
        mock_output.four_forces = MagicMock()
        mock_output.opportunity_tree = MagicMock()

        result = engine._update_cross_stage_data(mock_session, "opportunity_mapping", mock_output)

        assert result.four_forces is not None
        assert result.opportunity_tree is not None

    def test_stage_quality_requirements(self):
        """Should have quality requirements for each stage."""
        engine = DiscoveryEngineV4()

        # All stages should have requirements
        for stage in ["problem_love", "customer_truth", "opportunity_mapping", "solution_design", "validation_plan"]:
            assert stage in engine.STAGE_QUALITY_REQUIREMENTS
            reqs = engine.STAGE_QUALITY_REQUIREMENTS[stage]
            assert "min_score" in reqs
            assert "required_fields" in reqs
            assert "blocking_message" in reqs

    def test_deep_mode_interview_requirement(self, mock_session):
        """Deep mode should require minimum interviews for customer_truth."""
        engine = DiscoveryEngineV4()

        # Set to deep mode with insufficient interviews
        mock_session.mode = DiscoveryMode.DEEP
        mock_session.stages["customer_truth"].output = {"readiness_score": 8}
        mock_session.stages["customer_truth"].score = 8

        # Only 1 interview (need 3 for deep mode)
        mock_session.interviews = [MagicMock()]

        passed, blocked_reason, feedback = engine._check_quality_gate(mock_session, "customer_truth")

        # Should require more interviews
        assert any("interview" in f.lower() for f in feedback)
