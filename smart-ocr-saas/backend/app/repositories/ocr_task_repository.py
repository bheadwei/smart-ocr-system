"""
OCR Task repository for MongoDB operations.
"""
from typing import Optional, List
from datetime import datetime

from bson import ObjectId


class OCRTaskRepository:
    """Repository for OCR task data access."""

    def __init__(self):
        """Initialize repository."""
        self._db = None

    def _get_collection(self):
        """Get ocr_tasks collection."""
        if self._db is None:
            from app.core.database import get_database
            self._db = get_database()
        return self._db.ocr_tasks

    async def find_by_id(self, task_id: str) -> Optional[dict]:
        """Find task by ID."""
        collection = self._get_collection()

        # Handle both string ID and ObjectId
        try:
            query = {"_id": ObjectId(task_id)}
        except Exception:
            query = {"_id": task_id}

        task = await collection.find_one(query)
        if task:
            task["id"] = str(task["_id"])
        return task

    async def find_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
    ) -> List[dict]:
        """Find tasks by user with pagination."""
        collection = self._get_collection()

        query = {"user_id": user_id}
        if status_filter:
            query["status"] = status_filter

        cursor = (
            collection.find(query)
            .skip(skip)
            .limit(limit)
            .sort("created_at", -1)
        )

        tasks = []
        async for task in cursor:
            task["id"] = str(task["_id"])
            tasks.append(task)
        return tasks

    async def count_by_user(
        self, user_id: str, status_filter: Optional[str] = None
    ) -> int:
        """Count tasks by user."""
        collection = self._get_collection()

        query = {"user_id": user_id}
        if status_filter:
            query["status"] = status_filter

        return await collection.count_documents(query)

    async def create(self, task_data: dict) -> dict:
        """Create new task."""
        collection = self._get_collection()

        # Use provided _id or generate new one
        if "_id" not in task_data:
            task_data["_id"] = str(ObjectId())

        task_data["created_at"] = task_data.get("created_at", datetime.utcnow())
        task_data["updated_at"] = task_data.get("updated_at", datetime.utcnow())

        await collection.insert_one(task_data)
        task_data["id"] = str(task_data["_id"])
        return task_data

    async def update_status(
        self,
        task_id: str,
        status: str,
        progress: int,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        """Update task status and progress."""
        collection = self._get_collection()

        update_data = {
            "status": status,
            "progress": progress,
            "updated_at": datetime.utcnow(),
        }

        if error_message is not None:
            update_data["error_message"] = error_message

        try:
            query = {"_id": ObjectId(task_id)}
        except Exception:
            query = {"_id": task_id}

        result = await collection.find_one_and_update(
            query,
            {"$set": update_data},
            return_document=True,
        )

        if result:
            result["id"] = str(result["_id"])
        return result

    async def delete(self, task_id: str) -> bool:
        """Delete task."""
        collection = self._get_collection()

        try:
            query = {"_id": ObjectId(task_id)}
        except Exception:
            query = {"_id": task_id}

        result = await collection.delete_one(query)
        return result.deleted_count > 0
