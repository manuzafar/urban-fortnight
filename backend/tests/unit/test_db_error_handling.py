"""
Unit tests for database error handling in SupabaseSessionStore.

Tests verify that all database methods gracefully handle:
1. Supabase client returning None results
2. Supabase client raising exceptions
3. result.data being None

Each method should either:
- Return a safe default (None, [], False, 0) for read operations
- Log and re-raise for write operations that must succeed
"""

import pytest
from unittest.mock import MagicMock, patch
from utils.db import SupabaseSessionStore


class MockExecuteResult:
    """Mock for Supabase execute() result."""

    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


class TestReadOperationsGracefulDegradation:
    """Test that read operations return safe defaults on failure."""

    @pytest.fixture
    def store(self):
        """Create a store with mocked client."""
        store = SupabaseSessionStore()
        store._client = MagicMock()
        return store

    def test_get_returns_none_on_exception(self, store):
        """get() should return None when Supabase raises an exception."""
        store._client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get("test_session_id")

        assert result is None

    def test_get_returns_none_when_result_is_none(self, store):
        """get() should return None when execute() returns None."""
        store._client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = (
            None
        )

        result = store.get("test_session_id")

        assert result is None

    def test_get_inception_pack_returns_none_on_exception(self, store):
        """get_inception_pack() should return None on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get_inception_pack("test_session_id")

        assert result is None

    def test_get_inception_pack_returns_none_when_result_is_none(self, store):
        """get_inception_pack() should return None when result is None."""
        store._client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = (
            None
        )

        result = store.get_inception_pack("test_session_id")

        assert result is None

    def test_get_user_sessions_returns_empty_list_on_exception(self, store):
        """get_user_sessions() should return [] on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get_user_sessions("test_user_id")

        assert result == []

    def test_get_user_sessions_returns_empty_list_when_data_is_none(self, store):
        """get_user_sessions() should return [] when result.data is None."""
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.get_user_sessions("test_user_id")

        assert result == []

    def test_get_user_v4_sessions_returns_empty_list_on_exception(self, store):
        """get_user_v4_sessions() should return [] on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get_user_v4_sessions("test_user_id")

        assert result == []

    def test_get_user_v4_sessions_returns_empty_list_when_data_is_none(self, store):
        """get_user_v4_sessions() should return [] when result.data is None."""
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.get_user_v4_sessions("test_user_id")

        assert result == []

    def test_count_active_returns_zero_on_exception(self, store):
        """count_active() should return 0 on exception."""
        store._client.table.return_value.select.return_value.in_.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.count_active()

        assert result == 0

    def test_count_active_returns_zero_when_result_is_none(self, store):
        """count_active() should return 0 when result is None."""
        store._client.table.return_value.select.return_value.in_.return_value.execute.return_value = (
            None
        )

        result = store.count_active()

        assert result == 0

    def test_verify_ownership_returns_false_on_exception(self, store):
        """verify_ownership() should return False on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.verify_ownership("session_id", "user_id")

        assert result is False

    def test_verify_ownership_returns_false_when_result_is_none(self, store):
        """verify_ownership() should return False when result is None."""
        store._client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = (
            None
        )

        result = store.verify_ownership("session_id", "user_id")

        assert result is False

    def test_get_draft_state_returns_none_on_exception(self, store):
        """get_draft_state() should return None on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get_draft_state("session_id", "stage_name")

        assert result is None

    def test_get_interviews_returns_empty_list_on_exception(self, store):
        """get_interviews() should return [] on exception."""
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.get_interviews("session_id")

        assert result == []

    def test_load_v4_session_state_returns_none_on_exception(self, store):
        """load_v4_session_state() should return None on exception."""
        # Mock get() to raise
        with patch.object(store, "get", side_effect=Exception("Network error")):
            result = store.load_v4_session_state("session_id")

        assert result is None


class TestUpdateOperationsReturnFalse:
    """Test that update operations return False on failure."""

    @pytest.fixture
    def store(self):
        """Create a store with mocked client."""
        store = SupabaseSessionStore()
        store._client = MagicMock()
        return store

    def test_update_status_returns_false_on_exception(self, store):
        """update_status() should return False on exception."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.update_status("session_id", {"status": "completed"})

        assert result is False

    def test_update_status_returns_false_when_result_is_none(self, store):
        """update_status() should return False when result is None."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            None
        )

        result = store.update_status("session_id", {"status": "completed"})

        assert result is False

    def test_update_status_returns_false_when_data_is_none(self, store):
        """update_status() should return False when result.data is None."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.update_status("session_id", {"status": "completed"})

        assert result is False

    def test_delete_returns_false_on_exception(self, store):
        """delete() should return False on exception."""
        store._client.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.delete("session_id")

        assert result is False

    def test_delete_returns_false_when_data_is_none(self, store):
        """delete() should return False when result.data is None."""
        store._client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.delete("session_id")

        assert result is False

    def test_approve_stage_returns_false_on_exception(self, store):
        """approve_stage() should return False on exception."""
        store._client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.approve_stage("session_id", "stage_name")

        assert result is False

    def test_approve_stage_returns_false_when_data_is_none(self, store):
        """approve_stage() should return False when result.data is None."""
        store._client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.approve_stage("session_id", "stage_name")

        assert result is False

    def test_delete_interview_returns_false_on_exception(self, store):
        """delete_interview() should return False on exception."""
        store._client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.delete_interview("session_id", "interview_id")

        assert result is False

    def test_delete_interview_returns_false_when_data_is_none(self, store):
        """delete_interview() should return False when result.data is None."""
        store._client.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.delete_interview("session_id", "interview_id")

        assert result is False

    def test_save_v4_session_state_returns_false_on_exception(self, store):
        """save_v4_session_state() should return False on exception."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "Network error"
        )

        result = store.save_v4_session_state("session_id", {"mode": "guided"})

        assert result is False

    def test_save_v4_session_state_returns_false_when_data_is_none(self, store):
        """save_v4_session_state() should return False when result.data is None."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.save_v4_session_state("session_id", {"mode": "guided"})

        assert result is False


