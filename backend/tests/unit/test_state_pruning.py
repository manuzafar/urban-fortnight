"""
Tests for state pruning utilities.

Tests cover:
- Revision history pruning
- Error list pruning
- Cross-reference index pruning
- State size calculation
- Archive functionality
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from utils.state_pruning import (
    get_state_size,
    get_field_sizes,
    prune_revision_history,
    prune_errors,
    prune_cross_reference_index,
    prune_state,
    archive_old_revisions,
    PruningConfig,
    DEFAULT_MAX_REVISION_HISTORY,
    DEFAULT_MAX_ERRORS,
    DEFAULT_MAX_CLAIMS,
)
from agents.state import create_initial_state


class TestGetStateSize:
    """Tests for state size calculation."""

    def test_empty_state_has_minimal_size(self):
        """Empty dict should have minimal size."""
        size = get_state_size({})
        assert size > 0
        assert size < 100  # JSON "{}" is 2 bytes

    def test_calculates_size_of_simple_state(self):
        """Should calculate size of a simple state dict."""
        state = {"key": "value", "number": 123}
        size = get_state_size(state)

        # Compare with actual JSON size
        expected = len(json.dumps(state).encode("utf-8"))
        assert size == expected

    def test_calculates_size_with_nested_objects(self):
        """Should calculate size including nested objects."""
        state = {
            "level1": {
                "level2": {
                    "data": "nested value",
                    "list": [1, 2, 3, 4, 5],
                }
            }
        }
        size = get_state_size(state)

        expected = len(json.dumps(state).encode("utf-8"))
        assert size == expected

    def test_handles_large_state(self):
        """Should handle large state dictionaries."""
        # Create a large state with many entries
        state = {
            "revision_history": [{"iteration": i, "data": "x" * 1000} for i in range(100)],
            "errors": [f"Error {i}" for i in range(50)],
        }
        size = get_state_size(state)

        assert size > 100_000  # Should be over 100KB

    def test_handles_non_json_serializable_objects(self):
        """Should fallback gracefully for non-JSON-serializable objects."""
        # datetime objects are not JSON serializable by default
        from datetime import datetime

        state = {"timestamp": datetime.now()}
        size = get_state_size(state)

        # Should still return a reasonable size using str() conversion
        assert size > 0


class TestGetFieldSizes:
    """Tests for individual field size calculation."""

    def test_returns_sizes_for_each_field(self):
        """Should return size for each non-None field."""
        state = {
            "small_field": "abc",
            "large_field": "x" * 10000,
            "empty_field": None,
        }
        sizes = get_field_sizes(state)

        assert "small_field" in sizes
        assert "large_field" in sizes
        assert "empty_field" not in sizes  # None fields excluded
        assert sizes["large_field"] > sizes["small_field"]

    def test_identifies_largest_fields(self):
        """Should help identify which fields are consuming memory."""
        state = {
            "revision_history": [{"data": "x" * 100} for _ in range(50)],
            "errors": ["error"] * 10,
            "product_idea": "Simple idea",
        }
        sizes = get_field_sizes(state)

        # Revision history should be the largest
        assert sizes["revision_history"] > sizes["errors"]
        assert sizes["revision_history"] > sizes["product_idea"]


class TestPruneRevisionHistory:
    """Tests for revision history pruning."""

    @pytest.mark.asyncio
    async def test_no_pruning_when_under_limit(self):
        """Should not prune when history is under the limit."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [
            {"iteration": 1, "score": 0.5},
            {"iteration": 2, "score": 0.6},
        ]

        result = await prune_revision_history(state, max_entries=5, archive=False)

        assert len(result["revision_history"]) == 2

    @pytest.mark.asyncio
    async def test_prunes_old_entries(self):
        """Should keep only the most recent entries."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [
            {"iteration": i, "score": 0.5 + i * 0.1}
            for i in range(10)
        ]

        result = await prune_revision_history(state, max_entries=3, archive=False)

        assert len(result["revision_history"]) == 3
        # Should keep iterations 7, 8, 9 (most recent)
        assert result["revision_history"][0]["iteration"] == 7
        assert result["revision_history"][2]["iteration"] == 9

    @pytest.mark.asyncio
    async def test_handles_empty_history(self):
        """Should handle empty revision history."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = []

        result = await prune_revision_history(state, max_entries=5, archive=False)

        assert result["revision_history"] == []

    @pytest.mark.asyncio
    async def test_archive_called_when_enabled(self):
        """Should call archive function when archive=True."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [{"iteration": i} for i in range(10)]

        with patch("utils.state_pruning.archive_old_revisions") as mock_archive:
            mock_archive.return_value = None
            await prune_revision_history(state, max_entries=3, archive=True)

            mock_archive.assert_called_once()
            call_args = mock_archive.call_args
            assert call_args[0][0] == "test-123"  # session_id
            assert len(call_args[0][1]) == 7  # 7 entries archived

    @pytest.mark.asyncio
    async def test_continues_on_archive_failure(self):
        """Should continue pruning even if archive fails."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [{"iteration": i} for i in range(10)]

        with patch("utils.state_pruning.archive_old_revisions") as mock_archive:
            mock_archive.side_effect = Exception("Archive failed")
            result = await prune_revision_history(state, max_entries=3, archive=True)

            # Should still prune despite archive failure
            assert len(result["revision_history"]) == 3


