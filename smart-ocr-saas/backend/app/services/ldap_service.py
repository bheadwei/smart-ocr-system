"""
LDAP/Active Directory authentication service.
Uses ldap3 library (pure Python, cross-platform).
"""
from typing import Optional, Dict, Any

from app.config import settings
from app.core.exceptions import LDAPConnectionError


class LDAPService:
    """Service for LDAP/AD authentication."""

    def __init__(self):
        """Initialize LDAP service."""
        self.server_url = settings.LDAP_SERVER_URL
        self.use_ssl = settings.LDAP_USE_SSL
        self.base_dn = settings.LDAP_BASE_DN
        self.bind_dn = settings.LDAP_BIND_DN
        self.bind_password = settings.LDAP_BIND_PASSWORD
        self.user_search_filter = settings.LDAP_USER_SEARCH_FILTER
        self.username_attr = settings.LDAP_USERNAME_ATTRIBUTE
        self.display_name_attr = settings.LDAP_DISPLAY_NAME_ATTRIBUTE
        self.email_attr = settings.LDAP_EMAIL_ATTRIBUTE

    async def authenticate(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user against LDAP/AD.

        Args:
            username: User's username
            password: User's password

        Returns:
            User info dict if successful, None otherwise

        Raises:
            LDAPConnectionError: If LDAP server is unreachable
        """
        try:
            from ldap3 import Server, Connection, ALL, SUBTREE
            from ldap3.core.exceptions import LDAPBindError, LDAPSocketOpenError

            # Parse server URL
            server_host = self.server_url.replace("ldap://", "").replace("ldaps://", "")
            use_ssl = self.use_ssl or self.server_url.startswith("ldaps://")

            # Initialize server
            server = Server(server_host, use_ssl=use_ssl, get_info=ALL)

            # Bind with service account to search for user
            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
            )

            # Search for user
            search_filter = self.user_search_filter.format(username=username)
            conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=[self.username_attr, self.display_name_attr, self.email_attr],
            )

            if not conn.entries:
                conn.unbind()
                return None

            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn
            conn.unbind()

            # Try to bind as the user to verify password
            try:
                user_conn = Connection(
                    server,
                    user=user_dn,
                    password=password,
                    auto_bind=True,
                )
                user_conn.unbind()
            except LDAPBindError:
                return None

            # Extract user info
            def get_attr(entry, attr_name: str) -> Optional[str]:
                try:
                    value = getattr(entry, attr_name, None)
                    if value:
                        return str(value)
                except Exception:
                    pass
                return None

            return {
                "ldap_dn": user_dn,
                "username": get_attr(user_entry, self.username_attr) or username,
                "display_name": get_attr(user_entry, self.display_name_attr) or username,
                "email": get_attr(user_entry, self.email_attr),
            }

        except LDAPSocketOpenError:
            raise LDAPConnectionError("LDAP 伺服器無法連線")
        except Exception as e:
            raise LDAPConnectionError(f"LDAP 錯誤: {str(e)}")

    async def test_connection(self) -> bool:
        """
        Test LDAP server connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            from ldap3 import Server, Connection, ALL

            server_host = self.server_url.replace("ldap://", "").replace("ldaps://", "")
            use_ssl = self.use_ssl or self.server_url.startswith("ldaps://")

            server = Server(server_host, use_ssl=use_ssl, get_info=ALL, connect_timeout=5)

            conn = Connection(
                server,
                user=self.bind_dn,
                password=self.bind_password,
                auto_bind=True,
            )
            conn.unbind()

            return True

        except Exception:
            return False
