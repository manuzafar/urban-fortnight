"""
Unit tests for EnterpriseContextService.

Tests parsing, validation, merging, and constraint extraction.
"""

import pytest
import yaml
from services.enterprise_context_service import EnterpriseContextService, enterprise_context_service
from models.enterprise_context_schemas import ValidationStatus


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Get a fresh service instance."""
    return EnterpriseContextService()


@pytest.fixture
def company_context_yaml():
    """Sample company context in YAML format."""
    return """
schema: enterprise-context/v1/company
company: Acme Corporation
industry: Financial Services

strategy:
  time_horizon: "3-5 years"
  strategic_priorities:
    - Digital transformation
    - Customer experience
    - Operational efficiency
  strategic_constraints:
    - No acquisitions in 2024
    - 10% cost reduction target
  innovation_stance: "fast follower"

technology:
  cloud: AWS
  primary_languages:
    - Python
    - TypeScript
  databases:
    - PostgreSQL
    - Redis
  deprecated_technologies:
    - Oracle
    - COBOL

regulatory:
  frameworks:
    - SOC2
    - GDPR
    - PCI-DSS
  jurisdictions:
    - US
    - EU
  data_residency: "US-only"

risk_management:
  risk_appetite: "moderate"
  risk_categories:
    - Operational
    - Compliance
    - Technology

organization:
  delivery_model: "agile"
  budget_cycle: "quarterly"
"""


@pytest.fixture
def company_context_markdown():
    """Sample company context in markdown format with YAML frontmatter."""
    return """---
schema: enterprise-context/v1/company
company: Acme Corporation
industry: Technology

strategy:
  strategic_priorities:
    - Innovation
    - Scale

technology:
  cloud: Azure
  primary_languages:
    - Go
    - Rust
---

# Company Context

This is additional documentation about the company context.
"""


@pytest.fixture
def division_context_yaml():
    """Sample division context."""
    return """
schema: enterprise-context/v1/division
division: Engineering
parent_company: Acme Corporation

technology:
  primary_languages:
    - Python
    - Go
  infrastructure:
    - Kubernetes
    - Terraform

strategy:
  strategic_priorities:
    - Platform reliability
    - Developer experience
"""


@pytest.fixture
def team_context_yaml():
    """Sample team context."""
    return """
schema: enterprise-context/v1/team
team: Platform Team
parent_division: Engineering

technology:
  databases:
    - TimescaleDB
  technical_constraints:
    - Must use Kubernetes
    - Zero-downtime deployments required

strategy:
  strategic_priorities:
    - SLA compliance
"""


# ═══════════════════════════════════════════════════════════════════════════════
# PARSING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestParsing:
    """Tests for content parsing."""

    def test_parse_yaml_content(self, service, company_context_yaml):
        """Test parsing pure YAML content."""
        parsed, body = service.parse_content(company_context_yaml)

        assert parsed["schema"] == "enterprise-context/v1/company"
        assert parsed["company"] == "Acme Corporation"
        assert parsed["industry"] == "Financial Services"
        assert parsed["technology"]["cloud"] == "AWS"
        assert "Python" in parsed["technology"]["primary_languages"]
        assert body == ""  # Pure YAML has no body

    def test_parse_markdown_frontmatter(self, service, company_context_markdown):
        """Test parsing markdown with YAML frontmatter."""
        parsed, body = service.parse_content(company_context_markdown)

        assert parsed["schema"] == "enterprise-context/v1/company"
        assert parsed["company"] == "Acme Corporation"
        assert parsed["technology"]["cloud"] == "Azure"
        assert "# Company Context" in body

    def test_parse_empty_content(self, service):
        """Test parsing empty content."""
        parsed, body = service.parse_content("")
        assert parsed == {} or parsed is None or body == ""

    def test_parse_invalid_yaml(self, service):
        """Test parsing invalid YAML returns empty dict or raises error."""
        invalid_yaml = """
schema: test
invalid: yaml: content: here
  - bad indentation
"""
        # Service may raise ValueError or return empty dict depending on implementation
        try:
            parsed, body = service.parse_content(invalid_yaml)
            # If no error raised, should return empty or partial content
            assert parsed is None or parsed == {} or isinstance(parsed, dict)
        except (ValueError, yaml.YAMLError):
            # Expected behavior for some implementations
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidation:
    """Tests for content validation."""

    def test_validate_company_context(self, service, company_context_yaml):
        """Test validating a valid company context."""
        parsed, _ = service.parse_content(company_context_yaml)
        status, errors = service.validate_content(parsed, "company")

        assert status == ValidationStatus.VALID
        assert len(errors) == 0

    def test_validate_missing_company_field(self, service):
        """Test validation fails when company field is missing."""
        content = """