class TestPruneErrors:
    """Tests for error list pruning."""

    @pytest.mark.asyncio
    async def test_no_pruning_when_under_limit(self):
        """Should not prune when errors are under the limit."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["errors"] = ["Error 1", "Error 2"]

        result = await prune_errors(state, max_entries=20)

        assert len(result["errors"]) == 2

    @pytest.mark.asyncio
    async def test_prunes_old_errors(self):
        """Should keep only the most recent errors."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["errors"] = [f"Error {i}" for i in range(30)]

        result = await prune_errors(state, max_entries=10)

        assert len(result["errors"]) == 10
        # Should keep Error 20-29 (most recent)
        assert result["errors"][0] == "Error 20"
        assert result["errors"][9] == "Error 29"

    @pytest.mark.asyncio
    async def test_handles_empty_errors(self):
        """Should handle empty error list."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["errors"] = []

        result = await prune_errors(state, max_entries=10)

        assert result["errors"] == []


class TestPruneCrossReferenceIndex:
    """Tests for cross-reference index pruning."""

    @pytest.mark.asyncio
    async def test_no_pruning_when_under_limit(self):
        """Should not prune when claims are under the limit."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["cross_reference_index"] = {
            "claims": [
                {"claim_id": f"c{i}", "evidence_tier": "E3"}
                for i in range(10)
            ],
            "total_claims": 10,
        }

        result = await prune_cross_reference_index(state, max_claims=100)

        assert len(result["cross_reference_index"]["claims"]) == 10

    @pytest.mark.asyncio
    async def test_prioritizes_high_evidence_claims(self):
        """Should keep all E1-E2 claims before E3-E5 claims."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        claims = []
        # Add 20 E1 claims
        for i in range(20):
            claims.append({"claim_id": f"e1_{i}", "evidence_tier": "E1"})
        # Add 50 E3 claims
        for i in range(50):
            claims.append({"claim_id": f"e3_{i}", "evidence_tier": "E3"})
        # Add 50 E4 claims
        for i in range(50):
            claims.append({"claim_id": f"e4_{i}", "evidence_tier": "E4"})

        state["cross_reference_index"] = {
            "claims": claims,
            "total_claims": len(claims),
        }

        result = await prune_cross_reference_index(state, max_claims=50)

        pruned_claims = result["cross_reference_index"]["claims"]
        assert len(pruned_claims) == 50

        # All 20 E1 claims should be preserved
        e1_claims = [c for c in pruned_claims if c["evidence_tier"] == "E1"]
        assert len(e1_claims) == 20

        # Remaining slots (30) should be from E3/E4
        other_claims = [c for c in pruned_claims if c["evidence_tier"] != "E1"]
        assert len(other_claims) == 30

    @pytest.mark.asyncio
    async def test_recalculates_statistics_after_pruning(self):
        """Should recalculate tier distribution and evidence score."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["cross_reference_index"] = {
            "claims": [
                {"claim_id": f"e1_{i}", "evidence_tier": "E1"} for i in range(10)
            ] + [
                {"claim_id": f"e4_{i}", "evidence_tier": "E4"} for i in range(100)
            ],
            "total_claims": 110,
            "tier_distribution": {"E1": 10, "E4": 100},
        }

        result = await prune_cross_reference_index(state, max_claims=30)

        cross_ref = result["cross_reference_index"]
        assert cross_ref["total_claims"] == 30
        assert cross_ref["tier_distribution"]["E1"] == 10
        assert cross_ref["tier_distribution"].get("E4", 0) == 20
        assert cross_ref["pruned"] is True
        assert cross_ref["original_claim_count"] == 110

    @pytest.mark.asyncio
    async def test_handles_missing_cross_reference(self):
        """Should handle state without cross_reference_index."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        # cross_reference_index is None by default

        result = await prune_cross_reference_index(state, max_claims=50)

        assert result.get("cross_reference_index") is None


class TestPruneState:
    """Tests for comprehensive state pruning."""

    @pytest.mark.asyncio
    async def test_prunes_all_unbounded_fields(self):
        """Should prune all unbounded fields in one call."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [{"iteration": i} for i in range(20)]
        state["errors"] = [f"Error {i}" for i in range(50)]
        state["cross_reference_index"] = {
            "claims": [{"claim_id": f"c{i}", "evidence_tier": "E4"} for i in range(200)],
            "total_claims": 200,
        }

        result = await prune_state(
            state,
            max_revision_history=5,
            max_errors=10,
            max_claims=50,
            archive_revisions=False,
        )

        assert len(result["revision_history"]) == 5
        assert len(result["errors"]) == 10
        assert len(result["cross_reference_index"]["claims"]) == 50

    @pytest.mark.asyncio
    async def test_logs_size_reduction(self):
        """Should log size before and after pruning."""
        state = create_initial_state(
            session_id="test-123",
            product_idea="Test product",
        )
        state["revision_history"] = [{"iteration": i, "data": "x" * 1000} for i in range(100)]

        size_before = get_state_size(state)
        result = await prune_state(state, max_revision_history=5, archive_revisions=False)
        size_after = get_state_size(result)

        # Size should be significantly reduced
        assert size_after < size_before
        assert size_after < size_before / 2  # At least 50% reduction


