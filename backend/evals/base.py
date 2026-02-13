"""
Base classes and types for the eval system.

This module provides the foundational abstractions for all evaluation types:
- BaseEval: Abstract base class for all evaluators
- EvalResult: Result of a single evaluation
- EvalSuiteResult: Aggregated results from multiple evaluations
- EvalRegistry: Registry for discovering and managing evaluators
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from datetime import datetime


class EvalType(str, Enum):
    """Types of evaluations supported."""

    UNIT = "unit"
    LLM_JUDGE = "llm_judge"
    GOLDEN = "golden"
    CONSISTENCY = "consistency"
    AGENT_SPECIFIC = "agent_specific"


class EvalSeverity(str, Enum):
    """Severity levels for eval failures."""

    CRITICAL = "critical"  # Blocks PR
    WARNING = "warning"    # Should review
    INFO = "info"          # Informational


@dataclass
class EvalResult:
    """
    Result of a single evaluation.

    Attributes:
        eval_name: Name of the evaluation
        eval_type: Type of evaluation (unit, llm_judge, etc.)
        passed: Whether the evaluation passed
        score: Optional numeric score (0.0-1.0)
        severity: Severity level if failed
        message: Human-readable description of result
        details: Additional structured details
        agent_name: Name of the agent being evaluated (if applicable)
        duration_seconds: Time taken to run the evaluation
    """

    eval_name: str
    eval_type: EvalType
    passed: bool
    score: Optional[float] = None
    severity: EvalSeverity = EvalSeverity.INFO
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    agent_name: Optional[str] = None
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "eval_name": self.eval_name,
            "eval_type": self.eval_type.value,
            "passed": self.passed,
            "score": self.score,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "agent_name": self.agent_name,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }


@dataclass
class EvalSuiteResult:
    """
    Aggregated results from running multiple evaluations.

    Attributes:
        suite_name: Name of the evaluation suite
        total_evals: Total number of evaluations run
        passed: Number of evaluations that passed
        failed: Number of evaluations that failed
        warnings: Number of evaluations with warnings
        overall_score: Weighted overall score (0.0-1.0)
        results: Individual evaluation results
        critical_failures: List of critical failures that should block PR
        duration_seconds: Total time for all evaluations
    """

    suite_name: str
    total_evals: int
    passed: int
    failed: int
    warnings: int
    overall_score: float
    results: list[EvalResult] = field(default_factory=list)
    critical_failures: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def has_critical_failures(self) -> bool:
        """Check if there are any critical failures."""
        return len(self.critical_failures) > 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_evals == 0:
            return 100.0
        return (self.passed / self.total_evals) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "suite_name": self.suite_name,
            "total_evals": self.total_evals,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "overall_score": self.overall_score,
            "success_rate": self.success_rate,
            "has_critical_failures": self.has_critical_failures,
            "critical_failures": self.critical_failures,
            "results": [r.to_dict() for r in self.results],
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }


class BaseEval(ABC):
    """
    Abstract base class for all evaluations.

    Subclasses must implement the evaluate() method to perform
    the actual evaluation logic.

    Attributes:
        name: Unique identifier for this evaluation
        eval_type: Type of evaluation (unit, llm_judge, etc.)
        description: Human-readable description
        severity: Default severity level for failures
        applicable_agents: List of agent names this eval applies to (None = all)
    """

    name: str
    eval_type: EvalType
    description: str
    severity: EvalSeverity = EvalSeverity.WARNING
    applicable_agents: Optional[list[str]] = None

    @abstractmethod
    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Perform the evaluation on agent output.

        Args:
            agent_output: The output from an agent to evaluate
            agent_name: Name of the agent that produced the output
            context: Optional additional context (full state, golden set, etc.)

        Returns:
            EvalResult with the evaluation outcome
        """
        pass

    def is_applicable_to(self, agent_name: str) -> bool:
        """Check if this eval applies to the given agent."""
        if self.applicable_agents is None:
            return True
        return agent_name in self.applicable_agents


class EvalRegistry:
    """
    Registry for discovering and managing evaluations.

    This singleton registry allows evals to be registered at module load time
    and then discovered and run by the EvalRunner.
    """

    _evals: dict[str, BaseEval] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, eval_instance: BaseEval) -> BaseEval:
        """
        Register an evaluation instance.

        Args:
            eval_instance: The evaluation to register

        Returns:
            The registered evaluation (for decorator chaining)
        """
        cls._evals[eval_instance.name] = eval_instance
        return eval_instance

    @classmethod
    def get(cls, name: str) -> BaseEval | None:
        """Get an evaluation by name."""
        cls._ensure_initialized()
        return cls._evals.get(name)

    @classmethod
    def get_all(cls) -> list[BaseEval]:
        """Get all registered evaluations."""
        cls._ensure_initialized()
        return list(cls._evals.values())

    @classmethod
    def get_by_type(cls, eval_type: EvalType) -> list[BaseEval]:
        """Get all evaluations of a specific type."""
        cls._ensure_initialized()
        return [e for e in cls._evals.values() if e.eval_type == eval_type]

    @classmethod
    def get_for_agent(cls, agent_name: str) -> list[BaseEval]:
        """Get all evaluations applicable to a specific agent."""
        cls._ensure_initialized()
        return [e for e in cls._evals.values() if e.is_applicable_to(agent_name)]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered evaluations (useful for testing)."""
        cls._evals.clear()
        cls._initialized = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure all eval modules are imported."""
        if cls._initialized:
            return

        # Import all eval modules to trigger registration
        try:
            from evals.unit import schema_compliance, evidence_tier
            from evals.agents import (
                customer_research_eval,
                competitive_analysis_eval,
                persona_eval,
                business_case_eval,
                gtm_strategy_eval,
                financial_model_eval,
                prd_eval,
                technical_architecture_eval,
                legal_regulatory_eval,
                risk_assessment_eval,
                executive_summary_eval,
                stakeholder_views_eval,
                validation_playbook_eval,
                wireframes_eval,
                prototype_eval,
                planner_eval,
            )
            from evals.llm_judge import multi_dimension_judge
            from evals.golden import similarity_scorer
            from evals.consistency import contradiction_detector, numerical_consistency
        except ImportError:
            # Some modules may not exist yet during development
            pass

        cls._initialized = True


def register_eval(eval_class: type[BaseEval]) -> type[BaseEval]:
    """
    Decorator to register an eval class automatically.

    Usage:
        @register_eval
        class MyEval(BaseEval):
            name = "my_eval"
            ...
    """
    instance = eval_class()
    EvalRegistry.register(instance)
    return eval_class
