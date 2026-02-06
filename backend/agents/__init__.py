"""
Agent modules for the Product Discovery Multi-Agent System.

This package contains:
- state: LangGraph state definition
- prompts: Agent prompt templates
- base_agent: Shared LLM utilities
- Individual agent implementations
- orchestrator: LangGraph workflow
"""

from agents.state import (
    DiscoveryState,
    AgentOutput,
    CritiqueFeedback,
    create_initial_state,
    get_progress_percentage,
    get_current_agent_name,
)
from agents.prompts import (
    CUSTOMER_RESEARCH_PROMPT,
    BUSINESS_STRATEGY_PROMPT,
    PRODUCT_REQUIREMENTS_PROMPT,
    TECHNICAL_ARCHITECT_PROMPT,
    LEGAL_REGULATORY_PROMPT,
    LEGAL_PRELIMINARY_PROMPT,
    CRITIQUE_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    format_prompt,
)
from agents.base_agent import (
    configure_gemini,
    call_llm,
    LLMError,
    JSONParseError,
)
from agents.customer_research import (
    run_customer_research_agent,
    get_customer_research_summary,
)
from agents.business_strategy import (
    run_business_strategy_agent,
    get_business_case_summary,
)
from agents.product_requirements import (
    run_product_requirements_agent,
    get_product_requirements_summary,
    count_user_stories,
    get_story_priority_distribution,
)
from agents.technical_architect import (
    run_technical_architect_agent,
    get_technical_architecture_summary,
)
from agents.legal_regulatory import (
    run_legal_regulatory_agent,
    run_legal_preliminary_scan,
    get_legal_regulatory_summary,
)
from agents.critique import (
    run_critique_agent,
    should_revise,
    get_quality_summary,
)
from agents.orchestrator import (
    build_discovery_graph,
    create_discovery_workflow,
    run_discovery_workflow,
    get_workflow_state,
)
from agents.facilitator import (
    FacilitatorAgent,
    run_facilitator,
)
from agents.swarms import (
    BaseSwarm,
    DiscoverySwarm,
    StrategySwarm,
    DeliverySwarm,
)

__all__ = [
    # State
    "DiscoveryState",
    "AgentOutput",
    "CritiqueFeedback",
    "create_initial_state",
    "get_progress_percentage",
    "get_current_agent_name",
    # Prompts
    "CUSTOMER_RESEARCH_PROMPT",
    "BUSINESS_STRATEGY_PROMPT",
    "PRODUCT_REQUIREMENTS_PROMPT",
    "TECHNICAL_ARCHITECT_PROMPT",
    "LEGAL_REGULATORY_PROMPT",
    "LEGAL_PRELIMINARY_PROMPT",
    "CRITIQUE_PROMPT",
    "EXECUTIVE_SUMMARY_PROMPT",
    "format_prompt",
    # Base Agent
    "configure_gemini",
    "call_llm",
    "LLMError",
    "JSONParseError",
    # Agents
    "run_customer_research_agent",
    "get_customer_research_summary",
    "run_business_strategy_agent",
    "get_business_case_summary",
    "run_product_requirements_agent",
    "get_product_requirements_summary",
    "count_user_stories",
    "get_story_priority_distribution",
    "run_technical_architect_agent",
    "get_technical_architecture_summary",
    "run_legal_regulatory_agent",
    "run_legal_preliminary_scan",
    "get_legal_regulatory_summary",
    "run_critique_agent",
    "should_revise",
    "get_quality_summary",
    # Orchestrator
    "build_discovery_graph",
    "create_discovery_workflow",
    "run_discovery_workflow",
    "get_workflow_state",
    # Facilitator
    "FacilitatorAgent",
    "run_facilitator",
    # Swarms
    "BaseSwarm",
    "DiscoverySwarm",
    "StrategySwarm",
    "DeliverySwarm",
]
