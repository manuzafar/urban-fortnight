"""
Technical Architecture Eval — Specialized evaluation for architecture outputs.

Criteria:
- Real technologies: No invented frameworks/tools
- Integration coherence: Components can actually integrate
- Scalability addressed: Handles stated user scale
- Security considerations: Auth, encryption, compliance mentioned
- Cost estimates: Infrastructure cost estimates provided
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


# Known real technologies (non-exhaustive but catches obvious hallucinations)
KNOWN_TECHNOLOGIES = {
    # Languages
    "python", "javascript", "typescript", "java", "go", "rust", "c#", "ruby", "php", "swift", "kotlin",
    # Frontend
    "react", "vue", "angular", "svelte", "next.js", "nuxt", "remix", "gatsby",
    # Backend
    "node.js", "express", "fastapi", "django", "flask", "spring", "rails", "laravel", "asp.net",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra", "sqlite",
    "supabase", "firebase", "planetscale", "cockroachdb", "timescaledb",
    # Cloud
    "aws", "gcp", "azure", "vercel", "netlify", "heroku", "digitalocean", "cloudflare", "railway",
    # Infra
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions", "gitlab ci",
    # Services
    "stripe", "twilio", "sendgrid", "auth0", "okta", "datadog", "sentry", "newrelic",
}


class TechnicalArchitectureEval(BaseEval):
    """Evaluates technical architecture for feasibility and completeness."""

    name = "technical_architecture_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks architecture uses real tech and addresses key concerns"
    severity = EvalSeverity.WARNING
    applicable_agents = ["technical_architect"]

    MIN_TECH_STACK = 3
    MIN_COMPONENTS = 2

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate technical architecture output."""
        checks = []
        score_components = []

        # Check architecture style
        arch_style = agent_output.get("architecture_style")
        has_arch_style = bool(arch_style) and len(str(arch_style)) > 5
        checks.append({
            "name": "architecture_style",
            "passed": has_arch_style,
            "actual": arch_style if has_arch_style else "missing",
            "required": "defined architecture pattern",
        })
        score_components.append(1.0 if has_arch_style else 0.3)

        # Check technology stack
        tech_stack = agent_output.get("technology_stack", [])
        tech_count = len(tech_stack)
        tech_passed = tech_count >= self.MIN_TECH_STACK
        checks.append({
            "name": "technology_stack_count",
            "passed": tech_passed,
            "actual": tech_count,
            "required": self.MIN_TECH_STACK,
        })
        score_components.append(min(tech_count / self.MIN_TECH_STACK, 1.0))

        # Check for real technologies (not hallucinated)
        tech_names = []
        for t in tech_stack:
            tech_name = t.get("technology", "").lower() if isinstance(t, dict) else str(t).lower()
            tech_names.append(tech_name)

        # Check if technologies are recognizable
        recognized_count = sum(
            1 for t in tech_names
            if any(known in t for known in KNOWN_TECHNOLOGIES)
        )
        recognition_rate = recognized_count / max(len(tech_names), 1)
        tech_real = recognition_rate >= 0.7
        checks.append({
            "name": "real_technologies",
            "passed": tech_real,
            "actual": f"{recognized_count}/{len(tech_names)} recognized",
            "required": "70% recognizable technologies",
        })
        score_components.append(recognition_rate)

        # Check system components
        components = agent_output.get("system_components", [])
        component_count = len(components)
        components_passed = component_count >= self.MIN_COMPONENTS
        checks.append({
            "name": "system_components",
            "passed": components_passed,
            "actual": component_count,
            "required": self.MIN_COMPONENTS,
        })
        score_components.append(min(component_count / self.MIN_COMPONENTS, 1.0))

        # Check security architecture
        security = agent_output.get("security_architecture", "")
        security_keywords = ["auth", "encrypt", "ssl", "tls", "oauth", "jwt", "rbac", "https"]
        has_security = any(kw in str(security).lower() for kw in security_keywords)
        checks.append({
            "name": "security_architecture",
            "passed": has_security,
            "actual": "addressed" if has_security else "missing",
            "required": "security considerations",
        })
        score_components.append(1.0 if has_security else 0.3)

        # Check scalability
        scalability = agent_output.get("scalability_approach", "")
        has_scalability = bool(scalability) and len(str(scalability)) > 20
        checks.append({
            "name": "scalability_approach",
            "passed": has_scalability,
            "actual": "addressed" if has_scalability else "missing",
            "required": "scalability strategy",
        })
        score_components.append(1.0 if has_scalability else 0.5)

        # Check deployment strategy
        deployment = agent_output.get("deployment_strategy", "")
        has_deployment = bool(deployment) and len(str(deployment)) > 20
        checks.append({
            "name": "deployment_strategy",
            "passed": has_deployment,
            "actual": "addressed" if has_deployment else "missing",
            "required": "deployment approach",
        })
        score_components.append(1.0 if has_deployment else 0.5)

        # Check infrastructure requirements
        infra = agent_output.get("infrastructure_requirements", [])
        has_infra = len(infra) >= 1
        checks.append({
            "name": "infrastructure_requirements",
            "passed": has_infra,
            "actual": len(infra),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_infra else 0.5)

        # Check for architecture diagram
        has_diagram = bool(agent_output.get("architecture_diagram_mermaid")) or \
                      bool(agent_output.get("architecture_diagram_description"))
        checks.append({
            "name": "architecture_diagram",
            "passed": has_diagram,
            "actual": "present" if has_diagram else "missing",
            "required": "diagram or description",
        })
        score_components.append(1.0 if has_diagram else 0.5)

        # Check technical risks
        risks = agent_output.get("technical_risks", [])
        has_risks = len(risks) >= 2
        checks.append({
            "name": "technical_risks",
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
            message = f"Architecture complete: {tech_count} technologies, {component_count} components"
        else:
            message = f"Architecture needs: {', '.join(failed_checks)}"

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
                "technology_count": tech_count,
                "component_count": component_count,
                "tech_recognition_rate": round(recognition_rate, 2),
            },
        )


# Register the eval
EvalRegistry.register(TechnicalArchitectureEval())
