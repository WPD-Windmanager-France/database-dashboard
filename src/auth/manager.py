from typing import Dict, Any, Optional

from config import settings
from src.auth.provider import AuthProvider
from src.auth.local_auth import LocalProvider
from src.auth.supabase_auth import SupabaseProvider
from src.auth.entra_auth import EntraIDProvider # Placeholder

class AuthManager:
    """
    Manages authentication providers and provides a unified interface.
    """

    _instance = None
    _provider: AuthProvider
    _user_session: Dict[str, Any] = {} # Taipy state will manage actual session

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance._initialize_provider()
        return cls._instance

    def _initialize_provider(self):
        auth_type = settings.get('AUTH_TYPE', 'local').lower()
        if auth_type == 'local':
            self._provider = LocalProvider()
        elif auth_type == 'supabase':
            self._provider = SupabaseProvider()
        elif auth_type == 'entra':
            self._provider = EntraIDProvider()
        else:
            raise ValueError(f"Unsupported authentication type: {auth_type}")

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Logs in a user using the configured provider.
        Returns user info on success, raises ValueError on failure.
        """
        user_info = self._provider.login(email, password)
        self._user_session = user_info # Update internal session state
        return user_info

    def logout(self, user_id: Optional[str] = None):
        """
        Logs out the current user.
        """
        self._provider.logout(user_id)
        self._user_session = {} # Clear internal session state

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refreshes the user session.
        """
        user_info = self._provider.refresh_session(refresh_token)
        self._user_session = user_info
        return user_info

    def get_user_role(self, user_id: str) -> str:
        """
        Retrieves the role of a user.
        """
        return self._provider.get_user_role(user_id)

    def get_current_user(self) -> Dict[str, Any]:
        """
        Returns the current user session information.
        """
        return self._user_session

    def is_authenticated(self) -> bool:
        """
        Checks if a user is currently authenticated.
        """
        return self._user_session.get('authenticated', False)

    def check_role(self, required_role: str) -> bool:
        """
        Check if current user has required role based on a hierarchy.
        Ported from original auth.py.
        """
        role_hierarchy = {'viewer': 1, 'user': 2, 'admin': 3}
        user_role = self._user_session.get('role', 'viewer')

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 999)

        return user_level >= required_level

# Global instance of AuthManager
auth_manager = AuthManager()
