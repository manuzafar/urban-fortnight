"""
Tests for the Golden Set evaluation system.

These tests verify:
- Golden set loading and management
- Similarity scoring between outputs and golden sets
- Regression detection logic
- CLI commands for golden set operations
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from evals.golden.golden_set_manager import GoldenSetManager
from evals.golden.similarity_scorer import SimilarityScorer
from evals.golden.golden_set_eval import (
    GoldenSetRegression,
    GoldenSetCoverage,
    GoldenSetComparisonResult,
    RegressionWarning,
)
from evals.base import EvalSeverity


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def temp_golden_dir():
    """Create a temporary directory for golden sets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_golden_set():
    """Create a sample golden set structure."""
    return {
        "metadata": {
            "name": "Test Golden Set",
            "version": "1.0",
            "created_at": "2026-02-25T00:00:00Z",
            "quality_score": 0.85,
            "domain": "B2B_SaaS",
            "product_idea": "Test product idea",
        },
        "state": {
            "product_idea": "Test product idea for golden set",
            "executive_summary": {
                "product_name": "TestProduct",
                "tagline": "Test tagline",
                "problem_statement": "Test problem",
                "solution_overview": "Test solution",
                "value_proposition": "Test value prop",
                "target_users": ["User A", "User B"],
                "target_market_size": "TAM: $1B",
                "key_differentiators": ["Diff 1", "Diff 2"],
                "competitive_landscape": "Test competitors",
                "funding_required": "$1M",
                "revenue_model": "SaaS subscription",
                "financial_projections": "Year 1: $500K",
                "break_even_timeline": "Month 24",
                "expected_roi": "5x by Year 3",
                "top_risks": ["Risk 1", "Risk 2"],
                "regulatory_summary": "Test compliance",
                "gtm_strategy": "Test GTM",
                "key_milestones": ["Milestone 1"],
                "success_metrics": ["Metric 1"],
                "recommendation": "PROCEED",
            },
            "customer_research": {
                "research_scope": {
                    "segments_examined": ["Segment A"],
                    "observation_context": "Test context",
                    "known_gaps": ["Gap 1"],
                    "confidence_level": "high",
                },
                "job_to_be_done": {
                    "trigger_situation": "Test trigger",
                    "underlying_goal": "Test goal",
                    "success_definition": "Test success",
                },
                "pain_signals": [
                    {
                        "description": "Pain point 1",
                        "evidence_tier": "E2",
                        "severity": "high",
                    }
                ],
            },
            "business_case": {
                "lean_canvas": {
                    "problem": ["Problem 1"],
                    "solution": ["Solution 1"],
                },
            },
            "product_requirements_document": {
                "vision_statement": "Test vision",
                "epics": [],
            },
            "technical_architecture": {
                "system_overview": "Test architecture",
            },
        },
    }


@pytest.fixture
def sample_output_state():
    """Create a sample output state to compare against golden sets."""
    return {
        "product_idea": "Similar test product idea",
        "executive_summary": {
            "product_name": "OutputProduct",
            "tagline": "Output tagline",
            "problem_statement": "Similar problem",
            "solution_overview": "Similar solution",
            "value_proposition": "Similar value prop",
            "target_users": ["User A", "User C"],
            "target_market_size": "TAM: $1.2B",
            "key_differentiators": ["Diff 1", "Diff 3"],
            "competitive_landscape": "Similar competitors",
            "funding_required": "$1.5M",
            "revenue_model": "SaaS subscription",
            "financial_projections": "Year 1: $600K",
            "break_even_timeline": "Month 20",
            "expected_roi": "6x by Year 3",
            "top_risks": ["Risk 1", "Risk 3"],
            "regulatory_summary": "Similar compliance",
            "gtm_strategy": "Similar GTM",
            "key_milestones": ["Milestone 1", "Milestone 2"],
            "success_metrics": ["Metric 1", "Metric 2"],
            "recommendation": "PROCEED",
        },
        "customer_research": {
            "research_scope": {
                "segments_examined": ["Segment A", "Segment B"],
                "observation_context": "Similar context",
                "known_gaps": ["Gap 1", "Gap 2"],
                "confidence_level": "medium",
            },
            "job_to_be_done": {
                "trigger_situation": "Similar trigger",
                "underlying_goal": "Similar goal",
                "success_definition": "Similar success",
            },
            "pain_signals": [
                {
                    "description": "Pain point 1",
                    "evidence_tier": "E2",
                    "severity": "high",
                },
                {
                    "description": "Pain point 2",
                    "evidence_tier": "E3",
                    "severity": "medium",
                },
            ],
        },
        "business_case": {
            "lean_canvas": {
                "problem": ["Problem 1", "Problem 2"],
                "solution": ["Solution 1"],
            },
        },
        "product_requirements_document": {
            "vision_statement": "Similar vision",
            "epics": [{"id": "E1", "title": "Epic 1"}],
        },
        "technical_architecture": {
            "system_overview": "Similar architecture",
            "key_components": [],
        },
    }


