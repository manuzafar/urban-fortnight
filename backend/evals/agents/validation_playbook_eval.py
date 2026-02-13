"""
Validation Playbook Eval — Specialized evaluation for validation experiments.

Criteria:
- Test hypotheses: >= 3 testable hypotheses from claims
- Methods: Interview, survey, prototype test methods
- Success criteria: Measurable pass/fail criteria
- Timeline: Validation timeline with milestones
- Priority ranking: Tests prioritized by impact/effort
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


VALID_EXPERIMENT_TYPES = {
    "interview", "survey", "landing_page", "prototype", "concierge",
    "smoke_test", "a/b test", "usability", "focus_group", "mvp",
}


class ValidationPlaybookEval(BaseEval):
    """Evaluates validation playbook for actionable experiments."""

    name = "validation_playbook_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks validation playbook has testable experiments with criteria"
    severity = EvalSeverity.WARNING
    applicable_agents = ["validation_playbook"]

    MIN_EXPERIMENTS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate validation playbook output."""
        checks = []
        score_components = []

        # Get experiments
        experiments = agent_output.get("experiments", [])
        experiment_count = len(experiments)

        # Check experiment count
        count_passed = experiment_count >= self.MIN_EXPERIMENTS
        checks.append({
            "name": "experiment_count",
            "passed": count_passed,
            "actual": experiment_count,
            "required": self.MIN_EXPERIMENTS,
        })
        score_components.append(min(experiment_count / self.MIN_EXPERIMENTS, 1.0))

        # Check experiment types are valid
        valid_type_count = 0
        for exp in experiments:
            exp_type = str(exp.get("experiment_type", "")).lower()
            if any(valid in exp_type for valid in VALID_EXPERIMENT_TYPES):
                valid_type_count += 1

        type_rate = valid_type_count / max(experiment_count, 1)
        types_passed = type_rate >= 0.8 or experiment_count == 0
        checks.append({
            "name": "valid_experiment_types",
            "passed": types_passed,
            "actual": f"{valid_type_count}/{experiment_count} valid types",
            "required": "80% recognized experiment types",
        })
        score_components.append(type_rate if experiment_count else 1.0)

        # Check success criteria
        with_success_criteria = sum(
            1 for e in experiments
            if e.get("success_criteria") and len(str(e.get("success_criteria", ""))) > 10
        )
        success_rate = with_success_criteria / max(experiment_count, 1)
        success_passed = success_rate >= 0.8 or experiment_count == 0
        checks.append({
            "name": "success_criteria",
            "passed": success_passed,
            "actual": f"{with_success_criteria}/{experiment_count} have success criteria",
            "required": "80% with success criteria",
        })
        score_components.append(success_rate if experiment_count else 1.0)

        # Check failure criteria
        with_failure_criteria = sum(
            1 for e in experiments
            if e.get("failure_criteria") and len(str(e.get("failure_criteria", ""))) > 10
        )
        failure_rate = with_failure_criteria / max(experiment_count, 1)
        failure_passed = failure_rate >= 0.7 or experiment_count == 0
        checks.append({
            "name": "failure_criteria",
            "passed": failure_passed,
            "actual": f"{with_failure_criteria}/{experiment_count} have failure criteria",
            "required": "70% with failure criteria",
        })
        score_components.append(failure_rate if experiment_count else 1.0)

        # Check specific instructions
        with_instructions = sum(
            1 for e in experiments
            if e.get("specific_instructions") and len(str(e.get("specific_instructions", ""))) > 30
        )
        instructions_rate = with_instructions / max(experiment_count, 1)
        instructions_passed = instructions_rate >= 0.7 or experiment_count == 0
        checks.append({
            "name": "specific_instructions",
            "passed": instructions_passed,
            "actual": f"{with_instructions}/{experiment_count} have instructions",
            "required": "70% with detailed instructions",
        })
        score_components.append(instructions_rate if experiment_count else 1.0)

        # Check target profiles
        with_target = sum(
            1 for e in experiments
            if e.get("target_profile")
        )
        target_rate = with_target / max(experiment_count, 1)
        target_passed = target_rate >= 0.8 or experiment_count == 0
        checks.append({
            "name": "target_profiles",
            "passed": target_passed,
            "actual": f"{with_target}/{experiment_count} have targets",
            "required": "80% with target profile",
        })
        score_components.append(target_rate if experiment_count else 1.0)

        # Check priorities
        with_priority = sum(
            1 for e in experiments
            if e.get("priority")
        )
        priority_rate = with_priority / max(experiment_count, 1)
        priority_passed = priority_rate >= 0.7 or experiment_count == 0
        checks.append({
            "name": "priority_ranking",
            "passed": priority_passed,
            "actual": f"{with_priority}/{experiment_count} prioritized",
            "required": "70% with priority",
        })
        score_components.append(priority_rate if experiment_count else 1.0)

        # Check critical path
        critical_path = agent_output.get("critical_path_experiments", [])
        has_critical_path = len(critical_path) >= 1
        checks.append({
            "name": "critical_path",
            "passed": has_critical_path,
            "actual": len(critical_path),
            "required": ">= 1 critical experiment",
        })
        score_components.append(1.0 if has_critical_path else 0.5)

        # Check total timeline
        timeline = agent_output.get("total_validation_timeline")
        has_timeline = bool(timeline)
        checks.append({
            "name": "validation_timeline",
            "passed": has_timeline,
            "actual": "present" if has_timeline else "missing",
            "required": "overall timeline",
        })
        score_components.append(1.0 if has_timeline else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Validation playbook complete: {experiment_count} experiments"
        else:
            message = f"Validation playbook needs: {', '.join(failed_checks)}"

        return EvalResult(
            eval_name=self.name,
            eval_type=self.eval_type,
            passed=all_passed,
            score=round(score, 3),
            severity=self.severity if not all_passed else EvalSeverity.INFO,
            message=message,
            agent_name=agent_name,
            details={
                "checks": checks,
                "experiment_count": experiment_count,
                "with_success_criteria": with_success_criteria,
            },
        )


# Register the eval
EvalRegistry.register(ValidationPlaybookEval())
