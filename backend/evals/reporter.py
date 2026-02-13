"""
Eval Reporter — Aggregates and formats evaluation results.

This module provides reporting utilities for presenting evaluation
results in various formats (JSON, console, markdown).
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from evals.base import EvalResult, EvalSeverity, EvalSuiteResult, EvalType


class EvalReporter:
    """
    Reports evaluation results in various formats.

    Supports:
    - Console output with colors and formatting
    - JSON output for CI integration
    - Markdown output for documentation
    - Per-agent summaries
    """

    def __init__(self, suite_result: EvalSuiteResult):
        """Initialize with a suite result."""
        self.suite_result = suite_result

    def to_console(self, verbose: bool = False) -> str:
        """
        Generate console-friendly output.

        Args:
            verbose: Include detailed information for each eval

        Returns:
            Formatted string for console output
        """
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("EVAL SUITE RESULTS")
        lines.append("=" * 60)
        lines.append("")

        # Summary
        status_icon = "✅" if not self.suite_result.has_critical_failures else "❌"
        lines.append(f"{status_icon} Overall Score: {self.suite_result.overall_score:.1%}")
        lines.append(f"   Total Evals: {self.suite_result.total_evals}")
        lines.append(f"   Passed: {self.suite_result.passed}")
        lines.append(f"   Failed: {self.suite_result.failed}")
        lines.append(f"   Warnings: {self.suite_result.warnings}")
        lines.append(f"   Duration: {self.suite_result.duration_seconds:.2f}s")
        lines.append("")

        # Critical failures
        if self.suite_result.has_critical_failures:
            lines.append("❌ CRITICAL FAILURES (blocks PR):")
            for failure in self.suite_result.critical_failures:
                lines.append(f"   - {failure}")
            lines.append("")

        # Group by agent
        by_agent = self._group_by_agent()

        lines.append("-" * 60)
        lines.append("Results by Agent:")
        lines.append("-" * 60)

        for agent_name, results in sorted(by_agent.items()):
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            agent_icon = "✅" if passed == total else ("⚠️" if passed > 0 else "❌")
            lines.append(f"\n{agent_icon} {agent_name}: {passed}/{total} passed")

            if verbose:
                for result in results:
                    icon = "✓" if result.passed else "✗"
                    score_str = f" ({result.score:.1%})" if result.score else ""
                    lines.append(f"      {icon} {result.eval_name}{score_str}")
                    if not result.passed and result.message:
                        lines.append(f"        └─ {result.message[:80]}")

        # Group by eval type
        by_type = self._group_by_type()

        lines.append("")
        lines.append("-" * 60)
        lines.append("Results by Type:")
        lines.append("-" * 60)

        for eval_type, results in sorted(by_type.items(), key=lambda x: x[0].value):
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            type_icon = "✅" if passed == total else ("⚠️" if passed > 0 else "❌")
            lines.append(f"   {type_icon} {eval_type.value}: {passed}/{total} passed")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def to_json(self, indent: int = 2) -> str:
        """
        Generate JSON output for CI integration.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string representation
        """
        return json.dumps(self.suite_result.to_dict(), indent=indent, default=str)

    def to_markdown(self) -> str:
        """
        Generate markdown output for documentation.

        Returns:
            Markdown formatted string
        """
        lines = []

        # Title
        status = "✅ Passed" if not self.suite_result.has_critical_failures else "❌ Failed"
        lines.append(f"# Eval Suite Results {status}")
        lines.append("")

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Overall Score | {self.suite_result.overall_score:.1%} |")
        lines.append(f"| Total Evals | {self.suite_result.total_evals} |")
        lines.append(f"| Passed | {self.suite_result.passed} |")
        lines.append(f"| Failed | {self.suite_result.failed} |")
        lines.append(f"| Warnings | {self.suite_result.warnings} |")
        lines.append(f"| Duration | {self.suite_result.duration_seconds:.2f}s |")
        lines.append("")

        # Critical failures
        if self.suite_result.has_critical_failures:
            lines.append("## ❌ Critical Failures")
            lines.append("")
            for failure in self.suite_result.critical_failures:
                lines.append(f"- `{failure}`")
            lines.append("")

        # Results by agent
        by_agent = self._group_by_agent()
        lines.append("## Results by Agent")
        lines.append("")

        for agent_name, results in sorted(by_agent.items()):
            passed = sum(1 for r in results if r.passed)
            total = len(results)
            status_icon = "✅" if passed == total else ("⚠️" if passed > 0 else "❌")

            lines.append(f"### {status_icon} {agent_name}")
            lines.append("")
            lines.append(f"Passed: {passed}/{total}")
            lines.append("")
            lines.append("| Eval | Status | Score | Message |")
            lines.append("|------|--------|-------|---------|")

            for result in results:
                status = "✅" if result.passed else "❌"
                score = f"{result.score:.1%}" if result.score else "-"
                message = result.message[:50] + "..." if len(result.message) > 50 else result.message
                lines.append(f"| {result.eval_name} | {status} | {score} | {message} |")

            lines.append("")

        return "\n".join(lines)

    def save(self, output_path: str | Path, format: str = "json") -> None:
        """
        Save results to a file.

        Args:
            output_path: Path to save results
            format: Output format (json, markdown, or console)
        """
        path = Path(output_path)

        if format == "json":
            content = self.to_json()
        elif format == "markdown":
            content = self.to_markdown()
        else:
            content = self.to_console(verbose=True)

        with open(path, "w") as f:
            f.write(content)

    def get_agent_summary(self, agent_name: str) -> dict[str, Any]:
        """
        Get a summary for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dictionary with agent-specific summary
        """
        agent_results = [r for r in self.suite_result.results if r.agent_name == agent_name]

        if not agent_results:
            return {
                "agent_name": agent_name,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "score": None,
            }

        passed = sum(1 for r in agent_results if r.passed)
        scores = [r.score for r in agent_results if r.score is not None]
        avg_score = sum(scores) / len(scores) if scores else None

        return {
            "agent_name": agent_name,
            "total": len(agent_results),
            "passed": passed,
            "failed": len(agent_results) - passed,
            "score": avg_score,
            "results": [r.to_dict() for r in agent_results],
        }

    def get_critical_issues(self) -> list[dict[str, Any]]:
        """
        Get all critical issues that need attention.

        Returns:
            List of critical issue dictionaries
        """
        critical_results = [
            r for r in self.suite_result.results
            if not r.passed and r.severity == EvalSeverity.CRITICAL
        ]

        return [
            {
                "eval_name": r.eval_name,
                "agent_name": r.agent_name,
                "message": r.message,
                "details": r.details,
            }
            for r in critical_results
        ]

    def _group_by_agent(self) -> dict[str, list[EvalResult]]:
        """Group results by agent name."""
        by_agent: dict[str, list[EvalResult]] = defaultdict(list)
        for result in self.suite_result.results:
            agent = result.agent_name or "unknown"
            by_agent[agent].append(result)
        return dict(by_agent)

    def _group_by_type(self) -> dict[EvalType, list[EvalResult]]:
        """Group results by eval type."""
        by_type: dict[EvalType, list[EvalResult]] = defaultdict(list)
        for result in self.suite_result.results:
            by_type[result.eval_type].append(result)
        return dict(by_type)
