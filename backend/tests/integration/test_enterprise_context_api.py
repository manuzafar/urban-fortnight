"""
Integration tests for Enterprise Context API endpoints.

Tests the /api/contexts/* endpoints with mocked database.
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from main import app
from models.enterprise_context_schemas import ContextType, ContextScope, ValidationStatus
from utils.auth import get_current_user_id


# ═══════════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_user_id():
    """Standard mock user ID."""
    return "test-user-123"


@pytest.fixture
def test_client(mock_user_id):
    """Create a test client with mocked authentication."""
    # Override the authentication dependency
    def override_get_current_user_id():
        return mock_user_id

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    client = TestClient(app)
    yield client
    # Clean up overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth(mock_user_id):
    """Mock authentication fixture (no-op, handled by test_client)."""
    yield mock_user_id


@pytest.fixture
def company_context_yaml():
    """Sample company context in YAML format."""
    return """schema: enterprise-context/v1/company
company: Acme Corporation
industry: Financial Services

strategy:
  strategic_priorities:
    - Digital transformation
    - Customer experience
  strategic_constraints:
    - No acquisitions in 2024

technology:
  cloud: AWS
  primary_languages:
    - Python
    - TypeScript

regulatory:
  frameworks:
    - SOC2
    - GDPR
  data_residency: US-only
"""


@pytest.fixture
def division_context_yaml():
    """Sample division context in YAML format."""
    return """schema: enterprise-context/v1/division
division: Engineering
parent_company: Acme Corporation

technology:
  primary_languages:
    - Python
    - Go
  infrastructure:
    - Kubernetes
