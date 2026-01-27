from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AuthProvider(ABC):
    """Abstract Base Class for authentication providers."""

    @abstractmethod
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticates a user with email and password.

        Returns:
            A dictionary containing user information (e.g., id, email, role, access_token)
            or raises an exception on failure.
        """
        pass

    @abstractmethod
    def logout(self, user_id: Optional[str] = None):
        """
        Logs out a user.
        """
        pass

    @abstractmethod
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refreshes an authentication session using a refresh token.

        Returns:
            A dictionary containing new session information.
        """
        pass

    @abstractmethod
    def get_user_role(self, user_id: str) -> str:
        """
        Retrieves the role of a user.

        Returns:
            The user's role (e.g., 'admin', 'user', 'viewer').
        """
        pass
