"""
Discovery V4 API Routes.

This module provides REST API endpoints for the V4 hybrid discovery system
with three modes: Quick, Guided, and Deep.
"""

from datetime import datetime
from typing import Any, Literal

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from models.discovery_v4_schemas import (
    AIAssistanceRequest,
    CreateDiscoverySessionV4Request,
    CreateDiscoverySessionV4Response,
    DiscoveryMode,
    DiscoverySessionV4,
    EvidenceQuality,
    Interview,
    PatternSynthesis,
    RunStageRequest,
    SaveStageOutputRequest,
    SessionStatusV4Response,
    StageState,
    StageStatus,
    TarpitAnalysis,
)
from utils.auth import get_current_user_id
from utils.db import SupabaseSessionStore
from utils.helpers import generate_session_id

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/discovery/v4", tags=["Discovery V4"])

# Initialize session store
session_store = SupabaseSessionStore()


# In-memory session state cache for active sessions
# (Supplements database with fast access to running session state)
_active_sessions: dict[str, DiscoverySessionV4] = {}


def get_session_from_cache_or_db(session_id: str) -> DiscoverySessionV4 | None:
    """Get session from cache or database."""
    if session_id in _active_sessions:
        return _active_sessions[session_id]

    # Load from database
    db_session = session_store.get_v4_session(session_id)
    if not db_session:
        return None

    # Convert to V4 session model
    session = _db_to_session_model(db_session)
    _active_sessions[session_id] = session
    return session


def _db_to_session_model(db_data: dict[str, Any]) -> DiscoverySessionV4:
    """Convert database row to DiscoverySessionV4 model."""
    # Build stages from draft_states
    stages = {
        "problem_love": StageState(),
        "customer_truth": StageState(),
        "opportunity_mapping": StageState(),
        "solution_design": StageState(),
        "validation_plan": StageState(),
    }

    for draft in db_data.get("draft_states", []):
        stage_name = draft.get("stage_name")
        if stage_name in stages:
            stages[stage_name] = StageState(
                status=StageStatus(draft.get("stage_status", "not_started")),
                output=draft.get("stage_output"),
                coaching_messages=draft.get("ai_coaching", []),
                score=draft.get("score"),
            )

    # Convert interviews
    interviews = [
        Interview(
            id=i.get("id"),
            interviewee_name=i.get("interviewee_name", ""),
            interviewee_role=i.get("interviewee_role", ""),
            company_type=i.get("company_type", ""),
            company_size=i.get("company_size", ""),
            interview_date=i.get("interview_date", datetime.now().date()),
            story_raw=i.get("story_raw", ""),
            key_quote=i.get("key_quote", ""),
            struggling_moment=i.get("struggling_moment", ""),
            emotions=i.get("emotions", []),
            current_workaround=i.get("current_workaround", ""),
            desired_outcome=i.get("desired_outcome", ""),
            ai_pain_points=i.get("ai_extracted_insights", {}).get("pain_points", []),
            ai_triggers=i.get("ai_extracted_insights", {}).get("triggers", []),
            ai_goals=i.get("ai_extracted_insights", {}).get("goals", []),
        )
        for i in db_data.get("interviews", [])
    ]

    return DiscoverySessionV4(
        session_id=db_data["id"],
        user_id=db_data.get("user_id", ""),
        mode=DiscoveryMode(db_data.get("mode", "guided")),
        product_idea=db_data.get("product_idea", ""),
        industry=db_data.get("industry"),
        target_market=db_data.get("target_market"),
        stages=stages,
        interviews=interviews,
        patterns=PatternSynthesis(**db_data["patterns"]) if db_data.get("patterns") else None,
        overall_evidence_quality=EvidenceQuality(
            db_data.get("evidence_quality", "E4")
        ),
        quality_score=db_data.get("quality_score", 0),
        created_at=db_data.get("created_at", datetime.utcnow().isoformat()),
        updated_at=db_data.get("updated_at", datetime.utcnow().isoformat()),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT TEST ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/test/sessions", response_model=CreateDiscoverySessionV4Response)
async def create_test_session(
    request: CreateDiscoverySessionV4Request,
    background_tasks: BackgroundTasks,
) -> CreateDiscoverySessionV4Response:
    """
    [DEVELOPMENT ONLY] Create a test session without authentication.
    This endpoint is for testing purposes only.
    Uses in-memory storage only (no database).
    """
    from config import settings
    if settings.app_env == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint not available in production",
        )

    session_id = generate_session_id()
    test_user_id = "test-user-dev"

    # Create in-memory session only (skip database for testing)
    now = datetime.utcnow().isoformat()
    session = DiscoverySessionV4(
        session_id=session_id,
        user_id=test_user_id,
        mode=request.mode,
        product_idea=request.product_idea,
        industry=request.industry,
        target_market=request.target_market,
        created_at=now,
        updated_at=now,
    )
    _active_sessions[session_id] = session

    logger.info(
        "v4_test_session_created",
        session_id=session_id,
        mode=request.mode.value,
    )

    return CreateDiscoverySessionV4Response(
        session_id=session_id,
        mode=request.mode,
        status="created",
        message=f"Test session created in {request.mode.value} mode (in-memory only)",
    )


