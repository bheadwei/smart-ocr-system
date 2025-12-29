"""
OCR Result repository for MongoDB operations.
"""
from typing import Optional, List
from datetime import datetime

from bson import ObjectId


class OCRResultRepository:
    """Repository for OCR result data access."""

    def __init__(self):
        """Initialize repository."""
        self._db = None

    def _get_collection(self):
        """Get ocr_results collection."""
        if self._db is None:
            from app.core.database import get_database
            self._db = get_database()
        return self._db.ocr_results

    async def find_by_task(self, task_id: str) -> List[dict]:
        """Find all results for a task."""
        collection = self._get_collection()

        cursor = (
            collection.find({"task_id": task_id})
            .sort("page_number", 1)
        )

        results = []
        async for result in cursor:
            result["id"] = str(result["_id"])
            results.append(result)
        return results

    async def create(self, result_data: dict) -> dict:
        """Create new result."""
        collection = self._get_collection()

        result_data["created_at"] = datetime.utcnow()
        result_data["updated_at"] = datetime.utcnow()

        db_result = await collection.insert_one(result_data)
        result_data["_id"] = db_result.inserted_id
        result_data["id"] = str(db_result.inserted_id)
        return result_data

    async def bulk_create(self, task_id: str, results: List[dict]) -> List[dict]:
        """Create multiple results for a task."""
        collection = self._get_collection()

        now = datetime.utcnow()
        docs = []

        for result in results:
            doc = {
                "task_id": task_id,
                "user_id": result.get("user_id"),
                "page_number": result.get("page_number", 1),
                "extracted_text": result.get("extracted_text", ""),
                "structured_data": result.get("structured_data", {}),
                "confidence": result.get("confidence", 0),
                "created_at": now,
                "updated_at": now,
            }
            docs.append(doc)

        if docs:
            await collection.insert_many(docs)

        return docs

    async def update_by_page(
        self, task_id: str, page_number: int, update_data: dict
    ) -> Optional[dict]:
        """Update result by task ID and page number."""
        collection = self._get_collection()

        update_data["updated_at"] = datetime.utcnow()

        result = await collection.find_one_and_update(
            {"task_id": task_id, "page_number": page_number},
            {"$set": update_data},
            return_document=True,
        )

        if result:
            result["id"] = str(result["_id"])
        return result

    async def delete_by_task(self, task_id: str) -> int:
        """Delete all results for a task."""
        collection = self._get_collection()

        result = await collection.delete_many({"task_id": task_id})
        return result.deleted_count
