"""Unit tests for LocalProvider authentication."""

from unittest.mock import MagicMock, patch
import pytest


class TestLocalProvider:
    """Tests for LocalProvider authentication."""

    @patch('src.auth.local_auth.get_sqlite_engine')
    def test_login_success(self, mock_get_engine):
        """Test successful login with valid credentials."""
        # Setup mock
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            'user-uuid-123', 'test@example.com', 'password123', 'user'
        )
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        # Import after patching
        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        user_info = provider.login('test@example.com', 'password123')

        assert user_info['authenticated'] is True
        assert user_info['email'] == 'test@example.com'
        assert user_info['role'] == 'user'
        assert user_info['id'] == 'user-uuid-123'

    @patch('src.auth.local_auth.get_sqlite_engine')
    def test_login_invalid_email(self, mock_get_engine):
        """Test login with non-existent email."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        with pytest.raises(ValueError, match="Invalid email or password"):
            provider.login('nonexistent@example.com', 'password123')

    @patch('src.auth.local_auth.get_sqlite_engine')
    def test_login_invalid_password(self, mock_get_engine):
        """Test login with wrong password."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (
            'user-uuid-123', 'test@example.com', 'correctpassword', 'user'
        )
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        with pytest.raises(ValueError, match="Invalid email or password"):
            provider.login('test@example.com', 'wrongpassword')

    @patch('src.auth.local_auth.get_sqlite_engine')
    def test_get_user_role_success(self, mock_get_engine):
        """Test fetching user role successfully."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ('admin',)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        role = provider.get_user_role('user-uuid-admin')
        assert role == 'admin'

    @patch('src.auth.local_auth.get_sqlite_engine')
    def test_get_user_role_default(self, mock_get_engine):
        """Test default role when user not found."""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        role = provider.get_user_role('user-uuid-unknown')
        assert role == 'user'

    def test_refresh_session_not_implemented(self):
        """Test that refresh_session raises NotImplementedError."""
        from src.auth.local_auth import LocalProvider
        provider = LocalProvider()
        with pytest.raises(NotImplementedError, match="Session refresh not supported"):
            provider.refresh_session("some_refresh_token")
