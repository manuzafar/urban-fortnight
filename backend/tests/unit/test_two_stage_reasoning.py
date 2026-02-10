"""
Tests for two-stage grounded reasoning in two_stage_reasoning.py

These tests verify that:
- Two-stage reasoning separates research from structuring
- Constraints are properly injected
- Error handling works for both stages
"""

import pytest
from unittest.mock import AsyncMock, patch

from agents.two_stage_reasoning import (
    call_llm_two_stage,
    call_llm_two_stage_with_constraints,
    RESEARCH_ENHANCEMENT_PROMPT,
    STRUCTURING_PROMPT_TEMPLATE,
)


class TestCallLlmTwoStage:
    """Tests for call_llm_two_stage function."""

    @pytest.mark.asyncio
    async def test_successful_two_stage_call(self):
        """Should complete both stages successfully."""
        # Mock both LLM calls
        with patch("agents.two_stage_reasoning.call_llm_with_grounding") as mock_grounded, \
             patch("agents.two_stage_reasoning.call_llm") as mock_llm:

            # Stage 1: Research returns raw text
            mock_grounded.return_value = {
                "success": True,
                "data": {"raw": "data"},
                "raw_response": "Research findings: Market is $5B...",
                "tokens_used": 500,
                "duration_seconds": 2.0,
            }

            # Stage 2: Structure returns JSON
            mock_llm.return_value = {
                "success": True,
                "data": {"market_size": "$5B"},
                "raw_response": '{"market_size": "$5B"}',
                "tokens_used": 300,
                "duration_seconds": 1.0,
                "model_used": "gemini-2.0-flash",
            }

            result = await call_llm_two_stage(
                research_prompt="Research the market",
                structure_prompt="Output JSON with market_size field",
                agent_name="test_agent",
            )

            assert result["success"] is True
            assert result["data"]["market_size"] == "$5B"
            assert result["tokens_used"] == 800  # 500 + 300
            assert result["grounded"] is True
            assert "research_text" in result

    @pytest.mark.asyncio
    async def test_stage1_failure_returns_error(self):
        """Should return error if Stage 1 fails."""
        with patch("agents.two_stage_reasoning.call_llm_with_grounding") as mock_grounded:
            mock_grounded.return_value = {
                "success": False,
                "error": "API error",
                "tokens_used": 0,
                "duration_seconds": 0.5,
            }

            result = await call_llm_two_stage(
                research_prompt="Research",
                structure_prompt="Structure",
                agent_name="test_agent",
            )

            assert result["success"] is False
            assert "Stage 1" in result["error"]
            assert result["stage_failed"] == 1

    @pytest.mark.asyncio
    async def test_stage2_failure_preserves_research(self):
        """Should preserve research text even if Stage 2 fails."""
        with patch("agents.two_stage_reasoning.call_llm_with_grounding") as mock_grounded, \
             patch("agents.two_stage_reasoning.call_llm") as mock_llm:

            mock_grounded.return_value = {
                "success": True,
                "raw_response": "Good research findings",
                "tokens_used": 500,
                "duration_seconds": 2.0,
            }

            mock_llm.return_value = {
                "success": False,
                "error": "JSON parse error",
                "tokens_used": 100,
                "duration_seconds": 0.5,
            }

            result = await call_llm_two_stage(
                research_prompt="Research",
                structure_prompt="Structure",
                agent_name="test_agent",
            )

            assert result["success"] is False
            assert result["stage_failed"] == 2
            assert result["research_text"] == "Good research findings"

    @pytest.mark.asyncio
    async def test_no_grounding_skips_grounded_call(self):
        """Should use regular call_llm when use_grounding=False."""
        with patch("agents.two_stage_reasoning.call_llm") as mock_llm:
            mock_llm.return_value = {
                "success": True,
                "data": {"test": "data"},
                "raw_response": "response",
                "tokens_used": 300,
                "duration_seconds": 1.0,
                "model_used": "gemini-2.0-flash",
            }

            result = await call_llm_two_stage(
                research_prompt="Research",
                structure_prompt="Structure",
                agent_name="test_agent",
                use_grounding=False,
            )

            assert result["success"] is True
            assert result["grounded"] is False


class TestCallLlmTwoStageWithConstraints:
    """Tests for call_llm_two_stage_with_constraints function."""

    @pytest.mark.asyncio
    async def test_injects_constraints_into_both_prompts(self):
        """Should inject constraints into both research and structure prompts."""
        constraints = "## CONSTRAINTS\n- Market size: $5B"

        with patch("agents.two_stage_reasoning.call_llm_two_stage") as mock_two_stage:
            mock_two_stage.return_value = {"success": True, "data": {}}

            await call_llm_two_stage_with_constraints(
                research_prompt="Research the market",
                structure_prompt="Output JSON",
                agent_name="test_agent",
                constraints_prompt=constraints,
            )

            # Check that call_llm_two_stage was called with enhanced prompts
            call_args = mock_two_stage.call_args
            research_prompt = call_args[1]["research_prompt"]
            structure_prompt = call_args[1]["structure_prompt"]

            assert "CONSTRAINTS" in research_prompt
            assert "CONSTRAINTS" in structure_prompt

    @pytest.mark.asyncio
    async def test_no_constraints_passes_original_prompts(self):
        """Should pass original prompts when no constraints provided."""
        with patch("agents.two_stage_reasoning.call_llm_two_stage") as mock_two_stage:
            mock_two_stage.return_value = {"success": True, "data": {}}

            await call_llm_two_stage_with_constraints(
                research_prompt="Research",
                structure_prompt="Structure",
                agent_name="test_agent",
                constraints_prompt=None,
            )

            call_args = mock_two_stage.call_args
            assert call_args[1]["research_prompt"] == "Research"
            assert call_args[1]["structure_prompt"] == "Structure"


class TestPromptTemplates:
    """Tests for prompt template content."""

    def test_research_enhancement_prompt_exists(self):
        """Research enhancement prompt should contain key instructions."""
        assert "data points" in RESEARCH_ENHANCEMENT_PROMPT.lower()
        assert "source" in RESEARCH_ENHANCEMENT_PROMPT.lower()
        assert "confidence" in RESEARCH_ENHANCEMENT_PROMPT.lower()

    def test_structuring_prompt_template_has_placeholders(self):
        """Structuring prompt template should have required placeholders."""
        assert "{research_text}" in STRUCTURING_PROMPT_TEMPLATE
        assert "{structure_instructions}" in STRUCTURING_PROMPT_TEMPLATE

    def test_structuring_prompt_mentions_evidence_tiers(self):
        """Structuring prompt should mention evidence tiers."""
        assert "E1" in STRUCTURING_PROMPT_TEMPLATE
        assert "E2" in STRUCTURING_PROMPT_TEMPLATE
        assert "E4" in STRUCTURING_PROMPT_TEMPLATE
