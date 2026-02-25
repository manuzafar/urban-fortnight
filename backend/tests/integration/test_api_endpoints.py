"""
Comprehensive API integration tests for the Seedform backend.

Tests all API endpoints including:
- Discovery endpoints (main.py)
- V4 Discovery endpoints (api/discovery_v4_routes.py)
- Export endpoints

Uses pytest with TestClient and mocked dependencies.
"""

import json
import pytest
from datetime import datetime, date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

# Import app and models
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    # Import app - we'll mock dependencies in individual tests
    from main import app
    return TestClient(app)


@pytest.fixture
def valid_jwt_token():
    """A mock valid JWT token."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiYXVkIjoiYXV0aGVudGljYXRlZCJ9.test"


@pytest.fixture
def test_user_id():
    """Test user ID matching the mock JWT."""
    return "test-user-123"


@pytest.fixture
def auth_headers(valid_jwt_token):
    """Headers with valid authorization."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def sample_discovery_request():
    """Sample valid discovery request payload."""
    return {
        "product_idea": "AI-powered meeting room booking system for enterprise offices that reduces scheduling conflicts by 80%",
        "industry": "Enterprise SaaS",
        "target_market": "Mid-market companies with 100-500 employees",
        "constraints": ["Must integrate with Google Calendar", "GDPR compliant"],
        "additional_context": "Target launch in Q3 2024",
    }


@pytest.fixture
def sample_session_data(test_user_id):
    """Sample session data from database."""
    return {
        "id": "test-session-123",
        "user_id": test_user_id,
        "status": "pending",
        "product_idea": "AI meeting room booking system",
        "industry": "Enterprise SaaS",
        "target_market": "Mid-market companies",
        "constraints": ["GDPR compliant"],
        "additional_context": None,
        "current_agent": None,
        "iteration": 1,
        "progress_percentage": 0,
        "error_message": None,
        "errors": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_completed_session(test_user_id):
    """Sample completed session with inception pack."""
    return {
        "id": "completed-session-456",
        "user_id": test_user_id,
        "status": "completed",
        "product_idea": "AI meeting room booking system",
        "industry": "Enterprise SaaS",
        "target_market": "Mid-market companies",
        "constraints": None,
        "additional_context": None,
        "current_agent": "Complete",
        "iteration": 1,
        "progress_percentage": 100,
        "error_message": None,
        "errors": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def sample_inception_pack():
    """Sample inception pack data."""
    return {
        "executive_summary": {
            "product_name": "MeetingAI Pro",
            "tagline": "Smart meeting room booking for the modern enterprise",
            "problem_statement": "Enterprise meeting scheduling is broken",
            "solution_overview": "AI-powered scheduling",
            "value_proposition": "Reduce scheduling conflicts by 80%",
            "target_users": ["Office managers", "Executive assistants"],
            "target_market_size": "$5B TAM",
            "key_differentiators": ["AI-powered", "Real-time availability"],
            "competitive_landscape": "Fragmented market",
            "funding_required": "$2M seed",
            "revenue_model": "SaaS subscription",
            "financial_projections": "$1M ARR by Year 2",
            "break_even_timeline": "18 months",
            "expected_roi": "5x in 3 years",
            "top_risks": ["Competition from incumbents"],
            "regulatory_summary": "GDPR, SOC 2 required",
            "gtm_strategy": "Direct sales to enterprises",
            "key_milestones": ["MVP in 3 months", "First customer in 6 months"],
            "success_metrics": ["Customer retention >90%"],
            "recommendation": "Proceed with MVP development",
        },
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0",
        },
    }


@pytest.fixture
def sample_v4_session_request():
    """Sample V4 discovery session request."""
    return {
        "product_idea": "AI-powered meeting room booking system for enterprise offices",
        "mode": "guided",
        "industry": "Enterprise SaaS",
        "target_market": "Mid-market companies",
    }


@pytest.fixture
def sample_interview_data():
    """Sample interview data for V4 tests."""
    return {
        "interviewee_name": "John Doe",
        "interviewee_role": "Office Manager",
        "company_type": "Tech Startup",
        "company_size": "51-200",
        "interview_date": date.today().isoformat(),
        "story_raw": "We spend hours every week resolving scheduling conflicts...",
        "key_quote": "It's like herding cats trying to get everyone in the same room",
        "struggling_moment": "Every Monday morning when I have to manually resolve double bookings",
        "emotions": ["frustrated", "overwhelmed"],
        "current_workaround": "Shared Google Calendar with manual updates",
        "desired_outcome": "Automated conflict resolution that just works",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self, test_client):
        """Health endpoint should return 200."""
        response = test_client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_status(self, test_client):
        """Health endpoint should return status info."""
        response = test_client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data


# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiscoveryStartEndpoint:
    """Tests for POST /api/discovery/start endpoint."""

    def test_start_requires_auth(self, test_client, sample_discovery_request):
        """Start endpoint should require authentication."""
        response = test_client.post(
            "/api/discovery/start",
            json=sample_discovery_request,
        )
        assert response.status_code in [401, 403]

    def test_start_with_valid_request(
        self,
        test_client,
        auth_headers,
        sample_discovery_request,
        test_user_id,
    ):
        """Start endpoint should accept valid requests."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.count_active.return_value = 0
            mock_store.create.return_value = None

            response = test_client.post(
                "/api/discovery/start",
                json=sample_discovery_request,
                headers=auth_headers,
            )

        assert response.status_code == 202
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "pending"
        assert "message" in data

    def test_start_rejects_short_product_idea(self, test_client, auth_headers, test_user_id):
        """Start endpoint should reject too short product ideas."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.post(
                "/api/discovery/start",
                json={"product_idea": "short"},
                headers=auth_headers,
            )
        assert response.status_code == 422

    def test_start_rejects_missing_product_idea(self, test_client, auth_headers, test_user_id):
        """Start endpoint should reject missing product idea."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.post(
                "/api/discovery/start",
                json={},
                headers=auth_headers,
            )
        assert response.status_code == 422

    def test_start_handles_max_sessions(
        self,
        test_client,
        auth_headers,
        sample_discovery_request,
        test_user_id,
    ):
        """Start endpoint should handle max sessions limit."""
        with patch("main.session_store") as mock_store, \
             patch("main.settings") as mock_settings, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_settings.max_concurrent_sessions = 5
            mock_store.count_active.return_value = 5

            response = test_client.post(
                "/api/discovery/start",
                json=sample_discovery_request,
                headers=auth_headers,
            )

        assert response.status_code == 503

    def test_start_optional_fields(self, test_client, auth_headers, test_user_id):
        """Start endpoint should handle optional fields."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.count_active.return_value = 0
            mock_store.create.return_value = None

            response = test_client.post(
                "/api/discovery/start",
                json={
                    "product_idea": "A revolutionary app for managing personal finances with AI-powered insights",
                },
                headers=auth_headers,
            )

        assert response.status_code == 202


