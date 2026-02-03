"""
FastAPI application for the Product Discovery Multi-Agent System.

This module provides the REST API for:
- Starting product discovery sessions
- Checking session status
- Retrieving completed inception packs

Endpoints:
- POST /api/discovery/start - Start a new discovery session
- GET /api/discovery/session/{session_id} - Get session status/results
- GET /api/health - Health check
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agents.orchestrator import run_discovery_workflow
from agents.state import get_progress_percentage
from config import settings
from models.schemas import (
    DiscoveryRequest,
    DiscoveryResponse,
    SessionStatus,
    SessionStatusResponse,
    InceptionPack,
)
from utils.helpers import (
    generate_session_id,
    setup_logging,
    sanitize_input,
    sanitize_constraints,
    build_inception_pack,
    SessionStore,
)

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)

# In-memory session store
session_store = SessionStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Runs startup and shutdown tasks.
    """
    # Startup
    logger.info(
        "application_startup",
        environment=settings.app_env,
        debug=settings.debug,
        model=settings.llm_model,
    )
    yield
    # Shutdown
    logger.info("application_shutdown")


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Product Discovery Multi-Agent System",
    description=(
        "AI-powered product discovery that transforms product ideas into "
        "comprehensive inception packs with PRDs, business cases, and technical architecture."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# CORS middleware - allow all origins for deployment flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# EXCEPTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        path=request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASK
# ═══════════════════════════════════════════════════════════════════════════════


async def run_discovery_task(
    session_id: str,
    product_idea: str,
    industry: str | None,
    target_market: str | None,
    constraints: list[str] | None,
    additional_context: str | None,
) -> None:
    """
    Background task to run the discovery workflow.

    Updates session store with progress and final results.

    Args:
        session_id: Unique session identifier.
        product_idea: The product idea to analyze.
        industry: Optional industry context.
        target_market: Optional target market.
        constraints: Optional constraints.
        additional_context: Optional additional context.
    """
    logger.info("discovery_task_started", session_id=session_id)

    try:
        # Update status to in progress
        session_store.update(
            session_id,
            {
                "status": SessionStatus.IN_PROGRESS,
                "current_agent": "Customer Research Agent",
                "iteration": 1,
                "progress_percentage": 0,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        # Run the workflow
        final_state = await run_discovery_workflow(
            session_id=session_id,
            product_idea=product_idea,
            industry=industry,
            target_market=target_market,
            constraints=constraints,
            additional_context=additional_context,
        )

        # Build the inception pack
        inception_pack = build_inception_pack(final_state)

        # Update session with results
        session_store.update(
            session_id,
            {
                "status": final_state.get("status", SessionStatus.COMPLETED),
                "current_agent": "Complete",
                "iteration": final_state.get("iteration", 1),
                "progress_percentage": 100,
                "inception_pack": inception_pack,
                "errors": final_state.get("errors", []),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )

        logger.info(
            "discovery_task_completed",
            session_id=session_id,
            status=final_state.get("status"),
            quality_score=(final_state.get("quality_assessment") or {}).get("overall_score"),
        )

    except Exception as e:
        logger.error(
            "discovery_task_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )

        # Update session with error
        session_store.update(
            session_id,
            {
                "status": SessionStatus.FAILED,
                "error_message": str(e),
                "updated_at": datetime.utcnow().isoformat(),
            },
        )


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        dict: Health status and configuration info.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.app_env,
        "active_sessions": session_store.count(),
    }


@app.post(
    "/api/discovery/start",
    response_model=DiscoveryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Discovery"],
    summary="Start a new product discovery session",
    description=(
        "Initiates a new product discovery workflow. The workflow runs in the background "
        "and can take 3-5 minutes to complete. Use the session ID to check status."
    ),
)
async def start_discovery(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks,
) -> DiscoveryResponse:
    """
    Start a new product discovery session.

    Creates a new session and launches the discovery workflow
    as a background task.

    Args:
        request: Discovery request with product idea and context.
        background_tasks: FastAPI background tasks handler.

    Returns:
        DiscoveryResponse: Session ID and initial status.

    Raises:
        HTTPException: If max concurrent sessions reached.
    """
    # Check session limit
    max_sessions = settings.max_concurrent_sessions
    if max_sessions > 0 and session_store.count() >= max_sessions:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Maximum concurrent sessions ({max_sessions}) reached. Please try again later.",
        )

    # Generate session ID
    session_id = generate_session_id()

    # Sanitize inputs
    product_idea = sanitize_input(request.product_idea)
    industry = sanitize_input(request.industry) if request.industry else None
    target_market = sanitize_input(request.target_market) if request.target_market else None
    constraints = sanitize_constraints(request.constraints)
    additional_context = (
        sanitize_input(request.additional_context) if request.additional_context else None
    )

    # Create session
    created_at = datetime.utcnow()
    session_store.create(
        session_id,
        {
            "status": SessionStatus.PENDING,
            "product_idea": product_idea,
            "industry": industry,
            "target_market": target_market,
            "constraints": constraints,
            "additional_context": additional_context,
            "current_agent": None,
            "iteration": 1,
            "progress_percentage": 0,
            "inception_pack": None,
            "error_message": None,
            "errors": [],
            "created_at": created_at.isoformat(),
            "updated_at": created_at.isoformat(),
        },
    )

    logger.info(
        "discovery_session_created",
        session_id=session_id,
        product_idea=product_idea[:100],
        industry=industry,
    )

    # Launch background task
    background_tasks.add_task(
        run_discovery_task,
        session_id=session_id,
        product_idea=product_idea,
        industry=industry,
        target_market=target_market,
        constraints=constraints,
        additional_context=additional_context,
    )

    return DiscoveryResponse(
        session_id=session_id,
        status=SessionStatus.PENDING,
        message="Discovery session started. Use the session ID to check status.",
        created_at=created_at,
    )


@app.get(
    "/api/discovery/session/{session_id}",
    response_model=SessionStatusResponse,
    tags=["Discovery"],
    summary="Get discovery session status",
    description=(
        "Retrieves the current status of a discovery session. "
        "When completed, includes the full inception pack."
    ),
)
async def get_session_status(session_id: str) -> SessionStatusResponse:
    """
    Get the status of a discovery session.

    Args:
        session_id: The session ID to look up.

    Returns:
        SessionStatusResponse: Current session status and results.

    Raises:
        HTTPException: If session not found.
    """
    session_data = session_store.get(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found or has expired.",
        )

    # Parse datetime strings back to datetime objects
    created_at_str = session_data.get("created_at")
    updated_at_str = session_data.get("updated_at")

    created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.utcnow()
    updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else datetime.utcnow()

    # Build response
    response_data = {
        "session_id": session_id,
        "status": session_data.get("status", SessionStatus.PENDING),
        "current_agent": session_data.get("current_agent"),
        "iteration": session_data.get("iteration", 1),
        "progress_percentage": session_data.get("progress_percentage", 0),
        "created_at": created_at,
        "updated_at": updated_at,
    }

    # Add inception pack if completed
    if session_data.get("status") == SessionStatus.COMPLETED:
        response_data["inception_pack"] = session_data.get("inception_pack")

    # Add error message if failed
    if session_data.get("status") == SessionStatus.FAILED:
        response_data["error_message"] = session_data.get("error_message")

    return SessionStatusResponse(**response_data)


@app.get(
    "/api/discovery/session/{session_id}/pack",
    tags=["Discovery"],
    summary="Get inception pack only",
    description="Retrieves just the inception pack for a completed session.",
)
async def get_inception_pack(session_id: str) -> dict[str, Any]:
    """
    Get the inception pack for a completed session.

    Args:
        session_id: The session ID to look up.

    Returns:
        dict: The complete inception pack.

    Raises:
        HTTPException: If session not found or not completed.
    """
    session_data = session_store.get(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found or has expired.",
        )

    if session_data.get("status") != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not completed. Current status: {session_data.get('status')}",
        )

    inception_pack = session_data.get("inception_pack")
    if not inception_pack:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inception pack not available.",
        )

    return inception_pack


@app.delete(
    "/api/discovery/session/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Discovery"],
    summary="Delete a discovery session",
    description="Deletes a discovery session and its data.",
)
async def delete_session(session_id: str) -> None:
    """
    Delete a discovery session.

    Args:
        session_id: The session ID to delete.

    Raises:
        HTTPException: If session not found.
    """
    if not session_store.delete(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    logger.info("session_deleted", session_id=session_id)


@app.get(
    "/api/discovery/sessions",
    tags=["Discovery"],
    summary="List active sessions",
    description="Lists all active discovery sessions (admin endpoint).",
)
async def list_sessions() -> dict[str, Any]:
    """
    List all active sessions.

    Returns:
        dict: List of active session IDs and count.
    """
    session_ids = session_store.get_all_session_ids()
    return {
        "count": len(session_ids),
        "sessions": session_ids,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
