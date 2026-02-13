"""
Similarity Scorer — Compares outputs against golden sets.

Uses structural similarity and key overlap analysis to detect
regressions from curated baselines.
"""

import json
from difflib import SequenceMatcher
from typing import Any

import structlog

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)
from evals.golden.golden_set_manager import GoldenSetManager

logger = structlog.get_logger(__name__)


class SimilarityScorer:
    """
    Calculates similarity between outputs and golden sets.

    Uses multiple metrics:
    - Structural similarity (key overlap)
    - Content similarity (SequenceMatcher)
    - Field coverage (required fields present)
    """

    def __init__(self, golden_set_manager: GoldenSetManager | None = None):
        """Initialize with optional golden set manager."""
        self.golden_set_manager = golden_set_manager or GoldenSetManager()

    def score_section(
        self,
        section_output: dict[str, Any],
        golden_section: dict[str, Any],
    ) -> dict[str, float]:
        """
        Calculate similarity scores for a section.

        Args:
            section_output: The output section to evaluate
            golden_section: The golden baseline section

        Returns:
            Dictionary with similarity metrics
        """
        # Structural similarity (key overlap)
        output_keys = set(self._extract_keys(section_output))
        golden_keys = set(self._extract_keys(golden_section))

        key_overlap = len(output_keys & golden_keys) / max(len(golden_keys), 1)

        # Content similarity (stringify and compare)
        output_str = json.dumps(section_output, sort_keys=True, default=str)
        golden_str = json.dumps(golden_section, sort_keys=True, default=str)

        content_similarity = SequenceMatcher(
            None, output_str, golden_str
        ).ratio()

        # Field coverage
        required_fields = golden_keys  # All golden fields are "required"
        coverage = len(output_keys & required_fields) / max(len(required_fields), 1)

        # Length comparison (too short or too long is suspicious)
        length_ratio = len(output_str) / max(len(golden_str), 1)
        length_score = 1.0 - abs(1.0 - length_ratio) if length_ratio <= 2 else 0.5

        return {
            "key_overlap": round(key_overlap, 3),
            "content_similarity": round(content_similarity, 3),
            "field_coverage": round(coverage, 3),
            "length_score": round(length_score, 3),
            "overall": round(
                (key_overlap * 0.3 + content_similarity * 0.3 +
                 coverage * 0.3 + length_score * 0.1),
                3
            ),
        }

    def score_full_state(
        self,
        state: dict[str, Any],
        golden_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Calculate similarity scores for the full state.

        Args:
            state: The state to evaluate
            golden_state: The golden baseline state

        Returns:
            Dictionary with per-section and overall scores
        """
        section_scores = {}

        # Key sections to compare
        sections = [
            "customer_research",
            "business_case",
            "product_requirements_document",
            "technical_architecture",
            "executive_summary",
            "gtm_strategy",
            "financial_model",
            "legal_regulatory_review",
        ]

        for section in sections:
            output_section = state.get(section)
            golden_section = golden_state.get(section)

            if output_section and golden_section:
                section_scores[section] = self.score_section(
                    output_section, golden_section
                )

        # Calculate overall score
        if section_scores:
            overall_scores = [s["overall"] for s in section_scores.values()]
            overall = sum(overall_scores) / len(overall_scores)
        else:
            overall = 0.0

        return {
            "sections": section_scores,
            "overall": round(overall, 3),
            "sections_compared": len(section_scores),
        }

    def _extract_keys(self, data: Any, prefix: str = "") -> list[str]:
        """Recursively extract all keys from nested structure."""
        keys = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                keys.extend(self._extract_keys(value, full_key))
        elif isinstance(data, list) and len(data) > 0:
            # Just check first item structure
            keys.extend(self._extract_keys(data[0], f"{prefix}[0]"))

        return keys


class GoldenSetEval(BaseEval):
    """
    Evaluates outputs against golden set baselines.

    This eval detects regressions by comparing new outputs
    to curated high-quality examples.
    """

    name = "golden_set_similarity"
    eval_type = EvalType.GOLDEN
    description = "Compares output against golden set baseline"
    severity = EvalSeverity.WARNING

    # Thresholds
    MIN_SIMILARITY = 0.3
    WARN_SIMILARITY = 0.5

    def __init__(self):
        """Initialize with scorer."""
        self.scorer = SimilarityScorer()

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Evaluate output against golden set.

        Args:
            agent_output: The agent's output
            agent_name: Name of the agent
            context: Must contain 'golden_set' with golden state

        Returns:
            EvalResult with similarity scores
        """
        # Get golden set from context
        if not context or "golden_set" not in context:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message="No golden set provided for comparison",
                agent_name=agent_name,
            )

        golden_data = context["golden_set"]
        if not golden_data:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message="Golden set is empty",
                agent_name=agent_name,
            )

        # Get golden state (may be nested)
        golden_state = golden_data.get("state", golden_data)

        # Get the section for this agent
        section_key = self._agent_to_section(agent_name)
        golden_section = golden_state.get(section_key)

        if not golden_section:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message=f"No golden section found for '{section_key}'",
                agent_name=agent_name,
            )

        # Calculate similarity
        scores = self.scorer.score_section(agent_output, golden_section)
        overall = scores["overall"]

        # Determine pass/fail
        if overall >= self.WARN_SIMILARITY:
            passed = True
            severity = EvalSeverity.INFO
            message = f"Good similarity to golden set: {overall:.1%}"
        elif overall >= self.MIN_SIMILARITY:
            passed = True
            severity = EvalSeverity.WARNING
            message = f"Moderate similarity to golden set: {overall:.1%}"
        else:
            passed = False
            severity = self.severity
            message = f"Low similarity to golden set: {overall:.1%} (threshold: {self.MIN_SIMILARITY:.0%})"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=passed,
            score=overall,
            severity=severity,
            message=message,
            agent_name=agent_name,
            details={
                "scores": scores,
                "thresholds": {
                    "minimum": self.MIN_SIMILARITY,
                    "warning": self.WARN_SIMILARITY,
                },
            },
        )

    def _agent_to_section(self, agent_name: str) -> str:
        """Map agent name to state section key."""
        mapping = {
            "customer_research": "customer_research",
            "business_strategy": "business_case",
            "product_requirements": "product_requirements_document",
            "technical_architect": "technical_architecture",
            "legal_regulatory": "legal_regulatory_review",
            "executive_summary": "executive_summary",
            "gtm_agent": "gtm_strategy",
            "financial_model_agent": "financial_model",
            "stakeholder_views": "stakeholder_views",
            "validation_playbook": "validation_playbook",
            "wireframe_agent": "wireframes",
            "prototype_agent": "prototype",
        }
        return mapping.get(agent_name, agent_name)


# Register the eval
EvalRegistry.register(GoldenSetEval())
