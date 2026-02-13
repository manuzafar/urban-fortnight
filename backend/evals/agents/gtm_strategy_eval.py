"""
GTM Strategy Eval — Specialized evaluation for go-to-market strategy.

Criteria:
- Channel strategy: Specific acquisition channels
- Pricing strategy: Pricing tiers with rationale
- Launch timeline: Phased rollout plan
- Partnership opportunities: Potential partners identified
- Budget allocation: Marketing spend breakdown
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class GTMStrategyEval(BaseEval):
    """Evaluates GTM strategy for actionability and completeness."""

    name = "gtm_strategy_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks GTM strategy has executable plan elements"
    severity = EvalSeverity.WARNING
    applicable_agents = ["gtm_agent"]

    MIN_CHANNELS = 2
    MIN_LAUNCH_PHASES = 2
    MIN_METRICS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate GTM strategy output."""
        checks = []
        score_components = []

        # Check positioning statement
        positioning = agent_output.get("positioning_statement")
        has_positioning = bool(positioning) and len(str(positioning)) > 20
        checks.append({
            "name": "positioning_statement",
            "passed": has_positioning,
            "actual": "present" if has_positioning else "missing",
            "required": "clear positioning statement",
        })
        score_components.append(1.0 if has_positioning else 0.3)

        # Check channel strategy
        channels = agent_output.get("channel_strategy", [])
        channel_count = len(channels)
        channels_passed = channel_count >= self.MIN_CHANNELS
        checks.append({
            "name": "channel_strategy",
            "passed": channels_passed,
            "actual": channel_count,
            "required": self.MIN_CHANNELS,
        })
        score_components.append(min(channel_count / self.MIN_CHANNELS, 1.0))

        # Check launch phases
        phases = agent_output.get("launch_phases", [])
        phase_count = len(phases)
        phases_passed = phase_count >= self.MIN_LAUNCH_PHASES
        # Check phases have objectives
        phases_with_objectives = sum(
            1 for p in phases
            if p.get("objective") or p.get("goals")
        )
        checks.append({
            "name": "launch_phases",
            "passed": phases_passed,
            "actual": f"{phase_count} phases, {phases_with_objectives} with objectives",
            "required": f">= {self.MIN_LAUNCH_PHASES} phases",
        })
        score_components.append(min(phase_count / self.MIN_LAUNCH_PHASES, 1.0))

        # Check messaging by persona
        messaging = agent_output.get("messaging_by_persona", [])
        has_messaging = len(messaging) > 0
        checks.append({
            "name": "persona_messaging",
            "passed": has_messaging,
            "actual": len(messaging),
            "required": ">= 1 persona",
        })
        score_components.append(1.0 if has_messaging else 0.5)

        # Check metrics dashboard
        metrics = agent_output.get("metrics_dashboard", [])
        metrics_passed = len(metrics) >= self.MIN_METRICS
        checks.append({
            "name": "metrics_dashboard",
            "passed": metrics_passed,
            "actual": len(metrics),
            "required": self.MIN_METRICS,
        })
        score_components.append(min(len(metrics) / self.MIN_METRICS, 1.0))

        # Check partnership opportunities
        partnerships = agent_output.get("partnership_opportunities", [])
        has_partnerships = len(partnerships) > 0
        checks.append({
            "name": "partnership_opportunities",
            "passed": has_partnerships,
            "actual": len(partnerships),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_partnerships else 0.5)

        # Check GTM budget
        budget = agent_output.get("total_gtm_budget_estimate")
        has_budget = bool(budget) and len(str(budget)) > 5
        checks.append({
            "name": "budget_estimate",
            "passed": has_budget,
            "actual": "present" if has_budget else "missing",
            "required": "total GTM budget",
        })
        score_components.append(1.0 if has_budget else 0.5)

        # Check GTM risks
        risks = agent_output.get("gtm_risks", [])
        has_risks = len(risks) >= 2
        checks.append({
            "name": "gtm_risks",
            "passed": has_risks,
            "actual": len(risks),
            "required": ">= 2",
        })
        score_components.append(1.0 if has_risks else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"GTM strategy complete with {channel_count} channels, {phase_count} phases"
        else:
            message = f"GTM strategy missing: {', '.join(failed_checks)}"

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
                "channel_count": channel_count,
                "phase_count": phase_count,
                "metrics_count": len(metrics),
            },
        )


# Register the eval
EvalRegistry.register(GTMStrategyEval())