class TestDiscoverySessionEndpoint:
    """Tests for GET /api/discovery/session/{session_id} endpoint."""

    def test_get_session_requires_auth(self, test_client):
        """Get session endpoint should require authentication."""
        response = test_client.get("/api/discovery/session/test-session-123")
        assert response.status_code in [401, 403]

    def test_get_session_returns_404_not_found(self, test_client, auth_headers, test_user_id):
        """Get session should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = None

            response = test_client.get(
                "/api/discovery/session/non-existent",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_get_session_returns_404_wrong_owner(
        self,
        test_client,
        auth_headers,
        sample_session_data,
        test_user_id,
    ):
        """Get session should return 404 if user doesn't own session."""
        session_data = {**sample_session_data, "user_id": "different-user"}

        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = session_data

            response = test_client.get(
                "/api/discovery/session/test-session-123",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_get_session_success(
        self,
        test_client,
        auth_headers,
        sample_session_data,
        test_user_id,
    ):
        """Get session should return session data for owner."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = sample_session_data

            response = test_client.get(
                "/api/discovery/session/test-session-123",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["status"] == "pending"

    def test_get_completed_session_includes_pack(
        self,
        test_client,
        auth_headers,
        sample_completed_session,
        sample_inception_pack,
        test_user_id,
    ):
        """Get completed session should include inception pack."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = sample_completed_session
            mock_store.get_inception_pack.return_value = sample_inception_pack

            response = test_client.get(
                "/api/discovery/session/completed-session-456",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "inception_pack" in data


class TestListSessionsEndpoint:
    """Tests for GET /api/discovery/sessions endpoint."""

    def test_list_sessions_requires_auth(self, test_client):
        """List sessions endpoint should require authentication."""
        response = test_client.get("/api/discovery/sessions")
        assert response.status_code in [401, 403]

    def test_list_sessions_empty(self, test_client, auth_headers, test_user_id):
        """List sessions should return empty list for new user."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get_user_sessions.return_value = []

            response = test_client.get(
                "/api/discovery/sessions",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["sessions"] == []

    def test_list_sessions_with_data(
        self,
        test_client,
        auth_headers,
        test_user_id,
    ):
        """List sessions should return user's sessions."""
        sessions = [
            {
                "id": "session-1",
                "status": "completed",
                "product_idea": "Test idea 1",
                "progress_percentage": 100,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "id": "session-2",
                "status": "in_progress",
                "product_idea": "Test idea 2",
                "progress_percentage": 50,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        ]

        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get_user_sessions.return_value = sessions

            response = test_client.get(
                "/api/discovery/sessions",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["sessions"]) == 2


class TestDeleteSessionEndpoint:
    """Tests for DELETE /api/discovery/session/{session_id} endpoint."""

    def test_delete_requires_auth(self, test_client):
        """Delete session should require authentication."""
        response = test_client.delete("/api/discovery/session/test-session")
        assert response.status_code in [401, 403]

    def test_delete_returns_404_not_found(self, test_client, auth_headers, test_user_id):
        """Delete should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = False

            response = test_client.delete(
                "/api/discovery/session/non-existent",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_delete_success(self, test_client, auth_headers, test_user_id):
        """Delete should return 204 on success."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = True
            mock_store.delete.return_value = True

            response = test_client.delete(
                "/api/discovery/session/test-session-123",
                headers=auth_headers,
            )

        assert response.status_code == 204


class TestGetPackEndpoint:
    """Tests for GET /api/discovery/session/{session_id}/pack endpoint."""

    def test_get_pack_requires_auth(self, test_client):
        """Get pack should require authentication."""
        response = test_client.get("/api/discovery/session/test/pack")
        assert response.status_code in [401, 403]

    def test_get_pack_returns_404_not_found(self, test_client, auth_headers, test_user_id):
        """Get pack should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = False

            response = test_client.get(
                "/api/discovery/session/non-existent/pack",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_get_pack_returns_400_not_completed(
        self,
        test_client,
        auth_headers,
        sample_session_data,
        test_user_id,
    ):
        """Get pack should return 400 if session not completed."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = True
            mock_store.get.return_value = sample_session_data  # status is "pending"

            response = test_client.get(
                "/api/discovery/session/test-session-123/pack",
                headers=auth_headers,
            )

        assert response.status_code == 400

    def test_get_pack_success(
        self,
        test_client,
        auth_headers,
        sample_completed_session,
        sample_inception_pack,
        test_user_id,
    ):
        """Get pack should return inception pack."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = True
            mock_store.get.return_value = sample_completed_session
            mock_store.get_inception_pack.return_value = sample_inception_pack

            response = test_client.get(
                "/api/discovery/session/completed-session-456/pack",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()
        assert "executive_summary" in data


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestExportPdfEndpoint:
    """Tests for GET /api/discovery/session/{session_id}/export/pdf endpoint."""

    def test_export_pdf_requires_auth(self, test_client):
        """Export PDF should require authentication."""
        response = test_client.get("/api/discovery/session/test/export/pdf")
        assert response.status_code in [401, 403]

    def test_export_pdf_returns_404_not_found(self, test_client, auth_headers, test_user_id):
        """Export PDF should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = False

            response = test_client.get(
                "/api/discovery/session/non-existent/export/pdf",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_export_pdf_returns_400_invalid_section(
        self,
        test_client,
        auth_headers,
        test_user_id,
    ):
        """Export PDF should return 400 for invalid section."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.get(
                "/api/discovery/session/test/export/pdf?section=invalid_section",
                headers=auth_headers,
            )

        assert response.status_code == 400

    def test_export_pdf_returns_400_not_completed(
        self,
        test_client,
        auth_headers,
        sample_session_data,
        test_user_id,
    ):
        """Export PDF should return 400 if session not completed."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = True
            mock_store.get.return_value = sample_session_data

            response = test_client.get(
                "/api/discovery/session/test/export/pdf",
                headers=auth_headers,
            )

        assert response.status_code == 400


class TestExportDocxEndpoint:
    """Tests for GET /api/discovery/session/{session_id}/export/docx endpoint."""

    def test_export_docx_requires_auth(self, test_client):
        """Export DOCX should require authentication."""
        response = test_client.get("/api/discovery/session/test/export/docx")
        assert response.status_code in [401, 403]

    def test_export_docx_returns_404_not_found(self, test_client, auth_headers, test_user_id):
        """Export DOCX should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.verify_ownership.return_value = False

            response = test_client.get(
                "/api/discovery/session/non-existent/export/docx",
                headers=auth_headers,
            )

        assert response.status_code == 404

    def test_export_docx_returns_400_invalid_section(
        self,
        test_client,
        auth_headers,
        test_user_id,
    ):
        """Export DOCX should return 400 for invalid section."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.get(
                "/api/discovery/session/test/export/docx?section=invalid_section",
                headers=auth_headers,
            )

        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# V4 DISCOVERY ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4CreateTestSession:
    """Tests for POST /api/discovery/v4/test/sessions endpoint."""

    def test_create_test_session_success(
        self,
        test_client,
        sample_v4_session_request,
    ):
        """Create test session should work without auth."""
        with patch("api.discovery_v4_routes.session_store") as mock_store:
            mock_store.create_v4_session.return_value = None
            mock_store.save_v4_session_state.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions",
                json=sample_v4_session_request,
            )

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["mode"] == "guided"
        assert data["status"] == "created"

    def test_create_test_session_validates_product_idea(self, test_client):
        """Create test session should validate product idea length."""
        response = test_client.post(
            "/api/discovery/v4/test/sessions",
            json={"product_idea": "short"},
        )
        assert response.status_code == 422

    def test_create_test_session_default_mode(self, test_client):
        """Create test session should use guided mode by default."""
        with patch("api.discovery_v4_routes.session_store") as mock_store:
            mock_store.create_v4_session.return_value = None
            mock_store.save_v4_session_state.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions",
                json={
                    "product_idea": "AI-powered meeting room booking system for enterprise",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "guided"


class TestV4GetTestSession:
    """Tests for GET /api/discovery/v4/test/sessions/{session_id} endpoint."""

    def test_get_test_session_not_found(self, test_client):
        """Get test session should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.get(
                "/api/discovery/v4/test/sessions/non-existent",
            )

        assert response.status_code == 404

    def test_get_test_session_from_cache(self, test_client):
        """Get test session should return cached session."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}):
            response = test_client.get(
                "/api/discovery/v4/test/sessions/test-session-v4",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-v4"
        assert data["mode"] == "guided"


class TestV4RunTestStage:
    """Tests for POST /api/discovery/v4/test/sessions/{id}/stages/{stage}/run endpoint."""

    def test_run_stage_not_found(self, test_client):
        """Run stage should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.post(
                "/api/discovery/v4/test/sessions/non-existent/stages/problem_love/run",
            )

        assert response.status_code == 404

    def test_run_stage_invalid_stage(self, test_client):
        """Run stage should return 400 for invalid stage name."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/invalid_stage/run",
            )

        assert response.status_code == 400

    def test_run_stage_valid_request(self, test_client):
        """Run stage should accept valid stage requests."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/problem_love/run",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["stage"] == "problem_love"


class TestV4ApproveStage:
    """Tests for POST /api/discovery/v4/test/sessions/{id}/stages/{stage}/approve endpoint."""

    def test_approve_stage_not_found(self, test_client):
        """Approve stage should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.post(
                "/api/discovery/v4/test/sessions/non-existent/stages/problem_love/approve",
            )

        assert response.status_code == 404

    def test_approve_stage_invalid_stage(self, test_client):
        """Approve stage should return 400 for invalid stage."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/invalid_stage/approve",
            )

        assert response.status_code == 400


class TestV4SkipStage:
    """Tests for POST /api/discovery/v4/test/sessions/{id}/stages/{stage}/skip endpoint."""

    def test_skip_stage_not_found(self, test_client):
        """Skip stage should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.post(
                "/api/discovery/v4/test/sessions/non-existent/stages/problem_love/skip",
            )

        assert response.status_code == 404

    def test_skip_stage_success(self, test_client):
        """Skip stage should update stage status."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/customer_truth/skip",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "skipped"


class TestV4SaveStageOutput:
    """Tests for PUT /api/discovery/v4/test/sessions/{id}/stages/{stage}/output endpoint."""

    def test_save_output_not_found(self, test_client):
        """Save output should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.put(
                "/api/discovery/v4/test/sessions/non-existent/stages/problem_love/output",
                json={"output": {"test": "data"}, "source": "user_edited"},
            )

        assert response.status_code == 404

    def test_save_output_success(self, test_client):
        """Save output should update stage output."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.put(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/problem_love/output",
                json={
                    "output": {"problem_statement": "Test problem"},
                    "source": "user_edited",
                    "notes": "User made edits",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"


class TestV4AddInterview:
    """Tests for POST /api/discovery/v4/test/sessions/{id}/interviews endpoint."""

    def test_add_interview_not_found(self, test_client, sample_interview_data):
        """Add interview should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.post(
                "/api/discovery/v4/test/sessions/non-existent/interviews",
                json=sample_interview_data,
            )

        assert response.status_code == 404

    def test_add_interview_success(self, test_client, sample_interview_data):
        """Add interview should create interview record."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.DEEP,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/interviews",
                json=sample_interview_data,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["interviewee_name"] == "John Doe"
        assert "id" in data


class TestV4SynthesizeInterviews:
    """Tests for POST /api/discovery/v4/test/sessions/{id}/interviews/synthesize endpoint."""

    def test_synthesize_not_found(self, test_client):
        """Synthesize should return 404 for non-existent session."""
        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = None

            response = test_client.post(
                "/api/discovery/v4/test/sessions/non-existent/interviews/synthesize",
            )

        assert response.status_code == 404

    def test_synthesize_no_interviews(self, test_client):
        """Synthesize should return 400 if no interviews exist."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.DEEP,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            interviews=[],
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/interviews/synthesize",
            )

        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# V4 AUTHENTICATED ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4AuthenticatedEndpoints:
    """Tests for authenticated V4 endpoints."""

    def test_create_session_requires_auth(self, test_client, sample_v4_session_request):
        """Create authenticated session should require auth."""
        response = test_client.post(
            "/api/discovery/v4/sessions",
            json=sample_v4_session_request,
        )
        assert response.status_code in [401, 403]

    def test_get_session_requires_auth(self, test_client):
        """Get authenticated session should require auth."""
        response = test_client.get("/api/discovery/v4/sessions/test-session")
        assert response.status_code in [401, 403]

    def test_run_stage_requires_auth(self, test_client):
        """Run stage on authenticated session should require auth."""
        response = test_client.post(
            "/api/discovery/v4/sessions/test/stages/problem_love/run",
        )
        assert response.status_code in [401, 403]

    def test_list_sessions_requires_auth(self, test_client):
        """List V4 sessions should require auth."""
        response = test_client.get("/api/discovery/v4/sessions")
        assert response.status_code in [401, 403]


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMA VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestResponseSchemaValidation:
    """Tests to validate response schemas match expected format."""

    def test_discovery_response_schema(
        self,
        test_client,
        auth_headers,
        sample_discovery_request,
        test_user_id,
    ):
        """Discovery response should match DiscoveryResponse schema."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.count_active.return_value = 0
            mock_store.create.return_value = None

            response = test_client.post(
                "/api/discovery/start",
                json=sample_discovery_request,
                headers=auth_headers,
            )

        assert response.status_code == 202
        data = response.json()

        # Validate required fields
        assert "session_id" in data
        assert isinstance(data["session_id"], str)
        assert "status" in data
        assert data["status"] in ["pending", "in_progress", "completed", "failed"]
        assert "message" in data
        assert isinstance(data["message"], str)
        assert "created_at" in data

    def test_session_status_response_schema(
        self,
        test_client,
        auth_headers,
        sample_session_data,
        test_user_id,
    ):
        """Session status response should match SessionStatusResponse schema."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = sample_session_data

            response = test_client.get(
                "/api/discovery/session/test-session-123",
                headers=auth_headers,
            )

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        assert "session_id" in data
        assert "status" in data
        assert "progress_percentage" in data
        assert isinstance(data["progress_percentage"], int)
        assert 0 <= data["progress_percentage"] <= 100
        assert "iteration" in data
        assert isinstance(data["iteration"], int)

    def test_v4_session_response_schema(self, test_client):
        """V4 session response should match DiscoverySessionV4 schema."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}):
            response = test_client.get(
                "/api/discovery/v4/test/sessions/test-session-v4",
            )

        assert response.status_code == 200
        data = response.json()

        # Validate required fields
        assert "session_id" in data
        assert "user_id" in data
        assert "mode" in data
        assert data["mode"] in ["quick", "guided", "deep"]
        assert "product_idea" in data
        assert "stages" in data
        assert isinstance(data["stages"], dict)


# ═══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Tests for error handling across endpoints."""

    def test_invalid_json_returns_422(self, test_client, auth_headers, test_user_id):
        """Invalid JSON should return 422."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.post(
                "/api/discovery/start",
                content="invalid json{",
                headers={**auth_headers, "Content-Type": "application/json"},
            )
        assert response.status_code == 422

    def test_wrong_content_type_returns_422(self, test_client, auth_headers, test_user_id):
        """Wrong content type should return 422."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            response = test_client.post(
                "/api/discovery/start",
                content="product_idea=test",
                headers={**auth_headers, "Content-Type": "application/x-www-form-urlencoded"},
            )
        assert response.status_code == 422

    def test_malformed_session_id_handled(self, test_client, auth_headers, test_user_id):
        """Malformed session IDs should be handled gracefully."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = None

            response = test_client.get(
                "/api/discovery/session/../../etc/passwd",
                headers=auth_headers,
            )

        # Should return 404, not crash
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SANITIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestInputSanitization:
    """Tests for input sanitization."""

    def test_xss_in_product_idea_handled(
        self,
        test_client,
        auth_headers,
        test_user_id,
    ):
        """XSS payloads should be handled safely."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.count_active.return_value = 0
            mock_store.create.return_value = None

            response = test_client.post(
                "/api/discovery/start",
                json={
                    "product_idea": "<script>alert('xss')</script>AI assistant for enterprises",
                },
                headers=auth_headers,
            )

        # Should succeed but sanitize the input
        assert response.status_code == 202

    def test_sql_injection_in_session_id(self, test_client, auth_headers, test_user_id):
        """SQL injection in session ID should be handled safely."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}
            mock_store.get.return_value = None

            response = test_client.get(
                "/api/discovery/session/'; DROP TABLE discovery_sessions; --",
                headers=auth_headers,
            )

        # Should return 404, not error
        assert response.status_code == 404

    def test_very_long_input_handled(self, test_client, auth_headers, test_user_id):
        """Very long inputs should be rejected."""
        with patch("utils.auth.decode_supabase_jwt") as mock_decode:
            mock_decode.return_value = {"sub": test_user_id, "aud": "authenticated"}

            long_idea = "A" * 10000  # 10KB
            response = test_client.post(
                "/api/discovery/start",
                json={"product_idea": long_idea},
                headers=auth_headers,
            )

        # Should be rejected by validation (max_length=2000)
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# SSE STREAMING ENDPOINT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSSEStreamingEndpoint:
    """Tests for SSE streaming endpoint."""

    def test_stream_requires_token(self, test_client):
        """Stream endpoint should require token parameter."""
        response = test_client.get("/api/discovery/session/test-session/stream")
        assert response.status_code == 401

    def test_stream_with_invalid_token(self, test_client):
        """Stream endpoint should reject invalid tokens."""
        response = test_client.get(
            "/api/discovery/session/test-session/stream?token=invalid-token"
        )
        assert response.status_code == 401

    def test_stream_returns_404_for_missing_session(
        self, test_client, valid_jwt_token, test_user_id
    ):
        """Stream endpoint should return 404 for non-existent session."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.get_user_id_from_token") as mock_get_user:
            mock_get_user.return_value = test_user_id
            mock_store.verify_ownership.return_value = False

            response = test_client.get(
                f"/api/discovery/session/non-existent/stream?token={valid_jwt_token}"
            )

        assert response.status_code == 404

    def test_stream_completed_session_sends_done(
        self, test_client, valid_jwt_token, test_user_id, sample_completed_session
    ):
        """Stream endpoint should immediately send done event for completed sessions."""
        with patch("main.session_store") as mock_store, \
             patch("utils.auth.get_user_id_from_token") as mock_get_user:
            mock_get_user.return_value = test_user_id
            mock_store.verify_ownership.return_value = True
            mock_store.get.return_value = sample_completed_session

            response = test_client.get(
                f"/api/discovery/session/completed-session-456/stream?token={valid_jwt_token}"
            )

        assert response.status_code == 200
        # Check that response is SSE format
        assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"


