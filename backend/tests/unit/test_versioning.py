"""
Tests for agent output versioning in versioning.py

These tests verify that:
- Version creation and tracking works correctly
- Changes between versions are computed accurately
- Version history summarization is correct
"""

import pytest
from agents.versioning import (
    OutputVersion,
    OutputVersionManager,
    compute_changes,
    create_version,
    summarize_version_history,
)


class TestOutputVersion:
    """Tests for OutputVersion dataclass."""

    def test_version_creation(self):
        """Should create version with all required fields."""
        version = OutputVersion(
            version=1,
            output={"market_size": "$5B"},
            trigger="initial",
            changes=[],
            timestamp="2024-01-01T00:00:00",
        )

        assert version.version == 1
        assert version.output["market_size"] == "$5B"
        assert version.trigger == "initial"

    def test_to_dict(self):
        """Should convert to dictionary correctly."""
        version = OutputVersion(
            version=1,
            output={"data": "test"},
            trigger="revision",
            changes=["Added: field_a"],
            timestamp="2024-01-01T00:00:00",
            metadata={"score": 0.8},
        )

        d = version.to_dict()

        assert isinstance(d, dict)
        assert d["version"] == 1
        assert d["metadata"]["score"] == 0.8


class TestOutputVersionManager:
    """Tests for OutputVersionManager class."""

    def test_create_initial_version(self):
        """Should create first version with no changes."""
        manager = OutputVersionManager()

        version = manager.create_version(
            field_name="customer_research",
            new_output={"market_size": "$5B"},
            trigger="initial",
        )

        assert version.version == 1
        assert version.changes == []
        assert version.trigger == "initial"

    def test_create_subsequent_version_tracks_changes(self):
        """Should track changes from previous version."""
        manager = OutputVersionManager()

        # First version
        manager.create_version(
            field_name="customer_research",
            new_output={"market_size": "$5B"},
            trigger="initial",
        )

        # Second version with changes
        version2 = manager.create_version(
            field_name="customer_research",
            new_output={"market_size": "$6B", "competitors": 3},
            trigger="revision",
        )

        assert version2.version == 2
        assert len(version2.changes) > 0
        assert any("Modified" in c or "Added" in c for c in version2.changes)

    def test_get_history_returns_all_versions(self):
        """Should return full version history."""
        manager = OutputVersionManager()

        manager.create_version("field_a", {"v": 1}, "initial")
        manager.create_version("field_a", {"v": 2}, "revision")
        manager.create_version("field_a", {"v": 3}, "revision")

        history = manager.get_history("field_a")

        assert len(history) == 3
        assert history[0].version == 1
        assert history[2].version == 3

    def test_get_latest_version(self):
        """Should return the most recent version."""
        manager = OutputVersionManager()

        manager.create_version("field_a", {"v": 1}, "initial")
        manager.create_version("field_a", {"v": 2}, "revision")

        latest = manager.get_latest("field_a")

        assert latest.version == 2

    def test_get_specific_version(self):
        """Should return specific version by number."""
        manager = OutputVersionManager()

        manager.create_version("field_a", {"v": 1}, "initial")
        manager.create_version("field_a", {"v": 2}, "revision")

        version1 = manager.get_version("field_a", 1)
        version2 = manager.get_version("field_a", 2)

        assert version1.output["v"] == 1
        assert version2.output["v"] == 2

    def test_get_nonexistent_version_returns_none(self):
        """Should return None for nonexistent version."""
        manager = OutputVersionManager()

        version = manager.get_version("nonexistent", 1)

        assert version is None

    def test_get_changes_between_versions(self):
        """Should compute cumulative changes between versions."""
        manager = OutputVersionManager()

        manager.create_version("field_a", {"a": 1}, "initial")
        manager.create_version("field_a", {"a": 2, "b": 3}, "revision")

        changes = manager.get_changes("field_a", 1, 2)

        assert len(changes) > 0

    def test_to_dict_serialization(self):
        """Should serialize all versions to dictionary."""
        manager = OutputVersionManager()

        manager.create_version("field_a", {"v": 1}, "initial")
        manager.create_version("field_b", {"v": 1}, "initial")

        d = manager.to_dict()

        assert "field_a" in d
        assert "field_b" in d
        assert len(d["field_a"]) == 1

    def test_from_dict_deserialization(self):
        """Should deserialize from dictionary."""
        data = {
            "field_a": [
                {
                    "version": 1,
                    "output": {"v": 1},
                    "trigger": "initial",
                    "changes": [],
                    "timestamp": "2024-01-01T00:00:00",
                    "metadata": None,
                }
            ]
        }

        manager = OutputVersionManager.from_dict(data)
        history = manager.get_history("field_a")

        assert len(history) == 1
        assert history[0].version == 1


