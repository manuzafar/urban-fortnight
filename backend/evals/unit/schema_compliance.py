"""
Schema Compliance Eval — Validates agent outputs against Pydantic schemas.

This eval ensures all agent outputs conform to their expected schemas,
catching structural issues, missing required fields, and type mismatches.
"""

from typing import Any

from pydantic import ValidationError

from evals.base import (
    BaseEval,
    EvalRegistry,
    EvalResult,
    EvalSeverity,
    EvalType,
)
from models.schemas import (
    BusinessCase,
    CustomerResearch,
    ExecutiveSummary,
    FinancialModel,
    GoToMarket,
    LegalRegulatoryReview,
    ProductRequirementsDocument,
    StakeholderViews,
    TechnicalArchitecture,
    ValidationPlaybook,
    Wireframes,
    Prototype,
)


# Map agent names to their Pydantic schemas
AGENT_SCHEMAS: dict[str, type] = {
    "customer_research": CustomerResearch,
    "business_strategy": BusinessCase,
    "product_requirements": ProductRequirementsDocument,
    "technical_architect": TechnicalArchitecture,
    "legal_regulatory": LegalRegulatoryReview,
    "executive_summary": ExecutiveSummary,
    "gtm_agent": GoToMarket,
    "financial_model_agent": FinancialModel,
    "stakeholder_views": StakeholderViews,
    "validation_playbook": ValidationPlaybook,
    "wireframe_agent": Wireframes,
    "prototype_agent": Prototype,
}


class SchemaComplianceEval(BaseEval):
    """
    Evaluates agent output against its Pydantic schema.

    This is a CRITICAL eval that blocks PRs on failure, as schema violations
    indicate fundamental structural issues with agent outputs.
    """

    name = "schema_compliance"
    eval_type = EvalType.UNIT
    description = "Validates agent output against Pydantic schema"
    severity = EvalSeverity.CRITICAL

    async def evaluate(
        self,
        agent_output: dict[str, Any],
        agent_name: str,
        context: dict[str, Any] | None = None,
    ) -> EvalResult:
        """
        Validate agent output against its schema.

        Args:
            agent_output: The agent's output dictionary
            agent_name: Name of the agent
            context: Optional additional context

        Returns:
            EvalResult with validation outcome
        """
        # Get the schema for this agent
        schema_class = AGENT_SCHEMAS.get(agent_name)

        if schema_class is None:
            # No schema defined for this agent - pass with info
            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=1.0,
                severity=EvalSeverity.INFO,
                message=f"No schema defined for agent '{agent_name}'",
                agent_name=agent_name,
            )

        try:
            # Attempt validation
            schema_class.model_validate(agent_output)

            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=True,
                score=1.0,
                severity=EvalSeverity.INFO,
                message=f"Output conforms to {schema_class.__name__} schema",
                agent_name=agent_name,
                details={
                    "schema": schema_class.__name__,
                    "field_count": len(schema_class.model_fields),
                },
            )

        except ValidationError as e:
            # Extract error details
            errors = []
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error["loc"])
                errors.append({
                    "field": location,
                    "type": error["type"],
                    "message": error["msg"],
                })

            return EvalResult(
                eval_name=self.name,
                eval_type=self.eval_type,
                passed=False,
                score=0.0,
                severity=self.severity,
                message=f"Schema validation failed with {len(errors)} error(s)",
                agent_name=agent_name,
                details={
                    "schema": schema_class.__name__,
                    "error_count": len(errors),
                    "errors": errors[:10],  # Limit to first 10 errors
                },
            )


# Register the eval
EvalRegistry.register(SchemaComplianceEval())
