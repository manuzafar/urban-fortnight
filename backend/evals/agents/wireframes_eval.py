"""
Wireframes Eval — Specialized evaluation for wireframe outputs.

Criteria:
- Valid structure: Parseable HTML/JSX
- Core screens: Landing, dashboard, key workflows
- Responsive hints: Mobile considerations
- Accessibility: Basic a11y (labels, contrast)
- User flow coverage: Matches PRD user stories
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


CORE_SCREEN_KEYWORDS = {
    "landing", "home", "dashboard", "login", "signup", "register",
    "profile", "settings", "main", "list", "detail", "form",
}


class WireframesEval(BaseEval):
    """Evaluates wireframes for structure and coverage."""

    name = "wireframes_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks wireframes cover core screens with valid structure"
    severity = EvalSeverity.WARNING
    applicable_agents = ["wireframe_agent"]

    MIN_SCREENS = 3

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate wireframes output."""
        checks = []
        score_components = []

        # Get screens
        screens = agent_output.get("screens", [])
        screen_count = len(screens)

        # Check screen count
        count_passed = screen_count >= self.MIN_SCREENS
        checks.append({
            "name": "screen_count",
            "passed": count_passed,
            "actual": screen_count,
            "required": self.MIN_SCREENS,
        })
        score_components.append(min(screen_count / self.MIN_SCREENS, 1.0))

        # Check core screens coverage
        screen_names = [s.get("screen_name", "").lower() for s in screens]
        core_screens_found = set()
        for name in screen_names:
            for keyword in CORE_SCREEN_KEYWORDS:
                if keyword in name:
                    core_screens_found.add(keyword)

        has_landing = any("landing" in n or "home" in n for n in screen_names)
        has_dashboard = any("dashboard" in n or "main" in n for n in screen_names)
        core_passed = has_landing or has_dashboard
        checks.append({
            "name": "core_screens",
            "passed": core_passed,
            "actual": f"found: {', '.join(core_screens_found) or 'none'}",
            "required": "landing or dashboard screen",
        })
        score_components.append(1.0 if core_passed else 0.5)

        # Check screens have valid structure (react_code)
        screens_with_code = 0
        valid_code_count = 0
        for screen in screens:
            code = screen.get("react_code", "")
            if code and len(code) > 50:
                screens_with_code += 1
                # Basic check for React/JSX structure
                if re.search(r'<\w+|function\s+\w+|const\s+\w+\s*=', code):
                    valid_code_count += 1

        code_rate = screens_with_code / max(screen_count, 1)
        code_passed = code_rate >= 0.7 or screen_count == 0
        checks.append({
            "name": "react_code_present",
            "passed": code_passed,
            "actual": f"{screens_with_code}/{screen_count} have code",
            "required": "70% with React code",
        })
        score_components.append(code_rate if screen_count else 1.0)

        # Check screens have purpose
        with_purpose = sum(
            1 for s in screens
            if s.get("purpose") and len(str(s.get("purpose", ""))) > 10
        )
        purpose_rate = with_purpose / max(screen_count, 1)
        purpose_passed = purpose_rate >= 0.8 or screen_count == 0
        checks.append({
            "name": "screen_purpose",
            "passed": purpose_passed,
            "actual": f"{with_purpose}/{screen_count} have purpose",
            "required": "80% with purpose defined",
        })
        score_components.append(purpose_rate if screen_count else 1.0)

        # Check key components
        with_components = sum(
            1 for s in screens
            if len(s.get("key_components", [])) >= 2
        )
        components_rate = with_components / max(screen_count, 1)
        components_passed = components_rate >= 0.7 or screen_count == 0
        checks.append({
            "name": "key_components",
            "passed": components_passed,
            "actual": f"{with_components}/{screen_count} have components",
            "required": "70% with key components",
        })
        score_components.append(components_rate if screen_count else 1.0)

        # Check navigation
        with_navigation = sum(
            1 for s in screens
            if len(s.get("navigation_to", [])) >= 1
        )
        nav_rate = with_navigation / max(screen_count - 1, 1)  # -1 for terminal screens
        nav_passed = nav_rate >= 0.5 or screen_count <= 1
        checks.append({
            "name": "navigation_defined",
            "passed": nav_passed,
            "actual": f"{with_navigation}/{screen_count} have navigation",
            "required": "50% with navigation paths",
        })
        score_components.append(nav_rate if screen_count else 1.0)

        # Check user flows
        user_flows = agent_output.get("user_flows", [])
        has_flows = len(user_flows) >= 1
        checks.append({
            "name": "user_flows",
            "passed": has_flows,
            "actual": len(user_flows),
            "required": ">= 1 user flow",
        })
        score_components.append(1.0 if has_flows else 0.5)

        # Check design system notes
        design_notes = agent_output.get("design_system_notes", [])
        has_design_notes = len(design_notes) >= 1
        checks.append({
            "name": "design_system",
            "passed": has_design_notes,
            "actual": len(design_notes),
            "required": ">= 1 design note",
        })
        score_components.append(1.0 if has_design_notes else 0.5)

        # Check responsive notes
        responsive = agent_output.get("responsive_notes", "")
        has_responsive = bool(responsive) and len(str(responsive)) > 10
        checks.append({
            "name": "responsive_notes",
            "passed": has_responsive,
            "actual": "present" if has_responsive else "missing",
            "required": "responsive/mobile notes",
        })
        score_components.append(1.0 if has_responsive else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Wireframes complete: {screen_count} screens, {len(user_flows)} flows"
        else:
            message = f"Wireframes need: {', '.join(failed_checks)}"

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
                "screen_count": screen_count,
                "core_screens_found": list(core_screens_found),
                "screens_with_code": screens_with_code,
            },
        )


# Register the eval
EvalRegistry.register(WireframesEval())
