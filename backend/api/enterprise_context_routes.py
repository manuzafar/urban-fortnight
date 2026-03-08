"""
Enterprise Context API Routes.

This module provides REST API endpoints for managing enterprise context files
that provide organizational guidelines for AI agents.
"""

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from models.enterprise_context_schemas import (
    ContextScope,
    ContextType,
    EnterpriseContextCreate,
    EnterpriseContextListItem,
    EnterpriseContextListResponse,
    EnterpriseContextResponse,
    EnterpriseContextUpdate,
    ContextUploadResponse,
    MergedContextPreview,
    SessionContextAttach,
    SessionContextResponse,
    ValidationStatus,
)
from services.enterprise_context_service import enterprise_context_service
from utils.auth import get_current_user_id
from utils.supabase_client import get_supabase_client

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/contexts", tags=["Enterprise Context"])


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _get_supabase():
    """Get Supabase client."""
    return get_supabase_client()


def _db_row_to_response(row: dict) -> EnterpriseContextResponse:
    """Convert database row to response model."""
    return EnterpriseContextResponse(
        id=str(row["id"]),
        user_id=str(row["user_id"]),
        name=row["name"],
        context_type=ContextType(row["context_type"]),
        parent_id=str(row["parent_id"]) if row.get("parent_id") else None,
        raw_content=row["raw_content"],
        parsed_content=row["parsed_content"],
        validation_status=ValidationStatus(row["validation_status"]),
        validation_errors=row.get("validation_errors", []),
        scope=ContextScope(row["scope"]),
        is_default=row["is_default"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _db_row_to_list_item(row: dict) -> EnterpriseContextListItem:
    """Convert database row to list item model."""
    return EnterpriseContextListItem(
        id=str(row["id"]),
        name=row["name"],
        context_type=ContextType(row["context_type"]),
        parent_id=str(row["parent_id"]) if row.get("parent_id") else None,
        validation_status=ValidationStatus(row["validation_status"]),
        scope=ContextScope(row["scope"]),
        is_default=row["is_default"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT CRUD ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "",
    response_model=EnterpriseContextResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_context(
    request: EnterpriseContextCreate,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a new enterprise context from raw content.

    The content is parsed and validated against the enterprise-context-spec schema.
    """
    logger.info(
        "creating_enterprise_context",
        user_id=user_id,
        name=request.name,
        context_type=request.context_type,
    )

    # Parse and validate content
    parsed_content, validation_status, validation_errors = enterprise_context_service.parse_and_validate(
        request.raw_content,
        request.context_type.value,
    )

    # Create database record
    context_id = str(uuid.uuid4())
    client = _get_supabase()

    row = {
        "id": context_id,
        "user_id": user_id,
        "name": request.name,
        "context_type": request.context_type.value,
        "parent_id": request.parent_id,
        "raw_content": request.raw_content,
        "parsed_content": parsed_content,
        "validation_status": validation_status.value,
        "validation_errors": validation_errors,
        "scope": request.scope.value,
        "is_default": request.is_default,
    }

    try:
        result = client.table("enterprise_contexts").insert(row).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create context",
            )

        logger.info(
            "enterprise_context_created",
            context_id=context_id,
            validation_status=validation_status.value,
        )

        return _db_row_to_response(result.data[0])

    except Exception as e:
        logger.error("create_context_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create context: {str(e)}",
        )


@router.post(
    "/upload",
    response_model=ContextUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_context_file(
    file: UploadFile = File(...),
    name: str | None = None,
    context_type: ContextType | None = None,
    scope: ContextScope = ContextScope.PRIVATE,
    user_id: str = Depends(get_current_user_id),
):
    """
    Upload a context file (markdown or YAML).

    The file is parsed, validated, and stored. If context_type is not specified,
    it will be auto-detected from the file content.
    """
    # Validate file extension
    filename = file.filename or "context.md"
    if not filename.endswith((".md", ".yaml", ".yml")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be .md, .yaml, or .yml",
        )

    # Read file content
    try:
        content = await file.read()
        raw_content = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}",
        )

    # Detect context type if not specified
    if context_type is None:
        detected = enterprise_context_service.detect_context_type(raw_content)
        if detected is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not detect context type. Please specify context_type parameter.",
            )
        context_type = detected

    # Use filename as name if not specified
    if name is None:
        name = filename.rsplit(".", 1)[0]

    # Parse and validate
    parsed_content, validation_status, validation_errors = enterprise_context_service.parse_and_validate(
        raw_content,
        context_type.value,
    )

    # Create database record
    context_id = str(uuid.uuid4())
    client = _get_supabase()

    row = {
        "id": context_id,
        "user_id": user_id,
        "name": name,
        "context_type": context_type.value,
        "raw_content": raw_content,
        "parsed_content": parsed_content,
        "validation_status": validation_status.value,
        "validation_errors": validation_errors,
        "scope": scope.value,
        "is_default": False,
    }

    try:
        result = client.table("enterprise_contexts").insert(row).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded context",
            )

        logger.info(
            "enterprise_context_uploaded",
            context_id=context_id,
            filename=filename,
            context_type=context_type.value,
            validation_status=validation_status.value,
        )

        return ContextUploadResponse(
            id=context_id,
            name=name,
            context_type=context_type,
            validation_status=validation_status,
            validation_errors=validation_errors,
            parsed_content=parsed_content,
        )

    except Exception as e:
        logger.error("upload_context_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload context: {str(e)}",
        )


@router.get(
    "",
    response_model=EnterpriseContextListResponse,
)
async def list_contexts(
    context_type: ContextType | None = None,
    user_id: str = Depends(get_current_user_id),
):
    """
    List all enterprise contexts for the user.

    Optionally filter by context_type (company, division, team).
    Also includes organization-scoped contexts from other users.
    """
    client = _get_supabase()

    try:
        query = client.table("enterprise_contexts").select("*")

        # Filter by user or organization scope
        # Note: Using OR filter for user_id or organization scope
        query = query.or_(f"user_id.eq.{user_id},scope.eq.organization")

        if context_type:
            query = query.eq("context_type", context_type.value)

        query = query.order("created_at", desc=True)
        result = query.execute()

        contexts = [_db_row_to_list_item(row) for row in result.data or []]

        return EnterpriseContextListResponse(
            contexts=contexts,
            count=len(contexts),
        )

    except Exception as e:
        logger.error("list_contexts_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list contexts: {str(e)}",
        )


@router.get(
    "/{context_id}",
    response_model=EnterpriseContextResponse,
)
async def get_context(
    context_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a single enterprise context by ID."""
    client = _get_supabase()

    try:
        result = (
            client.table("enterprise_contexts")
            .select("*")
            .eq("id", context_id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Context not found",
            )

        row = result.data

        # Check access
        if row["user_id"] != user_id and row["scope"] != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        return _db_row_to_response(row)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_context_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context: {str(e)}",
        )


@router.patch(
    "/{context_id}",
    response_model=EnterpriseContextResponse,
)
async def update_context(
    context_id: str,
    request: EnterpriseContextUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Update an enterprise context."""
    client = _get_supabase()

    # Verify ownership
    existing = (
        client.table("enterprise_contexts")
        .select("user_id, context_type")
        .eq("id", context_id)
        .maybe_single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found",
        )

    if existing.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    updates: dict[str, Any] = {}

    if request.name is not None:
        updates["name"] = request.name

    if request.parent_id is not None:
        updates["parent_id"] = request.parent_id

    if request.scope is not None:
        updates["scope"] = request.scope.value

    if request.is_default is not None:
        updates["is_default"] = request.is_default

    if request.raw_content is not None:
        # Re-parse and validate
        parsed_content, validation_status, validation_errors = enterprise_context_service.parse_and_validate(
            request.raw_content,
            existing.data["context_type"],
        )
        updates["raw_content"] = request.raw_content
        updates["parsed_content"] = parsed_content
        updates["validation_status"] = validation_status.value
        updates["validation_errors"] = validation_errors

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        result = (
            client.table("enterprise_contexts")
            .update(updates)
            .eq("id", context_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update context",
            )

        return _db_row_to_response(result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_context_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update context: {str(e)}",
        )


@router.delete(
    "/{context_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_context(
    context_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete an enterprise context."""
    client = _get_supabase()

    # Verify ownership
    existing = (
        client.table("enterprise_contexts")
        .select("user_id")
        .eq("id", context_id)
        .maybe_single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found",
        )

    if existing.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    try:
        client.table("enterprise_contexts").delete().eq("id", context_id).execute()
        logger.info("enterprise_context_deleted", context_id=context_id)

    except Exception as e:
        logger.error("delete_context_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete context: {str(e)}",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT PREVIEW & MERGE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@router.get(
    "/{context_id}/preview",
    response_model=MergedContextPreview,
)
async def preview_merged_context(
    context_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """
    Preview the merged context for a given context ID.

    This follows the hierarchy (company <- division <- team) to produce
    the effective merged context with all inherited values.
    """
    client = _get_supabase()

    # Get the requested context
    context = (
        client.table("enterprise_contexts")
        .select("*")
        .eq("id", context_id)
        .maybe_single()
        .execute()
    )

    if not context.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found",
        )

    row = context.data

    # Check access
    if row["user_id"] != user_id and row["scope"] != "organization":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Build hierarchy
    company = None
    division = None
    team = None

    if row["context_type"] == "company":
        company = row["parsed_content"]
    elif row["context_type"] == "division":
        division = row["parsed_content"]
        # Try to get parent company
        if row.get("parent_id"):
            parent = (
                client.table("enterprise_contexts")
                .select("parsed_content")
                .eq("id", row["parent_id"])
                .maybe_single()
                .execute()
            )
            if parent.data:
                company = parent.data["parsed_content"]
    elif row["context_type"] == "team":
        team = row["parsed_content"]
        # Try to get parent division
        if row.get("parent_id"):
            parent = (
                client.table("enterprise_contexts")
                .select("parsed_content, parent_id")
                .eq("id", row["parent_id"])
                .maybe_single()
                .execute()
            )
            if parent.data:
                division = parent.data["parsed_content"]
                # Try to get grandparent company
                if parent.data.get("parent_id"):
                    grandparent = (
                        client.table("enterprise_contexts")
                        .select("parsed_content")
                        .eq("id", parent.data["parent_id"])
                        .maybe_single()
                        .execute()
                    )
                    if grandparent.data:
                        company = grandparent.data["parsed_content"]

    # Merge hierarchy
    merged = enterprise_context_service.merge_hierarchy(company, division, team)

    # Extract constraints for preview
    constraint_set = enterprise_context_service.extract_constraints(merged)

    return MergedContextPreview(
        merged_context=merged,
        sources=merged.get("_sources", []),
        constraints_preview=[c.model_dump() for c in constraint_set.constraints],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION-CONTEXT ATTACHMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@router.post(
    "/sessions/{session_id}/attach",
    response_model=SessionContextResponse,
)
async def attach_contexts_to_session(
    session_id: str,
    request: SessionContextAttach,
    user_id: str = Depends(get_current_user_id),
):
    """
    Attach enterprise contexts to a discovery session.

    The contexts are merged and stored with the session for use by agents.
    Maximum of 3 contexts (one per level: company, division, team).
    """
    client = _get_supabase()

    # Verify session exists and user owns it
    session = (
        client.table("discovery_sessions")
        .select("id, user_id")
        .eq("id", session_id)
        .maybe_single()
        .execute()
    )

    if not session.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Fetch all requested contexts
    contexts: dict[str, dict] = {}
    context_items: list[EnterpriseContextListItem] = []

    for ctx_id in request.context_ids:
        ctx = (
            client.table("enterprise_contexts")
            .select("*")
            .eq("id", ctx_id)
            .maybe_single()
            .execute()
        )

        if not ctx.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context {ctx_id} not found",
            )

        # Check access
        if ctx.data["user_id"] != user_id and ctx.data["scope"] != "organization":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to context {ctx_id}",
            )

        ctx_type = ctx.data["context_type"]
        if ctx_type in contexts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only one {ctx_type} context allowed per session",
            )

        contexts[ctx_type] = ctx.data
        context_items.append(_db_row_to_list_item(ctx.data))

    # Merge contexts
    merged = enterprise_context_service.merge_hierarchy(
        company=contexts.get("company", {}).get("parsed_content"),
        division=contexts.get("division", {}).get("parsed_content"),
        team=contexts.get("team", {}).get("parsed_content"),
    )

    # Delete existing session contexts
    client.table("session_contexts").delete().eq("session_id", session_id).execute()

    # Create new session-context associations
    for ctx_id in request.context_ids:
        ctx_data = next(c for c in contexts.values() if str(c["id"]) == ctx_id)
        client.table("session_contexts").insert({
            "session_id": session_id,
            "context_id": ctx_id,
            "context_type": ctx_data["context_type"],
            "merged_context": merged,
        }).execute()

    logger.info(
        "contexts_attached_to_session",
        session_id=session_id,
        context_ids=request.context_ids,
    )

    return SessionContextResponse(
        session_id=session_id,
        contexts=context_items,
        merged_context=merged,
    )


@router.get(
    "/sessions/{session_id}/contexts",
    response_model=SessionContextResponse,
)
async def get_session_contexts(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get the enterprise contexts attached to a session."""
    client = _get_supabase()

    # Verify session access
    session = (
        client.table("discovery_sessions")
        .select("user_id")
        .eq("id", session_id)
        .maybe_single()
        .execute()
    )

    if not session.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Get session contexts
    session_contexts = (
        client.table("session_contexts")
        .select("context_id, merged_context")
        .eq("session_id", session_id)
        .execute()
    )

    if not session_contexts.data:
        return SessionContextResponse(
            session_id=session_id,
            contexts=[],
            merged_context={},
        )

    # Get full context details
    context_ids = [sc["context_id"] for sc in session_contexts.data]
    contexts = (
        client.table("enterprise_contexts")
        .select("*")
        .in_("id", context_ids)
        .execute()
    )

    context_items = [_db_row_to_list_item(c) for c in contexts.data or []]
    merged_context = session_contexts.data[0].get("merged_context", {})

    return SessionContextResponse(
        session_id=session_id,
        contexts=context_items,
        merged_context=merged_context,
    )


@router.delete(
    "/sessions/{session_id}/contexts",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def detach_contexts_from_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Remove all enterprise contexts from a session."""
    client = _get_supabase()

    # Verify session access
    session = (
        client.table("discovery_sessions")
        .select("user_id")
        .eq("id", session_id)
        .maybe_single()
        .execute()
    )

    if not session.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.data["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    client.table("session_contexts").delete().eq("session_id", session_id).execute()

    logger.info("contexts_detached_from_session", session_id=session_id)
