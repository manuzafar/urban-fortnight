"""Pydantic models for the Product Discovery Multi-Agent System."""

from models.schemas import (
    # API Request/Response
    DiscoveryRequest,
    DiscoveryResponse,
    SessionStatus,
    SessionStatusResponse,
    # Inception Pack Sections
    ExecutiveSummary,
    CustomerResearch,
    BusinessCase,
    ProductRequirementsDocument,
    TechnicalArchitecture,
    QualityAssessment,
    # PRD Sub-models
    UserPersona,
    Epic,
    UserStory,
    FunctionalRequirement,
    NonFunctionalRequirement,
    DataModel,
    # Full Pack
    InceptionPack,
)

__all__ = [
    "DiscoveryRequest",
    "DiscoveryResponse",
    "SessionStatus",
    "SessionStatusResponse",
    "ExecutiveSummary",
    "CustomerResearch",
    "BusinessCase",
    "ProductRequirementsDocument",
    "TechnicalArchitecture",
    "QualityAssessment",
    "UserPersona",
    "Epic",
    "UserStory",
    "FunctionalRequirement",
    "NonFunctionalRequirement",
    "DataModel",
    "InceptionPack",
]