class TestArchiveOldRevisions:
    """Tests for revision archiving functionality."""

    @pytest.mark.asyncio
    async def test_archives_to_database(self):
        """Should insert revisions into revision_archive table."""
        revisions = [
            {"iteration": 1, "score": 0.5},
            {"iteration": 2, "score": 0.6},
        ]

        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[])

        with patch("utils.state_pruning.get_supabase_client", return_value=mock_client):
            await archive_old_revisions("test-123", revisions)

            mock_client.table.assert_called_once_with("revision_archive")
            mock_table.insert.assert_called_once()

            # Check the inserted data
            insert_call = mock_table.insert.call_args
            inserted_rows = insert_call[0][0]
            assert len(inserted_rows) == 2
            assert inserted_rows[0]["session_id"] == "test-123"
            assert inserted_rows[0]["revision_index"] == 0

    @pytest.mark.asyncio
    async def test_raises_on_database_error(self):
        """Should raise exception on database error."""
        revisions = [{"iteration": 1, "score": 0.5}]

        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")

        with patch("utils.state_pruning.get_supabase_client", return_value=mock_client):
            with pytest.raises(Exception, match="Database error"):
                await archive_old_revisions("test-123", revisions)


class TestPruningConfig:
    """Tests for pruning configuration."""

    def test_default_values(self):
        """Should have sensible default values."""
        config = PruningConfig()

        assert config.max_revision_history == DEFAULT_MAX_REVISION_HISTORY
        assert config.max_errors == DEFAULT_MAX_ERRORS
        assert config.max_claims == DEFAULT_MAX_CLAIMS
        assert config.archive_revisions is True
        assert config.prune_on_finalize is True
        assert config.prune_after_revision is True

    def test_custom_values(self):
        """Should accept custom configuration values."""
        config = PruningConfig(
            max_revision_history=10,
            max_errors=50,
            max_claims=200,
            archive_revisions=False,
            prune_on_finalize=False,
            prune_after_revision=False,
        )

        assert config.max_revision_history == 10
        assert config.max_errors == 50
        assert config.max_claims == 200
        assert config.archive_revisions is False
        assert config.prune_on_finalize is False
        assert config.prune_after_revision is False

    def test_from_settings(self):
        """Should create config from settings."""
        config = PruningConfig.from_settings()

        # Should return valid config (using defaults since settings don't have pruning keys)
        assert config.max_revision_history > 0
        assert config.max_errors > 0
        assert config.max_claims > 0


class TestIntegrationWithState:
    """Integration tests with actual DiscoveryState."""

    @pytest.mark.asyncio
    async def test_prune_real_state(self):
        """Should work with actual DiscoveryState structure."""
        state = create_initial_state(
            session_id="test-integration",
            product_idea="AI-powered scheduling assistant",
            industry="Technology",
        )

        # Simulate a long-running workflow
        for i in range(15):
            state["revision_history"].append({
                "iteration": i + 1,
                "agent": "customer_research",
                "quality_score": 0.5 + (i * 0.03),
                "timestamp": "2024-01-01T00:00:00Z",
            })

        state["errors"].extend([
            f"Retry {i}: Rate limit exceeded" for i in range(25)
        ])

        state["cross_reference_index"] = {
            "claims": [
                {
                    "claim_id": f"claim_{i}",
                    "evidence_tier": "E3" if i % 3 == 0 else "E4",
                    "section": "customer_research",
                    "content": f"Claim content {i}",
                }
                for i in range(150)
            ],
            "total_claims": 150,
        }

        # Prune the state
        pruned = await prune_state(
            state,
            max_revision_history=5,
            max_errors=10,
            max_claims=50,
            archive_revisions=False,
        )

        # Verify pruning
        assert len(pruned["revision_history"]) == 5
        assert len(pruned["errors"]) == 10
        assert len(pruned["cross_reference_index"]["claims"]) == 50

        # Verify state integrity
        assert pruned["session_id"] == "test-integration"
        assert pruned["product_idea"] == "AI-powered scheduling assistant"
        assert pruned["industry"] == "Technology"
