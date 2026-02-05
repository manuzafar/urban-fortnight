"""
Database access layer for Supabase PostgreSQL.

Replaces the in-memory SessionStore with persistent storage.
Uses service role key -- bypasses RLS for backend writes.
"""

from typing import Any, Optional

import structlog

from utils.supabase_client import get_supabase_client

logger = structlog.get_logger(__name__)


class SupabaseSessionStore:
    """
    Persistent session store backed by Supabase PostgreSQL.
    Drop-in replacement for the in-memory SessionStore.
    """

    def __init__(self):
        self._client = get_supabase_client()

    def create(self, session_id: str, user_id: str, data: dict[str, Any]) -> None:
        """Create a new session in the database."""
        row = {
            "id": session_id,
            "user_id": user_id,
            "status": data.get("status", "pending"),
            "product_idea": data["product_idea"],
            "industry": data.get("industry"),
            "target_market": data.get("target_market"),
            "constraints": data.get("constraints"),
            "additional_context": data.get("additional_context"),
            "current_agent": data.get("current_agent"),
            "iteration": data.get("iteration", 1),
            "progress_percentage": data.get("progress_percentage", 0),
            "error_message": data.get("error_message"),
            "errors": data.get("errors", []),
        }
        self._client.table("discovery_sessions").insert(row).execute()
        logger.info("session_created", session_id=session_id, user_id=user_id)

    def get(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get session data by ID."""
        result = (
            self._client.table("discovery_sessions")
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        return result.data

    def update_status(self, session_id: str, updates: dict[str, Any]) -> bool:
        """Update session status fields."""
        result = (
            self._client.table("discovery_sessions")
            .update(updates)
            .eq("id", session_id)
            .execute()
        )
        return len(result.data) > 0

    def save_inception_pack(
        self, session_id: str, user_id: str, pack: dict[str, Any]
    ) -> None:
        """Save inception pack to separate table."""
        self._client.table("inception_packs").upsert({
            "session_id": session_id,
            "user_id": user_id,
            "pack": pack,
        }).execute()
        logger.info("inception_pack_saved", session_id=session_id)

    def get_inception_pack(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get inception pack for a session."""
        result = (
            self._client.table("inception_packs")
            .select("pack")
            .eq("session_id", session_id)
            .maybe_single()
            .execute()
        )
        return result.data["pack"] if result.data else None

    def delete(self, session_id: str) -> bool:
        """Delete a session (cascade deletes inception_pack)."""
        result = (
            self._client.table("discovery_sessions")
            .delete()
            .eq("id", session_id)
            .execute()
        )
        return len(result.data) > 0

    def get_user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """Get all sessions for a user, ordered by creation date."""
        result = (
            self._client.table("discovery_sessions")
            .select("id, status, product_idea, progress_percentage, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def count_active(self) -> int:
        """Count active (non-terminal) sessions."""
        result = (
            self._client.table("discovery_sessions")
            .select("id", count="exact")
            .in_("status", ["pending", "in_progress"])
            .execute()
        )
        return result.count or 0

    def verify_ownership(self, session_id: str, user_id: str) -> bool:
        """Check that user_id owns session_id."""
        result = (
            self._client.table("discovery_sessions")
            .select("id")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return result.data is not None