class TestComputeChanges:
    """Tests for compute_changes function."""

    def test_detects_added_fields(self):
        """Should detect when fields are added."""
        old = {"a": 1}
        new = {"a": 1, "b": 2}

        changes = compute_changes(old, new)

        assert any("Added" in c and "b" in c for c in changes)

    def test_detects_removed_fields(self):
        """Should detect when fields are removed."""
        old = {"a": 1, "b": 2}
        new = {"a": 1}

        changes = compute_changes(old, new)

        assert any("Removed" in c and "b" in c for c in changes)

    def test_detects_modified_values(self):
        """Should detect when values are modified."""
        old = {"a": 1}
        new = {"a": 2}

        changes = compute_changes(old, new)

        assert any("Modified" in c and "a" in c for c in changes)

    def test_handles_nested_dicts(self):
        """Should recursively detect changes in nested dicts."""
        old = {"nested": {"a": 1}}
        new = {"nested": {"a": 2}}

        changes = compute_changes(old, new)

        assert any("nested.a" in c for c in changes)

    def test_handles_list_changes(self):
        """Should detect changes in list length."""
        old = {"items": [1, 2]}
        new = {"items": [1, 2, 3]}

        changes = compute_changes(old, new)

        assert any("items" in c for c in changes)

    def test_limits_changes_to_20(self):
        """Should limit changes to 20 entries."""
        old = {f"field_{i}": i for i in range(30)}
        new = {f"field_{i}": i + 100 for i in range(30)}

        changes = compute_changes(old, new)

        assert len(changes) <= 20

    def test_handles_none_values(self):
        """Should handle None values gracefully."""
        changes = compute_changes(None, {"a": 1})

        assert len(changes) > 0


class TestCreateVersionFunction:
    """Tests for standalone create_version function."""

    def test_creates_version_dict(self):
        """Should create version dictionary with all fields."""
        version = create_version(
            field_name="test_field",
            new_output={"data": "value"},
            existing_versions=[],
            trigger="initial",
        )

        assert version["version"] == 1
        assert version["output"]["data"] == "value"
        assert version["trigger"] == "initial"
        assert version["changes"] == []
        assert "timestamp" in version

    def test_computes_changes_from_previous(self):
        """Should compute changes from last version."""
        existing = [
            {
                "version": 1,
                "output": {"a": 1},
                "trigger": "initial",
                "changes": [],
                "timestamp": "2024-01-01",
            }
        ]

        version = create_version(
            field_name="test_field",
            new_output={"a": 2, "b": 3},
            existing_versions=existing,
            trigger="revision",
        )

        assert version["version"] == 2
        assert len(version["changes"]) > 0


class TestSummarizeVersionHistory:
    """Tests for summarize_version_history function."""

    def test_summarizes_empty_history(self):
        """Should handle empty history."""
        summary = summarize_version_history([])

        assert summary["total_versions"] == 0

    def test_counts_versions(self):
        """Should count total versions."""
        versions = [
            {"version": 1, "trigger": "initial", "changes": []},
            {"version": 2, "trigger": "revision", "changes": ["a"]},
        ]

        summary = summarize_version_history(versions)

        assert summary["total_versions"] == 2

    def test_counts_triggers(self):
        """Should count triggers by type."""
        versions = [
            {"version": 1, "trigger": "initial", "changes": []},
            {"version": 2, "trigger": "revision", "changes": []},
            {"version": 3, "trigger": "revision", "changes": []},
        ]

        summary = summarize_version_history(versions)

        assert summary["triggers"]["initial"] == 1
        assert summary["triggers"]["revision"] == 2

    def test_calculates_average_changes(self):
        """Should calculate average changes per version."""
        versions = [
            {"version": 1, "trigger": "initial", "changes": []},
            {"version": 2, "trigger": "revision", "changes": ["a", "b"]},
            {"version": 3, "trigger": "revision", "changes": ["c"]},
        ]

        summary = summarize_version_history(versions)

        assert summary["total_changes"] == 3
        assert summary["avg_changes_per_version"] == 1.0
