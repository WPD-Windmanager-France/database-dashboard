"""Unit tests for SupabaseProvider authentication."""

from unittest.mock import MagicMock, patch
import pytest


class TestSupabaseProvider:
    """Tests for SupabaseProvider authentication."""

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_login_success(self, mock_init_connection):
        """Test successful login with valid credentials."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.sign_in_with_password.return_value = MagicMock(
            user=MagicMock(id="user-id-123", email="test@wpd.fr"),
            session=MagicMock(access_token="abc", refresh_token="xyz")
        )
        # Mock role fetch
        mock_execute = MagicMock()
        mock_execute.data = [{"role": "user"}]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute

        from src.auth.supabase_auth import SupabaseProvider
        # Reset singleton
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()
        user_info = provider.login("test@wpd.fr", "password")

        assert user_info['authenticated'] is True
        assert user_info['email'] == "test@wpd.fr"
        assert user_info['role'] == "user"
        assert user_info['access_token'] == "abc"
        assert user_info['refresh_token'] == "xyz"

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_login_invalid_credentials(self, mock_init_connection):
        """Test login with invalid credentials."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()

        with pytest.raises(ValueError, match="Invalid email or password"):
            provider.login("invalid@wpd.fr", "wrongpass")

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_logout(self, mock_init_connection):
        """Test logout functionality."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()
        provider.logout()

        mock_client.auth.sign_out.assert_called_once()

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_refresh_session_success(self, mock_init_connection):
        """Test successful session refresh."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.refresh_session.return_value = MagicMock(
            user=MagicMock(id="user-id-123", email="test@wpd.fr"),
            session=MagicMock(access_token="new_abc", refresh_token="new_xyz")
        )
        # Mock role fetch
        mock_execute = MagicMock()
        mock_execute.data = [{"role": "admin"}]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()
        user_info = provider.refresh_session("old_refresh_token")

        assert user_info['authenticated'] is True
        assert user_info['access_token'] == "new_abc"
        assert user_info['refresh_token'] == "new_xyz"
        assert user_info['role'] == "admin"

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_refresh_session_failure(self, mock_init_connection):
        """Test session refresh failure."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.refresh_session.side_effect = Exception("Refresh failed")

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()

        with pytest.raises(ValueError, match="Supabase Refresh Session Error"):
            provider.refresh_session("invalid_refresh_token")

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_get_user_role(self, mock_init_connection):
        """Test fetching user role."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_execute = MagicMock()
        mock_execute.data = [{"role": "viewer"}]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()
        role = provider.get_user_role("user-id-viewer")

        assert role == "viewer"

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_signup_success(self, mock_init_connection):
        """Test successful signup."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.sign_up.return_value = MagicMock(
            user=MagicMock(id="new-user-id", email="newuser@wpd.fr")
        )

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()
        user_info = provider.signup("newuser@wpd.fr", "newpassword")

        assert user_info['id'] == "new-user-id"
        assert user_info['email'] == "newuser@wpd.fr"
        assert user_info['role'] == "user"
        assert user_info['authenticated'] is False

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_signup_invalid_domain(self, mock_init_connection):
        """Test signup with invalid email domain."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()

        with pytest.raises(ValueError, match="Only @wpd.fr emails are allowed"):
            provider.signup("newuser@gmail.com", "newpassword")

    @patch('src.auth.supabase_auth.init_supabase_connection')
    def test_signup_user_exists(self, mock_init_connection):
        """Test signup with already registered email."""
        mock_client = MagicMock()
        mock_init_connection.return_value = mock_client
        mock_client.auth.sign_up.side_effect = Exception("User already registered")

        from src.auth.supabase_auth import SupabaseProvider
        SupabaseProvider._supabase_client = None
        provider = SupabaseProvider()

        with pytest.raises(ValueError, match="This email is already registered"):
            provider.signup("existing@wpd.fr", "password")