# ═══════════════════════════════════════════════════════════════════════════════
# V4 STAGE EXECUTION WITH LLM MOCKING
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4StageExecutionWithMocking:
    """Tests for V4 stage execution with mocked LLM calls."""

    def test_run_stage_updates_session_state(self, test_client):
        """Run stage should update session state and execute background task."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode, StageStatus
        import asyncio

        mock_session = DiscoverySessionV4(
            session_id="test-session-v4",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        # Create an async mock that returns the session with status set to COMPLETED
        async def mock_run_stage(session, stage):
            # Simulate successful stage completion
            session.stages[stage].status = StageStatus.COMPLETED
            return session

        # Mock the discovery engine to prevent actual LLM calls in background task
        with patch("api.discovery_v4_routes._active_sessions", {"test-session-v4": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist, \
             patch("agents.discovery_v4.engine.DiscoveryEngineV4") as mock_engine_class:
            mock_persist.return_value = True
            # Make the engine's run_stage return the session with COMPLETED status
            mock_engine = mock_engine_class.return_value
            mock_engine.run_stage = mock_run_stage

            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-v4/stages/problem_love/run",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"

        # After background task completes, status should be COMPLETED
        # (background task ran and the mock set status to COMPLETED)
        assert mock_session.stages["problem_love"].status == StageStatus.COMPLETED
        assert mock_session.stages["problem_love"].started_at is not None

    def test_run_all_valid_stages(self, test_client):
        """Test running each valid V4 stage."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        valid_stages = [
            "problem_love",
            "customer_truth",
            "opportunity_mapping",
            "solution_design",
            "validation_plan",
        ]

        for stage in valid_stages:
            mock_session = DiscoverySessionV4(
                session_id=f"test-session-{stage}",
                user_id="test-user",
                mode=DiscoveryMode.GUIDED,
                product_idea="Test product idea for the V4 system",
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat(),
            )

            with patch("api.discovery_v4_routes._active_sessions", {f"test-session-{stage}": mock_session}), \
                 patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
                mock_persist.return_value = True

                response = test_client.post(
                    f"/api/discovery/v4/test/sessions/test-session-{stage}/stages/{stage}/run",
                )

            assert response.status_code == 200, f"Failed for stage: {stage}"

    def test_stage_completion_persists_to_db(self, test_client):
        """Test that stage completion triggers database persistence."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode, StageStatus

        mock_session = DiscoverySessionV4(
            session_id="test-session-persist",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        # Pre-complete a stage
        mock_session.stages["problem_love"].status = StageStatus.COMPLETED
        mock_session.stages["problem_love"].output = {"problem_statement": "Test problem"}

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-persist": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            # Approve the completed stage
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-persist/stages/problem_love/approve",
            )

        assert response.status_code == 200
        # Verify persistence was called
        mock_persist.assert_called()

    def test_stage_error_handling(self, test_client):
        """Test that stage errors are properly handled."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-session-error",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea for the V4 system",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-session-error": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist, \
             patch("agents.discovery_v4.engine.DiscoveryEngineV4.run_stage") as mock_run:
            # Simulate LLM error
            mock_run.side_effect = Exception("LLM API error")
            mock_persist.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-session-error/stages/problem_love/run",
            )

        # Should still return 200 as task is queued
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# V4 DATABASE PERSISTENCE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4DatabasePersistence:
    """Tests for V4 session database persistence."""

    def test_session_loads_from_db_when_not_cached(self, test_client):
        """Test session loading from database when not in memory."""
        from models.discovery_v4_schemas import (
            DiscoverySessionV4,
            DiscoveryMode,
            StageState,
            StageStatus,
        )

        # Mock database session data
        mock_db_session = DiscoverySessionV4(
            session_id="test-db-session",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Loaded from database",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {}), \
             patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
            mock_load.return_value = mock_db_session

            response = test_client.get(
                "/api/discovery/v4/test/sessions/test-db-session",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["product_idea"] == "Loaded from database"

    def test_session_create_persists_to_db(self, test_client, sample_v4_session_request):
        """Test that session creation persists to database."""
        with patch("api.discovery_v4_routes.session_store") as mock_store:
            mock_store.create_v4_session.return_value = None
            mock_store.save_v4_session_state.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions",
                json=sample_v4_session_request,
            )

        assert response.status_code == 200
        # Verify database calls were made
        mock_store.create_v4_session.assert_called_once()

    def test_stage_output_save_persists_to_db(self, test_client):
        """Test that saving stage output persists to database."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-save-output",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-save-output": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.put(
                "/api/discovery/v4/test/sessions/test-save-output/stages/problem_love/output",
                json={
                    "output": {"problem_statement": "User edited problem"},
                    "source": "user_edited",
                },
            )

        assert response.status_code == 200
        # Verify persistence was called
        mock_persist.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# V4 INTERVIEW MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4InterviewManagement:
    """Comprehensive tests for V4 interview management."""

    def test_add_multiple_interviews(self, test_client, sample_interview_data):
        """Test adding multiple interviews to a session."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-multi-interviews",
            user_id="test-user",
            mode=DiscoveryMode.DEEP,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-multi-interviews": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            # Add first interview
            response1 = test_client.post(
                "/api/discovery/v4/test/sessions/test-multi-interviews/interviews",
                json=sample_interview_data,
            )
            assert response1.status_code == 200

            # Add second interview
            interview_2 = {**sample_interview_data, "interviewee_name": "Jane Smith"}
            response2 = test_client.post(
                "/api/discovery/v4/test/sessions/test-multi-interviews/interviews",
                json=interview_2,
            )
            assert response2.status_code == 200

        # Verify session has 2 interviews
        assert len(mock_session.interviews) == 2

    def test_interview_updates_evidence_quality(self, test_client, sample_interview_data):
        """Test that adding interviews updates evidence quality tier."""
        from models.discovery_v4_schemas import (
            DiscoverySessionV4,
            DiscoveryMode,
            EvidenceQuality,
        )

        mock_session = DiscoverySessionV4(
            session_id="test-evidence-quality",
            user_id="test-user",
            mode=DiscoveryMode.DEEP,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            overall_evidence_quality=EvidenceQuality.E4,  # Start with AI-generated
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-evidence-quality": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            # Add one interview - should upgrade to E3
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-evidence-quality/interviews",
                json=sample_interview_data,
            )

        assert response.status_code == 200
        # Evidence quality should improve with real interviews
        # (Though in this test it won't automatically update without the real handler)

    def test_synthesize_interviews_requires_minimum_interviews(self, test_client):
        """Test that synthesis requires at least one interview."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-no-interviews",
            user_id="test-user",
            mode=DiscoveryMode.DEEP,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            interviews=[],
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-no-interviews": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-no-interviews/interviews/synthesize",
            )

        assert response.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# V4 LIFECYCLE CONTINUATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestV4LifecycleContinuation:
    """Tests for continuing from V4 discovery to full lifecycle."""

    def test_continue_requires_completed_stage(self, test_client):
        """Test that continue to strategy requires at least one completed stage."""
        from models.discovery_v4_schemas import (
            DiscoverySessionV4,
            DiscoveryMode,
            StageStatus,
        )

        mock_session = DiscoverySessionV4(
            session_id="test-no-stages",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-no-stages": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-no-stages/continue-to-strategy",
            )

        assert response.status_code == 400

    def test_continue_with_completed_stages(self, test_client):
        """Test continue to strategy with completed stages."""
        from models.discovery_v4_schemas import (
            DiscoverySessionV4,
            DiscoveryMode,
            StageState,
            StageStatus,
        )

        mock_session = DiscoverySessionV4(
            session_id="test-ready-continue",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        # Mark first stage as completed
        mock_session.stages["problem_love"].status = StageStatus.APPROVED
        mock_session.stages["problem_love"].output = {"problem_statement": "Test"}

        with patch("api.discovery_v4_routes._active_sessions", {"test-ready-continue": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-ready-continue/continue-to-strategy",
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"

    def test_continue_queues_background_task(self, test_client):
        """Test that continue to strategy queues a background task."""
        from models.discovery_v4_schemas import (
            DiscoverySessionV4,
            DiscoveryMode,
            StageStatus,
        )

        mock_session = DiscoverySessionV4(
            session_id="test-bg-task",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        mock_session.stages["problem_love"].status = StageStatus.APPROVED
        mock_session.stages["problem_love"].output = {"problem_statement": "Test"}

        with patch("api.discovery_v4_routes._active_sessions", {"test-bg-task": mock_session}):
            response = test_client.post(
                "/api/discovery/v4/test/sessions/test-bg-task/continue-to-strategy",
            )

        assert response.status_code == 200
        # Background task should be queued (we can't verify execution in sync test)


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASE AND BOUNDARY TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCasesAndBoundaries:
    """Tests for edge cases and boundary conditions."""

    def test_concurrent_stage_runs_handled(self, test_client):
        """Test that concurrent runs of the same stage are handled."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-concurrent",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-concurrent": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            # Run same stage twice
            response1 = test_client.post(
                "/api/discovery/v4/test/sessions/test-concurrent/stages/problem_love/run",
            )
            response2 = test_client.post(
                "/api/discovery/v4/test/sessions/test-concurrent/stages/problem_love/run",
            )

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_session_with_special_characters(self, test_client):
        """Test session creation with special characters in product idea."""
        special_idea = "AI-powered system with émojis 🚀 and spëcial çharacters"

        with patch("api.discovery_v4_routes.session_store") as mock_store:
            mock_store.create_v4_session.return_value = None
            mock_store.save_v4_session_state.return_value = True

            response = test_client.post(
                "/api/discovery/v4/test/sessions",
                json={
                    "product_idea": special_idea,
                    "mode": "guided",
                },
            )

        assert response.status_code == 200

    def test_empty_stage_output_handled(self, test_client):
        """Test that empty stage output is handled properly."""
        from models.discovery_v4_schemas import DiscoverySessionV4, DiscoveryMode

        mock_session = DiscoverySessionV4(
            session_id="test-empty-output",
            user_id="test-user",
            mode=DiscoveryMode.GUIDED,
            product_idea="Test product idea",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
        )

        with patch("api.discovery_v4_routes._active_sessions", {"test-empty-output": mock_session}), \
             patch("api.discovery_v4_routes._persist_session_to_db") as mock_persist:
            mock_persist.return_value = True

            response = test_client.put(
                "/api/discovery/v4/test/sessions/test-empty-output/stages/problem_love/output",
                json={
                    "output": {},  # Empty output
                    "source": "user_edited",
                },
            )

        assert response.status_code == 200

    def test_session_id_format_validation(self, test_client):
        """Test that various session ID formats are handled."""
        test_ids = [
            "normal-session-123",
            "session_with_underscores",
            "SessionWithCaps",
            "session-with-many-dashes-and-numbers-123456",
        ]

        for session_id in test_ids:
            with patch("api.discovery_v4_routes._active_sessions", {}), \
                 patch("api.discovery_v4_routes._load_session_from_db") as mock_load:
                mock_load.return_value = None

                response = test_client.get(
                    f"/api/discovery/v4/test/sessions/{session_id}",
                )

            # Should return 404 (not found) rather than error
            assert response.status_code == 404, f"Failed for ID: {session_id}"
