"""Golden Set evaluations — regression detection against curated baselines."""

from evals.golden.golden_set_manager import GoldenSetManager
from evals.golden.similarity_scorer import SimilarityScorer, GoldenSetEval

__all__ = [
    "GoldenSetManager",
    "SimilarityScorer",
    "GoldenSetEval",
]
