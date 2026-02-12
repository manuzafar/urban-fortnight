"""
Tests for critique agent retry logic.

Tests the new retry mechanism that prevents silent quality gate bypass
when the critique agent fails due to validation errors or LLM failures.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from agents.critique import run_critique_agent
from agents.state import create_initial_state


class TestCritiqueRetryOnValidationError:
    """Tests for retry behavior when validation fails."""

    @pytest.mark.asyncio
    async def test_validation_error_triggers_retry_flag(self):
        """Should set _retry_critique flag on validation error when attempts remain."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["critique_attempt"] = 1
        state["customer_research"] = {"data": "test"}
        state["business_case"] = {"data": "test"}
        state["product_requirements"] = {"data": "test"}
        state["technical_architecture"] = {"data": "test"}

        # Mock call_llm to return invalid data that will fail validation
        with patch("agents.critique.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": True,
                "data": {"invalid": "data"},  # Missing required fields
                "tokens_used": 100,
                "duration_seconds": 1.0,
            }
            with patch("agents.critique.settings") as mock_settings:
                mock_settings.max_critique_retries = 2
                mock_settings.min_quality_score = 0.7
                mock_settings.max_revision_iterations = 3

                result = await run_critique_agent(state)

        # Should set retry flag and increment attempt
        assert result.get("_retry_critique") is True
        assert result.get("critique_attempt") == 2
        assert result.get("quality_passed") is False
        assert "Critique validation failed" in str(result.get("errors", []))

    @pytest.mark.asyncio
    async def test_validation_error_bypasses_after_max_retries(self):
        """Should mark as passed after max retries exceeded."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["critique_attempt"] = 2  # Already at max retries
        state["customer_research"] = {"data": "test"}
        state["business_case"] = {"data": "test"}
        state["product_requirements"] = {"data": "test"}
        state["technical_architecture"] = {"data": "test"}

        with patch("agents.critique.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": True,
                "data": {"invalid": "data"},
                "tokens_used": 100,
                "duration_seconds": 1.0,
            }
            with patch("agents.critique.settings") as mock_settings:
                mock_settings.max_critique_retries = 2
                mock_settings.min_quality_score = 0.7
                mock_settings.max_revision_iterations = 3

                result = await run_critique_agent(state)

        # Should bypass with clear warning
        assert result.get("quality_passed") is True
        assert result.get("quality_passed_reason") == "max_critique_retries_exceeded"
        assert "QUALITY GATE BYPASSED" in str(result.get("errors", []))
        assert result.get("_retry_critique") is None or result.get("_retry_critique") is False


class TestCritiqueRetryOnLLMFailure:
    """Tests for retry behavior when LLM call fails."""

    @pytest.mark.asyncio
    async def test_llm_failure_triggers_retry_flag(self):
        """Should set _retry_critique flag on LLM failure when attempts remain."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["critique_attempt"] = 1
        state["customer_research"] = {"data": "test"}

        with patch("agents.critique.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": False,
                "error": "API timeout",
                "tokens_used": 0,
                "duration_seconds": 30.0,
            }
            with patch("agents.critique.settings") as mock_settings:
                mock_settings.max_critique_retries = 2
                mock_settings.min_quality_score = 0.7
                mock_settings.max_revision_iterations = 3

                result = await run_critique_agent(state)

        # Should set retry flag
        assert result.get("_retry_critique") is True
        assert result.get("critique_attempt") == 2
        assert result.get("quality_passed") is False
        assert "Critique LLM call failed" in str(result.get("errors", []))

    @pytest.mark.asyncio
    async def test_llm_failure_bypasses_after_max_retries(self):
        """Should mark as passed after max LLM failure retries."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["critique_attempt"] = 2  # Already at max
        state["customer_research"] = {"data": "test"}

        with patch("agents.critique.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": False,
                "error": "API timeout",
                "tokens_used": 0,
                "duration_seconds": 30.0,
            }
            with patch("agents.critique.settings") as mock_settings:
                mock_settings.max_critique_retries = 2
                mock_settings.min_quality_score = 0.7
                mock_settings.max_revision_iterations = 3

                result = await run_critique_agent(state)

        # Should bypass with clear warning
        assert result.get("quality_passed") is True
        assert result.get("quality_passed_reason") == "max_critique_retries_exceeded"
        assert "QUALITY GATE BYPASSED" in str(result.get("errors", []))


class TestCritiqueSuccessPath:
    """Tests for normal success path (no retries needed)."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt_no_retry(self):
        """Should not set retry flag on successful first attempt."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["critique_attempt"] = 1
        state["customer_research"] = {"data": "test"}
        state["business_case"] = {"data": "test"}
        state["product_requirements"] = {"data": "test"}
        state["technical_architecture"] = {"data": "test"}

        with patch("agents.critique.call_llm") as mock_llm:
            # Valid QualityAssessment data matching the Pydantic schema
            mock_llm.return_value = {
                "success": True,
                "data": {
                    "overall_score": 0.85,
                    "passed": True,
                    "iteration": 1,
                    "section_scores": [
                        {"section": "Customer Research", "score": 0.8, "feedback": "Good research depth"},
                        {"section": "Business Case", "score": 0.9, "feedback": "Strong business case"},
                    ],
                    "strengths": ["Good research"],
                    "weaknesses": [],
                    "critical_gaps": [],
                    "recommendations": [],
                    "ready_for_delivery": True,
                },
                "tokens_used": 100,
                "duration_seconds": 2.0,
            }
            with patch("agents.critique.settings") as mock_settings:
                mock_settings.max_critique_retries = 2
                mock_settings.min_quality_score = 0.7
                mock_settings.max_revision_iterations = 3

                result = await run_critique_agent(state)

        # Should NOT have retry flag set
        assert result.get("_retry_critique") is None or result.get("_retry_critique") is False
        assert result.get("quality_passed") is True
        assert result.get("quality_passed_reason") is None
        assert "QUALITY GATE BYPASSED" not in str(result.get("errors", []))


class TestConfigSetting:
    """Tests for the max_critique_retries config setting."""

    def test_max_critique_retries_default(self):
        """max_critique_retries should have sensible default."""
        from config import settings
        assert settings.max_critique_retries >= 1
        assert settings.max_critique_retries <= 5

    def test_critique_attempt_in_initial_state(self):
        """Initial state should include critique_attempt field."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        assert "critique_attempt" in state
        assert state["critique_attempt"] == 1
