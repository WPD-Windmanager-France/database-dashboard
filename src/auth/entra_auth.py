from typing import Dict, Any, Optional

from src.auth.provider import AuthProvider

class EntraIDProvider(AuthProvider):
    """
    Microsoft Entra ID authentication provider (DEFERRED).
    Currently a placeholder.
    """

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Entra ID login is not implemented in this MVP.
        """
        raise NotImplementedError("Microsoft Entra ID login is deferred for a future story.")

    def logout(self, user_id: Optional[str] = None):
        """
        Entra ID logout is not implemented in this MVP.
        """
        raise NotImplementedError("Microsoft Entra ID logout is deferred for a future story.")

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Entra ID session refresh is not implemented in this MVP.
        """
        raise NotImplementedError("Microsoft Entra ID session refresh is deferred for a future story.")

    def get_user_role(self, user_id: str) -> str:
        """
        Entra ID get user role is not implemented in this MVP.
        """
        raise NotImplementedError("Microsoft Entra ID get user role is deferred for a future story.")
