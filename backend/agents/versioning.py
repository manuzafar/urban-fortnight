"""
Agent Output Versioning — Tracks output evolution across revisions.

This module provides versioning capabilities for agent outputs, enabling:
- Track changes between versions
- Understand what triggered each revision
- Analyze output stability across iterations
- Debug quality issues by reviewing version history

Key concepts:
- OutputVersion: A single version of an agent's output
- Version triggers: "initial", "revision", "constraint", "contradiction"
- Change tracking: Semantic diffs between versions
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class OutputVersion:
    """
    A single version of an agent's output.

    Attributes:
        version: Version number (1-indexed)
        output: The actual output dictionary
        trigger: What caused this version:
            - "initial": First generation
            - "revision": Quality-based revision
            - "constraint": Constraint-based update
            - "contradiction": Contradiction resolution
        changes: List of changes from previous version
        timestamp: When this version was created
        metadata: Additional context (scores, tokens, etc.)
    """
    version: int
    output: dict[str, Any]
    trigger: str
    changes: list[str]
    timestamp: str
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class OutputVersionManager:
    """
    Manages version history for agent outputs.

    Usage:
        manager = OutputVersionManager()

        # Record initial version
        manager.create_version("customer_research", output1, "initial")

        # Record revision
        manager.create_version("customer_research", output2, "revision")

        # Get history
        history = manager.get_history("customer_research")

        # Get changes between versions
        changes = manager.get_changes("customer_research", 1, 2)
    """

    def __init__(self):
        self._versions: dict[str, list[OutputVersion]] = {}

    def create_version(
        self,
        field_name: str,
        new_output: dict[str, Any],
        trigger: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> OutputVersion:
        """
        Create a new version for a field.

        Args:
            field_name: State field name (e.g., "customer_research")
            new_output: The new output dictionary
            trigger: What triggered this version
            metadata: Optional metadata (scores, tokens, etc.)

        Returns:
            The created OutputVersion
        """
        if field_name not in self._versions:
            self._versions[field_name] = []

        existing = self._versions[field_name]
        version_num = len(existing) + 1

        # Calculate changes from previous version
        changes = []
        if existing:
            prev_output = existing[-1].output
            changes = compute_changes(prev_output, new_output)

        version = OutputVersion(
            version=version_num,
            output=new_output,
            trigger=trigger,
            changes=changes,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata,
        )

        self._versions[field_name].append(version)

        logger.info(
            "version_created",
            field=field_name,
            version=version_num,
            trigger=trigger,
            changes_count=len(changes),
        )

        return version

    def get_history(self, field_name: str) -> list[OutputVersion]:
        """Get full version history for a field."""
        return self._versions.get(field_name, [])

    def get_latest(self, field_name: str) -> Optional[OutputVersion]:
        """Get the latest version for a field."""
        history = self._versions.get(field_name, [])
        return history[-1] if history else None

    def get_version(self, field_name: str, version_num: int) -> Optional[OutputVersion]:
        """Get a specific version."""
        history = self._versions.get(field_name, [])
        if 0 < version_num <= len(history):
            return history[version_num - 1]
        return None

    def get_changes(
        self,
        field_name: str,
        from_version: int,
        to_version: int,
    ) -> list[str]:
        """Get cumulative changes between two versions."""
        history = self._versions.get(field_name, [])

        if from_version < 1 or to_version > len(history):
            return []

        from_output = history[from_version - 1].output
        to_output = history[to_version - 1].output

        return compute_changes(from_output, to_output)

    def to_dict(self) -> dict[str, list[dict]]:
        """Convert all versions to dictionary for serialization."""
        return {
            field: [v.to_dict() for v in versions]
            for field, versions in self._versions.items()
        }

    @classmethod
    def from_dict(cls, data: dict[str, list[dict]]) -> "OutputVersionManager":
        """Create manager from serialized dictionary."""
        manager = cls()
        for field, versions in data.items():
            manager._versions[field] = [
                OutputVersion(**v) for v in versions
            ]
        return manager


def compute_changes(old: dict, new: dict, path: str = "") -> list[str]:
    """
    Compute semantic changes between two output dictionaries.

    Identifies:
    - Added fields
    - Removed fields
    - Modified values
    - Nested changes (recursive)

    Args:
        old: Previous version dictionary
        new: Current version dictionary
        path: Current path for nested tracking

    Returns:
        List of change descriptions (limited to top 20)
    """
    changes: list[str] = []

    if old is None:
        old = {}
    if new is None:
        new = {}

    all_keys = set(old.keys()) | set(new.keys())

    for key in all_keys:
        current_path = f"{path}.{key}" if path else key

        if key not in old:
            changes.append(f"Added: {current_path}")
        elif key not in new:
            changes.append(f"Removed: {current_path}")
        elif old[key] != new[key]:
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                # Recurse for nested dicts
                nested_changes = compute_changes(old[key], new[key], current_path)
                changes.extend(nested_changes)
            elif isinstance(old[key], list) and isinstance(new[key], list):
                # Handle list changes
                if len(old[key]) != len(new[key]):
                    changes.append(f"Modified: {current_path} (length {len(old[key])} -> {len(new[key])})")
                else:
                    # Check if any items changed
                    items_changed = sum(1 for a, b in zip(old[key], new[key]) if a != b)
                    if items_changed > 0:
                        changes.append(f"Modified: {current_path} ({items_changed} items changed)")
            else:
                # Simple value change
                old_preview = str(old[key])[:50]
                new_preview = str(new[key])[:50]
                changes.append(f"Modified: {current_path} ({old_preview}... -> {new_preview}...)")

    # Limit to top 20 changes to avoid overwhelming output
    return changes[:20]


def create_version(
    field_name: str,
    new_output: dict,
    existing_versions: list[dict],
    trigger: str,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Create a new version with change tracking.

    Standalone function for use without the manager class.

    Args:
        field_name: Name of the field being versioned
        new_output: The new output dictionary
        existing_versions: List of existing version dictionaries
        trigger: What triggered this version
        metadata: Optional metadata

    Returns:
        Version dictionary with change tracking
    """
    version_num = len(existing_versions) + 1

    # Calculate changes from previous version
    changes = []
    if existing_versions:
        prev_output = existing_versions[-1].get("output", {})
        changes = compute_changes(prev_output, new_output)

    return {
        "version": version_num,
        "output": new_output,
        "trigger": trigger,
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": metadata or {},
    }


def summarize_version_history(versions: list[dict]) -> dict[str, Any]:
    """
    Summarize version history for analysis.

    Args:
        versions: List of version dictionaries

    Returns:
        Summary with statistics and key changes
    """
    if not versions:
        return {"total_versions": 0}

    triggers = {}
    total_changes = 0

    for v in versions:
        trigger = v.get("trigger", "unknown")
        triggers[trigger] = triggers.get(trigger, 0) + 1
        total_changes += len(v.get("changes", []))

    return {
        "total_versions": len(versions),
        "triggers": triggers,
        "total_changes": total_changes,
        "avg_changes_per_version": round(total_changes / len(versions), 1) if versions else 0,
        "latest_trigger": versions[-1].get("trigger") if versions else None,
        "first_timestamp": versions[0].get("timestamp") if versions else None,
        "latest_timestamp": versions[-1].get("timestamp") if versions else None,
    }
