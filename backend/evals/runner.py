"""
Eval Runner — Orchestrates running evaluations on agent outputs.

This module provides the main entry point for running evaluations,
handling parallel execution, result aggregation, and error handling.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Optional

import structlog

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalSuiteResult,
    EvalType,
)

logger = structlog.get_logger(__name__)


# Mapping of state keys to agent names
STATE_KEY_TO_AGENT: dict[str, str] = {
    "customer_research": "customer_research",
    "business_case": "business_strategy",
    "product_requirements_document": "product_requirements",
    "technical_architecture": "technical_architect",
    "legal_regulatory_review": "legal_regulatory",
    "executive_summary": "executive_summary",
    "gtm_strategy": "gtm_agent",
    "financial_model": "financial_model_agent",
    "risk_assessment": "risk_assessment",
    "stakeholder_views": "stakeholder_views",
    "validation_playbook": "validation_playbook",
    "wireframes": "wireframe_agent",
    "prototype": "prototype_agent",
    "competitive_analysis": "competitive_intelligence",
    "detailed_personas": "persona_development",
    "cross_reference_index": "planner",
}


class EvalRunner:
    """
    Orchestrates running evaluations on agent outputs.

    The runner can:
    - Run all registered evals on a state file
    - Run only specific types of evals (unit, llm_judge, etc.)
    - Run evals for specific agents
    - Compare outputs against golden sets
    """

    def __init__(
        self,
        eval_types: list[EvalType] | None = None,
        agents: list[str] | None = None,
        golden_set_path: str | None = None,
        parallel: bool = True,
    ):
        """
        Initialize the eval runner.

        Args:
            eval_types: Types of evals to run (None = all)
            agents: Specific agents to evaluate (None = all)
            golden_set_path: Path to golden set for comparison
            parallel: Whether to run evals in parallel
        """
        self.eval_types = eval_types
        self.agents = agents
        self.golden_set_path = golden_set_path
        self.parallel = parallel
        self._golden_set: dict[str, Any] | None = None

    async def run(
        self,
        state_path: str | Path,
    ) -> EvalSuiteResult:
        """
        Run all applicable evaluations on a state file.

        Args:
            state_path: Path to the state JSON file

        Returns:
            EvalSuiteResult with all evaluation results
        """
        start_time = time.time()

        # Load state
        state = self._load_state(state_path)
        if state is None:
            return self._create_error_result("Failed to load state file")

        # Load golden set if specified
        if self.golden_set_path:
            self._golden_set = self._load_golden_set(self.golden_set_path)

        # Get applicable evals
        evals = self._get_applicable_evals()
        if not evals:
            return self._create_error_result("No applicable evaluations found")

        logger.info(
            "eval_run_start",
            state_path=str(state_path),
            eval_count=len(evals),
            eval_types=[e.eval_type.value for e in evals],
        )

        # Run evaluations
        if self.parallel:
            results = await self._run_parallel(evals, state)
        else:
            results = await self._run_sequential(evals, state)

        # Aggregate results
        duration = time.time() - start_time
        suite_result = self._aggregate_results(results, duration)

        logger.info(
            "eval_run_complete",
            total_evals=suite_result.total_evals,
            passed=suite_result.passed,
            failed=suite_result.failed,
            overall_score=suite_result.overall_score,
            duration=round(duration, 2),
        )

        return suite_result

    async def run_on_output(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> list[EvalResult]:
        """
        Run evaluations on a single agent output.

        Args:
            agent_output: The agent's output to evaluate
            agent_name: Name of the agent
            context: Optional additional context

        Returns:
            List of evaluation results
        """
        evals = self._get_applicable_evals()
        applicable_evals = [e for e in evals if e.is_applicable_to(agent_name)]

        results = []
        for eval_instance in applicable_evals:
            try:
                result = await eval_instance.evaluate(
                    agent_output,
                    agent_name,
                    context,
                )
                results.append(result)
            except Exception as e:
                logger.error(
                    "eval_execution_error",
                    eval_name=eval_instance.name,
                    agent_name=agent_name,
                    error=str(e),
                )
                results.append(
                    EvalResult(
                        eval_name=eval_instance.name,
                        eval_type=eval_instance.eval_type,
                        passed=False,
                        severity=EvalSeverity.WARNING,
                        message=f"Eval execution error: {str(e)}",
                        agent_name=agent_name,
                    )
                )

        return results

    def _load_state(self, state_path: str | Path) -> dict[str, Any] | None:
        """Load and validate the state file."""
        try:
            path = Path(state_path)
            if not path.exists():
                logger.error("state_file_not_found", path=str(path))
                return None

            with open(path) as f:
                state = json.load(f)

            return state
        except json.JSONDecodeError as e:
            logger.error("state_file_invalid_json", error=str(e))
            return None
        except Exception as e:
            logger.error("state_file_load_error", error=str(e))
            return None

    def _load_golden_set(self, golden_path: str) -> dict[str, Any] | None:
        """Load a golden set for comparison."""
        try:
            # Check in fixtures directory first
            fixtures_path = Path(__file__).parent / "fixtures" / "golden_sets" / f"{golden_path}.json"
            if fixtures_path.exists():
                with open(fixtures_path) as f:
                    return json.load(f)

            # Try as absolute/relative path
            path = Path(golden_path)
            if path.exists():
                with open(path) as f:
                    return json.load(f)

            logger.warning("golden_set_not_found", path=golden_path)
            return None
        except Exception as e:
            logger.error("golden_set_load_error", error=str(e))
            return None

    def _get_applicable_evals(self) -> list[BaseEval]:
        """Get evaluations to run based on filters."""
        all_evals = EvalRegistry.get_all()

        # Filter by type if specified
        if self.eval_types:
            all_evals = [e for e in all_evals if e.eval_type in self.eval_types]

        return all_evals

    async def _run_parallel(
        self,
        evals: list[BaseEval],
        state: dict[str, Any],
    ) -> list[EvalResult]:
        """Run evaluations in parallel."""
        tasks = []

        for state_key, agent_name in STATE_KEY_TO_AGENT.items():
            # Skip if filtering by agent
            if self.agents and agent_name not in self.agents:
                continue

            agent_output = state.get(state_key)
            if not agent_output:
                continue

            # Get evals applicable to this agent
            applicable_evals = [e for e in evals if e.is_applicable_to(agent_name)]

            for eval_instance in applicable_evals:
                context = {
                    "full_state": state,
                    "golden_set": self._golden_set,
                }
                tasks.append(
                    self._run_single_eval(eval_instance, agent_output, agent_name, context)
                )

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error("eval_task_exception", error=str(result))
            elif isinstance(result, EvalResult):
                final_results.append(result)

        return final_results

    async def _run_sequential(
        self,
        evals: list[BaseEval],
        state: dict[str, Any],
    ) -> list[EvalResult]:
        """Run evaluations sequentially."""
        results = []

        for state_key, agent_name in STATE_KEY_TO_AGENT.items():
            # Skip if filtering by agent
            if self.agents and agent_name not in self.agents:
                continue

            agent_output = state.get(state_key)
            if not agent_output:
                continue

            # Get evals applicable to this agent
            applicable_evals = [e for e in evals if e.is_applicable_to(agent_name)]

            for eval_instance in applicable_evals:
                context = {
                    "full_state": state,
                    "golden_set": self._golden_set,
                }
                result = await self._run_single_eval(
                    eval_instance, agent_output, agent_name, context
                )
                results.append(result)

        return results

    async def _run_single_eval(
        self,
        eval_instance: BaseEval,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None,
    ) -> EvalResult:
        """Run a single evaluation with timing and error handling."""
        start_time = time.time()

        try:
            result = await eval_instance.evaluate(agent_output, agent_name, context)
            result.duration_seconds = time.time() - start_time
            return result
        except Exception as e:
            logger.error(
                "eval_execution_error",
                eval_name=eval_instance.name,
                agent_name=agent_name,
                error=str(e),
            )
            return EvalResult(
                eval_name=eval_instance.name,
                eval_type=eval_instance.eval_type,
                passed=False,
                severity=EvalSeverity.WARNING,
                message=f"Eval execution error: {str(e)}",
                agent_name=agent_name,
                duration_seconds=time.time() - start_time,
            )

    def _aggregate_results(
        self,
        results: list[EvalResult],
        duration: float,
    ) -> EvalSuiteResult:
        """Aggregate individual results into a suite result."""
        if not results:
            return EvalSuiteResult(
                suite_name="eval_suite",
                total_evals=0,
                passed=0,
                failed=0,
                warnings=0,
                overall_score=0.0,
                results=[],
                duration_seconds=duration,
            )

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed and r.severity != EvalSeverity.INFO)
        warnings = sum(1 for r in results if not r.passed and r.severity == EvalSeverity.WARNING)

        # Calculate overall score
        scores = [r.score for r in results if r.score is not None]
        overall_score = sum(scores) / len(scores) if scores else (passed / len(results))

        # Identify critical failures
        critical_failures = [
            r.eval_name for r in results
            if not r.passed and r.severity == EvalSeverity.CRITICAL
        ]

        return EvalSuiteResult(
            suite_name="eval_suite",
            total_evals=len(results),
            passed=passed,
            failed=failed,
            warnings=warnings,
            overall_score=round(overall_score, 3),
            results=results,
            critical_failures=critical_failures,
            duration_seconds=duration,
        )

    def _create_error_result(self, message: str) -> EvalSuiteResult:
        """Create an error suite result."""
        return EvalSuiteResult(
            suite_name="eval_suite",
            total_evals=0,
            passed=0,
            failed=1,
            warnings=0,
            overall_score=0.0,
            results=[
                EvalResult(
                    eval_name="suite_error",
                    eval_type=EvalType.UNIT,
                    passed=False,
                    severity=EvalSeverity.CRITICAL,
                    message=message,
                )
            ],
            critical_failures=["suite_error"],
        )
