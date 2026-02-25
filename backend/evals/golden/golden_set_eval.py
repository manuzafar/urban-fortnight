"""
Golden Set Evaluation — Regression detection against curated baselines.

This module provides comprehensive evaluation of outputs against golden sets,
detecting quality regressions across multiple dimensions.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
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
from evals.golden.similarity_scorer import SimilarityScorer

logger = structlog.get_logger(__name__)


@dataclass
class RegressionWarning:
    """Represents a detected quality regression."""

    section: str
    metric: str
    golden_value: float
    current_value: float
    regression_pct: float
    severity: EvalSeverity


@dataclass
class GoldenSetComparisonResult:
    """Complete comparison result against golden sets."""

    best_match_id: str | None
    best_match_score: float
    regression_detected: bool
    regressions: list[RegressionWarning] = field(default_factory=list)
    section_scores: dict[str, dict[str, float]] = field(default_factory=dict)
    overall_similarity: float = 0.0
    domains_compared: list[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "best_match_id": self.best_match_id,
            "best_match_score": self.best_match_score,
            "regression_detected": self.regression_detected,
            "regressions": [
                {
                    "section": r.section,
                    "metric": r.metric,
                    "golden_value": r.golden_value,
                    "current_value": r.current_value,
                    "regression_pct": r.regression_pct,
                    "severity": r.severity.value,
                }
                for r in self.regressions
            ],
            "section_scores": self.section_scores,
            "overall_similarity": self.overall_similarity,
            "domains_compared": self.domains_compared,
            "message": self.message,
        }


class GoldenSetRegression(BaseEval):
    """
    Evaluates outputs against golden set baselines for regression detection.

    This eval compares new outputs against curated high-quality examples
    and flags significant quality degradation.
    """

    name = "golden_set_regression"
    eval_type = EvalType.GOLDEN
    description = "Detects quality regressions against golden set baselines"
    severity = EvalSeverity.WARNING

    # Thresholds for regression detection
    REGRESSION_THRESHOLD = 0.15  # 15% drop triggers warning
    CRITICAL_REGRESSION_THRESHOLD = 0.30  # 30% drop triggers critical
    MIN_ACCEPTABLE_SIMILARITY = 0.25  # Below this is always a failure

    # Section weights for overall scoring
    SECTION_WEIGHTS = {
        "executive_summary": 0.15,
        "customer_research": 0.20,
        "business_case": 0.15,
        "product_requirements_document": 0.15,
        "technical_architecture": 0.10,
        "gtm_strategy": 0.10,
        "financial_model": 0.10,
        "legal_regulatory_review": 0.05,
    }

    def __init__(self, golden_set_manager: GoldenSetManager | None = None):
        """Initialize with optional golden set manager."""
        self.manager = golden_set_manager or GoldenSetManager()
        self.scorer = SimilarityScorer(self.manager)

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Evaluate agent output against golden sets.

        Args:
            agent_output: The agent's output section
            agent_name: Name of the agent
            context: Must contain 'full_state' for full comparison

        Returns:
            EvalResult with regression analysis
        """
        # Get full state from context
        full_state = context.get("full_state", {}) if context else {}

        # If no golden sets available, pass with info
        golden_sets = self.manager.list_golden_sets()
        if not golden_sets:
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=None,
                severity=EvalSeverity.INFO,
                message="No golden sets available for comparison",
                agent_name=agent_name,
            )

        # Compare against all golden sets
        comparison = self._compare_against_golden_sets(full_state)

        # Determine pass/fail based on regressions
        if comparison.regression_detected:
            critical_regressions = [
                r for r in comparison.regressions
                if r.severity == EvalSeverity.CRITICAL
            ]
            if critical_regressions:
                passed = False
                severity = EvalSeverity.CRITICAL
                message = f"Critical regressions detected in {len(critical_regressions)} section(s)"
            else:
                passed = True  # Warnings don't fail
                severity = EvalSeverity.WARNING
                message = f"Quality regressions detected in {len(comparison.regressions)} section(s)"
        elif comparison.overall_similarity < self.MIN_ACCEPTABLE_SIMILARITY:
            passed = False
            severity = EvalSeverity.WARNING
            message = f"Overall similarity {comparison.overall_similarity:.1%} below minimum threshold"
        else:
            passed = True
            severity = EvalSeverity.INFO
            message = f"No regressions detected. Best match: {comparison.best_match_id} ({comparison.best_match_score:.1%})"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=passed,
            score=comparison.overall_similarity,
            severity=severity,
            message=message,
            agent_name=agent_name,
            details=comparison.to_dict(),
        )

    def _compare_against_golden_sets(
        self,
        state: dict[str, Any],
    ) -> GoldenSetComparisonResult:
        """
        Compare state against all golden sets and detect regressions.

        Args:
            state: The full state to compare

        Returns:
            Comprehensive comparison result
        """
        all_comparisons = self.manager.compare_to_all(state, self.scorer)

        best_match_id = all_comparisons.get("best_match")
        best_score = all_comparisons.get("best_score", 0.0)
        domains = []
        regressions = []
        section_scores = {}

        # Analyze each comparison for regressions
        for gs_id, comp_data in all_comparisons.get("all_comparisons", {}).items():
            domain = comp_data.get("domain", "unknown")
            if domain not in domains:
                domains.append(domain)

            scores = comp_data.get("scores", {})
            sections = scores.get("sections", {})

            for section, section_metrics in sections.items():
                if section not in section_scores:
                    section_scores[section] = {}

                overall = section_metrics.get("overall", 0.0)
                section_scores[section][gs_id] = overall

                # Check for regression (comparing to expected baseline of 0.7+)
                expected_baseline = 0.7  # Golden sets should score 0.7+ similarity
                if overall < expected_baseline:
                    regression_pct = (expected_baseline - overall) / expected_baseline

                    if regression_pct >= self.CRITICAL_REGRESSION_THRESHOLD:
                        severity = EvalSeverity.CRITICAL
                    elif regression_pct >= self.REGRESSION_THRESHOLD:
                        severity = EvalSeverity.WARNING
                    else:
                        continue  # Not significant enough

                    regressions.append(RegressionWarning(
                        section=section,
                        metric="overall_similarity",
                        golden_value=expected_baseline,
                        current_value=overall,
                        regression_pct=regression_pct,
                        severity=severity,
                    ))

        # Calculate weighted overall similarity
        weighted_sum = 0.0
        weight_total = 0.0

        if best_match_id:
            best_comparison = all_comparisons.get("all_comparisons", {}).get(best_match_id, {})
            best_sections = best_comparison.get("scores", {}).get("sections", {})

            for section, weight in self.SECTION_WEIGHTS.items():
                if section in best_sections:
                    weighted_sum += best_sections[section].get("overall", 0.0) * weight
                    weight_total += weight

        overall_similarity = weighted_sum / weight_total if weight_total > 0 else best_score

        return GoldenSetComparisonResult(
            best_match_id=best_match_id,
            best_match_score=best_score,
            regression_detected=len(regressions) > 0,
            regressions=regressions,
            section_scores=section_scores,
            overall_similarity=overall_similarity,
            domains_compared=domains,
            message=f"Compared against {len(all_comparisons.get('all_comparisons', {}))} golden sets",
        )


