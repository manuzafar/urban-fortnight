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
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sse_starlette.sse import EventSourceResponse

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
)
from utils.auth import get_current_user_id, get_user_id_from_token
from utils.db import SupabaseSessionStore
from utils.sse import (
    get_or_create_emitter,
    get_emitter,
    remove_emitter,
    stream_session_events,
    StreamEventType,
)
from api.discovery_v4_routes import router as discovery_v4_router

# ═══════════════════════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)

# Persistent session store (Supabase PostgreSQL)
session_store = SupabaseSessionStore()


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

# CORS middleware - explicit origins required for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Discovery V4 routes
app.include_router(discovery_v4_router)


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
    user_id: str,
    product_idea: str,
    industry: str | None,
    target_market: str | None,
    constraints: list[str] | None,
    additional_context: str | None,
) -> None:
    """
    Background task to run the discovery workflow.

    Updates Supabase DB with progress and final results.
    Also emits SSE events for real-time streaming to frontend.

    Args:
        session_id: Unique session identifier.
        user_id: Supabase user ID who owns this session.
        product_idea: The product idea to analyze.
        industry: Optional industry context.
        target_market: Optional target market.
        constraints: Optional constraints.
        additional_context: Optional additional context.
    """
    logger.info("discovery_task_started", session_id=session_id, user_id=user_id)

    # Get or create SSE emitter for this session
    emitter = get_or_create_emitter(session_id)

    try:
        # Update status to in progress
        session_store.update_status(
            session_id,
            {
                "status": SessionStatus.IN_PROGRESS,
                "current_agent": "Customer Research Agent",
                "iteration": 1,
                "progress_percentage": 0,
            },
        )

        # Run the workflow with SSE callback
        final_state = await run_discovery_workflow(
            session_id=session_id,
            product_idea=product_idea,
            industry=industry,
            target_market=target_market,
            constraints=constraints,
            additional_context=additional_context,
            event_emitter=emitter,
        )

        # Build the inception pack
        inception_pack = build_inception_pack(final_state)

        # Save inception pack to separate table
        session_store.save_inception_pack(session_id, user_id, inception_pack)

        # Update session status
        session_store.update_status(
            session_id,
            {
                "status": final_state.get("status", SessionStatus.COMPLETED),
                "current_agent": "Complete",
                "iteration": final_state.get("iteration", 1),
                "progress_percentage": 100,
                "errors": final_state.get("errors", []),
            },
        )

        # Determine actual completion status
        actual_status = final_state.get("status", SessionStatus.COMPLETED)
        is_success = actual_status == SessionStatus.COMPLETED

        logger.info(
            "discovery_task_completed",
            session_id=session_id,
            status=actual_status,
            is_success=is_success,
            quality_score=(final_state.get("quality_assessment") or {}).get("overall_score"),
        )

        # Emit completion event with actual status
        await emitter.emit_done(status="completed" if is_success else "failed")

        # Send founder alert email (fire and forget, don't block on failure)
        if final_state.get("status") == SessionStatus.COMPLETED:
            try:
                from utils.email import send_founder_alert, get_user_email_from_supabase

                user_email = await get_user_email_from_supabase(user_id)
                if user_email:
                    product_name = inception_pack.get("executive_summary", {}).get("product_name")
                    await send_founder_alert(
                        user_email=user_email,
                        product_idea=product_idea[:500],
                        session_id=session_id,
                        product_name=product_name,
                    )
            except Exception as email_error:
                logger.warning(
                    "founder_alert_exception",
                    error=str(email_error),
                    session_id=session_id,
                )

    except Exception as e:
        logger.error(
            "discovery_task_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )

        # Emit error event
        await emitter.emit_error(str(e))
        await emitter.emit_done(status="failed")

        # Update session with error
        session_store.update_status(
            session_id,
            {
                "status": SessionStatus.FAILED,
                "error_message": str(e),
            },
        )

    finally:
        # Clean up emitter
        remove_emitter(session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/health", tags=["Health"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns 200 even if database is slow to connect, to prevent
    Railway health check timeouts during startup.

    Returns:
        dict: Health status and configuration info.
    """
    try:
        active = session_store.count_active()
    except Exception:
        active = -1  # DB not ready, but app is alive

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.app_env,
        "active_sessions": active,
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
    user_id: str = Depends(get_current_user_id),
) -> DiscoveryResponse:
    """
    Start a new product discovery session.

    Creates a new session and launches the discovery workflow
    as a background task. Requires authentication.

    Args:
        request: Discovery request with product idea and context.
        background_tasks: FastAPI background tasks handler.
        user_id: Authenticated user ID from JWT.

    Returns:
        DiscoveryResponse: Session ID and initial status.

    Raises:
        HTTPException: If max concurrent sessions reached.
    """
    # Check session limit
    max_sessions = settings.max_concurrent_sessions
    if max_sessions > 0 and session_store.count_active() >= max_sessions:
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

    # Create session in database
    created_at = datetime.utcnow()
    session_store.create(
        session_id,
        user_id=user_id,
        data={
            "status": SessionStatus.PENDING,
            "product_idea": product_idea,
            "industry": industry,
            "target_market": target_market,
            "constraints": constraints,
            "additional_context": additional_context,
            "current_agent": None,
            "iteration": 1,
            "progress_percentage": 0,
            "error_message": None,
            "errors": [],
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
        user_id=user_id,
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
async def get_session_status(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> SessionStatusResponse:
    """
    Get the status of a discovery session. Requires authentication.

    Args:
        session_id: The session ID to look up.
        user_id: Authenticated user ID from JWT.

    Returns:
        SessionStatusResponse: Current session status and results.

    Raises:
        HTTPException: If session not found or not owned by user.
    """
    session_data = session_store.get(session_id)

    if not session_data or session_data.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Build response
    response_data = {
        "session_id": session_data["id"],
        "status": session_data.get("status", SessionStatus.PENDING),
        "current_agent": session_data.get("current_agent"),
        "iteration": session_data.get("iteration", 1),
        "progress_percentage": session_data.get("progress_percentage", 0),
        "created_at": session_data["created_at"],
        "updated_at": session_data["updated_at"],
    }

    # Fetch inception pack from separate table if completed
    if session_data.get("status") == SessionStatus.COMPLETED:
        pack = session_store.get_inception_pack(session_id)
        if pack:
            response_data["inception_pack"] = pack

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
async def get_inception_pack(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Get the inception pack for a completed session. Requires authentication.

    Args:
        session_id: The session ID to look up.
        user_id: Authenticated user ID from JWT.

    Returns:
        dict: The complete inception pack.

    Raises:
        HTTPException: If session not found, not owned by user, or not completed.
    """
    if not session_store.verify_ownership(session_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    session_data = session_store.get(session_id)

    if session_data.get("status") != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not completed. Current status: {session_data.get('status')}",
        )

    inception_pack = session_store.get_inception_pack(session_id)
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
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Delete a discovery session. Requires authentication.

    Args:
        session_id: The session ID to delete.
        user_id: Authenticated user ID from JWT.

    Raises:
        HTTPException: If session not found or not owned by user.
    """
    if not session_store.verify_ownership(session_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    session_store.delete(session_id)
    logger.info("session_deleted", session_id=session_id, user_id=user_id)


@app.get(
    "/api/discovery/sessions",
    tags=["Discovery"],
    summary="List user's sessions",
    description="Lists all discovery sessions for the authenticated user.",
)
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    List all sessions for the authenticated user.

    Args:
        user_id: Authenticated user ID from JWT.

    Returns:
        dict: List of user's sessions and count.
    """
    sessions = session_store.get_user_sessions(user_id)
    return {
        "count": len(sessions),
        "sessions": sessions,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SSE STREAMING ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════


@app.get(
    "/api/discovery/session/{session_id}/stream",
    tags=["Discovery"],
    summary="Stream session events",
    description=(
        "Stream real-time updates for a discovery session via Server-Sent Events. "
        "Events include agent starts, insights, completions, and progress updates. "
        "Authentication can be via Authorization header or 'token' query parameter."
    ),
)
async def stream_session(
    session_id: str,
    token: str | None = Query(default=None, description="JWT token for SSE auth"),
    user_id: str | None = None,
):
    """
    Stream real-time updates via Server-Sent Events.

    This endpoint provides a real-time event stream for monitoring
    discovery session progress. Events are sent as agents start,
    find insights, and complete their work.

    Since EventSource API doesn't support custom headers, authentication
    can be provided via the 'token' query parameter as an alternative
    to the Authorization header.

    Event Types:
    - agent_start: An agent has started processing
    - insight: A key finding has been discovered
    - agent_complete: An agent has finished
    - progress: Overall progress percentage update
    - error: An error has occurred
    - done: Session is complete
    - heartbeat: Keep-alive signal (every 30s)

    Args:
        session_id: The session ID to stream.
        token: Optional JWT token (for EventSource which can't send headers).
        user_id: Not used directly, extracted from token.

    Returns:
        EventSourceResponse: SSE event stream.

    Raises:
        HTTPException: If session not found, not owned by user, or auth fails.
    """
    # Get user_id from token query param (EventSource doesn't support headers)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide token query parameter.",
        )

    try:
        user_id = get_user_id_from_token(token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )

    # Verify session ownership
    if not session_store.verify_ownership(session_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Get session status
    session_data = session_store.get(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # If session is already completed, send done event immediately
    if session_data.get("status") == SessionStatus.COMPLETED:
        async def completed_stream():
            yield {
                "event": "done",
                "data": json.dumps({
                    "type": "done",
                    "agent": None,
                    "data": {"session_id": session_id, "status": "completed"},
                    "timestamp": datetime.utcnow().isoformat(),
                }),
            }

        return EventSourceResponse(completed_stream())

    # If session failed, send error and done
    if session_data.get("status") == SessionStatus.FAILED:
        async def failed_stream():
            error_msg = session_data.get("error_message") or "Unknown error"
            yield {
                "event": "workflow_error",
                "data": json.dumps({
                    "type": "workflow_error",
                    "agent": None,
                    "data": {"message": error_msg},
                    "timestamp": datetime.utcnow().isoformat(),
                }),
            }
            yield {
                "event": "done",
                "data": json.dumps({
                    "type": "done",
                    "agent": None,
                    "data": {"session_id": session_id, "status": "failed"},
                    "timestamp": datetime.utcnow().isoformat(),
                }),
            }

        return EventSourceResponse(failed_stream())

    # Stream events for in-progress sessions
    async def event_stream():
        # Send an immediate heartbeat to establish the connection
        # This prevents browser timeout while waiting for the first real event
        yield {
            "event": "heartbeat",
            "data": json.dumps({
                "type": "heartbeat",
                "agent": None,
                "data": {"timestamp": datetime.utcnow().isoformat(), "session_id": session_id},
                "timestamp": datetime.utcnow().isoformat(),
            }),
        }

        async for event_str in stream_session_events(session_id):
            # Parse the SSE format to extract event and data
            lines = event_str.strip().split("\n")
            event_type = None
            event_data = None

            for line in lines:
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    event_data = line[6:]

            if event_type and event_data:
                yield {
                    "event": event_type,
                    "data": event_data,
                }

    logger.info(
        "sse_stream_started",
        session_id=session_id,
        user_id=user_id,
    )

    return EventSourceResponse(event_stream())


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

# Valid section names for export
VALID_SECTIONS = {
    "executive_summary",
    "customer_research",
    "business_case",
    "product_requirements_document",
    "technical_architecture",
    "legal_regulatory_review",
    "quality_assessment",
}


@app.get(
    "/api/discovery/session/{session_id}/export/pdf",
    tags=["Export"],
    summary="Export inception pack as PDF",
    description="Generates a PDF file of the inception pack or a specific section.",
)
async def export_pdf(
    session_id: str,
    section: str | None = Query(
        default=None,
        description="Optional section to export (e.g., 'executive_summary')",
    ),
    user_id: str = Depends(get_current_user_id),
) -> Response:
    """
    Export an inception pack as a PDF file.

    Args:
        session_id: The session ID to export.
        section: Optional section name to export only that section.
        user_id: Authenticated user ID from JWT.

    Returns:
        Response: PDF file download.

    Raises:
        HTTPException: If session not found, not completed, or invalid section.
    """
    # Validate section if provided
    if section and section not in VALID_SECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid section: {section}. Valid sections are: {', '.join(sorted(VALID_SECTIONS))}",
        )

    # Verify ownership
    if not session_store.verify_ownership(session_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Get session and check status
    session_data = session_store.get(session_id)
    if session_data.get("status") != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not completed. Current status: {session_data.get('status')}",
        )

    # Get inception pack
    pack = session_store.get_inception_pack(session_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inception pack not available.",
        )

    # Generate PDF
    try:
        from utils.export_pdf import generate_pdf, get_pdf_filename

        pdf_bytes = generate_pdf(pack, section)
        filename = get_pdf_filename(session_id, section)

        logger.info(
            "pdf_export_generated",
            session_id=session_id,
            section=section,
            size_bytes=len(pdf_bytes),
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.error(
            "pdf_export_failed",
            session_id=session_id,
            section=section,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}",
        )


@app.get(
    "/api/discovery/session/{session_id}/export/docx",
    tags=["Export"],
    summary="Export inception pack as DOCX",
    description="Generates a Word document of the inception pack or a specific section.",
)
async def export_docx(
    session_id: str,
    section: str | None = Query(
        default=None,
        description="Optional section to export (e.g., 'executive_summary')",
    ),
    user_id: str = Depends(get_current_user_id),
) -> Response:
    """
    Export an inception pack as a DOCX file.

    Args:
        session_id: The session ID to export.
        section: Optional section name to export only that section.
        user_id: Authenticated user ID from JWT.

    Returns:
        Response: DOCX file download.

    Raises:
        HTTPException: If session not found, not completed, or invalid section.
    """
    # Validate section if provided
    if section and section not in VALID_SECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid section: {section}. Valid sections are: {', '.join(sorted(VALID_SECTIONS))}",
        )

    # Verify ownership
    if not session_store.verify_ownership(session_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    # Get session and check status
    session_data = session_store.get(session_id)
    if session_data.get("status") != SessionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not completed. Current status: {session_data.get('status')}",
        )

    # Get inception pack
    pack = session_store.get_inception_pack(session_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inception pack not available.",
        )

    # Generate DOCX
    try:
        from utils.export_docx import generate_docx, get_docx_filename

        docx_bytes = generate_docx(pack, section)
        filename = get_docx_filename(session_id, section)

        logger.info(
            "docx_export_generated",
            session_id=session_id,
            section=section,
            size_bytes=len(docx_bytes),
        )

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.error(
            "docx_export_failed",
            session_id=session_id,
            section=section,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate DOCX: {str(e)}",
        )


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
