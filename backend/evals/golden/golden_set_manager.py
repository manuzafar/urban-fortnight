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


# Default location for golden sets - now in evals/golden/sets/
GOLDEN_SETS_DIR = Path(__file__).parent / "sets"

# Fallback to legacy location for backwards compatibility
LEGACY_GOLDEN_SETS_DIR = Path(__file__).parent.parent / "fixtures" / "golden_sets"


class GoldenSetManager:
    """
    Manages golden set storage, loading, and versioning.

    Golden sets are JSON files containing:
    - metadata: version, name, created_at, quality_score
    - state: the full inception pack state
    """

    def __init__(self, golden_sets_dir: Path | str | None = None):
        """Initialize with optional custom directory."""
        if golden_sets_dir:
            self.golden_sets_dir = Path(golden_sets_dir)
        elif GOLDEN_SETS_DIR.exists():
            self.golden_sets_dir = GOLDEN_SETS_DIR
        elif LEGACY_GOLDEN_SETS_DIR.exists():
            self.golden_sets_dir = LEGACY_GOLDEN_SETS_DIR
        else:
            self.golden_sets_dir = GOLDEN_SETS_DIR
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
                    "domain": metadata.get("domain", ""),
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

    def list_by_domain(self, domain: str) -> list[dict[str, Any]]:
        """
        List golden sets filtered by domain.

        Args:
            domain: Domain to filter by (e.g., 'B2B_SaaS', 'Fintech', 'Healthcare')

        Returns:
            List of golden sets matching the domain
        """
        all_sets = self.list_golden_sets()
        return [
            gs for gs in all_sets
            if gs.get("domain", "").lower() == domain.lower()
            or domain.lower() in gs.get("id", "").lower()
        ]

    def find_best_match(self, product_idea: str) -> dict[str, Any] | None:
        """
        Find the golden set most similar to a given product idea.

        Uses simple keyword matching for domain detection.

        Args:
            product_idea: The product idea to match against

        Returns:
            Best matching golden set info or None
        """
        idea_lower = product_idea.lower()

        # Domain keywords
        domain_keywords = {
            "healthcare": ["health", "medical", "patient", "doctor", "hospital", "clinic", "care"],
            "fintech": ["payment", "bank", "finance", "money", "transaction", "lending", "crypto"],
            "b2b_saas": ["enterprise", "saas", "b2b", "business", "workspace", "team", "collaboration"],
        }

        # Find matching domain
        best_domain = None
        best_score = 0

        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in idea_lower)
            if score > best_score:
                best_score = score
                best_domain = domain

        # Get golden sets for that domain
        if best_domain:
            domain_sets = self.list_by_domain(best_domain)
            if domain_sets:
                return domain_sets[0]

        # Fallback to first available golden set
        all_sets = self.list_golden_sets()
        return all_sets[0] if all_sets else None

    def get_all_golden_states(self) -> dict[str, dict[str, Any]]:
        """
        Load all golden sets and return their states.

        Returns:
            Dictionary mapping golden set ID to state
        """
        result = {}
        for gs_info in self.list_golden_sets():
            gs_id = gs_info["id"]
            state = self.get_state(gs_id)
            if state:
                result[gs_id] = state
        return result

    def compare_to_all(
        self,
        state: dict[str, Any],
        scorer: Any = None,
    ) -> dict[str, Any]:
        """
        Compare a state against all golden sets and find best match.

        Args:
            state: The state to compare
            scorer: Optional SimilarityScorer instance

        Returns:
            Comparison results with best match and all scores
        """
        if scorer is None:
            from evals.golden.similarity_scorer import SimilarityScorer
            scorer = SimilarityScorer(self)

        results = {}
        best_match = None
        best_score = 0.0

        for gs_info in self.list_golden_sets():
            gs_id = gs_info["id"]
            golden_state = self.get_state(gs_id)

            if golden_state:
                comparison = scorer.score_full_state(state, golden_state)
                results[gs_id] = {
                    "name": gs_info.get("name", gs_id),
                    "domain": gs_info.get("domain", "unknown"),
                    "scores": comparison,
                }

                if comparison["overall"] > best_score:
                    best_score = comparison["overall"]
                    best_match = gs_id

        return {
            "best_match": best_match,
            "best_score": best_score,
            "all_comparisons": results,
        }
