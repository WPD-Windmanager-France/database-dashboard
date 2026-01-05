"""Tests for authentication module"""

from config import settings


def test_email_validation():
    """Test email domain validation"""
    from auth import ALLOWED_EMAIL_DOMAIN, validate_email_domain

    # Valid emails
    is_valid, _ = validate_email_domain(f"test@{ALLOWED_EMAIL_DOMAIN}")
    assert is_valid is True

    is_valid, _ = validate_email_domain(f"john.doe@{ALLOWED_EMAIL_DOMAIN}")
    assert is_valid is True

    # Invalid domain
    is_valid, msg = validate_email_domain("test@gmail.com")
    assert is_valid is False
    assert ALLOWED_EMAIL_DOMAIN in msg

    is_valid, msg = validate_email_domain("user@example.com")
    assert is_valid is False

    # Invalid format
    is_valid, msg = validate_email_domain("not-an-email")
    assert is_valid is False
    assert "invalid" in msg.lower()

    is_valid, msg = validate_email_domain("missing-at-sign.com")
    assert is_valid is False

    is_valid, msg = validate_email_domain("@wpd.fr")
    assert is_valid is False


def test_role_hierarchy():
    """Test role checking logic"""
    import streamlit as st

    from auth import check_role

    # Mock session state for admin
    st.session_state['user_role'] = 'admin'
    assert check_role('viewer') is True
    assert check_role('user') is True
    assert check_role('admin') is True

    # Mock session state for user
    st.session_state['user_role'] = 'user'
    assert check_role('viewer') is True
    assert check_role('user') is True
    assert check_role('admin') is False

    # Mock session state for viewer
    st.session_state['user_role'] = 'viewer'
    assert check_role('viewer') is True
    assert check_role('user') is False
    assert check_role('admin') is False


def test_session_initialization():
    """Test session state initialization"""
    import streamlit as st

    from auth import SESSION_KEYS, clear_session_state, init_session_state

    # Clear any existing state
    for key in SESSION_KEYS.keys():
        if key in st.session_state:
            del st.session_state[key]

    # Initialize
    init_session_state()

    # Check all keys are initialized
    for key, default_value in SESSION_KEYS.items():
        assert key in st.session_state
        assert st.session_state[key] == default_value

    # Test clear
    st.session_state['authenticated'] = True
    st.session_state['user'] = {'id': '123', 'email': 'test@wpd.fr'}

    clear_session_state()

    # Verify cleared back to defaults
    assert st.session_state['authenticated'] is False
    assert st.session_state['user'] is None


def test_sqlite_mode_detection():
    """Test that auth module correctly detects SQLite mode"""
    if settings.db_type == "sqlite":
        from auth import get_user_role_sqlite, login_user_sqlite

        # These functions should exist in SQLite mode
        assert callable(login_user_sqlite)
        assert callable(get_user_role_sqlite)

        print("SQLite mode detected correctly")


def test_supabase_mode_detection():
    """Test that auth module correctly detects Supabase mode"""
    if settings.db_type == "supabase":
        from auth import get_auth_client

        # These functions should exist in Supabase mode
        assert callable(get_auth_client)

        print("Supabase mode detected correctly")


def test_unified_interface():
    """Test that unified authentication interface exists"""
    from auth import login_user, logout_user, signup_user

    # These functions should always exist regardless of mode
    assert callable(login_user)
    assert callable(logout_user)
    assert callable(signup_user)

    print(f"Unified interface available for {settings.db_type} mode")
