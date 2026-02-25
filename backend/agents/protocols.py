"""
Agent Protocol Definitions for the Product Discovery Multi-Agent System.

This module defines the standard interface contract that all agents must follow.
Using Protocol classes enables structural subtyping (duck typing with type safety),
making it easy for existing agents to adopt the interface without inheritance.

Benefits:
1. Type safety - Static type checkers can verify agent implementations
2. Documentation - Interface requirements are clearly specified
3. Composability - Agents can be swapped, tested, and orchestrated uniformly
4. Dependency tracking - Explicit input/output declarations enable DAG construction

Usage:
    class MyAgent:
        name = "My Agent"
        description = "Does something useful"

        async def run(self, state: DiscoveryState) -> DiscoveryState:
            # Agent implementation
            return state

        def get_required_inputs(self) -> list[str]:
            return ["product_idea"]

        def get_outputs(self) -> list[str]:
            return ["my_output_field"]
"""

from typing import Protocol, Any, runtime_checkable

from agents.state import DiscoveryState


@runtime_checkable
class AgentProtocol(Protocol):
    """
    Standard interface for all agents in the discovery workflow.

    All agents must implement this protocol to be registered and used
    by the orchestrator. The @runtime_checkable decorator enables
    isinstance() checks at runtime.

    Attributes:
        name: Human-readable name of the agent (e.g., "Planning Agent")
        description: Brief description of what the agent does
    """

    name: str
    description: str

    async def run(self, state: DiscoveryState) -> DiscoveryState:
        """
        Execute the agent and return the updated state.

        The agent should:
        1. Read required inputs from state
        2. Perform its analysis/generation
        3. Write outputs to state
        4. Handle errors gracefully (add to state["errors"])

        Args:
            state: Current workflow state containing all inputs and
                   outputs from previous agents.

        Returns:
            DiscoveryState: Updated state with agent outputs populated.

        Note:
            Agents should NOT raise exceptions for recoverable errors.
            Instead, they should add error messages to state["errors"]
            and return the state with appropriate fallback values.
        """
        ...

    def get_required_inputs(self) -> list[str]:
        """
        Return list of state fields this agent requires as input.

        Used by the orchestrator to:
        - Validate state before running the agent
        - Build dependency graphs for parallel execution
        - Provide helpful error messages when inputs are missing

        Returns:
            list[str]: Field names from DiscoveryState that must be present.
                       Core fields like 'session_id' and 'product_idea' are
                       always required implicitly.

        Example:
            return ["research_plan", "customer_research"]
        """
        ...

    def get_outputs(self) -> list[str]:
        """
        Return list of state fields this agent produces.

        Used by the orchestrator to:
        - Build dependency graphs for parallel execution
        - Track which agents have completed
        - Validate workflow completion

        Returns:
            list[str]: Field names that will be populated after agent runs.

        Example:
            return ["business_case", "gtm_plan"]
        """
        ...


class AgentMetadata:
    """
    Metadata container for agent registration and discovery.

    Stores additional information about an agent beyond the protocol
    requirements, useful for UI display, debugging, and orchestration.

    Attributes:
        name: Human-readable agent name
        description: What the agent does
        required_inputs: State fields the agent needs
        outputs: State fields the agent produces
        category: Agent category for grouping (planning, discovery, strategy, etc.)
        uses_grounding: Whether the agent uses Google Search grounding
        uses_pro_model: Whether the agent requires the Pro model
        estimated_duration_seconds: Typical execution time
        retry_on_failure: Whether to retry the agent on failure
        max_retries: Maximum number of retry attempts
    """

    def __init__(
        self,
        name: str,
        description: str,
        required_inputs: list[str],
        outputs: list[str],
        category: str = "general",
        uses_grounding: bool = False,
        uses_pro_model: bool = False,
        estimated_duration_seconds: float = 30.0,
        retry_on_failure: bool = True,
        max_retries: int = 3,
    ):
        self.name = name
        self.description = description
        self.required_inputs = required_inputs
        self.outputs = outputs
        self.category = category
        self.uses_grounding = uses_grounding
        self.uses_pro_model = uses_pro_model
        self.estimated_duration_seconds = estimated_duration_seconds
        self.retry_on_failure = retry_on_failure
        self.max_retries = max_retries

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "required_inputs": self.required_inputs,
            "outputs": self.outputs,
            "category": self.category,
            "uses_grounding": self.uses_grounding,
            "uses_pro_model": self.uses_pro_model,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "retry_on_failure": self.retry_on_failure,
            "max_retries": self.max_retries,
        }


class AgentValidationError(Exception):
    """Raised when an agent does not comply with the AgentProtocol."""

    def __init__(self, agent_name: str, issues: list[str]):
        self.agent_name = agent_name
        self.issues = issues
        message = f"Agent '{agent_name}' does not comply with AgentProtocol:\n"
        message += "\n".join(f"  - {issue}" for issue in issues)
        super().__init__(message)


def validate_agent_protocol(agent: Any) -> list[str]:
    """
    Validate that an object implements the AgentProtocol correctly.

    Performs both structural checks (has required attributes/methods)
    and semantic checks (methods return correct types).

    Args:
        agent: Object to validate against AgentProtocol.

    Returns:
        list[str]: List of validation issues (empty if valid).

    Example:
        issues = validate_agent_protocol(my_agent)
        if issues:
            raise AgentValidationError(my_agent.name, issues)
    """
    issues: list[str] = []

    # Check required attributes
    if not hasattr(agent, "name"):
        issues.append("Missing 'name' attribute")
    elif not isinstance(agent.name, str):
        issues.append(f"'name' should be str, got {type(agent.name).__name__}")
    elif not agent.name.strip():
        issues.append("'name' cannot be empty")

    if not hasattr(agent, "description"):
        issues.append("Missing 'description' attribute")
    elif not isinstance(agent.description, str):
        issues.append(f"'description' should be str, got {type(agent.description).__name__}")

    # Check required methods
    if not hasattr(agent, "run"):
        issues.append("Missing 'run' method")
    elif not callable(agent.run):
        issues.append("'run' is not callable")

    if not hasattr(agent, "get_required_inputs"):
        issues.append("Missing 'get_required_inputs' method")
    elif not callable(agent.get_required_inputs):
        issues.append("'get_required_inputs' is not callable")
    else:
        try:
            inputs = agent.get_required_inputs()
            if not isinstance(inputs, list):
                issues.append(f"'get_required_inputs()' should return list, got {type(inputs).__name__}")
            elif not all(isinstance(i, str) for i in inputs):
                issues.append("'get_required_inputs()' should return list of strings")
        except Exception as e:
            issues.append(f"'get_required_inputs()' raised exception: {e}")

    if not hasattr(agent, "get_outputs"):
        issues.append("Missing 'get_outputs' method")
    elif not callable(agent.get_outputs):
        issues.append("'get_outputs' is not callable")
    else:
        try:
            outputs = agent.get_outputs()
            if not isinstance(outputs, list):
                issues.append(f"'get_outputs()' should return list, got {type(outputs).__name__}")
            elif not all(isinstance(o, str) for o in outputs):
                issues.append("'get_outputs()' should return list of strings")
        except Exception as e:
            issues.append(f"'get_outputs()' raised exception: {e}")

    return issues


def is_protocol_compliant(agent: Any) -> bool:
    """
    Check if an agent is compliant with AgentProtocol.

    Args:
        agent: Object to check.

    Returns:
        bool: True if agent implements AgentProtocol correctly.
    """
    return len(validate_agent_protocol(agent)) == 0
