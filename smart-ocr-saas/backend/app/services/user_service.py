"""
User management service.
"""
from typing import Optional, List

from app.core.security import get_password_hash
from app.models.user import UserCreate, UserUpdate


class UserService:
    """Service for user management."""

    async def list_users(self, skip: int = 0, limit: int = 20) -> List[dict]:
        """
        List all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of user dicts
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        return await user_repo.find_all(skip=skip, limit=limit)

    async def count_users(self) -> int:
        """
        Count total users.

        Returns:
            Total user count
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        return await user_repo.count()

    async def get_by_username(self, username: str) -> Optional[dict]:
        """
        Get user by username.

        Args:
            username: User's username

        Returns:
            User dict if found, None otherwise
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        return await user_repo.find_by_username(username)

    async def create_user(self, user_data: UserCreate) -> dict:
        """
        Create a new local user.

        Args:
            user_data: User creation data

        Returns:
            Created user dict
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()

        user_dict = {
            "username": user_data.username,
            "password_hash": get_password_hash(user_data.password),
            "display_name": user_data.display_name,
            "email": user_data.email,
            "auth_type": "local",
            "role": user_data.role,
            "is_active": True,
        }

        return await user_repo.create(user_dict)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[dict]:
        """
        Update user data.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user dict if found, None otherwise
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()

        update_dict = {}

        if user_data.display_name is not None:
            update_dict["display_name"] = user_data.display_name

        if user_data.email is not None:
            update_dict["email"] = user_data.email

        if user_data.role is not None:
            update_dict["role"] = user_data.role

        if user_data.is_active is not None:
            update_dict["is_active"] = user_data.is_active

        if user_data.password is not None:
            update_dict["password_hash"] = get_password_hash(user_data.password)

        if not update_dict:
            return await user_repo.find_by_id(user_id)

        return await user_repo.update(user_id, update_dict)

    async def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user.

        Args:
            user_id: User ID

        Returns:
            True if successful, False if user not found
        """
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository()
        result = await user_repo.update(user_id, {"is_active": False})
        return result is not None