class TestWriteOperationsReraise:
    """Test that write operations re-raise exceptions after logging."""

    @pytest.fixture
    def store(self):
        """Create a store with mocked client."""
        store = SupabaseSessionStore()
        store._client = MagicMock()
        return store

    def test_create_raises_on_exception(self, store):
        """create() should re-raise exception after logging."""
        store._client.table.return_value.insert.return_value.execute.side_effect = (
            Exception("Network error")
        )

        with pytest.raises(Exception, match="Network error"):
            store.create(
                "session_id",
                "user_id",
                {"product_idea": "Test idea"},
            )

    def test_save_inception_pack_raises_on_exception(self, store):
        """save_inception_pack() should re-raise exception after logging."""
        store._client.table.return_value.upsert.return_value.execute.side_effect = (
            Exception("Network error")
        )

        with pytest.raises(Exception, match="Network error"):
            store.save_inception_pack("session_id", "user_id", {"data": "test"})

    def test_create_v4_session_raises_on_exception(self, store):
        """create_v4_session() should re-raise exception after logging."""
        store._client.table.return_value.insert.return_value.execute.side_effect = (
            Exception("Network error")
        )

        with pytest.raises(Exception, match="Network error"):
            store.create_v4_session(
                "session_id",
                "user_id",
                {"product_idea": "Test idea", "mode": "guided"},
            )


class TestSuccessfulOperations:
    """Test that operations work correctly when Supabase returns valid data."""

    @pytest.fixture
    def store(self):
        """Create a store with mocked client."""
        store = SupabaseSessionStore()
        store._client = MagicMock()
        return store

    def test_get_returns_data_on_success(self, store):
        """get() should return data when Supabase succeeds."""
        expected_data = {"id": "test_id", "product_idea": "Test idea"}
        store._client.table.return_value.select.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MockExecuteResult(
            data=expected_data
        )

        result = store.get("test_session_id")

        assert result == expected_data

    def test_get_user_sessions_returns_data_on_success(self, store):
        """get_user_sessions() should return list of sessions on success."""
        expected_data = [{"id": "1"}, {"id": "2"}]
        store._client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = MockExecuteResult(
            data=expected_data
        )

        result = store.get_user_sessions("user_id")

        assert result == expected_data

    def test_update_status_returns_true_on_success(self, store):
        """update_status() should return True on success."""
        store._client.table.return_value.update.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=[{"id": "session_id"}]
        )

        result = store.update_status("session_id", {"status": "completed"})

        assert result is True

    def test_delete_returns_true_on_success(self, store):
        """delete() should return True on success."""
        store._client.table.return_value.delete.return_value.eq.return_value.execute.return_value = MockExecuteResult(
            data=[{"id": "session_id"}]
        )

        result = store.delete("session_id")

        assert result is True

    def test_count_active_returns_count_on_success(self, store):
        """count_active() should return count on success."""
        store._client.table.return_value.select.return_value.in_.return_value.execute.return_value = MockExecuteResult(
            data=[], count=5
        )

        result = store.count_active()

        assert result == 5

    def test_verify_ownership_returns_true_when_session_exists(self, store):
        """verify_ownership() should return True when session exists."""
        store._client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MockExecuteResult(
            data={"id": "session_id"}
        )

        result = store.verify_ownership("session_id", "user_id")

        assert result is True

    def test_verify_ownership_returns_false_when_session_not_found(self, store):
        """verify_ownership() should return False when session doesn't exist."""
        store._client.table.return_value.select.return_value.eq.return_value.eq.return_value.maybe_single.return_value.execute.return_value = MockExecuteResult(
            data=None
        )

        result = store.verify_ownership("session_id", "user_id")

        assert result is False
