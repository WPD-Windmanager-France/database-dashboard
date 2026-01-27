"""
Unit tests for the database facade (src/database.py).
Tests the Taipy-compatible database layer without Streamlit dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestDatabaseFacade:
    """Tests for the database facade module."""

    def test_import_no_streamlit(self):
        """Verify src/database.py can be imported without Streamlit."""
        # This should not raise ImportError for streamlit
        import src.database as db
        assert db is not None

    def test_get_all_farms_returns_list(self):
        """Test get_all_farms returns a list."""
        from src.database import get_all_farms
        farms = get_all_farms()
        assert isinstance(farms, list)

    def test_get_all_farms_has_expected_fields(self):
        """Test that farms have the expected fields."""
        from src.database import get_all_farms
        farms = get_all_farms()
        if farms:  # Only test if there are farms in the DB
            farm = farms[0]
            assert 'uuid' in farm or 'code' in farm
            assert 'project' in farm or 'code' in farm

    def test_get_farm_by_code(self):
        """Test get_farm_by_code with a known farm."""
        from src.database import get_all_farms, get_farm_by_code
        farms = get_all_farms()
        if farms:
            farm_code = farms[0]['code']
            farm = get_farm_by_code(farm_code)
            assert farm is not None
            assert farm['code'] == farm_code

    def test_get_farm_by_code_not_found(self):
        """Test get_farm_by_code with non-existent code."""
        from src.database import get_farm_by_code
        farm = get_farm_by_code("NONEXISTENT_CODE_12345")
        assert farm is None

    def test_execute_query_basic(self):
        """Test basic execute_query functionality."""
        from src.database import execute_query
        result = execute_query("farms", columns="code, project", order_by="code")
        assert result is not None
        assert isinstance(result, list)

    def test_execute_query_with_filters(self):
        """Test execute_query with filters."""
        from src.database import execute_query, get_all_farms
        farms = get_all_farms()
        if farms:
            farm_code = farms[0]['code']
            result = execute_query("farms", filters={"code": farm_code})
            assert result is not None
            assert len(result) == 1
            assert result[0]['code'] == farm_code

    def test_get_farm_general_info(self):
        """Test get_farm_general_info returns expected structure."""
        from src.database import get_all_farms, get_farm_general_info
        farms = get_all_farms()
        if farms:
            farm_uuid = farms[0]['uuid']
            info = get_farm_general_info(farm_uuid)
            assert isinstance(info, dict)
            assert 'farm' in info
            # These may or may not exist depending on data
            assert 'farm_type' in info or info.get('farm') is None
            assert 'status' in info or info.get('farm') is None
            assert 'location' in info or info.get('farm') is None


class TestStateModule:
    """Tests for the state management module."""

    def test_import_state(self):
        """Verify src/state.py can be imported."""
        from src.state import AppState, get_state, reset_state
        assert AppState is not None
        assert get_state is not None
        assert reset_state is not None

    def test_get_state_singleton(self):
        """Test that get_state returns a singleton."""
        from src.state import get_state
        state1 = get_state()
        state2 = get_state()
        assert state1 is state2

    def test_state_default_values(self):
        """Test default state values."""
        from src.state import AppState
        state = AppState()
        assert state.authenticated is False
        assert state.user_email == ""
        assert state.selected_farm_uuid is None
        assert state.farms_list == []

    def test_state_set_user(self):
        """Test setting user info."""
        from src.state import AppState
        state = AppState()
        state.set_user("test@example.com", "admin")
        assert state.authenticated is True
        assert state.user_email == "test@example.com"
        assert state.user_role == "admin"

    def test_state_logout(self):
        """Test logout clears user info."""
        from src.state import AppState
        state = AppState()
        state.set_user("test@example.com", "admin")
        state.logout()
        assert state.authenticated is False
        assert state.user_email == ""

    def test_state_clear(self):
        """Test clear resets all state."""
        from src.state import AppState
        state = AppState()
        state.set_user("test@example.com", "admin")
        state.selected_farm_uuid = "test-uuid"
        state.clear()
        assert state.authenticated is False
        assert state.selected_farm_uuid is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
