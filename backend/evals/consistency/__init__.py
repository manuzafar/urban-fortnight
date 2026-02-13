"""Consistency evaluations — cross-section contradiction and numerical checks."""

from evals.consistency.contradiction_detector import ContradictionDetectorEval
from evals.consistency.numerical_consistency import NumericalConsistencyEval

__all__ = [
    "ContradictionDetectorEval",
    "NumericalConsistencyEval",
]