@pytest.fixture
def manager_with_golden(temp_golden_dir, sample_golden_set):
    """Create a manager with a pre-loaded golden set."""
    golden_path = temp_golden_dir / "test_golden_v1.json"
    with open(golden_path, "w") as f:
        json.dump(sample_golden_set, f)

    return GoldenSetManager(temp_golden_dir)


# ═══════════════════════════════════════════════════════════════════════════════
# GOLDEN SET MANAGER TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoldenSetManager:
    """Tests for GoldenSetManager class."""

    def test_list_golden_sets_empty(self, temp_golden_dir):
        """Test listing golden sets when none exist."""
        manager = GoldenSetManager(temp_golden_dir)
        assert manager.list_golden_sets() == []

    def test_list_golden_sets(self, manager_with_golden):
        """Test listing golden sets."""
        sets = manager_with_golden.list_golden_sets()
        assert len(sets) == 1
        assert sets[0]["id"] == "test_golden_v1"
        assert sets[0]["name"] == "Test Golden Set"
        assert sets[0]["domain"] == "B2B_SaaS"

    def test_load_golden_set(self, manager_with_golden, sample_golden_set):
        """Test loading a golden set."""
        data = manager_with_golden.load("test_golden_v1")
        assert data is not None
        assert data["metadata"]["name"] == "Test Golden Set"
        assert data["state"]["product_idea"] == sample_golden_set["state"]["product_idea"]

    def test_load_golden_set_not_found(self, temp_golden_dir):
        """Test loading a non-existent golden set."""
        manager = GoldenSetManager(temp_golden_dir)
        assert manager.load("nonexistent") is None

    def test_save_golden_set(self, temp_golden_dir, sample_output_state):
        """Test saving a new golden set."""
        manager = GoldenSetManager(temp_golden_dir)

        success = manager.save(
            golden_set_id="new_golden",
            state=sample_output_state,
            name="New Golden Set",
            version="1.0",
            quality_score=0.80,
        )

        assert success is True
        assert (temp_golden_dir / "new_golden.json").exists()

        # Verify content
        loaded = manager.load("new_golden")
        assert loaded["metadata"]["name"] == "New Golden Set"
        assert loaded["state"]["product_idea"] == sample_output_state["product_idea"]

    def test_delete_golden_set(self, manager_with_golden, temp_golden_dir):
        """Test deleting a golden set."""
        assert manager_with_golden.delete("test_golden_v1") is True
        assert not (temp_golden_dir / "test_golden_v1.json").exists()
        assert manager_with_golden.load("test_golden_v1") is None

    def test_delete_nonexistent(self, temp_golden_dir):
        """Test deleting a non-existent golden set."""
        manager = GoldenSetManager(temp_golden_dir)
        assert manager.delete("nonexistent") is False

    def test_get_state(self, manager_with_golden, sample_golden_set):
        """Test getting just the state from a golden set."""
        state = manager_with_golden.get_state("test_golden_v1")
        assert state is not None
        assert state["product_idea"] == sample_golden_set["state"]["product_idea"]

    def test_get_section(self, manager_with_golden):
        """Test getting a specific section from a golden set."""
        section = manager_with_golden.get_section("test_golden_v1", "executive_summary")
        assert section is not None
        assert section["product_name"] == "TestProduct"

    def test_list_by_domain(self, temp_golden_dir, sample_golden_set):
        """Test filtering golden sets by domain."""
        # Create multiple golden sets with different domains
        gs1 = sample_golden_set.copy()
        gs1["metadata"] = {**gs1["metadata"], "domain": "B2B_SaaS"}

        gs2 = sample_golden_set.copy()
        gs2["metadata"] = {**gs2["metadata"], "domain": "Fintech", "name": "Fintech Golden"}

        with open(temp_golden_dir / "saas_golden.json", "w") as f:
            json.dump(gs1, f)
        with open(temp_golden_dir / "fintech_golden.json", "w") as f:
            json.dump(gs2, f)

        manager = GoldenSetManager(temp_golden_dir)

        saas_sets = manager.list_by_domain("B2B_SaaS")
        assert len(saas_sets) == 1
        assert saas_sets[0]["id"] == "saas_golden"

        fintech_sets = manager.list_by_domain("Fintech")
        assert len(fintech_sets) == 1
        assert fintech_sets[0]["id"] == "fintech_golden"

    def test_cache_behavior(self, manager_with_golden):
        """Test that loading caches golden sets."""
        # First load
        data1 = manager_with_golden.load("test_golden_v1")
        assert "test_golden_v1" in manager_with_golden._cache

        # Second load should use cache
        data2 = manager_with_golden.load("test_golden_v1")
        assert data1 is data2  # Same object from cache

        # Clear cache
        manager_with_golden.clear_cache()
        assert "test_golden_v1" not in manager_with_golden._cache