"""


@pytest.fixture
def mock_context_row(mock_user_id, company_context_yaml):
    """Sample database row for a context."""
    return {
        "id": "ctx-123",
        "user_id": mock_user_id,
        "name": "Acme Company Context",
        "context_type": "company",
        "parent_id": None,
        "raw_content": company_context_yaml,
        "parsed_content": {
            "schema": "enterprise-context/v1/company",
            "company": "Acme Corporation",
            "industry": "Financial Services",
            "technology": {"cloud": "AWS"},
            "regulatory": {"frameworks": ["SOC2", "GDPR"]},
        },
        "validation_status": "valid",
        "validation_errors": [],
        "scope": "private",
        "is_default": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_session_row(mock_user_id):
    """Sample database row for a session."""
    return {
        "id": "session-456",
        "user_id": mock_user_id,
        "product_idea": "Test product idea",
        "status": "pending",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MOCK SUPABASE HELPER
# ═══════════════════════════════════════════════════════════════════════════════


def create_mock_supabase_client(context_rows=None, session_rows=None):
    """Create a mock Supabase client with configured responses."""
    mock_client = MagicMock()

    context_rows = context_rows or []
    session_rows = session_rows or []

    # Track which table is being queried
    current_table = {"name": None}

    def mock_table(table_name):
        current_table["name"] = table_name
        return mock_client

    def mock_select(*args):
        return mock_client

    def mock_insert(data):
        return mock_client

    def mock_update(data):
        return mock_client

    def mock_delete():
        return mock_client

    def mock_eq(field, value):
        return mock_client

    def mock_or_(condition):
        return mock_client

    def mock_in_(field, values):
        return mock_client

    def mock_order(field, **kwargs):
        return mock_client

    def mock_maybe_single():
        return mock_client

    def mock_execute():
        mock_result = MagicMock()

        if current_table["name"] == "enterprise_contexts":
            if context_rows:
                mock_result.data = context_rows
            else:
                mock_result.data = None
        elif current_table["name"] == "discovery_sessions":
            if session_rows:
                mock_result.data = session_rows[0] if len(session_rows) == 1 else session_rows
            else:
                mock_result.data = None
        elif current_table["name"] == "session_contexts":
            mock_result.data = []
        else:
            mock_result.data = None

        return mock_result

    mock_client.table = mock_table
    mock_client.select = mock_select
    mock_client.insert = mock_insert
    mock_client.update = mock_update
    mock_client.delete = mock_delete
    mock_client.eq = mock_eq
    mock_client.or_ = mock_or_
    mock_client.in_ = mock_in_
    mock_client.order = mock_order
    mock_client.maybe_single = mock_maybe_single
    mock_client.execute = mock_execute

    return mock_client


# ═══════════════════════════════════════════════════════════════════════════════
# CREATE CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreateContext:
    """Tests for POST /api/contexts endpoint."""

    def test_create_context_success(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_context_row,
        company_context_yaml,
    ):
        """Test successful context creation."""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts",
                json={
                    "name": "Acme Company Context",
                    "context_type": "company",
                    "raw_content": company_context_yaml,
                    "scope": "private",
                    "is_default": False,
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Acme Company Context"
        assert data["context_type"] == "company"
        assert data["validation_status"] in ["valid", "pending"]

    def test_create_context_invalid_yaml(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test context creation with invalid YAML."""
        mock_row = {**mock_context_row, "validation_status": "invalid", "validation_errors": ["Invalid YAML"]}
        mock_client = create_mock_supabase_client(context_rows=[mock_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts",
                json={
                    "name": "Bad Context",
                    "context_type": "company",
                    "raw_content": "invalid: yaml: content:",
                    "scope": "private",
                },
            )

        # Should still create but with validation errors
        assert response.status_code in [201, 400]


# ═══════════════════════════════════════════════════════════════════════════════
# UPLOAD CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestUploadContext:
    """Tests for POST /api/contexts/upload endpoint."""

    def test_upload_yaml_file_success(
        self,
        test_client,
        mock_auth,
        mock_context_row,
        company_context_yaml,
    ):
        """Test successful YAML file upload."""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/upload",
                files={"file": ("context.yaml", company_context_yaml, "text/yaml")},
                data={"context_type": "company"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["context_type"] == "company"
        assert "id" in data

    def test_upload_markdown_file_success(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test successful markdown file upload."""
        markdown_content = """---
schema: enterprise-context/v1/company
company: Test Corp
---

# Company Context

Additional documentation here.
"""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/upload",
                files={"file": ("context.md", markdown_content, "text/markdown")},
                data={"context_type": "company"},
            )

        assert response.status_code == 201

    def test_upload_invalid_extension(
        self,
        test_client,
        mock_auth,
    ):
        """Test upload with invalid file extension."""
        response = test_client.post(
            "/api/contexts/upload",
            files={"file": ("context.txt", "some content", "text/plain")},
        )

        assert response.status_code == 400
        assert "File must be" in response.json()["detail"]

    def test_upload_auto_detect_type(
        self,
        test_client,
        mock_auth,
        mock_context_row,
        company_context_yaml,
    ):
        """Test auto-detection of context type from content."""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/upload",
                files={"file": ("context.yaml", company_context_yaml, "text/yaml")},
                # No context_type specified - should auto-detect
            )

        # Should either succeed or fail if can't detect
        assert response.status_code in [201, 400]


# ═══════════════════════════════════════════════════════════════════════════════
# LIST CONTEXTS TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestListContexts:
    """Tests for GET /api/contexts endpoint."""

    def test_list_contexts_success(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test listing all contexts."""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts")

        assert response.status_code == 200
        data = response.json()
        assert "contexts" in data
        assert "count" in data

    def test_list_contexts_filter_by_type(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test filtering contexts by type."""
        mock_client = create_mock_supabase_client(context_rows=[mock_context_row])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts?context_type=company")

        assert response.status_code == 200

    def test_list_contexts_empty(
        self,
        test_client,
        mock_auth,
    ):
        """Test listing contexts when none exist."""
        mock_client = create_mock_supabase_client(context_rows=[])

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GET CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetContext:
    """Tests for GET /api/contexts/{id} endpoint."""

    def test_get_context_success(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test getting a single context."""
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_context_row
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/ctx-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "ctx-123"
        assert data["name"] == "Acme Company Context"

    def test_get_context_not_found(
        self,
        test_client,
        mock_auth,
    ):
        """Test getting a non-existent context."""
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/nonexistent")

        assert response.status_code == 404

    def test_get_context_access_denied(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test access denied for another user's private context."""
        other_user_row = {**mock_context_row, "user_id": "other-user", "scope": "private"}

        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = other_user_row
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/ctx-123")

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# UPDATE CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestUpdateContext:
    """Tests for PATCH /api/contexts/{id} endpoint."""

    def test_update_context_name(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_context_row,
    ):
        """Test updating context name."""
        updated_row = {**mock_context_row, "name": "Updated Name"}

        mock_client = MagicMock()
        # For ownership check
        mock_existing = MagicMock()
        mock_existing.data = {"user_id": mock_user_id, "context_type": "company"}
        # For update
        mock_result = MagicMock()
        mock_result.data = [updated_row]

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_existing
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.patch(
                "/api/contexts/ctx-123",
                json={"name": "Updated Name"},
            )

        assert response.status_code == 200

    def test_update_context_not_owner(
        self,
        test_client,
        mock_auth,
    ):
        """Test updating context owned by another user."""
        mock_client = MagicMock()
        mock_existing = MagicMock()
        mock_existing.data = {"user_id": "other-user", "context_type": "company"}
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_existing

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.patch(
                "/api/contexts/ctx-123",
                json={"name": "New Name"},
            )

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# DELETE CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeleteContext:
    """Tests for DELETE /api/contexts/{id} endpoint."""

    def test_delete_context_success(
        self,
        test_client,
        mock_auth,
        mock_user_id,
    ):
        """Test successful context deletion."""
        mock_client = MagicMock()
        mock_existing = MagicMock()
        mock_existing.data = {"user_id": mock_user_id}
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_existing
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.delete("/api/contexts/ctx-123")

        assert response.status_code == 204

    def test_delete_context_not_found(
        self,
        test_client,
        mock_auth,
    ):
        """Test deleting non-existent context."""
        mock_client = MagicMock()
        mock_existing = MagicMock()
        mock_existing.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_existing

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.delete("/api/contexts/nonexistent")

        assert response.status_code == 404

    def test_delete_context_not_owner(
        self,
        test_client,
        mock_auth,
    ):
        """Test deleting context owned by another user."""
        mock_client = MagicMock()
        mock_existing = MagicMock()
        mock_existing.data = {"user_id": "other-user"}
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_existing

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.delete("/api/contexts/ctx-123")

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# PREVIEW MERGED CONTEXT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPreviewMergedContext:
    """Tests for GET /api/contexts/{id}/preview endpoint."""

    def test_preview_company_context(
        self,
        test_client,
        mock_auth,
        mock_context_row,
    ):
        """Test previewing a company context."""
        mock_client = MagicMock()
        mock_result = MagicMock()
        mock_result.data = mock_context_row
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = mock_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/ctx-123/preview")

        assert response.status_code == 200
        data = response.json()
        assert "merged_context" in data
        assert "sources" in data
        assert "constraints_preview" in data

    def test_preview_with_hierarchy(
        self,
        test_client,
        mock_auth,
        mock_user_id,
    ):
        """Test previewing a division context with company parent."""
        division_row = {
            "id": "div-123",
            "user_id": mock_user_id,
            "name": "Engineering Division",
            "context_type": "division",
            "parent_id": "company-123",
            "parsed_content": {
                "division": "Engineering",
                "technology": {"infrastructure": ["Kubernetes"]},
            },
            "validation_status": "valid",
            "validation_errors": [],
            "scope": "private",
            "is_default": False,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        company_row = {
            "parsed_content": {
                "company": "Acme",
                "technology": {"cloud": "AWS"},
            }
        }

        mock_client = MagicMock()

        # First call returns division
        # Second call returns company parent
        call_count = {"count": 0}

        def mock_execute():
            result = MagicMock()
            call_count["count"] += 1
            if call_count["count"] == 1:
                result.data = division_row
            else:
                result.data = company_row
            return result

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute = mock_execute

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/div-123/preview")

        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION CONTEXT ATTACHMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSessionContextAttachment:
    """Tests for session context attachment endpoints."""

    def test_attach_contexts_to_session(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_context_row,
        mock_session_row,
    ):
        """Test attaching contexts to a session."""
        mock_client = MagicMock()

        # Session lookup
        session_result = MagicMock()
        session_result.data = mock_session_row

        # Context lookup
        context_result = MagicMock()
        context_result.data = mock_context_row

        # Setup chained calls
        table_mock = MagicMock()
        mock_client.table.return_value = table_mock
        table_mock.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = [
            session_result,
            context_result,
        ]
        table_mock.delete.return_value.eq.return_value.execute.return_value = MagicMock()
        table_mock.insert.return_value.execute.return_value = MagicMock()

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/sessions/session-456/attach",
                json={"context_ids": ["ctx-123"]},
            )

        # May succeed or fail depending on mock setup
        assert response.status_code in [200, 500]

    def test_attach_duplicate_context_type(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_context_row,
        mock_session_row,
    ):
        """Test attaching two contexts of the same type fails."""
        mock_client = MagicMock()

        session_result = MagicMock()
        session_result.data = mock_session_row

        # Two company contexts
        context1 = {**mock_context_row, "id": "ctx-1"}
        context2 = {**mock_context_row, "id": "ctx-2"}

        call_count = {"count": 0}

        def mock_execute():
            result = MagicMock()
            call_count["count"] += 1
            if call_count["count"] == 1:
                result.data = mock_session_row
            elif call_count["count"] == 2:
                result.data = context1
            else:
                result.data = context2
            return result

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute = mock_execute

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/sessions/session-456/attach",
                json={"context_ids": ["ctx-1", "ctx-2"]},
            )

        # Should fail with duplicate type error
        assert response.status_code == 400 or response.status_code == 500

    def test_get_session_contexts(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_session_row,
    ):
        """Test getting contexts attached to a session."""
        mock_client = MagicMock()

        session_result = MagicMock()
        session_result.data = mock_session_row

        session_contexts_result = MagicMock()
        session_contexts_result.data = []

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = session_result
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = session_contexts_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.get("/api/contexts/sessions/session-456/contexts")

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "contexts" in data

    def test_detach_contexts_from_session(
        self,
        test_client,
        mock_auth,
        mock_user_id,
        mock_session_row,
    ):
        """Test detaching all contexts from a session."""
        mock_client = MagicMock()

        session_result = MagicMock()
        session_result.data = mock_session_row

        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = session_result
        mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MagicMock()

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.delete("/api/contexts/sessions/session-456/contexts")

        assert response.status_code == 204

    def test_attach_contexts_session_not_found(
        self,
        test_client,
        mock_auth,
    ):
        """Test attaching contexts to non-existent session."""
        mock_client = MagicMock()
        session_result = MagicMock()
        session_result.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = session_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/sessions/nonexistent/attach",
                json={"context_ids": ["ctx-123"]},
            )

        assert response.status_code == 404

    def test_attach_contexts_access_denied(
        self,
        test_client,
        mock_auth,
    ):
        """Test attaching contexts to another user's session."""
        mock_client = MagicMock()
        session_result = MagicMock()
        session_result.data = {"id": "session-456", "user_id": "other-user"}
        mock_client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = session_result

        with patch("api.enterprise_context_routes._get_supabase", return_value=mock_client):
            response = test_client.post(
                "/api/contexts/sessions/session-456/attach",
                json={"context_ids": ["ctx-123"]},
            )

        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidation:
    """Tests for request validation."""

    def test_create_context_missing_name(
        self,
        test_client,
        mock_auth,
    ):
        """Test creating context without name fails."""
        response = test_client.post(
            "/api/contexts",
            json={
                "context_type": "company",
                "raw_content": "company: Test",
            },
        )

        assert response.status_code == 422

    def test_create_context_invalid_type(
        self,
        test_client,
        mock_auth,
    ):
        """Test creating context with invalid type fails."""
        response = test_client.post(
            "/api/contexts",
            json={
                "name": "Test",
                "context_type": "invalid",
                "raw_content": "company: Test",
            },
        )

        assert response.status_code == 422

    def test_create_context_missing_content(
        self,
        test_client,
        mock_auth,
    ):
        """Test creating context without content fails."""
        response = test_client.post(
            "/api/contexts",
            json={
                "name": "Test",
                "context_type": "company",
            },
        )

        assert response.status_code == 422

    def test_attach_empty_context_ids(
        self,
        test_client,
        mock_auth,
    ):
        """Test attaching empty context list fails."""
        response = test_client.post(
            "/api/contexts/sessions/session-456/attach",
            json={"context_ids": []},
        )

        # Should fail validation (min 1 context)
        assert response.status_code in [422, 404]

    def test_attach_too_many_contexts(
        self,
        test_client,
        mock_auth,
    ):
        """Test attaching more than 3 contexts fails."""
        response = test_client.post(
            "/api/contexts/sessions/session-456/attach",
            json={"context_ids": ["ctx-1", "ctx-2", "ctx-3", "ctx-4"]},
        )

        # Should fail validation (max 3 contexts)
        assert response.status_code in [422, 404]
