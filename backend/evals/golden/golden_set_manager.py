"""
Golden Set Manager — Load, save, and version golden sets.

Golden sets are curated high-quality outputs that serve as baselines
for regression detection. New outputs are compared against these
baselines to detect quality degradation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger(__name__)


# Default location for golden sets
GOLDEN_SETS_DIR = Path(__file__).parent.parent / "fixtures" / "golden_sets"


class GoldenSetManager:
    """
    Manages golden set storage, loading, and versioning.

    Golden sets are JSON files containing:
    - metadata: version, name, created_at, quality_score
    - state: the full inception pack state
    """

    def __init__(self, golden_sets_dir: Path | str | None = None):
        """Initialize with optional custom directory."""
        self.golden_sets_dir = Path(golden_sets_dir) if golden_sets_dir else GOLDEN_SETS_DIR
        self._cache: dict[str, dict[str, Any]] = {}

    def list_golden_sets(self) -> list[dict[str, Any]]:
        """
        List all available golden sets with metadata.

        Returns:
            List of golden set info dictionaries
        """
        golden_sets = []

        if not self.golden_sets_dir.exists():
            return golden_sets

        for path in self.golden_sets_dir.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)

                metadata = data.get("metadata", {})
                golden_sets.append({
                    "id": path.stem,
                    "name": metadata.get("name", path.stem),
                    "version": metadata.get("version", "1.0"),
                    "created_at": metadata.get("created_at", "unknown"),
                    "quality_score": metadata.get("quality_score"),
                    "product_idea": data.get("state", {}).get("product_idea", "")[:100],
                    "path": str(path),
                })
            except Exception as e:
                logger.warning("golden_set_list_error", path=str(path), error=str(e))

        return golden_sets

    def load(self, golden_set_id: str) -> dict[str, Any] | None:
        """
        Load a golden set by ID.

        Args:
            golden_set_id: ID of the golden set (filename without .json)

        Returns:
            Golden set data or None if not found
        """
        # Check cache
        if golden_set_id in self._cache:
            return self._cache[golden_set_id]

        # Try to load
        path = self.golden_sets_dir / f"{golden_set_id}.json"
        if not path.exists():
            logger.warning("golden_set_not_found", id=golden_set_id)
            return None

        try:
            with open(path) as f:
                data = json.load(f)

            self._cache[golden_set_id] = data
            logger.info("golden_set_loaded", id=golden_set_id)
            return data
        except Exception as e:
            logger.error("golden_set_load_error", id=golden_set_id, error=str(e))
            return None

    def save(
        self,
        golden_set_id: str,
        state: dict[str, Any],
        name: str | None = None,
        version: str = "1.0",
        quality_score: float | None = None,
    ) -> bool:
        """
        Save a state as a golden set.

        Args:
            golden_set_id: ID for the golden set
            state: The full inception pack state
            name: Human-readable name
            version: Version string
            quality_score: Optional quality score (from eval)

        Returns:
            True if saved successfully
        """
        # Ensure directory exists
        self.golden_sets_dir.mkdir(parents=True, exist_ok=True)

        # Build golden set structure
        golden_data = {
            "metadata": {
                "name": name or golden_set_id,
                "version": version,
                "created_at": datetime.utcnow().isoformat(),
                "quality_score": quality_score,
                "product_idea": state.get("product_idea", ""),
            },
            "state": state,
        }

        # Save
        path = self.golden_sets_dir / f"{golden_set_id}.json"
        try:
            with open(path, "w") as f:
                json.dump(golden_data, f, indent=2, default=str)

            # Update cache
            self._cache[golden_set_id] = golden_data
            logger.info("golden_set_saved", id=golden_set_id, path=str(path))
            return True
        except Exception as e:
            logger.error("golden_set_save_error", id=golden_set_id, error=str(e))
            return False

    def get_state(self, golden_set_id: str) -> dict[str, Any] | None:
        """
        Get just the state from a golden set.

        Args:
            golden_set_id: ID of the golden set

        Returns:
            The state dictionary or None
        """
        data = self.load(golden_set_id)
        if data:
            return data.get("state")
        return None

    def get_section(
        self,
        golden_set_id: str,
        section_key: str,
    ) -> dict[str, Any] | None:
        """
        Get a specific section from a golden set.

        Args:
            golden_set_id: ID of the golden set
            section_key: Key of the section (e.g., 'customer_research')

        Returns:
            The section data or None
        """
        state = self.get_state(golden_set_id)
        if state:
            return state.get(section_key)
        return None

    def delete(self, golden_set_id: str) -> bool:
        """
        Delete a golden set.

        Args:
            golden_set_id: ID of the golden set to delete

        Returns:
            True if deleted successfully
        """
        path = self.golden_sets_dir / f"{golden_set_id}.json"
        try:
            if path.exists():
                path.unlink()
                if golden_set_id in self._cache:
                    del self._cache[golden_set_id]
                logger.info("golden_set_deleted", id=golden_set_id)
                return True
            return False
        except Exception as e:
            logger.error("golden_set_delete_error", id=golden_set_id, error=str(e))
            return False

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()
