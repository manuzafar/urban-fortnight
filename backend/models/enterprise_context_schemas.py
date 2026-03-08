"""
Pydantic models for Enterprise Context integration.

These models define the data structures for:
- Enterprise context storage and validation
- Context merging and hierarchy
- Constraint extraction for agent prompts
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ContextType(str, Enum):
    """Types of enterprise context files."""
    COMPANY = "company"
    DIVISION = "division"
    TEAM = "team"


class ContextScope(str, Enum):
    """Visibility scope for enterprise contexts."""
    PRIVATE = "private"      # Only visible to owner
    SHARED = "shared"        # Shared with specific users
    ORGANIZATION = "organization"  # Visible to all org users


class ValidationStatus(str, Enum):
    """Validation status for uploaded contexts."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════


class EnterpriseContextCreate(BaseModel):
    """Request model for creating an enterprise context."""
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable name")
    context_type: ContextType = Field(..., description="Type: company, division, or team")
    raw_content: str = Field(..., min_length=1, description="Raw markdown or YAML content")
    parent_id: Optional[str] = Field(None, description="Parent context ID for hierarchy")
    scope: ContextScope = Field(ContextScope.PRIVATE, description="Visibility scope")
    is_default: bool = Field(False, description="Whether this is the default context of its type")


class EnterpriseContextUpdate(BaseModel):
    """Request model for updating an enterprise context."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    raw_content: Optional[str] = Field(None, min_length=1)
    parent_id: Optional[str] = None
    scope: Optional[ContextScope] = None
    is_default: Optional[bool] = None


class EnterpriseContextResponse(BaseModel):
    """Response model for an enterprise context."""
    id: str
    user_id: str
    name: str
    context_type: ContextType
    parent_id: Optional[str] = None
    raw_content: str
    parsed_content: dict[str, Any]
    validation_status: ValidationStatus
    validation_errors: list[str]
    scope: ContextScope
    is_default: bool
    created_at: datetime
    updated_at: datetime


class EnterpriseContextListItem(BaseModel):
    """Summary model for listing enterprise contexts."""
    id: str
    name: str
    context_type: ContextType
    parent_id: Optional[str] = None
    validation_status: ValidationStatus
    scope: ContextScope
    is_default: bool
    created_at: datetime
    updated_at: datetime


class EnterpriseContextListResponse(BaseModel):
    """Response for listing enterprise contexts."""
    contexts: list[EnterpriseContextListItem]
    count: int


class ContextUploadResponse(BaseModel):
    """Response after uploading and validating a context file."""
    id: str
    name: str
    context_type: ContextType
    validation_status: ValidationStatus
    validation_errors: list[str]
    parsed_content: dict[str, Any]


class MergedContextPreview(BaseModel):
    """Preview of merged context hierarchy."""
    merged_context: dict[str, Any]
    sources: list[str]
    constraints_preview: list[dict[str, Any]]


class SessionContextAttach(BaseModel):
    """Request to attach contexts to a session."""
    context_ids: list[str] = Field(..., min_items=1, max_items=3)


class SessionContextResponse(BaseModel):
    """Response with attached session contexts."""
    session_id: str
    contexts: list[EnterpriseContextListItem]
    merged_context: dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL MODELS (for service layer)
# ═══════════════════════════════════════════════════════════════════════════════


class EnterpriseContextDB(BaseModel):
    """Database representation of an enterprise context."""
    id: str
    user_id: str
    name: str
    context_type: str
    parent_id: Optional[str] = None
    raw_content: str
    parsed_content: dict[str, Any]
    validation_status: str
    validation_errors: list[str]
    scope: str
    is_default: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionContextDB(BaseModel):
    """Database representation of session-context association."""
    id: str
    session_id: str
    context_id: str
    context_type: str
    merged_context: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════════════════════════════
# PARSED CONTENT STRUCTURE (matches enterprise-context-spec)
# ═══════════════════════════════════════════════════════════════════════════════


class StrategyContext(BaseModel):
    """Strategy section of enterprise context."""
    time_horizon: Optional[str] = None
    strategic_priorities: Optional[list[str]] = None
    strategic_constraints: Optional[list[str]] = None
    innovation_stance: Optional[str] = None
    investment_thesis: Optional[str] = None


class TechnologyContext(BaseModel):
    """Technology section of enterprise context."""
    cloud: Optional[str] = None
    primary_languages: Optional[list[str]] = None
    databases: Optional[list[str]] = None
    infrastructure: Optional[list[str]] = None
    technical_constraints: Optional[list[str]] = None
    approved_vendors: Optional[list[str]] = None
    deprecated_technologies: Optional[list[str]] = None


class RegulatoryContext(BaseModel):
    """Regulatory section of enterprise context."""
    frameworks: Optional[list[str]] = None
    jurisdictions: Optional[list[str]] = None
    data_residency: Optional[str] = None
    audit_requirements: Optional[list[str]] = None


class OrganizationContext(BaseModel):
    """Organization section of enterprise context."""
    delivery_model: Optional[str] = None
    decision_authority: Optional[str] = None
    budget_cycle: Optional[str] = None
    approval_process: Optional[str] = None


class RiskManagementContext(BaseModel):
    """Risk management section of enterprise context."""
    risk_appetite: Optional[str] = None
    risk_categories: Optional[list[str]] = None
    mitigation_requirements: Optional[list[str]] = None


class ParsedEnterpriseContext(BaseModel):
    """Full parsed enterprise context structure."""
    schema_version: Optional[str] = Field(None, alias="schema")
    company: Optional[str] = None
    division: Optional[str] = None
    team: Optional[str] = None
    industry: Optional[str] = None

    strategy: Optional[StrategyContext] = None
    technology: Optional[TechnologyContext] = None
    regulatory: Optional[RegulatoryContext] = None
    organization: Optional[OrganizationContext] = None
    risk_management: Optional[RiskManagementContext] = None

    # Merged context tracking
    _sources: Optional[list[str]] = None

    model_config = {"extra": "allow", "populate_by_name": True}


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRAINT MODELS (for agent integration)
# ═══════════════════════════════════════════════════════════════════════════════


class EnterpriseConstraint(BaseModel):
    """
    A constraint extracted from enterprise context.

    Similar to ExecutionConstraint but specifically for enterprise context.
    These are soft constraints that guide agent behavior.
    """
    field: str = Field(..., description="The field being constrained")
    value: Any = Field(..., description="The constrained value")
    source_section: str = Field(..., description="Which context section this came from")
    source_claim_id: str = Field(..., description="Claim ID for tracking")
    constraint_type: str = Field(..., description="Type: must_use, must_align, guidance")
    evidence_tier: str = Field("E1", description="Evidence tier (E1 for org policy)")
    confidence: float = Field(0.95, description="Confidence level")
    is_negotiable: bool = Field(True, description="Whether agents can deviate with justification")


class EnterpriseConstraintSet(BaseModel):
    """Set of constraints extracted from enterprise context."""
    constraints: list[EnterpriseConstraint]
    source_contexts: list[str]  # Context IDs that contributed
    formatted_prompt: str  # Pre-formatted prompt section
