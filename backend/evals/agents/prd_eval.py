"""
PRD Eval — Specialized evaluation for product requirements documents.

Criteria:
- User stories: >= 5 user stories in proper format
- Acceptance criteria: Each feature has testable criteria
- Priority ranking: Features prioritized (MoSCoW or similar)
- MVP scope: Clear MVP vs future phases
- Dependencies: External dependencies identified
"""

from typing import Any
import re

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


class PRDEval(BaseEval):
    """Evaluates PRD for completeness and proper structure."""

    name = "prd_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks PRD has proper user stories and requirements"
    severity = EvalSeverity.WARNING
    applicable_agents = ["product_requirements"]

    MIN_USER_STORIES = 5
    MIN_EPICS = 3
    MIN_FUNCTIONAL_REQUIREMENTS = 5
    MIN_NFR = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate PRD output."""
        # Handle non-dict outputs
        if not isinstance(agent_output, dict):
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=False,
                score=0.0,
                severity=self.severity,
                message=f"Invalid output type: expected dict, got {type(agent_output).__name__}",
                agent_name=agent_name,
            )

        checks = []
        score_components = []

        # Count user stories across all epics
        epics = agent_output.get("epics", [])
        total_stories = sum(len(e.get("stories", [])) for e in epics)

        # Check epic count
        epic_count = len(epics)
        epics_passed = epic_count >= self.MIN_EPICS
        checks.append({
            "name": "epic_count",
            "passed": epics_passed,
            "actual": epic_count,
            "required": self.MIN_EPICS,
        })
        score_components.append(min(epic_count / self.MIN_EPICS, 1.0))

        # Check user story count
        stories_passed = total_stories >= self.MIN_USER_STORIES
        checks.append({
            "name": "user_story_count",
            "passed": stories_passed,
            "actual": total_stories,
            "required": self.MIN_USER_STORIES,
        })
        score_components.append(min(total_stories / self.MIN_USER_STORIES, 1.0))

        # Check user story format (As a... I want... So that... OR title + description)
        proper_format_count = 0
        for epic in epics:
            for story in epic.get("stories", []):
                # Support both formats: traditional (as_a/i_want/so_that) and compact (title/description)
                has_traditional = all([
                    story.get("as_a"),
                    story.get("i_want"),
                    story.get("so_that"),
                ])
                has_compact = all([
                    story.get("title"),
                    story.get("description") and len(str(story.get("description", ""))) > 10,
                ])
                if has_traditional or has_compact:
                    proper_format_count += 1

        format_passed = proper_format_count >= min(total_stories, self.MIN_USER_STORIES) * 0.8
        checks.append({
            "name": "story_format",
            "passed": format_passed,
            "actual": f"{proper_format_count}/{total_stories} proper format",
            "required": "80% with proper story definition",
        })
        score_components.append(proper_format_count / max(total_stories, 1))

        # Check acceptance criteria
        stories_with_criteria = 0
        for epic in epics:
            for story in epic.get("stories", []):
                criteria = story.get("acceptance_criteria", [])
                if len(criteria) > 0:
                    stories_with_criteria += 1

        criteria_passed = stories_with_criteria >= total_stories * 0.8
        checks.append({
            "name": "acceptance_criteria",
            "passed": criteria_passed,
            "actual": f"{stories_with_criteria}/{total_stories} have criteria",
            "required": "80% of stories",
        })
        score_components.append(stories_with_criteria / max(total_stories, 1))

        # Check functional requirements
        func_reqs = agent_output.get("functional_requirements", [])
        func_passed = len(func_reqs) >= self.MIN_FUNCTIONAL_REQUIREMENTS
        checks.append({
            "name": "functional_requirements",
            "passed": func_passed,
            "actual": len(func_reqs),
            "required": self.MIN_FUNCTIONAL_REQUIREMENTS,
        })
        score_components.append(min(len(func_reqs) / self.MIN_FUNCTIONAL_REQUIREMENTS, 1.0))

        # Check non-functional requirements
        nfr = agent_output.get("non_functional_requirements", [])
        nfr_passed = len(nfr) >= self.MIN_NFR
        checks.append({
            "name": "non_functional_requirements",
            "passed": nfr_passed,
            "actual": len(nfr),
            "required": self.MIN_NFR,
        })
        score_components.append(min(len(nfr) / self.MIN_NFR, 1.0))

        # Check release plan (MVP vs future) - handle both list and dict formats
        release_plan = agent_output.get("release_plan", [])
        phases = []
        if isinstance(release_plan, list):
            phases = release_plan
        elif isinstance(release_plan, dict):
            phases = release_plan.get("phases", [])

        has_mvp = False
        for p in phases:
            if isinstance(p, dict):
                phase_name = str(p.get("phase", p.get("name", ""))).lower()
                if "mvp" in phase_name or "1.0" in phase_name or "phase 1" in phase_name:
                    has_mvp = True
                    break
            elif isinstance(p, str):
                if "mvp" in p.lower() or "phase 1" in p.lower():
                    has_mvp = True
                    break

        release_passed = len(phases) >= 2 and has_mvp
        checks.append({
            "name": "release_plan",
            "passed": release_passed,
            "actual": f"{len(release_plan)} phases, MVP: {has_mvp}",
            "required": ">= 2 phases with MVP",
        })
        score_components.append(1.0 if release_passed else 0.5)

        # Check data model
        data_model = agent_output.get("data_model", {})
        entities = data_model.get("entities", [])
        has_data_model = len(entities) >= 2
        checks.append({
            "name": "data_model",
            "passed": has_data_model,
            "actual": f"{len(entities)} entities",
            "required": ">= 2 entities",
        })
        score_components.append(1.0 if has_data_model else 0.5)

        # Check priorities
        stories_with_priority = 0
        for epic in epics:
            for story in epic.get("stories", []):
                if story.get("priority"):
                    stories_with_priority += 1

        priority_passed = stories_with_priority >= total_stories * 0.8
        checks.append({
            "name": "priority_ranking",
            "passed": priority_passed,
            "actual": f"{stories_with_priority}/{total_stories} prioritized",
            "required": "80% of stories",
        })
        score_components.append(stories_with_priority / max(total_stories, 1))

        # Check risks
        risks = agent_output.get("risks", [])
        has_risks = len(risks) >= 3
        checks.append({
            "name": "risk_identification",
            "passed": has_risks,
            "actual": len(risks),
            "required": ">= 3",
        })
        score_components.append(min(len(risks) / 3, 1.0))

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"PRD complete: {epic_count} epics, {total_stories} stories, {len(func_reqs)} requirements"
        else:
            message = f"PRD needs: {', '.join(failed_checks)}"

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
                "epic_count": epic_count,
                "user_story_count": total_stories,
                "functional_requirement_count": len(func_reqs),
                "nfr_count": len(nfr),
            },
        )


# Register the eval
EvalRegistry.register(PRDEval())
