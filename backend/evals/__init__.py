"""
Agent Eval System for the Product Discovery Multi-Agent System.

This module provides comprehensive evaluation capabilities for measuring
and improving agent quality across the 15+ agents generating inception packs.

Eval Types:
    - Unit Evals: Fast, deterministic schema/completeness checks
    - LLM-as-Judge Evals: Qualitative evaluation of accuracy, relevance, actionability
    - Golden Set Evals: Regression detection against curated baselines
    - Cross-Section Consistency Evals: Contradiction and numerical consistency checks
"""

from evals.base import (
    BaseEval,
    EvalResult,
    EvalSeverity,
    EvalSuiteResult,
    EvalType,
    EvalRegistry,
)
from evals.runner import EvalRunner
from evals.reporter import EvalReporter

__all__ = [
    "BaseEval",
    "EvalResult",
    "EvalSeverity",
    "EvalSuiteResult",
    "EvalType",
    "EvalRegistry",
    "EvalRunner",
    "EvalReporter",
]
