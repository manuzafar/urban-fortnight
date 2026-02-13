"""
Legal & Regulatory Eval — Specialized evaluation for compliance outputs.

Criteria:
- Real regulations: Cites actual laws/standards (GDPR, HIPAA, etc.)
- Jurisdiction-specific: Matches stated target market
- Compliance requirements: Specific requirements listed, not vague
- Risk assessment: Legal risks identified with mitigation
- No invented regulations: No hallucinated compliance requirements
"""

from typing import Any

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)


# Known real regulations (non-exhaustive)
KNOWN_REGULATIONS = {
    # Privacy
    "gdpr", "ccpa", "cpra", "pipeda", "lgpd", "popia",
    # Healthcare
    "hipaa", "hitech", "fda", "mhra",
    # Finance
    "pci dss", "pci-dss", "sox", "sarbanes-oxley", "glba", "aml", "kyc",
    "dodd-frank", "mifid", "psd2",
    # Security
    "soc 2", "soc2", "iso 27001", "iso27001", "nist", "fedramp",
    # General
    "coppa", "can-spam", "tcpa", "ada", "wcag", "section 508",
    # Industry specific
    "ferpa", "sec", "finra", "cfpb",
}


class LegalRegulatoryEval(BaseEval):
    """Evaluates legal/regulatory review for accuracy and completeness."""

    name = "legal_regulatory_quality"
    eval_type = EvalType.AGENT_SPECIFIC
    description = "Checks legal review cites real regulations with specific requirements"
    severity = EvalSeverity.WARNING
    applicable_agents = ["legal_regulatory"]

    MIN_REGULATIONS = 1
    MIN_LEGAL_RISKS = 2

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """Evaluate legal/regulatory review output."""
        checks = []
        score_components = []

        # Check executive summary
        summary = agent_output.get("executive_summary", "")
        has_summary = bool(summary) and len(str(summary)) > 50
        checks.append({
            "name": "executive_summary",
            "passed": has_summary,
            "actual": "present" if has_summary else "missing",
            "required": "executive summary",
        })
        score_components.append(1.0 if has_summary else 0.5)

        # Check applicable regulations
        regulations = agent_output.get("applicable_regulations", [])
        reg_count = len(regulations)
        reg_passed = reg_count >= self.MIN_REGULATIONS
        checks.append({
            "name": "regulation_count",
            "passed": reg_passed,
            "actual": reg_count,
            "required": self.MIN_REGULATIONS,
        })
        score_components.append(min(reg_count / max(self.MIN_REGULATIONS, 1), 1.0))

        # Check for real regulations (not hallucinated)
        reg_names = []
        for r in regulations:
            reg_name = r.get("name", "").lower() if isinstance(r, dict) else str(r).lower()
            reg_names.append(reg_name)

        recognized_count = sum(
            1 for r in reg_names
            if any(known in r for known in KNOWN_REGULATIONS)
        )
        recognition_rate = recognized_count / max(len(reg_names), 1)
        real_regs = recognition_rate >= 0.5 or reg_count == 0
        checks.append({
            "name": "real_regulations",
            "passed": real_regs,
            "actual": f"{recognized_count}/{len(reg_names)} recognized",
            "required": "50% recognizable regulations",
        })
        score_components.append(recognition_rate if reg_names else 1.0)

        # Check compliance requirements are specific
        regs_with_requirements = sum(
            1 for r in regulations
            if isinstance(r, dict) and len(r.get("compliance_requirements", [])) >= 2
        )
        specificity_rate = regs_with_requirements / max(reg_count, 1)
        specific_passed = specificity_rate >= 0.7 or reg_count == 0
        checks.append({
            "name": "specific_requirements",
            "passed": specific_passed,
            "actual": f"{regs_with_requirements}/{reg_count} have detailed requirements",
            "required": "70% with specific requirements",
        })
        score_components.append(specificity_rate if reg_count else 1.0)

        # Check data protection requirements
        data_protection = agent_output.get("data_protection_requirements", [])
        has_data_protection = len(data_protection) > 0
        checks.append({
            "name": "data_protection",
            "passed": has_data_protection,
            "actual": len(data_protection),
            "required": ">= 1",
        })
        score_components.append(1.0 if has_data_protection else 0.5)

        # Check legal risks
        legal_risks = agent_output.get("legal_risks", [])
        risks_passed = len(legal_risks) >= self.MIN_LEGAL_RISKS
        checks.append({
            "name": "legal_risks",
            "passed": risks_passed,
            "actual": len(legal_risks),
            "required": self.MIN_LEGAL_RISKS,
        })
        score_components.append(min(len(legal_risks) / self.MIN_LEGAL_RISKS, 1.0))

        # Check risks have mitigations
        risks_with_mitigations = sum(
            1 for r in legal_risks
            if isinstance(r, dict) and r.get("mitigation_strategies")
        )
        mitigation_rate = risks_with_mitigations / max(len(legal_risks), 1)
        mitigations_passed = mitigation_rate >= 0.7 or len(legal_risks) == 0
        checks.append({
            "name": "risk_mitigations",
            "passed": mitigations_passed,
            "actual": f"{risks_with_mitigations}/{len(legal_risks)} have mitigations",
            "required": "70% with mitigations",
        })
        score_components.append(mitigation_rate if legal_risks else 1.0)

        # Check overall risk assessment
        overall_assessment = agent_output.get("overall_risk_assessment", {})
        has_assessment = bool(overall_assessment.get("risk_level"))
        checks.append({
            "name": "overall_assessment",
            "passed": has_assessment,
            "actual": "present" if has_assessment else "missing",
            "required": "overall risk level",
        })
        score_components.append(1.0 if has_assessment else 0.5)

        # Check next steps
        next_steps = agent_output.get("next_steps", [])
        has_next_steps = len(next_steps) >= 2
        checks.append({
            "name": "next_steps",
            "passed": has_next_steps,
            "actual": len(next_steps),
            "required": ">= 2",
        })
        score_components.append(1.0 if has_next_steps else 0.5)

        # Calculate overall
        all_passed = all(c["passed"] for c in checks)
        score = sum(score_components) / len(score_components)

        failed_checks = [c["name"] for c in checks if not c["passed"]]

        if all_passed:
            message = f"Legal review complete: {reg_count} regulations, {len(legal_risks)} risks identified"
        else:
            message = f"Legal review needs: {', '.join(failed_checks)}"

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
                "regulation_count": reg_count,
                "legal_risk_count": len(legal_risks),
                "regulation_recognition_rate": round(recognition_rate, 2),
            },
        )


# Register the eval
EvalRegistry.register(LegalRegulatoryEval())
