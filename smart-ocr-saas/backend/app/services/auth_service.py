"""
Authentication service.
"""
from typing import Optional
from datetime import timedelta

from app.core.security import verify_password, create_access_token
from app.config import settings


class AuthService:
    """Service for handling authentication."""

    async def authenticate_local(
        self, username: str, password: str
    ) -> Optional[dict]:
        """
        Authenticate user with local credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            User dict if authentication successful, None otherwise
        """
        # TODO: Implement with actual database
        # This is a placeholder implementation
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        user = await user_repo.find_by_username(username)

        if not user:
            return None

        if user.get("auth_type") != "local":
            return None

        if not user.get("is_active"):
            return None

        if not verify_password(password, user.get("password_hash", "")):
            return None

        # Update last login
        await user_repo.update_last_login(user["_id"])

        return user

    async def authenticate_ldap(
        self, username: str, password: str
    ) -> Optional[dict]:
        """
        Authenticate user with LDAP/AD credentials.

        Args:
            username: User's username
            password: User's password

        Returns:
            User dict if authentication successful, None otherwise
        """
        if not settings.LDAP_ENABLED:
            return None

        from app.services.ldap_service import LDAPService

        ldap_service = LDAPService()

        try:
            ldap_user = await ldap_service.authenticate(username, password)

            if not ldap_user:
                return None

            # Sync user to local database
            from app.repositories.user_repository import UserRepository

            user_repo = UserRepository()
            user = await user_repo.sync_ldap_user(ldap_user)

            return user

        except Exception:
            # LDAP connection failed, try fallback to cached local auth
            return await self._ldap_fallback(username, password)

    async def _ldap_fallback(
        self, username: str, password: str
    ) -> Optional[dict]:
        """
        Fallback authentication when LDAP is unavailable.
        Uses cached credentials for existing LDAP users.
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        user = await user_repo.find_by_username(username)

        if not user:
            return None

        # Only allow fallback for LDAP users who have logged in before
        if user.get("auth_type") != "ldap":
            return None

        if not user.get("is_active"):
            return None

        # Check cached password (if we store one for fallback)
        cached_hash = user.get("cached_password_hash")
        if cached_hash and verify_password(password, cached_hash):
            return user

        return None

    def create_access_token(self, user: dict) -> str:
        """
        Create JWT access token for user.

        Args:
            user: User dict

        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.get("_id")),
            "username": user.get("username"),
            "role": user.get("role", "user"),
            "auth_type": user.get("auth_type", "local"),
        }

        return create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        )