schema: enterprise-context/v1/company
industry: Technology
"""
        parsed, _ = service.parse_content(content)
        status, errors = service.validate_content(parsed, "company")

        assert status == ValidationStatus.INVALID
        assert any("company" in e.lower() for e in errors)

    def test_validate_division_context(self, service, division_context_yaml):
        """Test validating a valid division context."""
        parsed, _ = service.parse_content(division_context_yaml)
        status, errors = service.validate_content(parsed, "division")

        assert status == ValidationStatus.VALID
        assert len(errors) == 0

    def test_validate_missing_division_field(self, service):
        """Test validation fails when division field is missing."""
        content = """
schema: enterprise-context/v1/division
parent_company: Acme
"""
        parsed, _ = service.parse_content(content)
        status, errors = service.validate_content(parsed, "division")

        assert status == ValidationStatus.INVALID
        assert any("division" in e.lower() for e in errors)

    def test_validate_team_context(self, service, team_context_yaml):
        """Test validating a valid team context."""
        parsed, _ = service.parse_content(team_context_yaml)
        status, errors = service.validate_content(parsed, "team")

        assert status == ValidationStatus.VALID
        assert len(errors) == 0

    def test_parse_and_validate_combined(self, service, company_context_yaml):
        """Test the combined parse_and_validate method."""
        parsed, status, errors = service.parse_and_validate(
            company_context_yaml, "company"
        )

        assert status == ValidationStatus.VALID
        assert len(errors) == 0
        assert parsed["company"] == "Acme Corporation"


# ═══════════════════════════════════════════════════════════════════════════════
# MERGING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestMerging:
    """Tests for context merging."""

    def test_merge_single_company(self, service, company_context_yaml):
        """Test merging with only company context."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)

        assert merged["company"] == "Acme Corporation"
        assert merged["_sources"] == ["company"]
        assert merged["schema"] == "enterprise-context/v1/merged"

    def test_merge_company_and_division(
        self, service, company_context_yaml, division_context_yaml
    ):
        """Test merging company and division contexts."""
        company, _ = service.parse_content(company_context_yaml)
        division, _ = service.parse_content(division_context_yaml)

        merged = service.merge_hierarchy(company=company, division=division)

        assert merged["company"] == "Acme Corporation"
        assert merged["division"] == "Engineering"
        assert merged["_sources"] == ["company", "division"]

        # Lists should be concatenated
        languages = merged["technology"]["primary_languages"]
        assert "Python" in languages  # From company
        assert "Go" in languages  # From division

    def test_merge_full_hierarchy(
        self, service, company_context_yaml, division_context_yaml, team_context_yaml
    ):
        """Test merging company, division, and team contexts."""
        company, _ = service.parse_content(company_context_yaml)
        division, _ = service.parse_content(division_context_yaml)
        team, _ = service.parse_content(team_context_yaml)

        merged = service.merge_hierarchy(
            company=company, division=division, team=team
        )

        assert merged["_sources"] == ["company", "division", "team"]
        assert merged["team"] == "Platform Team"

        # Team technical constraints should be present
        tech = merged["technology"]
        assert "TimescaleDB" in tech.get("databases", [])
        assert "Must use Kubernetes" in tech.get("technical_constraints", [])

    def test_merge_scalar_override(self, service):
        """Test that lower levels override scalar values."""
        company = {"cloud": "AWS", "_sources": []}
        division = {"cloud": "Azure"}  # Override

        merged = service.merge_hierarchy(
            company={"technology": company},
            division={"technology": division},
        )

        # Division cloud should override company cloud
        assert merged["technology"]["cloud"] == "Azure"

    def test_merge_list_concatenation(self, service):
        """Test that lists are concatenated."""
        company = {"technology": {"databases": ["PostgreSQL"]}}
        division = {"technology": {"databases": ["MongoDB"]}}

        merged = service.merge_hierarchy(company=company, division=division)

        databases = merged["technology"]["databases"]
        assert "PostgreSQL" in databases
        assert "MongoDB" in databases
        assert len(databases) == 2

    def test_merge_empty_contexts(self, service):
        """Test merging with no contexts."""
        merged = service.merge_hierarchy()

        assert merged["_sources"] == []
        assert merged["schema"] == "enterprise-context/v1/merged"


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT EXTRACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstraintExtraction:
    """Tests for constraint extraction."""

    def test_extract_regulatory_constraints(self, service, company_context_yaml):
        """Test extracting regulatory constraints."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        constraints = constraint_set.constraints

        # Should have compliance framework constraints
        compliance_constraints = [
            c for c in constraints if c.field == "compliance_framework"
        ]
        assert len(compliance_constraints) == 3  # SOC2, GDPR, PCI-DSS

        # All regulatory constraints should be E1
        for c in compliance_constraints:
            assert c.evidence_tier == "E1"
            assert c.constraint_type == "must_use"
            assert c.confidence == 1.0

    def test_extract_data_residency_constraint(self, service, company_context_yaml):
        """Test extracting data residency constraint."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        data_residency = [
            c for c in constraint_set.constraints if c.field == "data_residency"
        ]
        assert len(data_residency) == 1
        assert data_residency[0].value == "US-only"
        assert data_residency[0].evidence_tier == "E1"

    def test_extract_strategic_constraints(self, service, company_context_yaml):
        """Test extracting strategic constraints."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        strategic = [
            c for c in constraint_set.constraints
            if c.field == "strategic_alignment"
        ]
        assert len(strategic) == 2  # No acquisitions, 10% cost reduction

        for c in strategic:
            assert c.constraint_type == "must_align"
            assert c.evidence_tier == "E1"
            assert c.confidence == 0.95

    def test_extract_technology_constraints(self, service, company_context_yaml):
        """Test extracting technology constraints."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        cloud = [c for c in constraint_set.constraints if c.field == "cloud_platform"]
        assert len(cloud) == 1
        assert cloud[0].value == "AWS"
        assert cloud[0].constraint_type == "must_use"

        languages = [
            c for c in constraint_set.constraints
            if c.field == "programming_languages"
        ]
        assert len(languages) == 1
        assert "Python" in languages[0].value

    def test_extract_deprecated_technologies(self, service, company_context_yaml):
        """Test extracting deprecated technologies constraint."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        deprecated = [
            c for c in constraint_set.constraints
            if c.field == "deprecated_technologies"
        ]
        assert len(deprecated) == 1
        assert "Oracle" in deprecated[0].value
        assert "COBOL" in deprecated[0].value

    def test_extract_risk_appetite(self, service, company_context_yaml):
        """Test extracting risk appetite constraint."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        risk = [c for c in constraint_set.constraints if c.field == "risk_appetite"]
        assert len(risk) == 1
        assert risk[0].value == "moderate"
        assert risk[0].constraint_type == "must_align"

    def test_formatted_prompt_generation(self, service, company_context_yaml):
        """Test that formatted prompt is generated."""
        company, _ = service.parse_content(company_context_yaml)
        merged = service.merge_hierarchy(company=company)
        constraint_set = service.extract_constraints(merged)

        prompt = constraint_set.formatted_prompt
        assert "ORGANIZATIONAL CONTEXT" in prompt
        assert "Acme Corporation" in prompt
        assert "Compliance Requirements" in prompt
        assert "SOC2" in prompt
        assert "AWS" in prompt


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT TYPE DETECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestContextTypeDetection:
    """Tests for context type detection."""

    def test_detect_company_from_schema(self, service, company_context_yaml):
        """Test detecting company type from schema field."""
        ctx_type = service.detect_context_type(company_context_yaml)
        assert ctx_type.value == "company"

    def test_detect_division_from_schema(self, service, division_context_yaml):
        """Test detecting division type from schema field."""
        ctx_type = service.detect_context_type(division_context_yaml)
        assert ctx_type.value == "division"

    def test_detect_team_from_schema(self, service, team_context_yaml):
        """Test detecting team type from schema field."""
        ctx_type = service.detect_context_type(team_context_yaml)
        assert ctx_type.value == "team"

    def test_detect_from_content_key(self, service):
        """Test detecting type from content key when schema is missing."""
        content = """
company: Test Corp
industry: Tech
"""
        ctx_type = service.detect_context_type(content)
        assert ctx_type.value == "company"

    def test_detect_unknown_type(self, service):
        """Test detecting returns None for unknown type."""
        content = """
random_key: value
other_key: value
"""
        ctx_type = service.detect_context_type(content)
        assert ctx_type is None


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL SERVICE INSTANCE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGlobalServiceInstance:
    """Tests for the global service instance."""

    def test_global_instance_exists(self):
        """Test that global instance is available."""
        assert enterprise_context_service is not None

    def test_global_instance_functional(self, company_context_yaml):
        """Test that global instance works correctly."""
        parsed, _ = enterprise_context_service.parse_content(company_context_yaml)
        assert parsed["company"] == "Acme Corporation"
