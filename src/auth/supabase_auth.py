from typing import Dict, Any, Optional
from supabase import Client

from src.auth.provider import AuthProvider
from src.data.supabase_db import init_supabase_connection # Assuming this path after Story 1.3
from config import settings # For ALLOWED_EMAIL_DOMAIN, Supabase URL/KEY

class SupabaseProvider(AuthProvider):
    """
    Supabase authentication provider.
    Implements the AuthProvider interface.
    """

    _supabase_client: Optional[Client] = None

    def __init__(self):
        if not SupabaseProvider._supabase_client:
            SupabaseProvider._supabase_client = init_supabase_connection()

    def _get_client(self) -> Client:
        if not self._supabase_client:
            raise ConnectionError("Supabase client not initialized.")
        return self._supabase_client

    def _validate_email_domain(self, email: str) -> bool:
        """
        Validate that email belongs to allowed domain.
        Ported from original auth.py.
        """
        # In a real app, ALLOWED_EMAIL_DOMAIN should come from settings
        allowed_domain = "wpd.fr" # settings.get('ALLOWED_EMAIL_DOMAIN', 'wpd.fr')
        return email.strip().lower().endswith(f"@{allowed_domain}")


    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Log in an existing user with Supabase.

        Returns:
            A dictionary containing user information (id, email, role, access_token, refresh_token)
            or raises a ValueError on failure.
        """
        client = self._get_client()

        try:
            response = client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

            if response.user and response.session:
                user_id = response.user.id
                # Fetch user role from profiles table
                role = self.get_user_role(user_id)

                return {
                    'id': user_id,
                    'email': response.user.email,
                    'role': role,
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'authenticated': True
                }
            else:
                raise ValueError("Connection error during login.")

        except Exception as e:
            error_message = str(e)
            if "Invalid login credentials" in error_message:
                raise ValueError("Invalid email or password")
            elif "Email not confirmed" in error_message:
                raise ValueError("Please confirm your email before logging in")
            else:
                raise ValueError(f"Supabase Login Error: {error_message}")

    def logout(self, user_id: Optional[str] = None):
        """
        Log out current user from Supabase.
        """
        client = self._get_client()
        try:
            client.auth.sign_out()
        except Exception:
            # Silent fail on logout, similar to original behavior
            pass

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session if expired (Supabase only).

        Returns:
            A dictionary containing new session information or raises ValueError.
        """
        client = self._get_client()
        try:
            response = client.auth.refresh_session(refresh_token)

            if response.session:
                user_id = response.user.id
                role = self.get_user_role(user_id) # Re-fetch role
                return {
                    'id': user_id,
                    'email': response.user.email,
                    'role': role,
                    'access_token': response.session.access_token,
                    'refresh_token': response.session.refresh_token,
                    'authenticated': True
                }
            else:
                raise ValueError("Failed to refresh session.")
        except Exception as e:
            raise ValueError(f"Supabase Refresh Session Error: {str(e)}")

    def get_user_role(self, user_id: str) -> str:
        """
        Fetch user role from Supabase profiles table.
        Removed @st.cache_data as it's Streamlit specific.
        """
        client = self._get_client()
        try:
            response = client.table('profiles').select('role').eq('id', user_id).execute()

            if response.data and len(response.data) > 0:
                data = response.data[0]
                if isinstance(data, dict):
                    return str(data.get('role', 'user'))
            return 'user' # Default role
        except Exception:
            return 'user' # Default role on error

    def signup(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign up a new user with Supabase.

        Returns:
            A dictionary with user info on success, raises ValueError on failure.
        """
        if not self._validate_email_domain(email):
            raise ValueError(f"Only @{settings.ALLOWED_EMAIL_DOMAIN} emails are allowed for sign up.")

        client = self._get_client()
        try:
            response = client.auth.sign_up({
                "email": email,
                "password": password,
            })
            if response.user:
                # Supabase sign up might not immediately return role, handle default
                return {
                    'id': response.user.id,
                    'email': response.user.email,
                    'role': 'user', # Default for new sign-ups
                    'access_token': None, # No session on sign-up until confirmed
                    'refresh_token': None,
                    'authenticated': False # Not authenticated until email confirmed
                }
            else:
                raise ValueError("Error creating account.")
        except Exception as e:
            error_message = str(e)
            if "User already registered" in error_message:
                raise ValueError("This email is already registered")
            elif "Password should be" in error_message:
                raise ValueError("Password must be at least 6 characters")
            elif "Invalid email" in error_message:
                raise ValueError("Invalid email format")
            else:
                raise ValueError(f"Supabase Signup Error: {error_message}")
