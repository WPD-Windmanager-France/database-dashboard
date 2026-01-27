"""Authentication module for Supabase and SQLite integration"""

import re
from typing import Optional, Tuple

import streamlit as st

from config import settings

# Imports conditionnels selon l'environnement
if settings.db_type == "supabase":
    from supabase import Client

    from database import init_supabase_connection
elif settings.db_type == "sqlite":
    from sqlalchemy import text

    from database import get_sqlite_engine


# ==================== Constants ====================

ALLOWED_EMAIL_DOMAIN = "wpd.fr"
SESSION_KEYS = {
    'authenticated': False,
    'user': None,
    'access_token': None,
    'refresh_token': None,
    'user_role': None,
}


# ==================== Session Management ====================

def init_session_state():
    """Initialize session state variables for authentication"""
    for key, default_value in SESSION_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def clear_session_state():
    """Clear all authentication session state"""
    for key, default_value in SESSION_KEYS.items():
        st.session_state[key] = default_value


def get_auth_client() -> Optional["Client"]:
    """Get Supabase client for authentication operations"""
    if settings.db_type == "supabase":
        return init_supabase_connection()
    return None


# ==================== Email Validation ====================

def validate_email_domain(email: str) -> Tuple[bool, str]:
    """
    Validate that email belongs to allowed domain

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    email = email.strip().lower()

    # Basic email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return False, "Invalid email format"

    # Extract domain
    domain = email.split('@')[1]

    # Check if domain is allowed
    if domain != ALLOWED_EMAIL_DOMAIN:
        return False, f"Only @{ALLOWED_EMAIL_DOMAIN} emails are allowed"

    return True, ""


# ==================== SQLite Authentication ====================

def login_user_sqlite(email: str, password: str) -> Tuple[bool, str]:
    """
    Log in user with SQLite (development mode)

    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        engine = get_sqlite_engine()

        with engine.connect() as conn:
            query = text("""
                SELECT id, email, password, role
                FROM profiles
                WHERE email = :email
            """)
            result = conn.execute(query, {"email": email})
            user_data = result.fetchone()

            if not user_data:
                return False, "Invalid email or password"

            # Compare passwords (plain text in dev mode)
            if user_data[2] != password:
                return False, "Invalid email or password"

            # Store session data
            st.session_state['authenticated'] = True
            st.session_state['user'] = {
                'id': user_data[0],
                'email': user_data[1],
            }
            st.session_state['user_role'] = user_data[3]

            return True, "Login successful!"

    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_user_role_sqlite(email: str) -> str:
    """
    Fetch user role from SQLite profiles table

    Returns:
        str: User role or 'user' as default
    """
    try:
        engine = get_sqlite_engine()

        with engine.connect() as conn:
            query = text("SELECT role FROM profiles WHERE email = :email")
            result = conn.execute(query, {"email": email})
            role_data = result.fetchone()

            if role_data:
                return role_data[0]
            else:
                return 'user'

    except Exception:
        return 'user'


# ==================== Supabase Authentication ====================

def signup_user_supabase(email: str, password: str) -> Tuple[bool, str]:
    """
    Sign up a new user with Supabase

    Returns:
        Tuple[bool, str]: (success, message)
    """
    # Validate email domain BEFORE calling Supabase
    is_valid, error_msg = validate_email_domain(email)
    if not is_valid:
        return False, error_msg

    client = get_auth_client()
    if not client:
        return False, "Supabase not configured"

    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
        })

        if response.user:
            return True, "Account created successfully! Check your email to confirm your account."
        else:
            return False, "Error creating account"

    except Exception as e:
        error_message = str(e)

        # Parse common Supabase errors
        if "User already registered" in error_message:
            return False, "This email is already registered"
        elif "Password should be" in error_message:
            return False, "Password must be at least 6 characters"
        elif "Invalid email" in error_message:
            return False, "Invalid email format"
        else:
            return False, f"Error: {error_message}"


def login_user_supabase(email: str, password: str) -> Tuple[bool, str]:
    """
    Log in an existing user with Supabase

    Returns:
        Tuple[bool, str]: (success, message)
    """
    client = get_auth_client()
    if not client:
        return False, "Supabase not configured"

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        if response.user and response.session:
            # Store session data
            st.session_state['authenticated'] = True
            st.session_state['user'] = {
                'id': response.user.id,
                'email': response.user.email,
            }
            st.session_state['access_token'] = response.session.access_token
            st.session_state['refresh_token'] = response.session.refresh_token

            # Fetch user role from profiles table
            role = get_user_role_supabase(response.user.id)
            st.session_state['user_role'] = role

            return True, "Login successful!"
        else:
            return False, "Connection error"

    except Exception as e:
        error_message = str(e)

        # Parse common Supabase errors
        if "Invalid login credentials" in error_message:
            return False, "Invalid email or password"
        elif "Email not confirmed" in error_message:
            return False, "Please confirm your email before logging in"
        else:
            return False, f"Error: {error_message}"