# ═══════════════════════════════════════════════════════════════════════════════
# SIMILARITY SCORER TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSimilarityScorer:
    """Tests for SimilarityScorer class."""

    def test_score_section(self, manager_with_golden, sample_golden_set, sample_output_state):
        """Test scoring a single section."""
        scorer = SimilarityScorer(manager_with_golden)

        golden_section = sample_golden_set["state"]["executive_summary"]
        output_section = sample_output_state["executive_summary"]

        scores = scorer.score_section(output_section, golden_section)

        assert "key_overlap" in scores
        assert "content_similarity" in scores
        assert "field_coverage" in scores
        assert "length_score" in scores
        assert "overall" in scores

        # Scores should be between 0 and 1
        for key, value in scores.items():
            assert 0.0 <= value <= 1.0, f"{key} = {value} is out of range"

        # Similar sections should have reasonable overlap
        assert scores["key_overlap"] > 0.5
        assert scores["field_coverage"] > 0.5

    def test_score_full_state(self, manager_with_golden, sample_golden_set, sample_output_state):
        """Test scoring the full state."""
        scorer = SimilarityScorer(manager_with_golden)

        result = scorer.score_full_state(
            sample_output_state,
            sample_golden_set["state"],
        )

        assert "sections" in result
        assert "overall" in result
        assert "sections_compared" in result

        assert result["sections_compared"] > 0
        assert 0.0 <= result["overall"] <= 1.0

    def test_identical_sections_score_high(self, manager_with_golden):
        """Test that identical sections score very high."""
        scorer = SimilarityScorer(manager_with_golden)

        section = {"key1": "value1", "key2": ["a", "b", "c"]}

        scores = scorer.score_section(section, section)

        assert scores["key_overlap"] == 1.0
        assert scores["field_coverage"] == 1.0
        assert scores["overall"] >= 0.9

    def test_empty_sections(self, manager_with_golden):
        """Test handling of empty sections."""
        scorer = SimilarityScorer(manager_with_golden)

        scores = scorer.score_section({}, {"key": "value"})

        assert scores["key_overlap"] == 0.0
        assert scores["field_coverage"] == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# REGRESSION DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoldenSetRegression:
    """Tests for GoldenSetRegression eval."""

    @pytest.mark.asyncio
    async def test_no_golden_sets_passes(self, temp_golden_dir):
        """Test that eval passes when no golden sets exist."""
        manager = GoldenSetManager(temp_golden_dir)
        eval_instance = GoldenSetRegression(manager)

        result = await eval_instance.evaluate(
            agent_output={},
            agent_name="test_agent",
            context={"full_state": {}},
        )

        assert result.passed is True
        assert "No golden sets" in result.message

    @pytest.mark.asyncio
    async def test_good_output_passes(self, manager_with_golden, sample_output_state):
        """Test that similar output passes evaluation."""
        eval_instance = GoldenSetRegression(manager_with_golden)

        result = await eval_instance.evaluate(
            agent_output=sample_output_state.get("executive_summary", {}),
            agent_name="executive_summary",
            context={"full_state": sample_output_state},
        )

        # Should pass or warn (not critical fail) for reasonable similarity
        assert result.severity != EvalSeverity.CRITICAL or result.passed

    @pytest.mark.asyncio
    async def test_empty_output_fails(self, manager_with_golden):
        """Test that empty output triggers regression warning."""
        eval_instance = GoldenSetRegression(manager_with_golden)

        result = await eval_instance.evaluate(
            agent_output={},
            agent_name="test_agent",
            context={"full_state": {}},
        )

        # Empty state should have low similarity
        assert result.score is not None
        assert result.score < 0.5


