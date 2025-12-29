"""
User repository for MongoDB operations.
"""
from typing import Optional, List
from datetime import datetime

from bson import ObjectId


class UserRepository:
    """Repository for user data access."""

    def __init__(self):
        """Initialize repository with database connection."""
        self._db = None

    def _get_collection(self):
        """Get users collection."""
        if self._db is None:
            from app.core.database import get_database
            self._db = get_database()
        return self._db.users

    async def find_by_id(self, user_id: str) -> Optional[dict]:
        """Find user by ID."""
        collection = self._get_collection()
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["id"] = str(user["_id"])
        return user

    async def find_by_username(self, username: str) -> Optional[dict]:
        """Find user by username."""
        collection = self._get_collection()
        user = await collection.find_one({"username": username})
        if user:
            user["id"] = str(user["_id"])
        return user

    async def find_all(self, skip: int = 0, limit: int = 20) -> List[dict]:
        """Find all users with pagination."""
        collection = self._get_collection()
        cursor = collection.find().skip(skip).limit(limit).sort("created_at", -1)
        users = []
        async for user in cursor:
            user["id"] = str(user["_id"])
            users.append(user)
        return users

    async def count(self) -> int:
        """Count total users."""
        collection = self._get_collection()
        return await collection.count_documents({})

    async def create(self, user_data: dict) -> dict:
        """Create new user."""
        collection = self._get_collection()
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        user_data["last_login"] = None

        result = await collection.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        user_data["id"] = str(result.inserted_id)
        return user_data

    async def update(self, user_id: str, update_data: dict) -> Optional[dict]:
        """Update user data."""
        collection = self._get_collection()
        update_data["updated_at"] = datetime.utcnow()

        result = await collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            result["id"] = str(result["_id"])
        return result

    async def update_last_login(self, user_id) -> None:
        """Update user's last login timestamp."""
        collection = self._get_collection()
        await collection.update_one(
            {"_id": ObjectId(user_id) if isinstance(user_id, str) else user_id},
            {"$set": {"last_login": datetime.utcnow()}},
        )

    async def sync_ldap_user(self, ldap_user: dict) -> dict:
        """
        Sync LDAP user to local database.
        Creates new user if not exists, updates if exists.
        """
        collection = self._get_collection()

        existing = await collection.find_one({"ldap_dn": ldap_user["ldap_dn"]})

        if existing:
            # Update existing user
            await collection.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "display_name": ldap_user.get("display_name"),
                        "email": ldap_user.get("email"),
                        "updated_at": datetime.utcnow(),
                        "last_login": datetime.utcnow(),
                    }
                },
            )
            existing["id"] = str(existing["_id"])
            return existing
        else:
            # Create new LDAP user
            new_user = {
                "username": ldap_user["username"],
                "password_hash": None,
                "display_name": ldap_user.get("display_name", ldap_user["username"]),
                "email": ldap_user.get("email"),
                "auth_type": "ldap",
                "ldap_dn": ldap_user["ldap_dn"],
                "role": "user",
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
            }
            return await self.create(new_user)
