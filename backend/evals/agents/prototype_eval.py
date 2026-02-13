"""
Prototype Eval — Specialized evaluation for interactive prototype outputs.

Criteria:
- Valid React code: Compiles without errors
- Interactive elements: Buttons, forms, navigation work
- State management: Proper state handling
- No placeholder data: Real mock data, not "Lorem ipsum"
- Matches wireframes: Consistent with wireframe structure
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


# Patterns that indicate placeholder content
PLACEHOLDER_PATTERNS = [
    r"lorem\s*ipsum",
    r"placeholder",
    r"todo:",
    r"\.\.\.",
    r"xxx",
    r"coming\s*soon",
    r"tbd",
    r"example\s*text",
]


class PrototypeEval(BaseEval):
    """Evaluates prototype for interactivity and code quality."""

    name = "prototype_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks prototype has valid React code with real content"
    severity = EvalSeverity.WARNING
    applicable_agents = ["prototype_agent"]

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate prototype output."""
        checks = []
        score_components = []

        # Check prototype name
        proto_name = agent_output.get("prototype_name")
        has_name = bool(proto_name)
        checks.append({
            "name": "prototype_name",
            "passed": has_name,
            "actual": proto_name if has_name else "missing",
            "required": "prototype name",
        })
        score_components.append(1.0 if has_name else 0.5)

        # Check React code exists
        react_code = agent_output.get("react_component_code", "")
        has_code = bool(react_code) and len(react_code) > 100
        checks.append({
            "name": "react_code_present",
            "passed": has_code,
            "actual": f"{len(react_code)} chars" if has_code else "missing",
            "required": "React component code",
        })
        score_components.append(1.0 if has_code else 0.0)

        if has_code:
            # Check for valid React patterns
            has_component = bool(re.search(r'function\s+\w+|const\s+\w+\s*=\s*\(', react_code))
            has_jsx = bool(re.search(r'<\w+[^>]*>', react_code))
            has_return = bool(re.search(r'return\s*\(', react_code))

            react_valid = has_component and has_jsx and has_return
            checks.append({
                "name": "valid_react_structure",
                "passed": react_valid,
                "actual": f"component: {has_component}, JSX: {has_jsx}, return: {has_return}",
                "required": "function/const component with JSX return",
            })
            score_components.append(1.0 if react_valid else 0.3)

            # Check for state management
            has_usestate = "useState" in react_code
            has_state = has_usestate or "this.state" in react_code
            checks.append({
                "name": "state_management",
                "passed": has_state,
                "actual": "useState present" if has_usestate else ("class state" if has_state else "no state"),
                "required": "state handling",
            })
            score_components.append(1.0 if has_state else 0.5)

            # Check for interactive elements
            has_onclick = "onClick" in react_code or "onSubmit" in react_code
            has_button = "<button" in react_code.lower() or "Button" in react_code
            has_form = "<form" in react_code.lower() or "<input" in react_code.lower()
            interactive = has_onclick or has_button or has_form

            checks.append({
                "name": "interactive_elements",
                "passed": interactive,
                "actual": f"onClick: {has_onclick}, button: {has_button}, form: {has_form}",
                "required": "interactive elements (buttons, forms)",
            })
            score_components.append(1.0 if interactive else 0.3)

            # Check for placeholder content
            placeholder_found = []
            code_lower = react_code.lower()
            for pattern in PLACEHOLDER_PATTERNS:
                if re.search(pattern, code_lower):
                    placeholder_found.append(pattern)

            no_placeholders = len(placeholder_found) == 0
            checks.append({
                "name": "no_placeholder_content",
                "passed": no_placeholders,
                "actual": f"found: {', '.join(placeholder_found)}" if placeholder_found else "no placeholders",
                "required": "real mock data, no Lorem ipsum",
            })
            score_components.append(1.0 if no_placeholders else 0.5)

        # Check primary persona
        persona = agent_output.get("primary_persona")
        has_persona = bool(persona)
        checks.append({
            "name": "primary_persona",
            "passed": has_persona,
            "actual": persona if has_persona else "missing",
            "required": "target persona specified",
        })
        score_components.append(1.0 if has_persona else 0.5)

        # Check key user story
        user_story = agent_output.get("key_user_story")
        has_story = bool(user_story) and len(str(user_story)) > 20
        checks.append({
            "name": "key_user_story",
            "passed": has_story,
            "actual": "defined" if has_story else "missing",
            "required": "user story being demonstrated",
        })
        score_components.append(1.0 if has_story else 0.5)

        # Check demo scenario
        demo = agent_output.get("demo_scenario")
        has_demo = bool(demo) and len(str(demo)) > 30
        checks.append({
            "name": "demo_scenario",
            "passed": has_demo,
            "actual": "defined" if has_demo else "missing",
            "required": "demo walkthrough script",
        })
        score_components.append(1.0 if has_demo else 0.5)

        # Check color palette
        palette = agent_output.get("color_palette", {})
        has_palette = bool(palette) and palette.get("primary")
        checks.append({
            "name": "color_palette",
            "passed": has_palette,
            "actual": "defined" if has_palette else "missing",
            "required": "color palette with primary",
        })
        score_components.append(1.0 if has_palette else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Prototype complete with valid React code"
        else:
            message = f"Prototype needs: {', '.join(failed_checks)}"

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
                "code_length": len(react_code) if has_code else 0,
            },
        )


# Register the eval
EvalRegistry.register(PrototypeEval())
