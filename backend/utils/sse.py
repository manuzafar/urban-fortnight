"""
Server-Sent Events (SSE) utilities for real-time streaming.

This module provides event types and formatting utilities for streaming
agent progress and insights to the frontend during discovery sessions.
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Optional

from pydantic import BaseModel


class StreamEventType(str, Enum):
    """Types of events that can be streamed during discovery."""

    # Core events
    AGENT_START = "agent_start"  # Agent begins work
    INSIGHT = "insight"  # Key finding discovered
    AGENT_COMPLETE = "agent_complete"  # Agent finished
    PROGRESS = "progress"  # Progress percentage update
    ERROR = "workflow_error"  # Error occurred (avoid 'error' which is reserved by EventSource)
    DONE = "done"  # Session complete
    HEARTBEAT = "heartbeat"  # Keep-alive signal

    # Enhanced events for richer UI
    PLAN_READY = "plan_ready"  # Research plan created
    COMPETITOR_FOUND = "competitor"  # Named competitor identified
    MARKET_DATA = "market_data"  # Market size or trend data
    RISK_IDENTIFIED = "risk"  # Risk flagged
    FINANCIAL_METRIC = "financial"  # Financial data point
    DIAGRAM_READY = "diagram"  # Architecture diagram available
    CITATION = "citation"  # Source citation for claim
    DECISION_POINT = "decision"  # Key decision identified

    # V3.0 design and synthesis events
    WIREFRAME_READY = "wireframe_ready"  # Wireframe screen generated
    PROTOTYPE_READY = "prototype_ready"  # Interactive prototype ready
    DESIGN_PHASE = "design_phase"  # Design phase started/completed
    CLAIM_EXTRACTED = "claim_extracted"  # Cross-reference claim added
    EVIDENCE_SCORE = "evidence_score"  # Evidence score updated
    STAKEHOLDER_VIEW = "stakeholder_view"  # Stakeholder view generated
    VALIDATION_EXPERIMENT = "validation_experiment"  # Experiment defined

    # V4.0 transparency events
    PHASE_START = "phase_start"  # Phase execution started
    PHASE_COMPLETE = "phase_complete"  # Phase execution completed
    CONSTRAINT_INJECTED = "constraint_injected"  # Constraint passed between phases
    REVISION_STARTED = "revision_started"  # Quality revision loop started
    REVISION_COMPLETE = "revision_complete"  # Quality revision loop completed
    PARALLEL_START = "parallel_start"  # Parallel agent group started


class StreamEvent(BaseModel):
    """A single SSE event to be streamed to the client."""

    type: StreamEventType
    agent: Optional[str] = None
    data: dict[str, Any]
    timestamp: datetime = None

    def __init__(self, **kwargs):
        if "timestamp" not in kwargs or kwargs["timestamp"] is None:
            kwargs["timestamp"] = datetime.utcnow()
        super().__init__(**kwargs)

    def to_sse_format(self) -> str:
        """Format the event as an SSE message string."""
        event_data = {
            "type": self.type.value,
            "agent": self.agent,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }
        return f"event: {self.type.value}\ndata: {json.dumps(event_data)}\n\n"


# Agent display names and descriptions
AGENT_INFO = {
    "planner": {
        "name": "Research Planner",
        "icon": "compass",
        "description": "Creating research strategy and plan",
    },
    "legal_preliminary": {
        "name": "Legal Scout",
        "icon": "shield-check",
        "description": "Quick regulatory landscape scan",
    },
    "customer_research": {
        "name": "Customer Research",
        "icon": "search",
        "description": "Analyzing market and customer needs",
    },
    "convergence": {
        "name": "Synthesis",
        "icon": "git-merge",
        "description": "Merging parallel research tracks",
    },
    "business_strategy": {
        "name": "Business Strategy",
        "icon": "trending-up",
        "description": "Building business case and revenue model",
    },
    "product_requirements": {
        "name": "Product Requirements",
        "icon": "file-text",
        "description": "Generating PRD with epics and stories",
    },
    "technical_architect": {
        "name": "Technical Architecture",
        "icon": "cpu",
        "description": "Designing system architecture",
    },
    "legal_regulatory": {
        "name": "Legal Review",
        "icon": "shield",
        "description": "Reviewing compliance and regulations",
    },
    "critique": {
        "name": "Quality Check",
        "icon": "check-circle",
        "description": "Validating quality and consistency",
    },
    "executive_summary": {
        "name": "Summary",
        "icon": "file-check",
        "description": "Generating executive summary",
    },
    # V3.0 new agents
    "gtm_strategy": {
        "name": "Go-to-Market",
        "icon": "rocket",
        "description": "Building go-to-market strategy",
    },
    "financial_model": {
        "name": "Financial Model",
        "icon": "dollar-sign",
        "description": "Creating financial projections",
    },
    "wireframe_designer": {
        "name": "Wireframe Designer",
        "icon": "layout",
        "description": "Generating UI wireframes",
    },
    "prototype_generator": {
        "name": "Prototype",
        "icon": "code",
        "description": "Creating interactive prototype",
    },
    "stakeholder_views": {
        "name": "Stakeholder Views",
        "icon": "users",
        "description": "Generating stakeholder briefings",
    },
    "validation_playbook": {
        "name": "Validation Playbook",
        "icon": "clipboard-check",
        "description": "Designing validation experiments",
    },
    "claim_extractor": {
        "name": "Evidence Tracker",
        "icon": "database",
        "description": "Extracting and grading claims",
    },
}


def get_agent_display_info(agent_key: str) -> dict[str, str]:
    """Get display information for an agent."""
    return AGENT_INFO.get(
        agent_key,
        {
            "name": agent_key.replace("_", " ").title(),
            "icon": "cpu",
            "description": f"Running {agent_key}",
        },
    )


class SessionEventEmitter:
    """
    Event emitter for a single discovery session.

    Manages a queue of events that can be consumed by an SSE endpoint.
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        self._closed = False

    async def emit(self, event: StreamEvent) -> None:
        """Add an event to the queue."""
        if not self._closed:
            await self.queue.put(event)

    async def emit_agent_start(self, agent: str, message: Optional[str] = None) -> None:
        """Emit an agent start event."""
        info = get_agent_display_info(agent)
        await self.emit(
            StreamEvent(
                type=StreamEventType.AGENT_START,
                agent=agent,
                data={
                    "message": message or info["description"],
                    "display_name": info["name"],
                    "icon": info["icon"],
                },
            )
        )

    async def emit_insight(
        self,
        agent: str,
        key: str,
        value: str,
        preview: Optional[Any] = None,
    ) -> None:
        """Emit an insight event."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.INSIGHT,
                agent=agent,
                data={
                    "key": key,
                    "value": value,
                    "preview": preview,
                },
            )
        )

    async def emit_agent_complete(
        self,
        agent: str,
        summary: str,
        insights_count: int = 0,
    ) -> None:
        """Emit an agent complete event."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.AGENT_COMPLETE,
                agent=agent,
                data={
                    "summary": summary,
                    "insights_count": insights_count,
                },
            )
        )

    async def emit_progress(self, percentage: int, current_agent: str) -> None:
        """Emit a progress update event."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.PROGRESS,
                agent=current_agent,
                data={
                    "percentage": percentage,
                    "current_agent": current_agent,
                },
            )
        )

    async def emit_error(self, error_message: str, agent: Optional[str] = None) -> None:
        """Emit an error event."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.ERROR,
                agent=agent,
                data={
                    "message": error_message,
                },
            )
        )

    async def emit_done(self, status: str = "completed", pack: dict | None = None) -> None:
        """Emit completion event and close the emitter.

        Args:
            status: Completion status ('completed' or 'failed')
            pack: Optional inception pack data to include in the done event
        """
        data = {
            "session_id": self.session_id,
            "status": status,
        }
        if pack is not None:
            data["pack"] = pack
        await self.emit(
            StreamEvent(
                type=StreamEventType.DONE,
                data=data,
            )
        )
        self._closed = True

    async def emit_heartbeat(self) -> None:
        """Emit a heartbeat to keep the connection alive."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.HEARTBEAT,
                data={"timestamp": datetime.utcnow().isoformat()},
            )
        )

    async def emit_plan_ready(self, domain_type: str, summary: str) -> None:
        """Emit event when research plan is ready."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.PLAN_READY,
                agent="planner",
                data={
                    "domain_type": domain_type,
                    "summary": summary,
                },
            )
        )

    async def emit_competitor(
        self,
        agent: str,
        name: str,
        competitor_type: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Emit event when a competitor is identified."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.COMPETITOR_FOUND,
                agent=agent,
                data={
                    "name": name,
                    "type": competitor_type,
                    "details": details or {},
                },
            )
        )

    async def emit_market_data(
        self,
        agent: str,
        metric: str,
        value: str,
        source: Optional[str] = None,
    ) -> None:
        """Emit market data point."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.MARKET_DATA,
                agent=agent,
                data={
                    "metric": metric,
                    "value": value,
                    "source": source,
                },
            )
        )

    async def emit_risk(
        self,
        agent: str,
        risk_name: str,
        severity: str,
        mitigation: Optional[str] = None,
    ) -> None:
        """Emit identified risk."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.RISK_IDENTIFIED,
                agent=agent,
                data={
                    "risk": risk_name,
                    "severity": severity,
                    "mitigation": mitigation,
                },
            )
        )

    async def emit_financial(
        self,
        agent: str,
        metric: str,
        value: str,
        context: Optional[str] = None,
    ) -> None:
        """Emit financial metric."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.FINANCIAL_METRIC,
                agent=agent,
                data={
                    "metric": metric,
                    "value": value,
                    "context": context,
                },
            )
        )

    async def emit_diagram(
        self,
        agent: str,
        diagram_type: str,
        content: str,
    ) -> None:
        """Emit diagram content (e.g., Mermaid)."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.DIAGRAM_READY,
                agent=agent,
                data={
                    "diagram_type": diagram_type,
                    "content": content,
                },
            )
        )

    async def emit_citation(
        self,
        agent: str,
        claim: str,
        source: str,
        date: Optional[str] = None,
    ) -> None:
        """Emit a citation for a claim."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.CITATION,
                agent=agent,
                data={
                    "claim": claim,
                    "source": source,
                    "date": date,
                },
            )
        )

    async def emit_decision_point(
        self,
        title: str,
        options: list[str],
        recommendation: Optional[str] = None,
    ) -> None:
        """Emit a key decision point."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.DECISION_POINT,
                agent="executive_summary",
                data={
                    "title": title,
                    "options": options,
                    "recommendation": recommendation,
                },
            )
        )

    # V4.0 Transparency events
    async def emit_phase_start(
        self,
        phase: str,
        agents: list[str],
    ) -> None:
        """Emit event when a phase starts execution."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.PHASE_START,
                data={
                    "phase": phase,
                    "agents": agents,
                },
            )
        )

    async def emit_phase_complete(
        self,
        phase: str,
    ) -> None:
        """Emit event when a phase completes."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.PHASE_COMPLETE,
                data={
                    "phase": phase,
                },
            )
        )

    async def emit_constraint_injected(
        self,
        from_agent: str,
        from_phase: str,
        to_agents: list[str],
        to_phase: str,
        constraint_type: str,
        summary: str,
    ) -> None:
        """Emit event when constraints are passed between phases."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.CONSTRAINT_INJECTED,
                data={
                    "from_agent": from_agent,
                    "from_phase": from_phase,
                    "to_agents": to_agents,
                    "to_phase": to_phase,
                    "constraint_type": constraint_type,
                    "summary": summary,
                },
            )
        )

    async def emit_revision_started(
        self,
        agent: str,
        iteration: int,
        max_iterations: int,
        failed_criteria: list[str],
    ) -> None:
        """Emit event when a quality revision loop starts."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.REVISION_STARTED,
                agent=agent,
                data={
                    "agent": agent,
                    "iteration": iteration,
                    "max_iterations": max_iterations,
                    "failed_criteria": failed_criteria,
                },
            )
        )

    async def emit_revision_complete(
        self,
        agent: str,
        iteration: int,
        improvements: Optional[list[str]] = None,
    ) -> None:
        """Emit event when a quality revision loop completes."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.REVISION_COMPLETE,
                agent=agent,
                data={
                    "agent": agent,
                    "iteration": iteration,
                    "improvements": improvements or [],
                },
            )
        )

    async def emit_parallel_start(
        self,
        agents: list[str],
        phase: str,
    ) -> None:
        """Emit event when parallel agents start execution."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.PARALLEL_START,
                data={
                    "agents": agents,
                    "phase": phase,
                },
            )
        )

    def close(self) -> None:
        """Close the emitter."""
        self._closed = True

    @property
    def is_closed(self) -> bool:
        """Check if the emitter is closed."""
        return self._closed

    async def events(self) -> AsyncGenerator[StreamEvent, None]:
        """Async generator for consuming events."""
        while not self._closed:
            try:
                event = await asyncio.wait_for(self.queue.get(), timeout=30.0)
                yield event
                if event.type == StreamEventType.DONE:
                    break
            except asyncio.TimeoutError:
                # Send heartbeat on timeout
                yield StreamEvent(
                    type=StreamEventType.HEARTBEAT,
                    data={"timestamp": datetime.utcnow().isoformat()},
                )


# Global registry of active session emitters
_session_emitters: dict[str, SessionEventEmitter] = {}


def get_or_create_emitter(session_id: str) -> SessionEventEmitter:
    """Get or create an event emitter for a session."""
    if session_id not in _session_emitters:
        _session_emitters[session_id] = SessionEventEmitter(session_id)
    return _session_emitters[session_id]


def get_emitter(session_id: str) -> Optional[SessionEventEmitter]:
    """Get the event emitter for a session if it exists."""
    return _session_emitters.get(session_id)


def remove_emitter(session_id: str) -> None:
    """Remove an emitter from the registry."""
    if session_id in _session_emitters:
        _session_emitters[session_id].close()
        del _session_emitters[session_id]


async def stream_session_events(session_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator that yields SSE-formatted event strings for a session.

    This is the main entry point for SSE streaming endpoints.
    """
    emitter = get_or_create_emitter(session_id)

    try:
        async for event in emitter.events():
            yield event.to_sse_format()
    finally:
        remove_emitter(session_id)
