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

    AGENT_START = "agent_start"  # Agent begins work
    INSIGHT = "insight"  # Key finding discovered
    AGENT_COMPLETE = "agent_complete"  # Agent finished
    PROGRESS = "progress"  # Progress percentage update
    ERROR = "error"  # Error occurred
    DONE = "done"  # Session complete
    HEARTBEAT = "heartbeat"  # Keep-alive signal


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
    "customer_research": {
        "name": "Customer Research",
        "icon": "search",
        "description": "Analyzing market and customer needs",
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

    async def emit_done(self, status: str = "completed") -> None:
        """Emit completion event and close the emitter."""
        await self.emit(
            StreamEvent(
                type=StreamEventType.DONE,
                data={
                    "session_id": self.session_id,
                    "status": status,
                },
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
