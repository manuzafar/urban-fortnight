"""
Enterprise Context Service — Handles parsing, validation, merging, and constraint extraction.

This service integrates with the enterprise-context-spec package to provide
organizational context for AI agents.
"""

import re
from typing import Any, Optional

import structlog
import yaml

from models.enterprise_context_schemas import (
    ContextType,
    EnterpriseConstraint,
    EnterpriseConstraintSet,
    ValidationStatus,
)

logger = structlog.get_logger(__name__)


class EnterpriseContextService:
    """
    Service for managing enterprise context files.

    Provides methods for:
    - Parsing markdown/YAML content
    - Validating against enterprise-context-spec schemas
    - Merging context hierarchies
    - Extracting constraints for agent prompts
    """

    def __init__(self):
        """Initialize the service."""
        self._has_enterprise_context_package = False
        try:
            from enterprise_context import (
                load_context_file,
                merge_contexts,
                parse_markdown_frontmatter,
                validate_context,
            )
            self._has_enterprise_context_package = True
            self._parse_frontmatter = parse_markdown_frontmatter
            self._validate = validate_context
            self._merge = merge_contexts
            self._load = load_context_file
        except ImportError:
            logger.warning(
                "enterprise_context_package_not_found",
                msg="Using fallback implementation",
            )

    def parse_content(self, raw_content: str) -> tuple[dict[str, Any], str]:
        """
        Parse markdown/YAML content into structured data.

        Args:
            raw_content: Raw markdown with YAML frontmatter or pure YAML

        Returns:
            Tuple of (parsed_dict, remaining_body)
        """
        if self._has_enterprise_context_package:
            return self._parse_frontmatter(raw_content)

        # Fallback implementation
        return self._parse_markdown_frontmatter_fallback(raw_content)

    def _parse_markdown_frontmatter_fallback(
        self, content: str
    ) -> tuple[dict[str, Any], str]:
        """Fallback parser when enterprise-context package is not available."""
        if not content.startswith("---"):
            # Try parsing as pure YAML
            try:
                return yaml.safe_load(content) or {}, ""
            except yaml.YAMLError:
                return {}, content

        # Find the closing ---
        end_index = content.find("---", 3)
        if end_index == -1:
            return {}, content

        frontmatter_str = content[3:end_index].strip()
        body = content[end_index + 3:].strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}")

        return frontmatter, body

    def validate_content(
        self, parsed_content: dict[str, Any], context_type: str
    ) -> tuple[ValidationStatus, list[str]]:
        """
        Validate parsed content against schema.

        Args:
            parsed_content: Parsed context dictionary
            context_type: Type of context (company, division, team)

        Returns:
            Tuple of (validation_status, list_of_errors)
        """
        errors = []

        if self._has_enterprise_context_package:
            try:
                validation_errors = self._validate(parsed_content, context_type)
                if validation_errors:
                    return ValidationStatus.INVALID, validation_errors
                return ValidationStatus.VALID, []
            except Exception as e:
                logger.error("validation_error", error=str(e))
                return ValidationStatus.INVALID, [str(e)]

        # Fallback validation
        return self._validate_fallback(parsed_content, context_type)

    def _validate_fallback(
        self, content: dict[str, Any], context_type: str
    ) -> tuple[ValidationStatus, list[str]]:
        """Fallback validation when enterprise-context package is not available."""
        errors = []

        # Basic required field checks
        if context_type == "company":
            if not content.get("company"):
                errors.append("company: Missing required field 'company'")
        elif context_type == "division":
            if not content.get("division"):
                errors.append("division: Missing required field 'division'")
        elif context_type == "team":
            if not content.get("team"):
                errors.append("team: Missing required field 'team'")

        # Validate strategy section if present
        strategy = content.get("strategy", {})
        if strategy:
            if "strategic_priorities" in strategy:
                if not isinstance(strategy["strategic_priorities"], list):
                    errors.append("strategy.strategic_priorities: Must be a list")

        # Validate technology section if present
        tech = content.get("technology", {})
        if tech:
            if "primary_languages" in tech:
                if not isinstance(tech["primary_languages"], list):
                    errors.append("technology.primary_languages: Must be a list")

        # Validate regulatory section if present
        reg = content.get("regulatory", {})
        if reg:
            if "frameworks" in reg:
                if not isinstance(reg["frameworks"], list):
                    errors.append("regulatory.frameworks: Must be a list")

        if errors:
            return ValidationStatus.INVALID, errors
        return ValidationStatus.VALID, []

    def parse_and_validate(
        self, raw_content: str, context_type: str
    ) -> tuple[dict[str, Any], ValidationStatus, list[str]]:
        """
        Parse and validate content in one call.

        Args:
            raw_content: Raw markdown/YAML content
            context_type: Type of context

        Returns:
            Tuple of (parsed_content, validation_status, errors)
        """
        try:
            parsed_content, _ = self.parse_content(raw_content)
        except ValueError as e:
            return {}, ValidationStatus.INVALID, [str(e)]

        if not parsed_content:
            return {}, ValidationStatus.INVALID, ["Empty or invalid content"]

        status, errors = self.validate_content(parsed_content, context_type)
        return parsed_content, status, errors

    def merge_hierarchy(
        self,
        company: Optional[dict[str, Any]] = None,
        division: Optional[dict[str, Any]] = None,
        team: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Merge context hierarchy with inheritance.

        Inheritance chain: company <- division <- team
        - Lists are concatenated (lower level extends higher)
        - Dicts are recursively merged
        - Scalars are overridden (lower level wins)

        Args:
            company: Company-level context (base)
            division: Division-level context (extends company)
            team: Team-level context (extends division)

        Returns:
            Merged context dictionary
        """
        if self._has_enterprise_context_package:
            return self._merge(company=company, division=division, team=team)

        # Fallback implementation
        return self._merge_fallback(company, division, team)

    def _merge_fallback(
        self,
        company: Optional[dict[str, Any]] = None,
        division: Optional[dict[str, Any]] = None,
        team: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Fallback merge when enterprise-context package is not available."""
        result: dict[str, Any] = {"_sources": []}

        if company:
            result = self._deep_merge(result, company)
            result["_sources"].append("company")

        if division:
            result = self._deep_merge(result, division)
            result["_sources"].append("division")

        if team:
            result = self._deep_merge(result, team)
            result["_sources"].append("team")

        result["schema"] = "enterprise-context/v1/merged"
        return result

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    def extract_constraints(
        self, merged_context: dict[str, Any]
    ) -> EnterpriseConstraintSet:
        """
        Extract constraints from merged enterprise context.

        Maps context fields to constraint objects that can be used
        by the constraint broadcaster.

        Args:
            merged_context: Merged context from merge_hierarchy()

        Returns:
            EnterpriseConstraintSet with constraints and formatted prompt
        """
        constraints: list[EnterpriseConstraint] = []
        claim_counter = 1

        # Extract regulatory constraints (E1, non-negotiable)
        regulatory = merged_context.get("regulatory", {})
        if regulatory.get("frameworks"):
            for framework in regulatory["frameworks"]:
                constraints.append(EnterpriseConstraint(
                    field="compliance_framework",
                    value=framework,
                    source_section="enterprise_context.regulatory",
                    source_claim_id=f"EC-REG-{claim_counter}",
                    constraint_type="must_use",
                    evidence_tier="E1",
                    confidence=1.0,
                    is_negotiable=False,
                ))
                claim_counter += 1

        if regulatory.get("data_residency"):
            constraints.append(EnterpriseConstraint(
                field="data_residency",
                value=regulatory["data_residency"],
                source_section="enterprise_context.regulatory",
                source_claim_id=f"EC-REG-{claim_counter}",
                constraint_type="must_use",
                evidence_tier="E1",
                confidence=1.0,
                is_negotiable=False,
            ))
            claim_counter += 1

        # Extract strategy constraints (E1, soft)
        strategy = merged_context.get("strategy", {})
        if strategy.get("strategic_constraints"):
            for sc in strategy["strategic_constraints"]:
                constraints.append(EnterpriseConstraint(
                    field="strategic_alignment",
                    value=sc,
                    source_section="enterprise_context.strategy",
                    source_claim_id=f"EC-STR-{claim_counter}",
                    constraint_type="must_align",
                    evidence_tier="E1",
                    confidence=0.95,
                    is_negotiable=True,
                ))
                claim_counter += 1

        if strategy.get("strategic_priorities"):
            constraints.append(EnterpriseConstraint(
                field="strategic_priorities",
                value=strategy["strategic_priorities"],
                source_section="enterprise_context.strategy",
                source_claim_id=f"EC-STR-{claim_counter}",
                constraint_type="must_align",
                evidence_tier="E1",
                confidence=0.95,
                is_negotiable=True,
            ))
            claim_counter += 1

        if strategy.get("innovation_stance"):
            constraints.append(EnterpriseConstraint(
                field="innovation_stance",
                value=strategy["innovation_stance"],
                source_section="enterprise_context.strategy",
                source_claim_id=f"EC-STR-{claim_counter}",
                constraint_type="guidance",
                evidence_tier="E2",
                confidence=0.85,
                is_negotiable=True,
            ))
            claim_counter += 1

        # Extract technology constraints (E1-E2)
        tech = merged_context.get("technology", {})
        if tech.get("cloud"):
            constraints.append(EnterpriseConstraint(
                field="cloud_platform",
                value=tech["cloud"],
                source_section="enterprise_context.technology",
                source_claim_id=f"EC-TECH-{claim_counter}",
                constraint_type="must_use",
                evidence_tier="E1",
                confidence=0.95,
                is_negotiable=True,
            ))
            claim_counter += 1

        if tech.get("primary_languages"):
            constraints.append(EnterpriseConstraint(
                field="programming_languages",
                value=tech["primary_languages"],
                source_section="enterprise_context.technology",
                source_claim_id=f"EC-TECH-{claim_counter}",
                constraint_type="must_use",
                evidence_tier="E1",
                confidence=0.9,
                is_negotiable=True,
            ))
            claim_counter += 1

        if tech.get("databases"):
            constraints.append(EnterpriseConstraint(
                field="database_technologies",
                value=tech["databases"],
                source_section="enterprise_context.technology",
                source_claim_id=f"EC-TECH-{claim_counter}",
                constraint_type="must_use",
                evidence_tier="E1",
                confidence=0.9,
                is_negotiable=True,
            ))
            claim_counter += 1

        if tech.get("technical_constraints"):
            for tc in tech["technical_constraints"]:
                constraints.append(EnterpriseConstraint(
                    field="technical_constraint",
                    value=tc,
                    source_section="enterprise_context.technology",
                    source_claim_id=f"EC-TECH-{claim_counter}",
                    constraint_type="guidance",
                    evidence_tier="E2",
                    confidence=0.85,
                    is_negotiable=True,
                ))
                claim_counter += 1

        if tech.get("deprecated_technologies"):
            constraints.append(EnterpriseConstraint(
                field="deprecated_technologies",
                value=tech["deprecated_technologies"],
                source_section="enterprise_context.technology",
                source_claim_id=f"EC-TECH-{claim_counter}",
                constraint_type="must_not_use",
                evidence_tier="E1",
                confidence=0.95,
                is_negotiable=False,
            ))
            claim_counter += 1

        # Extract risk management constraints (E1)
        risk = merged_context.get("risk_management", {})
        if risk.get("risk_appetite"):
            constraints.append(EnterpriseConstraint(
                field="risk_appetite",
                value=risk["risk_appetite"],
                source_section="enterprise_context.risk_management",
                source_claim_id=f"EC-RISK-{claim_counter}",
                constraint_type="must_align",
                evidence_tier="E1",
                confidence=0.95,
                is_negotiable=True,
            ))
            claim_counter += 1

        # Extract organization constraints (E2, guidance)
        org = merged_context.get("organization", {})
        if org.get("delivery_model"):
            constraints.append(EnterpriseConstraint(
                field="delivery_model",
                value=org["delivery_model"],
                source_section="enterprise_context.organization",
                source_claim_id=f"EC-ORG-{claim_counter}",
                constraint_type="guidance",
                evidence_tier="E2",
                confidence=0.8,
                is_negotiable=True,
            ))
            claim_counter += 1

        # Format prompt
        formatted_prompt = self.format_constraints_prompt(constraints, merged_context)

        return EnterpriseConstraintSet(
            constraints=constraints,
            source_contexts=merged_context.get("_sources", []),
            formatted_prompt=formatted_prompt,
        )

    def format_constraints_prompt(
        self,
        constraints: list[EnterpriseConstraint],
        merged_context: dict[str, Any],
        max_chars: int = 4000,
    ) -> str:
        """
        Format enterprise context as soft guidance for agents.

        Creates a structured prompt section that agents can understand and follow.

        Args:
            constraints: List of extracted constraints
            merged_context: The merged context for additional details
            max_chars: Maximum characters for the prompt

        Returns:
            Formatted string for prompt injection
        """
        lines = [
            "## ORGANIZATIONAL CONTEXT (Guidelines)",
            "",
            "**Note:** Align with these organizational guidelines unless there's a",
            "compelling reason to deviate. If deviating, explain your reasoning.",
            "",
        ]

        # Add company info if available
        company = merged_context.get("company")
        if company:
            lines.append(f"**Company:** {company}")
            if merged_context.get("industry"):
                lines.append(f"**Industry:** {merged_context['industry']}")
            lines.append("")

        # Group constraints by category
        regulatory = [c for c in constraints if "regulatory" in c.source_section.lower()]
        strategic = [c for c in constraints if "strategy" in c.source_section.lower()]
        technology = [c for c in constraints if "technology" in c.source_section.lower()]
        other = [
            c for c in constraints
            if c not in regulatory and c not in strategic and c not in technology
        ]

        # Format regulatory (non-negotiable)
        if regulatory:
            lines.append("### Compliance Requirements (Non-negotiable)")
            for c in regulatory:
                if isinstance(c.value, list):
                    lines.append(f"- **{c.field}:** {', '.join(c.value)}")
                else:
                    lines.append(f"- **{c.field}:** {c.value}")
            lines.append("")

        # Format strategic
        if strategic:
            lines.append("### Strategic Alignment")
            for c in strategic:
                if isinstance(c.value, list):
                    lines.append(f"- **{c.field}:** {', '.join(c.value)}")
                else:
                    lines.append(f"- **{c.field}:** {c.value}")
            lines.append("")

        # Format technology
        if technology:
            lines.append("### Technology Standards")
            for c in technology:
                if isinstance(c.value, list):
                    lines.append(f"- **{c.field}:** {', '.join(c.value)}")
                else:
                    lines.append(f"- **{c.field}:** {c.value}")
            lines.append("")

        # Format other constraints
        if other:
            lines.append("### Other Organizational Guidelines")
            for c in other:
                if isinstance(c.value, list):
                    lines.append(f"- **{c.field}:** {', '.join(c.value)}")
                else:
                    lines.append(f"- **{c.field}:** {c.value}")
            lines.append("")

        lines.append("---")

        result = "\n".join(lines)
        if len(result) > max_chars:
            return result[:max_chars - 30] + "\n\n... [truncated]"
        return result

    def detect_context_type(self, content: str) -> Optional[ContextType]:
        """
        Detect the context type from content.

        Args:
            content: Raw content string

        Returns:
            Detected ContextType or None if cannot detect
        """
        try:
            parsed, _ = self.parse_content(content)

            schema = parsed.get("schema", "")
            if "company" in schema.lower():
                return ContextType.COMPANY
            if "division" in schema.lower():
                return ContextType.DIVISION
            if "team" in schema.lower():
                return ContextType.TEAM

            # Try to guess from content
            if "company" in parsed:
                return ContextType.COMPANY
            if "division" in parsed:
                return ContextType.DIVISION
            if "team" in parsed:
                return ContextType.TEAM

        except Exception:
            pass

        return None


# Global instance for easy import
enterprise_context_service = EnterpriseContextService()
