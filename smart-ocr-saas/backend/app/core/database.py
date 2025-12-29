"""
Database connection management.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

# Global database client
_client: AsyncIOMotorClient = None
_database: AsyncIOMotorDatabase = None


def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance.

    Returns:
        AsyncIOMotorDatabase instance
    """
    global _client, _database

    if _database is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _database = _client[settings.MONGODB_DB_NAME]

    return _database


async def close_database():
    """Close database connection."""
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None


async def init_database():
    """
    Initialize database with indexes.
    """
    db = get_database()

    # Users collection indexes
    await db.users.create_index("username", unique=True)
    await db.users.create_index([("auth_type", 1), ("is_active", 1)])

    # OCR Tasks collection indexes
    await db.ocr_tasks.create_index([("user_id", 1), ("created_at", -1)])
    await db.ocr_tasks.create_index("status")

    # OCR Results collection indexes
    await db.ocr_results.create_index([("task_id", 1), ("page_number", 1)])
    await db.ocr_results.create_index([("user_id", 1), ("created_at", -1)])

    print("Database indexes created successfully")
