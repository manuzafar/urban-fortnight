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
        # Lazy initialization - don't get client in constructor
        self._client = None

    @property
    def client(self):
        """Get Supabase client (lazy-loaded on first use)."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

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
        self.client.table("discovery_sessions").insert(row).execute()
        logger.info("session_created", session_id=session_id, user_id=user_id)

    def get(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get session data by ID."""
        result = (
            self.client.table("discovery_sessions")
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        return result.data

    def update_status(self, session_id: str, updates: dict[str, Any]) -> bool:
        """Update session status fields."""
        result = (
            self.client.table("discovery_sessions")
            .update(updates)
            .eq("id", session_id)
            .execute()
        )
        return len(result.data) > 0

    def save_inception_pack(
        self, session_id: str, user_id: str, pack: dict[str, Any]
    ) -> None:
        """Save inception pack to separate table."""
        self.client.table("inception_packs").upsert({
            "session_id": session_id,
            "user_id": user_id,
            "pack": pack,
        }).execute()
        logger.info("inception_pack_saved", session_id=session_id)

    def get_inception_pack(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get inception pack for a session."""
        result = (
            self.client.table("inception_packs")
            .select("pack")
            .eq("session_id", session_id)
            .maybe_single()
            .execute()
        )
        return result.data["pack"] if result.data else None

    def delete(self, session_id: str) -> bool:
        """Delete a session (cascade deletes inception_pack)."""
        result = (
            self.client.table("discovery_sessions")
            .delete()
            .eq("id", session_id)
            .execute()
        )
        return len(result.data) > 0

    def get_user_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """Get all sessions for a user, ordered by creation date."""
        result = (
            self.client.table("discovery_sessions")
            .select("id, status, product_idea, progress_percentage, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def count_active(self) -> int:
        """Count active (non-terminal) sessions."""
        result = (
            self.client.table("discovery_sessions")
            .select("id", count="exact")
            .in_("status", ["pending", "in_progress"])
            .execute()
        )
        return result.count or 0

    def verify_ownership(self, session_id: str, user_id: str) -> bool:
        """Check that user_id owns session_id."""
        result = (
            self.client.table("discovery_sessions")
            .select("id")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        return result.data is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # DISCOVERY V4 METHODS
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_v4_session(
        self, session_id: str, user_id: str, data: dict[str, Any]
    ) -> None:
        """Create a new V4 discovery session."""
        import json

        # Store V4-specific data in additional_context as JSON
        v4_context = {
            "discovery_version": "v4",
            "mode": data.get("mode", "guided"),
        }

        row = {
            "id": session_id,
            "user_id": user_id,
            "status": data.get("status", "pending"),
            "product_idea": data["product_idea"],
            "industry": data.get("industry"),
            "target_market": data.get("target_market"),
            "additional_context": json.dumps(v4_context),
            "current_agent": data.get("current_agent"),
            "iteration": 1,
            "progress_percentage": 0,
        }
        self.client.table("discovery_sessions").insert(row).execute()
        logger.info(
            "v4_session_created",
            session_id=session_id,
            user_id=user_id,
            mode=data.get("mode", "guided"),
        )

    def get_v4_session(self, session_id: str) -> Optional[dict[str, Any]]:
        """Get V4 session data including stage states."""
        session = self.get(session_id)
        if not session:
            return None

        # Get draft states for this session
        draft_states = self._get_draft_states(session_id)

        # Get interviews
        interviews = self.get_interviews(session_id)

        # Get pattern synthesis
        patterns = self._get_pattern_synthesis(session_id)

        return {
            **session,
            "draft_states": draft_states,
            "interviews": interviews,
            "patterns": patterns,
        }

    def _get_draft_states(self, session_id: str) -> list[dict[str, Any]]:
        """Get all draft states for a session."""
        try:
            result = (
                self.client.table("draft_states")
                .select("*")
                .eq("session_id", session_id)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.warning("draft_states_fetch_failed", error=str(e))
            return []

    def save_draft_state(
        self,
        session_id: str,
        stage_name: str,
        stage_output: dict[str, Any],
        stage_status: str = "completed",
        user_edits: Optional[list[dict]] = None,
        ai_coaching: Optional[list[str]] = None,
        score: Optional[int] = None,
    ) -> None:
        """Save or update a draft state for a stage."""
        row = {
            "session_id": session_id,
            "stage_name": stage_name,
            "stage_output": stage_output,
            "stage_status": stage_status,
            "user_edits": user_edits or [],
            "ai_coaching": ai_coaching or [],
            "score": score,
            "updated_at": "now()",
        }

        try:
            # Try upsert (requires unique constraint on session_id + stage_name)
            self.client.table("draft_states").upsert(
                row,
                on_conflict="session_id,stage_name",
            ).execute()
            logger.info(
                "draft_state_saved",
                session_id=session_id,
                stage_name=stage_name,
                status=stage_status,
            )
        except Exception as e:
            logger.warning(
                "draft_state_upsert_failed_trying_insert",
                error=str(e),
            )
            # Fallback: try direct insert (table might not have constraint)
            self.client.table("draft_states").insert(row).execute()

    def get_draft_state(
        self, session_id: str, stage_name: str
    ) -> Optional[dict[str, Any]]:
        """Get draft state for a specific stage."""
        try:
            result = (
                self.client.table("draft_states")
                .select("*")
                .eq("session_id", session_id)
                .eq("stage_name", stage_name)
                .maybe_single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.warning("draft_state_fetch_failed", error=str(e))
            return None

    def approve_stage(self, session_id: str, stage_name: str) -> bool:
        """Mark a stage as approved."""
        try:
            result = (
                self.client.table("draft_states")
                .update({"stage_status": "approved", "updated_at": "now()"})
                .eq("session_id", session_id)
                .eq("stage_name", stage_name)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            logger.warning("approve_stage_failed", error=str(e))
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # INTERVIEW METHODS
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_interview(
        self, session_id: str, interview: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a customer interview."""
        import uuid

        interview_id = str(uuid.uuid4())
        row = {
            "id": interview_id,
            "session_id": session_id,
            "interviewee_name": interview.get("interviewee_name"),
            "interviewee_role": interview.get("interviewee_role"),
            "company_type": interview.get("company_type"),
            "company_size": interview.get("company_size"),
            "interview_date": interview.get("interview_date"),
            "story_raw": interview.get("story_raw"),
            "key_quote": interview.get("key_quote"),
            "struggling_moment": interview.get("struggling_moment"),
            "emotions": interview.get("emotions", []),
            "current_workaround": interview.get("current_workaround"),
            "desired_outcome": interview.get("desired_outcome"),
            "ai_extracted_insights": interview.get("ai_extracted_insights", {}),
        }

        try:
            result = self.client.table("interviews").insert(row).execute()
            logger.info(
                "interview_added",
                session_id=session_id,
                interview_id=interview_id,
            )
            return result.data[0] if result.data else {**row}
        except Exception as e:
            logger.warning("interview_add_failed", error=str(e))
            # Return the row anyway for in-memory tracking
            return {**row}

    def get_interviews(self, session_id: str) -> list[dict[str, Any]]:
        """Get all interviews for a session."""
        try:
            result = (
                self.client.table("interviews")
                .select("*")
                .eq("session_id", session_id)
                .order("interview_date", desc=True)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.warning("interviews_fetch_failed", error=str(e))
            return []

    def update_interview(
        self, session_id: str, interview_id: str, interview: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Update an interview."""
        try:
            result = (
                self.client.table("interviews")
                .update(interview)
                .eq("id", interview_id)
                .eq("session_id", session_id)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            logger.warning("interview_update_failed", error=str(e))
            return None

    def delete_interview(self, session_id: str, interview_id: str) -> bool:
        """Delete an interview."""
        try:
            result = (
                self.client.table("interviews")
                .delete()
                .eq("id", interview_id)
                .eq("session_id", session_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            logger.warning("interview_delete_failed", error=str(e))
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # PATTERN SYNTHESIS METHODS
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_pattern_synthesis(
        self, session_id: str, synthesis: dict[str, Any]
    ) -> None:
        """Save pattern synthesis results."""
        row = {
            "session_id": session_id,
            "pain_patterns": synthesis.get("pain_patterns", []),
            "trigger_patterns": synthesis.get("trigger_patterns", []),
            "outcome_patterns": synthesis.get("outcome_patterns", []),
            "contradictions": synthesis.get("contradictions", []),
            "interview_gaps": synthesis.get("interview_gaps", []),
            "synthesized_at": "now()",
        }

        try:
            self.client.table("pattern_synthesis").upsert(
                row,
                on_conflict="session_id",
            ).execute()
            logger.info("pattern_synthesis_saved", session_id=session_id)
        except Exception as e:
            logger.warning("pattern_synthesis_save_failed", error=str(e))

    def _get_pattern_synthesis(
        self, session_id: str
    ) -> Optional[dict[str, Any]]:
        """Get pattern synthesis for a session."""
        try:
            result = (
                self.client.table("pattern_synthesis")
                .select("*")
                .eq("session_id", session_id)
                .maybe_single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.warning("pattern_synthesis_fetch_failed", error=str(e))
            return None

    def get_user_v4_sessions(self, user_id: str) -> list[dict[str, Any]]:
        """Get all V4 sessions for a user."""
        import json

        result = (
            self.client.table("discovery_sessions")
            .select("id, status, product_idea, additional_context, progress_percentage, created_at, updated_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        # Filter to V4 sessions and extract mode from additional_context
        v4_sessions = []
        for session in result.data:
            try:
                ctx = json.loads(session.get("additional_context") or "{}")
                if ctx.get("discovery_version") == "v4":
                    session["mode"] = ctx.get("mode", "guided")
                    v4_sessions.append(session)
            except (json.JSONDecodeError, TypeError):
                pass

        return v4_sessions