@st.cache_data(ttl=300)
def get_user_role_supabase(user_id: str) -> str:
    """
    Fetch user role from Supabase profiles table

    Returns:
        str: User role ('admin', 'user', 'viewer') or 'user' as default
    """
    client = get_auth_client()
    if not client:
        return 'user'

    try:
        response = client.table('profiles').select('role').eq('id', user_id).execute()

        if response.data and len(response.data) > 0:
            data = response.data[0]
            if isinstance(data, dict):
                return str(data.get('role', 'user'))

        return 'user'

    except Exception:
        return 'user'


def refresh_session() -> bool:
    """
    Refresh user session if expired (Supabase only)

    Returns:
        bool: True if session is valid/refreshed, False otherwise
    """
    if settings.db_type != "supabase":
        return True  # SQLite doesn't use session refresh

    if not st.session_state.get('refresh_token'):
        return False

    client = get_auth_client()
    if not client:
        return False

    try:
        response = client.auth.refresh_session(
            st.session_state['refresh_token']
        )

        if response.session:
            st.session_state['access_token'] = response.session.access_token
            st.session_state['refresh_token'] = response.session.refresh_token
            return True
        else:
            clear_session_state()
            return False

    except Exception:
        clear_session_state()
        return False


# ==================== Unified Authentication Interface ====================

def signup_user(email: str, password: str) -> Tuple[bool, str]:
    """
    Sign up a new user (unified interface)

    Returns:
        Tuple[bool, str]: (success, message)
    """
    if settings.db_type == "supabase":
        return signup_user_supabase(email, password)
    else:
        # SQLite mode - signup not supported
        return False, f"Development mode: use test@{ALLOWED_EMAIL_DOMAIN} to login"


def login_user(email: str, password: str) -> Tuple[bool, str]:
    """
    Log in an existing user (unified interface)

    Returns:
        Tuple[bool, str]: (success, message)
    """
    if settings.db_type == "supabase":
        return login_user_supabase(email, password)
    else:
        return login_user_sqlite(email, password)


def logout_user():
    """Log out current user"""
    if settings.db_type == "supabase":
        client = get_auth_client()

        if client and st.session_state.get('access_token'):
            try:
                client.auth.sign_out()
            except Exception:
                pass  # Silent fail on logout

    clear_session_state()


# ==================== Role Management ====================

def check_role(required_role: str) -> bool:
    """
    Check if current user has required role

    Role hierarchy: admin > user > viewer

    Args:
        required_role: Minimum required role

    Returns:
        bool: True if user has sufficient permissions
    """
    role_hierarchy = {'viewer': 1, 'user': 2, 'admin': 3}

    user_role = st.session_state.get('user_role', 'viewer')

    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 999)

    return user_level >= required_level


# ==================== UI Components ====================

def require_authentication():
    """
    Decorator-style function to protect app content
    Shows login/signup UI if user is not authenticated

    Returns:
        bool: True if authenticated, False otherwise
    """
    init_session_state()

    # Check if session needs refresh (Supabase only)
    if settings.db_type == "supabase":
        if st.session_state.get('authenticated') and st.session_state.get('refresh_token'):
            refresh_session()

    if not st.session_state.get('authenticated'):
        show_auth_ui()
        return False

    return True


def show_auth_ui():
    """Display login/signup UI"""
    st.title("Windmanager France Database")

    # Show environment info
    env_label = "Production (Supabase)" if settings.db_type == "supabase" else "Development (SQLite)"
    st.caption(f"Environment: {env_label}")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        show_login_form()

    with tab2:
        show_signup_form()


def show_login_form():
    """Display login form"""
    st.subheader("Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder=f"your.name@{ALLOWED_EMAIL_DOMAIN}")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                success, message = login_user(email, password)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def show_signup_form():
    """Display signup form"""
    st.subheader("Create an Account")

    # Show different messages based on environment
    if settings.db_type == "sqlite":
        st.info(f"Development mode: use test credentials (test@{ALLOWED_EMAIL_DOMAIN} / password123)")
    else:
        st.info(f"Only @{ALLOWED_EMAIL_DOMAIN} emails are allowed")

    with st.form("signup_form"):
        email = st.text_input("E-mail", placeholder=f"your.name@{ALLOWED_EMAIL_DOMAIN}")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Sign Up", use_container_width=True)

        if submitted:
            if not email or not password or not password_confirm:
                st.error("Please fill in all fields")
            elif password != password_confirm:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = signup_user(email, password)

                if success:
                    st.success(message)
                else:
                    st.error(message)


def show_user_info():
    """Display logged-in user info in sidebar (compact version)"""
    if st.session_state.get('authenticated'):
        with st.sidebar:
            user = st.session_state.get('user', {})
            role = st.session_state.get('user_role', 'user')
            email = user.get('email', 'User')

            # Compact expander for user info
            with st.expander(email, expanded=False):
                st.caption(f"**Role:** {role.upper()}")
                if st.button("Logout", use_container_width=True, key="logout_btn"):
                    logout_user()
                    st.rerun()

            st.divider()