class GoldenSetCoverage(BaseEval):
    """
    Evaluates whether output contains all sections present in golden sets.

    This eval ensures outputs are complete relative to golden baselines.
    """

    name = "golden_set_coverage"
    eval_type = EvalType.GOLDEN
    description = "Checks output completeness against golden set structure"
    severity = EvalSeverity.WARNING

    REQUIRED_SECTIONS = [
        "executive_summary",
        "customer_research",
        "business_case",
        "product_requirements_document",
        "technical_architecture",
    ]

    OPTIONAL_SECTIONS = [
        "gtm_strategy",
        "financial_model",
        "legal_regulatory_review",
        "risk_assessment",
        "stakeholder_views",
        "validation_playbook",
    ]

    def __init__(self, golden_set_manager: GoldenSetManager | None = None):
        """Initialize with optional golden set manager."""
        self.manager = golden_set_manager or GoldenSetManager()

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Evaluate output coverage against golden sets.

        Args:
            agent_output: The agent's output
            agent_name: Name of the agent
            context: Must contain 'full_state' for coverage analysis

        Returns:
            EvalResult with coverage analysis
        """
        full_state = context.get("full_state", {}) if context else {}

        # Check required sections
        missing_required = []
        for section in self.REQUIRED_SECTIONS:
            if not full_state.get(section):
                missing_required.append(section)

        # Check optional sections
        present_optional = []
        for section in self.OPTIONAL_SECTIONS:
            if full_state.get(section):
                present_optional.append(section)

        # Calculate coverage score
        required_coverage = (len(self.REQUIRED_SECTIONS) - len(missing_required)) / len(self.REQUIRED_SECTIONS)
        total_sections = len(self.REQUIRED_SECTIONS) + len(self.OPTIONAL_SECTIONS)
        present_sections = len(self.REQUIRED_SECTIONS) - len(missing_required) + len(present_optional)
        total_coverage = present_sections / total_sections

        # Determine pass/fail
        if missing_required:
            passed = False
            severity = EvalSeverity.WARNING
            message = f"Missing required sections: {', '.join(missing_required)}"
        else:
            passed = True
            severity = EvalSeverity.INFO
            message = f"All required sections present. Coverage: {total_coverage:.1%}"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=passed,
            score=total_coverage,
            severity=severity,
            message=message,
            agent_name=agent_name,
            details={
                "required_coverage": required_coverage,
                "total_coverage": total_coverage,
                "missing_required": missing_required,
                "present_optional": present_optional,
            },
        )


def run_golden_set_comparison(
    state_path: str | Path,
    output_path: str | Path | None = None,
) -> GoldenSetComparisonResult:
    """
    Run a standalone golden set comparison on a state file.

    Args:
        state_path: Path to the state JSON file
        output_path: Optional path to save comparison results

    Returns:
        GoldenSetComparisonResult with full analysis
    """
    # Load state
    with open(state_path) as f:
        state = json.load(f)

    # Run comparison
    manager = GoldenSetManager()
    scorer = SimilarityScorer(manager)
    eval_instance = GoldenSetRegression(manager)

    comparison = eval_instance._compare_against_golden_sets(state)

    # Save results if output path provided
    if output_path:
        with open(output_path, "w") as f:
            json.dump(comparison.to_dict(), f, indent=2)

    return comparison


# Register the evals
EvalRegistry.register(GoldenSetRegression())
EvalRegistry.register(GoldenSetCoverage())
