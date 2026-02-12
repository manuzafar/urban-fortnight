"""
Configuration management for the Product Discovery Multi-Agent System.

This module provides centralized configuration using Pydantic Settings,
supporting environment variables and .env file loading with validation.

Usage:
    from config import settings

    api_key = settings.google_api_key
    model = settings.llm_model
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    Environment variables take precedence over .env file values.

    Attributes:
        anthropic_api_key: API key for Anthropic Claude API.
        app_env: Application environment (development/staging/production).
        debug: Enable debug mode with verbose logging.
        api_host: Host address for the FastAPI server.
        api_port: Port number for the FastAPI server.
        llm_model: Claude model identifier to use for agents.
        llm_temperature: Temperature for LLM generation (0.0-1.0).
        llm_max_tokens: Maximum tokens per agent response.
        llm_timeout: Request timeout in seconds.
        max_revision_iterations: Maximum quality revision loops.
        min_quality_score: Minimum score to pass quality check.
        log_level: Logging verbosity level.
        log_json_format: Enable JSON structured logging.
        cors_origins: Allowed CORS origins.
        session_expiry_seconds: Session TTL in seconds.
        max_concurrent_sessions: Maximum parallel sessions (0=unlimited).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SUPABASE
    # ═══════════════════════════════════════════════════════════════════════
    supabase_url: str = Field(
        default="",
        description="Supabase project URL",
        validation_alias="SUPABASE_URL",
    )

    supabase_service_key: str = Field(
        default="",
        description="Supabase service role key (private, backend only)",
        validation_alias="SUPABASE_SERVICE_KEY",
    )

    supabase_jwt_secret: str = Field(
        default="",
        description="Supabase JWT secret for token verification",
        validation_alias="SUPABASE_JWT_SECRET",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # GOOGLE GEMINI API
    # ═══════════════════════════════════════════════════════════════════════
    google_api_key: str = Field(
        ...,
        description="Google API key for Gemini access",
        min_length=10,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # APPLICATION SETTINGS
    # ═══════════════════════════════════════════════════════════════════════
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Application environment",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    api_host: str = Field(
        default="0.0.0.0",
        description="API server host",
    )

    api_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="API server port",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # LLM CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════
    llm_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model to use",
    )

    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="LLM temperature (0.0-1.0)",
    )

    llm_max_tokens: int = Field(
        default=8192,
        ge=100,
        le=32768,
        description="Maximum tokens per response",
    )

    llm_timeout: int = Field(
        default=120,
        ge=10,
        le=600,
        description="Request timeout in seconds",
    )

    llm_enable_grounding: bool = Field(
        default=True,
        description="Enable Google Search grounding for supported agents",
    )

    llm_pro_model: str = Field(
        default="gemini-2.5-pro",
        description="Gemini Pro model for deeper reasoning tasks",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # QUALITY IMPROVEMENT SYSTEM
    # ═══════════════════════════════════════════════════════════════════════

    enable_memory_augmentation: bool = Field(
        default=True,
        description="Enable memory-augmented prompts for applicable agents. "
                    "When enabled, agents receive context from similar successful "
                    "past runs to improve output quality.",
    )

    enable_two_stage_reasoning: bool = Field(
        default=True,
        description="Enable two-stage grounded reasoning (research then structure). "
                    "Improves JSON parsing reliability for grounded agents.",
    )

    enable_self_reflection: bool = Field(
        default=False,
        description="Enable self-reflection pattern for agents. "
                    "Adds a reflection/revision loop to improve output quality. "
                    "Disabled by default as it increases token usage.",
    )

    max_reflection_rounds: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Maximum self-reflection rounds when enabled (0 = disabled)",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # AGENT ORCHESTRATION
    # ═══════════════════════════════════════════════════════════════════════
    max_revision_iterations: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum quality revision loops",
    )

    min_quality_score: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum quality score to pass",
    )

    max_critique_retries: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum critique retry attempts before accepting with warning",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # PRD SUB-WORKFLOW CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════
    prd_quality_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum PRD quality score to pass critic review",
    )

    prd_max_iterations: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum PRD generation/critique iterations",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════════════
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    log_json_format: bool = Field(
        default=False,
        description="Enable JSON structured logging",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # CORS
    # ═══════════════════════════════════════════════════════════════════════
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated allowed origins",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SESSION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════
    session_expiry_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Session expiry in seconds",
    )

    max_concurrent_sessions: int = Field(
        default=100,
        ge=0,
        description="Max concurrent sessions (0=unlimited)",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # EMAIL ALERTS
    # ═══════════════════════════════════════════════════════════════════════
    resend_api_key: str | None = Field(
        default=None,
        description="Resend API key for email delivery",
    )

    founder_email: str | None = Field(
        default=None,
        description="Founder email for pack generation alerts",
    )

    email_from_address: str = Field(
        default="alerts@seedcraft.ai",
        description="From address for outbound emails",
    )

    frontend_url: str = Field(
        default="https://seedcraft.ai",
        description="Frontend URL for links in emails",
    )

    # ═══════════════════════════════════════════════════════════════════════
    # COMPUTED PROPERTIES
    # ═══════════════════════════════════════════════════════════════════════

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"

    # ═══════════════════════════════════════════════════════════════════════
    # VALIDATORS
    # ═══════════════════════════════════════════════════════════════════════

    @field_validator("google_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate Google API key format."""
        if len(v) < 20:
            raise ValueError("Google API key appears to be invalid (too short)")
        return v

    @field_validator("llm_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate Gemini model name."""
        valid_prefixes = ("gemini-1.5", "gemini-2.0", "gemini-2.5", "gemini-3", "gemini-pro", "gemini-flash")
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"Invalid model '{v}'. Must be a valid Gemini model "
                f"(e.g., gemini-2.0-flash, gemini-2.5-pro)"
            )
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses LRU cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() to reload settings.

    Returns:
        Settings: Application settings instance.

    Raises:
        ValidationError: If required settings are missing or invalid.
    """
    return Settings()


# Singleton instance for direct import
settings = get_settings()


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT-SPECIFIC MODEL ROUTING
# ═══════════════════════════════════════════════════════════════════════════════

# Maps agent names to their optimal model
# - Flash: Fast, cost-effective for volume output and structured generation
# - Pro: Deeper reasoning for critical evaluation and complex analysis
AGENT_MODEL_CONFIG: dict[str, str] = {
    # Research agents - Flash for speed + grounding
    "customer_research": "gemini-2.0-flash",
    "Customer Research Agent": "gemini-2.0-flash",

    # Strategy agents - Pro for deeper financial reasoning
    "business_strategy": "gemini-2.5-pro",
    "Business Strategy Agent": "gemini-2.5-pro",

    # PRD sub-workflow
    "prd_generator": "gemini-2.0-flash",  # Volume output
    "PRD Generator": "gemini-2.0-flash",
    "prd_critic": "gemini-2.5-pro",  # Critical evaluation
    "PRD Critic": "gemini-2.5-pro",
    "prd_formatter": "gemini-2.0-flash",  # Formatting speed
    "PRD Formatter": "gemini-2.0-flash",
    "Product Requirements Agent": "gemini-2.0-flash",

    # Technical agents - Flash for deterministic design
    "technical_architect": "gemini-2.0-flash",
    "Technical Architect Agent": "gemini-2.0-flash",

    # Legal review - Pro for regulatory precision
    "legal_regulatory": "gemini-2.5-pro",
    "Legal & Regulatory Review Agent": "gemini-2.5-pro",

    # Quality gate - Pro for critical evaluation
    "critique": "gemini-2.5-pro",
    "Critique Agent": "gemini-2.5-pro",

    # Executive summary - Flash for synthesis speed
    "executive_summary": "gemini-2.0-flash",
    "Executive Summary Generator": "gemini-2.0-flash",

    # V3.0 New agents
    "claim_extractor": "gemini-2.0-flash",  # Fast extraction

    # Market Intelligence (replaces customer_research for prompts)
    "Market Intelligence": "gemini-2.0-flash",

    # Competitive Landscape
    "Competitive Landscape": "gemini-2.0-flash",

    # Customer Personas
    "Customer Personas": "gemini-2.0-flash",

    # Business Case (uses Pro for deeper reasoning)
    "Business Case": "gemini-2.5-pro",

    # Go-to-Market
    "Go-to-Market": "gemini-2.5-pro",

    # Financial Model (using Flash to avoid Railway timeout)
    "Financial Model": "gemini-2.0-flash",

    # Product Requirements
    "Product Requirements": "gemini-2.0-flash",

    # Technical Architecture
    "Technical Architecture": "gemini-2.0-flash",

    # Regulatory & Compliance
    "Regulatory & Compliance": "gemini-2.5-pro",

    # Risk Assessment
    "Risk Assessment": "gemini-2.0-flash",

    # Wireframe Designer
    "Wireframe Designer": "gemini-2.0-flash",

    # Prototype Generator
    "Prototype Generator": "gemini-2.5-pro",

    # Stakeholder Views
    "Stakeholder Views": "gemini-2.5-pro",

    # Validation Playbook
    "Validation Playbook": "gemini-2.5-pro",

    # Critique (evidence-aware)
    "Critique": "gemini-2.5-pro",
}


def get_agent_model(agent_name: str) -> str:
    """
    Get the optimal model for a specific agent.

    Args:
        agent_name: Name of the agent.

    Returns:
        str: Model identifier to use for this agent.
    """
    return AGENT_MODEL_CONFIG.get(agent_name, settings.llm_model)


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT MAX TOKENS CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_MAX_TOKENS_CONFIG: dict[str, int] = {
    # Prototype Generator needs more tokens for React component code
    "Prototype Generator": 16384,

    # Wireframe Designer also generates code
    "Wireframe Designer": 12288,

    # PRD Generator produces large outputs
    "PRD Generator": 12288,
    "Product Requirements Agent": 12288,
}


def get_agent_max_tokens(agent_name: str) -> int:
    """
    Get the max output tokens for a specific agent.

    Args:
        agent_name: Name of the agent.

    Returns:
        int: Max output tokens to use for this agent.
    """
    return AGENT_MAX_TOKENS_CONFIG.get(agent_name, settings.llm_max_tokens)