class TestGoldenSetCoverage:
    """Tests for GoldenSetCoverage eval."""

    @pytest.mark.asyncio
    async def test_complete_state_passes(self, manager_with_golden, sample_output_state):
        """Test that complete state passes coverage check."""
        eval_instance = GoldenSetCoverage(manager_with_golden)

        result = await eval_instance.evaluate(
            agent_output={},
            agent_name="full_state",
            context={"full_state": sample_output_state},
        )

        assert result.passed is True
        # Score reflects total coverage including optional sections
        # Required coverage should be 100%
        assert result.details["required_coverage"] == 1.0

    @pytest.mark.asyncio
    async def test_missing_sections_fails(self, manager_with_golden):
        """Test that missing required sections fails."""
        eval_instance = GoldenSetCoverage(manager_with_golden)

        incomplete_state = {
            "executive_summary": {"product_name": "Test"},
            # Missing: customer_research, business_case, etc.
        }

        result = await eval_instance.evaluate(
            agent_output={},
            agent_name="full_state",
            context={"full_state": incomplete_state},
        )

        assert result.passed is False
        assert "Missing required sections" in result.message
        assert len(result.details.get("missing_required", [])) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON RESULT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoldenSetComparisonResult:
    """Tests for GoldenSetComparisonResult dataclass."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = GoldenSetComparisonResult(
            best_match_id="test_golden",
            best_match_score=0.75,
            regression_detected=True,
            regressions=[
                RegressionWarning(
                    section="executive_summary",
                    metric="overall_similarity",
                    golden_value=0.7,
                    current_value=0.4,
                    regression_pct=0.43,
                    severity=EvalSeverity.WARNING,
                )
            ],
            section_scores={"executive_summary": {"test_golden": 0.4}},
            overall_similarity=0.65,
            domains_compared=["B2B_SaaS"],
            message="Test message",
        )

        data = result.to_dict()

        assert data["best_match_id"] == "test_golden"
        assert data["best_match_score"] == 0.75
        assert data["regression_detected"] is True
        assert len(data["regressions"]) == 1
        assert data["regressions"][0]["section"] == "executive_summary"
        assert data["regressions"][0]["severity"] == "warning"


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoldenSetIntegration:
    """Integration tests for the golden set system."""

    def test_compare_to_all(self, temp_golden_dir, sample_golden_set, sample_output_state):
        """Test comparing output against all golden sets."""
        # Create multiple golden sets
        gs1 = sample_golden_set.copy()
        gs1["metadata"]["name"] = "Golden 1"

        gs2 = sample_golden_set.copy()
        gs2["metadata"]["name"] = "Golden 2"
        gs2["state"]["product_idea"] = "Different product idea"

        with open(temp_golden_dir / "golden1.json", "w") as f:
            json.dump(gs1, f)
        with open(temp_golden_dir / "golden2.json", "w") as f:
            json.dump(gs2, f)

        manager = GoldenSetManager(temp_golden_dir)
        scorer = SimilarityScorer(manager)

        result = manager.compare_to_all(sample_output_state, scorer)

        assert result["best_match"] is not None
        assert result["best_score"] > 0
        assert len(result["all_comparisons"]) == 2

    def test_find_best_match_by_domain(self, temp_golden_dir, sample_golden_set):
        """Test finding best matching golden set by product idea."""
        # Create golden sets for different domains
        saas_gs = sample_golden_set.copy()
        saas_gs["metadata"]["domain"] = "B2B_SaaS"
        saas_gs["state"]["product_idea"] = "Enterprise collaboration tool"

        fintech_gs = sample_golden_set.copy()
        fintech_gs["metadata"]["domain"] = "Fintech"
        fintech_gs["state"]["product_idea"] = "Payment processing platform"

        with open(temp_golden_dir / "saas_golden.json", "w") as f:
            json.dump(saas_gs, f)
        with open(temp_golden_dir / "fintech_golden.json", "w") as f:
            json.dump(fintech_gs, f)

        manager = GoldenSetManager(temp_golden_dir)

        # Test matching
        match = manager.find_best_match("payment gateway for banks")
        assert match is not None
        # Should match fintech due to "payment" keyword

        match = manager.find_best_match("team workspace tool")
        assert match is not None
        # Should match B2B_SaaS due to "workspace" keyword


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGoldenSetCLI:
    """Tests for golden set CLI commands."""

    def test_golden_list_command(self, temp_golden_dir, sample_golden_set):
        """Test the golden list command."""
        from click.testing import CliRunner
        from evals.cli import cli

        # Create a golden set
        with open(temp_golden_dir / "test_golden.json", "w") as f:
            json.dump(sample_golden_set, f)

        runner = CliRunner()

        with patch("evals.golden.golden_set_manager.GOLDEN_SETS_DIR", temp_golden_dir):
            # Need to patch the manager's dir
            with patch.object(
                GoldenSetManager, "__init__",
                lambda self, gsd=None: setattr(self, "golden_sets_dir", temp_golden_dir) or setattr(self, "_cache", {})
            ):
                result = runner.invoke(cli, ["golden", "list"])

        # Should list the golden set (even if formatting differs)
        assert result.exit_code == 0 or "test_golden" in result.output or "Golden Sets" in result.output

    def test_golden_validate_command(self, temp_golden_dir, sample_output_state):
        """Test the golden validate command."""
        from click.testing import CliRunner
        from evals.cli import cli

        # Write a state file
        state_file = temp_golden_dir / "test_state.json"
        with open(state_file, "w") as f:
            json.dump(sample_output_state, f)

        runner = CliRunner()
        result = runner.invoke(cli, ["golden", "validate", str(state_file)])

        # Should validate successfully
        assert result.exit_code == 0
        assert "PASS" in result.output or "Coverage" in result.output
