"""Golden Set evaluations — regression detection against curated baselines."""

from evals.golden.golden_set_manager import GoldenSetManager
from evals.golden.similarity_scorer import SimilarityScorer, GoldenSetEval
from evals.golden.golden_set_eval import (
    GoldenSetRegression,
    GoldenSetCoverage,
    GoldenSetComparisonResult,
    RegressionWarning,
    run_golden_set_comparison,
)

__all__ = [
    "GoldenSetManager",
    "SimilarityScorer",
    "GoldenSetEval",
    "GoldenSetRegression",
    "GoldenSetCoverage",
    "GoldenSetComparisonResult",
    "RegressionWarning",
    "run_golden_set_comparison",
]