@router.get("/test/sessions/{session_id}", response_model=DiscoverySessionV4)
async def get_test_session(session_id: str) -> DiscoverySessionV4:
    """
    [DEVELOPMENT ONLY] Get a test session without authentication.
    """
    from config import settings
    if settings.app_env == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint not available in production",
        )

    if session_id not in _active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test session {session_id} not found",
        )

    return _active_sessions[session_id]


@router.post("/test/sessions/{session_id}/stages/{stage}/run")
async def run_test_stage(
    session_id: str,
    stage: str,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """
    [DEVELOPMENT ONLY] Run a stage on a test session without authentication.
    """
    from config import settings
    if settings.app_env == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test endpoint not available in production",
        )

    if session_id not in _active_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test session {session_id} not found",
        )

    session = _active_sessions[session_id]
    valid_stages = ["problem_love", "customer_truth", "opportunity_mapping",
                    "solution_design", "validation_plan"]

    if stage not in valid_stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stage. Must be one of: {valid_stages}",
        )

    # Import and run the engine
    from agents.discovery_v4.engine import DiscoveryEngineV4

    engine = DiscoveryEngineV4()

    # Run stage in background
    async def _run_stage():
        try:
            updated_session = await engine.run_stage(session, stage)
            _active_sessions[session_id] = updated_session
            logger.info(
                "v4_test_stage_completed",
                session_id=session_id,
                stage=stage,
            )
        except Exception as e:
            logger.error(
                "v4_test_stage_failed",
                session_id=session_id,
                stage=stage,
                error=str(e),
            )
            session.stages[stage].status = StageStatus.NOT_STARTED

    background_tasks.add_task(_run_stage)

    # Mark stage as in-progress
    session.stages[stage].status = StageStatus.IN_PROGRESS
    session.stages[stage].started_at = datetime.utcnow().isoformat()

    return {
        "status": "started",
        "session_id": session_id,
        "stage": stage,
        "message": f"Stage {stage} started in background",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/sessions", response_model=CreateDiscoverySessionV4Response)
async def create_discovery_session(
    request: CreateDiscoverySessionV4Request,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
) -> CreateDiscoverySessionV4Response:
    """
    Create a new V4 discovery session with specified mode.

    Quick mode starts generating immediately in background.
    Guided mode creates session and waits for user to start stages.
    Deep mode creates session and waits for interviews.
    """
    session_id = generate_session_id()

    # Create session in database
    session_store.create_v4_session(
        session_id=session_id,
        user_id=user_id,
        data={
            "product_idea": request.product_idea,
            "industry": request.industry,
            "target_market": request.target_market,
            "mode": request.mode.value,
            "status": "pending",
        },
    )

    # Create in-memory session state
    session = DiscoverySessionV4(
        session_id=session_id,
        user_id=user_id,
        mode=request.mode,
        product_idea=request.product_idea,
        industry=request.industry,
        target_market=request.target_market,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )
    _active_sessions[session_id] = session

    logger.info(
        "v4_session_created",
        session_id=session_id,
        user_id=user_id,
        mode=request.mode.value,
    )

    # For Quick mode, start generating automatically
    if request.mode == DiscoveryMode.QUICK:
        background_tasks.add_task(
            _run_quick_mode_pipeline,
            session_id,
            user_id,
        )

    return CreateDiscoverySessionV4Response(
        session_id=session_id,
        mode=request.mode,
        status="created",
        created_at=datetime.utcnow(),
    )


@router.get("/sessions/{session_id}", response_model=DiscoverySessionV4)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> DiscoverySessionV4:
    """Get full session state including all stages."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Verify ownership
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    return session


@router.get("/sessions/{session_id}/status", response_model=SessionStatusV4Response)
async def get_session_status(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> SessionStatusV4Response:
    """Get lightweight status for polling."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Calculate progress
    stages_complete = sum(
        1 for s in session.stages.values()
        if s.status in (StageStatus.COMPLETED, StageStatus.APPROVED, StageStatus.SKIPPED)
    )
    progress = int((stages_complete / len(session.stages)) * 100)

    # Find current stage
    current_stage = None
    for name, state in session.stages.items():
        if state.status == StageStatus.IN_PROGRESS:
            current_stage = name
            break

    return SessionStatusV4Response(
        session_id=session_id,
        mode=session.mode,
        current_stage=current_stage,
        stages={
            name: {
                "status": state.status.value,
                "score": state.score,
                "has_output": state.output is not None,
            }
            for name, state in session.stages.items()
        },
        overall_progress=progress,
        evidence_quality=session.overall_evidence_quality,
        quality_score=session.quality_score,
    )


@router.get("/sessions")
async def list_sessions(
    user_id: str = Depends(get_current_user_id),
) -> list[dict[str, Any]]:
    """List all V4 sessions for the current user."""
    return session_store.get_user_v4_sessions(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/sessions/{session_id}/stages/{stage}/run")
async def run_stage(
    session_id: str,
    stage: Literal[
        "problem_love",
        "customer_truth",
        "opportunity_mapping",
        "solution_design",
        "validation_plan",
    ],
    request: RunStageRequest = RunStageRequest(),
    background_tasks: BackgroundTasks = None,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Run a specific stage.

    - Uses outputs from previous stages if available
    - Can be re-run with force_regenerate=True
    - Returns immediately, runs in background
    """
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Check if stage is already complete and not forcing regenerate
    stage_state = session.stages.get(stage)
    if (
        stage_state
        and stage_state.status in (StageStatus.COMPLETED, StageStatus.APPROVED)
        and not request.force_regenerate
    ):
        return {
            "status": "already_complete",
            "message": f"Stage {stage} is already complete. Use force_regenerate=True to re-run.",
            "output": stage_state.output,
        }

    # Mark stage as in progress
    session.stages[stage].status = StageStatus.IN_PROGRESS
    session.stages[stage].started_at = datetime.utcnow().isoformat()
    session.updated_at = datetime.utcnow().isoformat()

    # Run stage in background
    if background_tasks:
        background_tasks.add_task(
            _run_stage_task,
            session_id,
            stage,
            request.user_context,
        )

    return {
        "status": "started",
        "message": f"Stage {stage} started",
        "stage": stage,
    }


@router.post("/sessions/{session_id}/stages/{stage}/ai-assist")
async def get_ai_assistance(
    session_id: str,
    stage: str,
    request: AIAssistanceRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Get AI coaching/suggestions without running full stage."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Import and run assistance based on type
    from agents.discovery_v4.engine import DiscoveryEngineV4

    engine = DiscoveryEngineV4()

    if request.assistance_type == "coaching":
        result = await engine.get_coaching(session, stage, request.context)
    elif request.assistance_type == "synthesis":
        result = await engine.synthesize_data(session, stage, request.context)
    elif request.assistance_type == "suggestions":
        result = await engine.get_suggestions(session, stage, request.context)
    elif request.assistance_type == "tarpit_check":
        result = await engine.check_tarpit(
            request.context.get("problem", session.product_idea),
            request.context.get("solution"),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown assistance type: {request.assistance_type}",
        )

    return {"assistance_type": request.assistance_type, "result": result}


@router.put("/sessions/{session_id}/stages/{stage}/output")
async def save_stage_output(
    session_id: str,
    stage: str,
    request: SaveStageOutputRequest,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Save user's edits to a stage output."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    if stage not in session.stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown stage: {stage}",
        )

    # Update session state
    session.stages[stage].output = request.output
    session.stages[stage].output_source = request.source
    session.stages[stage].user_notes = request.notes
    session.stages[stage].status = StageStatus.COMPLETED
    session.stages[stage].completed_at = datetime.utcnow().isoformat()
    session.updated_at = datetime.utcnow().isoformat()

    # Persist to database
    session_store.save_draft_state(
        session_id=session_id,
        stage_name=stage,
        stage_output=request.output,
        stage_status="completed",
        user_edits=[{"source": request.source, "notes": request.notes}],
    )

    return {
        "status": "saved",
        "stage": stage,
        "source": request.source,
    }


@router.post("/sessions/{session_id}/stages/{stage}/approve")
async def approve_stage(
    session_id: str,
    stage: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Mark a stage as approved and unlock next stage."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    if stage not in session.stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown stage: {stage}",
        )

    stage_state = session.stages[stage]
    if stage_state.status not in (StageStatus.COMPLETED, StageStatus.APPROVED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stage {stage} is not complete. Cannot approve.",
        )

    # Mark as approved
    session.stages[stage].status = StageStatus.APPROVED
    session.stages[stage].approved_at = datetime.utcnow().isoformat()
    session.updated_at = datetime.utcnow().isoformat()

    # Persist
    session_store.approve_stage(session_id, stage)

    # Determine next stage
    stage_order = [
        "problem_love",
        "customer_truth",
        "opportunity_mapping",
        "solution_design",
        "validation_plan",
    ]
    current_idx = stage_order.index(stage)
    next_stage = stage_order[current_idx + 1] if current_idx < len(stage_order) - 1 else None

    return {
        "status": "approved",
        "stage": stage,
        "next_stage": next_stage,
    }


@router.post("/sessions/{session_id}/stages/{stage}/skip")
async def skip_stage(
    session_id: str,
    stage: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Skip a stage (Quick mode or user has own data)."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    if stage not in session.stages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown stage: {stage}",
        )

    session.stages[stage].status = StageStatus.SKIPPED
    session.updated_at = datetime.utcnow().isoformat()

    session_store.save_draft_state(
        session_id=session_id,
        stage_name=stage,
        stage_output={},
        stage_status="skipped",
    )

    return {
        "status": "skipped",
        "stage": stage,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INTERVIEW MANAGEMENT (Stage 2)
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/sessions/{session_id}/interviews")
async def add_interview(
    session_id: str,
    interview: Interview,
    user_id: str = Depends(get_current_user_id),
) -> Interview:
    """Add a customer interview."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Add to database
    db_interview = session_store.add_interview(
        session_id=session_id,
        interview=interview.model_dump(mode="json"),
    )

    # Update session cache
    interview.id = db_interview.get("id")
    session.interviews.append(interview)
    session.updated_at = datetime.utcnow().isoformat()

    # Update evidence quality based on interview count
    if len(session.interviews) >= 5:
        session.overall_evidence_quality = EvidenceQuality.E1
    elif len(session.interviews) >= 3:
        session.overall_evidence_quality = EvidenceQuality.E2
    elif len(session.interviews) >= 1:
        session.overall_evidence_quality = EvidenceQuality.E3

    logger.info(
        "interview_added",
        session_id=session_id,
        interview_id=interview.id,
        total_interviews=len(session.interviews),
    )

    return interview


@router.get("/sessions/{session_id}/interviews")
async def list_interviews(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> list[Interview]:
    """List all interviews for session."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    return session.interviews


@router.put("/sessions/{session_id}/interviews/{interview_id}")
async def update_interview(
    session_id: str,
    interview_id: str,
    interview: Interview,
    user_id: str = Depends(get_current_user_id),
) -> Interview:
    """Update an interview."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Update in database
    updated = session_store.update_interview(
        session_id=session_id,
        interview_id=interview_id,
        interview=interview.model_dump(mode="json"),
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Update cache
    for i, existing in enumerate(session.interviews):
        if existing.id == interview_id:
            interview.id = interview_id
            session.interviews[i] = interview
            break

    session.updated_at = datetime.utcnow().isoformat()

    return interview


@router.delete("/sessions/{session_id}/interviews/{interview_id}")
async def delete_interview(
    session_id: str,
    interview_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Delete an interview."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Delete from database
    deleted = session_store.delete_interview(session_id, interview_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview {interview_id} not found",
        )

    # Update cache
    session.interviews = [i for i in session.interviews if i.id != interview_id]
    session.updated_at = datetime.utcnow().isoformat()

    return {"status": "deleted", "interview_id": interview_id}


@router.post("/sessions/{session_id}/interviews/synthesize")
async def synthesize_interviews(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> PatternSynthesis:
    """AI synthesizes patterns from interviews."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    if not session.interviews:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No interviews to synthesize",
        )

    # Run synthesis
    from agents.discovery_v4.stages.customer_truth import CustomerTruthStage

    stage = CustomerTruthStage()
    patterns = await stage.synthesize_patterns(session.interviews)

    # Update session
    session.patterns = patterns
    session.updated_at = datetime.utcnow().isoformat()

    # Persist
    session_store.save_pattern_synthesis(
        session_id=session_id,
        synthesis=patterns.model_dump(),
    )

    return patterns


@router.get("/sessions/{session_id}/interview-guide")
async def get_interview_guide(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Generate Teresa Torres interview guide."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    from agents.discovery_v4.stages.customer_truth import CustomerTruthStage

    stage = CustomerTruthStage()

    # Get problem statement from Stage 1 if available
    problem_statement = session.product_idea
    if session.stages["problem_love"].output:
        problem_statement = (
            session.stages["problem_love"].output.get("problem_statement_refined")
            or session.stages["problem_love"].output.get("problem_statement")
            or session.product_idea
        )

    guide = await stage.generate_interview_guide({
        "problem_statement": problem_statement,
        "target_market": session.target_market,
        "industry": session.industry,
        "previous_findings": session.patterns.model_dump() if session.patterns else None,
    })

    return guide


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE-SPECIFIC HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/sessions/{session_id}/tarpit-check")
async def check_tarpit(
    session_id: str,
    problem: str,
    solution: str = None,
    user_id: str = Depends(get_current_user_id),
) -> TarpitAnalysis:
    """Check if idea is a tarpit (Stage 1)."""
    # Verify session access
    session = get_session_from_cache_or_db(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    from agents.discovery_v4.stages.problem_love import ProblemLoveStage

    stage = ProblemLoveStage()
    return await stage.check_tarpit(problem, solution)


@router.post("/sessions/{session_id}/four-forces")
async def generate_four_forces(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Generate 4 forces from interviews (Stage 3)."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    from agents.discovery_v4.stages.opportunity_mapping import OpportunityMappingStage

    stage = OpportunityMappingStage()
    four_forces = await stage.generate_four_forces(session)

    # Update session
    session.four_forces = four_forces
    session.updated_at = datetime.utcnow().isoformat()

    return four_forces.model_dump()


@router.post("/sessions/{session_id}/opportunity-tree")
async def generate_opportunity_tree(
    session_id: str,
    outcome: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Generate OST from patterns (Stage 3)."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    from agents.discovery_v4.stages.opportunity_mapping import OpportunityMappingStage

    stage = OpportunityMappingStage()
    tree = await stage.generate_opportunity_tree(session, outcome)

    # Update session
    session.opportunity_tree = tree
    session.updated_at = datetime.utcnow().isoformat()

    return tree.model_dump()


@router.post("/sessions/{session_id}/dhm-analysis")
async def analyze_dhm(
    session_id: str,
    solution: str,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """AI-assisted DHM scoring (Stage 4)."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    from agents.discovery_v4.stages.solution_design import SolutionDesignStage

    stage = SolutionDesignStage()
    dhm = await stage.analyze_dhm(session, solution)

    return dhm.model_dump()


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT & CONTINUE
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/sessions/{session_id}/continue-to-strategy")
async def continue_to_strategy(
    session_id: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Continue to full lifecycle (Strategy, Delivery, Design phases).
    Passes discovery outputs as constraints to downstream agents.
    """
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    # Validate that at least some discovery is complete
    stages_complete = sum(
        1 for s in session.stages.values()
        if s.status in (StageStatus.COMPLETED, StageStatus.APPROVED)
    )

    if stages_complete == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete at least one discovery stage before continuing",
        )

    # Queue full lifecycle run
    background_tasks.add_task(
        _run_full_lifecycle_with_v4,
        session_id,
        user_id,
    )

    return {
        "status": "started",
        "message": "Full lifecycle generation started",
        "session_id": session_id,
    }


@router.get("/sessions/{session_id}/export")
async def export_discovery(
    session_id: str,
    format: Literal["pdf", "json", "notion"] = "json",
    user_id: str = Depends(get_current_user_id),
) -> dict[str, Any]:
    """Export discovery pack in specified format."""
    session = get_session_from_cache_or_db(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    if session.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )

    if format == "json":
        return {
            "format": "json",
            "data": session.model_dump(mode="json"),
        }
    elif format == "pdf":
        # TODO: Implement PDF export
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF export not yet implemented",
        )
    elif format == "notion":
        # TODO: Implement Notion export
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Notion export not yet implemented",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# BACKGROUND TASKS
# ═══════════════════════════════════════════════════════════════════════════════


async def _run_quick_mode_pipeline(session_id: str, user_id: str) -> None:
    """Run all stages automatically for Quick mode."""
    try:
        from agents.discovery_v4.engine import DiscoveryEngineV4

        session = _active_sessions.get(session_id)
        if not session:
            logger.error("quick_mode_session_not_found", session_id=session_id)
            return

        engine = DiscoveryEngineV4()
        updated_session = await engine.run_session(session)
        _active_sessions[session_id] = updated_session

        # Update database
        session_store.update_status(
            session_id,
            {
                "status": "completed",
                "progress_percentage": 100,
            },
        )

        logger.info("quick_mode_pipeline_complete", session_id=session_id)

    except Exception as e:
        logger.error(
            "quick_mode_pipeline_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )
        session_store.update_status(
            session_id,
            {
                "status": "failed",
                "error_message": str(e),
            },
        )


async def _run_stage_task(
    session_id: str,
    stage: str,
    user_context: dict[str, Any] | None,
) -> None:
    """Run a single stage in background."""
    try:
        from agents.discovery_v4.engine import DiscoveryEngineV4

        session = _active_sessions.get(session_id)
        if not session:
            logger.error("stage_task_session_not_found", session_id=session_id)
            return

        engine = DiscoveryEngineV4()
        updated_session = await engine.run_stage(session, stage)
        _active_sessions[session_id] = updated_session

        logger.info("stage_task_complete", session_id=session_id, stage=stage)

    except Exception as e:
        logger.error(
            "stage_task_failed",
            session_id=session_id,
            stage=stage,
            error=str(e),
            exc_info=True,
        )
        # Mark stage as failed
        session = _active_sessions.get(session_id)
        if session:
            session.stages[stage].status = StageStatus.NOT_STARTED
            session.stages[stage].coaching_messages.append(f"Error: {str(e)}")


async def _run_full_lifecycle_with_v4(session_id: str, user_id: str) -> None:
    """Run full lifecycle using V4 discovery outputs."""
    try:
        from agents.facilitator import Facilitator

        session = _active_sessions.get(session_id)
        if not session:
            logger.error("full_lifecycle_session_not_found", session_id=session_id)
            return

        facilitator = Facilitator()
        # Pass V4 session data to facilitator
        await facilitator.run_with_v4_discovery(session)

        logger.info("full_lifecycle_complete", session_id=session_id)

    except Exception as e:
        logger.error(
            "full_lifecycle_failed",
            session_id=session_id,
            error=str(e),
            exc_info=True,
        )
