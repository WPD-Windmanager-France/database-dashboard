from typing import Dict, Any, Optional
from sqlalchemy import text

from src.auth.provider import AuthProvider
from src.data.sqlite_db import get_sqlite_engine # Assuming this path after Story 1.3

class LocalProvider(AuthProvider):
    """
    Local authentication provider using SQLite (development mode).
    Implements the AuthProvider interface.
    """

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticates a user with email and password against the SQLite database.

        Returns:
            A dictionary containing user information (id, email, role, access_token=None)
            or raises a ValueError on failure.
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
                    raise ValueError("Invalid email or password")

                # Compare passwords (plain text in dev mode)
                if user_data[2] != password:
                    raise ValueError("Invalid email or password")

                return {
                    'id': user_data[0],
                    'email': user_data[1],
                    'role': user_data[3],
                    'access_token': None, # No access token for local auth
                    'refresh_token': None, # No refresh token for local auth
                    'authenticated': True
                }

        except Exception as e:
            raise ValueError(f"Login error: {str(e)}")

    def logout(self, user_id: Optional[str] = None):
        """
        Logs out a user. For local provider, this is a no-op as session is managed externally.
        """
        pass

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh session is not applicable for local SQLite provider.
        """
        raise NotImplementedError("Session refresh not supported for LocalProvider")

    def get_user_role(self, user_id: str) -> str:
        """
        Fetch user role from SQLite profiles table.
        """
        try:
            engine = get_sqlite_engine()

            with engine.connect() as conn:
                query = text("SELECT role FROM profiles WHERE id = :user_id")
                result = conn.execute(query, {"user_id": user_id})
                role_data = result.fetchone()

                if role_data:
                    return role_data[0]
                else:
                    return 'user' # Default role

        except Exception:
            return 'user' # Default role on error
