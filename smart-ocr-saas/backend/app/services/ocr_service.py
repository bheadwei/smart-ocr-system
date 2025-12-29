"""
OCR processing service.
"""
from typing import Optional, List

from app.models.ocr import OCRResultUpdate


class OCRService:
    """Service for OCR processing."""

    async def get_task(self, task_id: str) -> Optional[dict]:
        """
        Get OCR task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task dict if found, None otherwise
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository

        task_repo = OCRTaskRepository()
        return await task_repo.find_by_id(task_id)

    async def list_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None,
    ) -> List[dict]:
        """
        List OCR tasks for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Optional status filter

        Returns:
            List of task dicts
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository

        task_repo = OCRTaskRepository()
        return await task_repo.find_by_user(
            user_id, skip=skip, limit=limit, status_filter=status_filter
        )

    async def count_tasks(
        self, user_id: str, status_filter: Optional[str] = None
    ) -> int:
        """
        Count OCR tasks for a user.

        Args:
            user_id: User ID
            status_filter: Optional status filter

        Returns:
            Task count
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository

        task_repo = OCRTaskRepository()
        return await task_repo.count_by_user(user_id, status_filter=status_filter)

    async def process(self, task_id: str) -> dict:
        """
        Process OCR for a task.

        Args:
            task_id: Task ID

        Returns:
            OCR result dict
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository
        from app.repositories.ocr_result_repository import OCRResultRepository
        from app.services.file_service import FileService
        from app.services.openai_service import OpenAIVisionService
        from app.api.v1.routes.websocket import get_websocket_manager

        task_repo = OCRTaskRepository()
        result_repo = OCRResultRepository()
        file_service = FileService()
        vision_service = OpenAIVisionService()
        ws_manager = get_websocket_manager()

        # Update status to processing
        await task_repo.update_status(task_id, "processing", 0)
        await ws_manager.send_progress(task_id, 0, "processing")

        try:
            # Get task info
            task = await task_repo.find_by_id(task_id)

            # Download file from MinIO
            file_content = await file_service.download_file(
                task["minio_bucket"], task["minio_object_key"]
            )

            # Convert PDF to images if needed
            if task["file_type"] == "pdf":
                images = await self._pdf_to_images(file_content)
            else:
                images = [file_content]

            results = []
            total_pages = len(images)

            for i, image_data in enumerate(images):
                # Update progress
                progress = int((i / total_pages) * 90)
                await task_repo.update_status(task_id, "processing", progress)
                await ws_manager.send_progress(task_id, progress, "processing")

                # Call OpenAI Vision API
                ocr_result = await vision_service.analyze_image(image_data)

                # Save result
                result = await result_repo.create({
                    "task_id": task_id,
                    "user_id": task["user_id"],
                    "page_number": i + 1,
                    "extracted_text": ocr_result.get("extracted_text", ""),
                    "structured_data": ocr_result.get("structured_data", {}),
                    "confidence": ocr_result.get("confidence", 0),
                })
                results.append(result)

            # Update status to completed
            await task_repo.update_status(task_id, "completed", 100)
            await ws_manager.send_progress(task_id, 100, "completed")

            return {
                "task_id": task_id,
                "status": "completed",
                "results": results,
            }

        except Exception as e:
            # Update status to failed
            await task_repo.update_status(task_id, "failed", 0, str(e))
            await ws_manager.send_progress(task_id, 0, "failed")
            raise

    async def _pdf_to_images(self, pdf_content: bytes) -> List[bytes]:
        """
        Convert PDF to list of images.

        Args:
            pdf_content: PDF file content

        Returns:
            List of image bytes
        """
        import fitz  # PyMuPDF
        import io

        from app.config import settings

        images = []
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")

        max_pages = min(len(pdf_document), settings.MAX_PDF_PAGES)

        for page_num in range(max_pages):
            page = pdf_document.load_page(page_num)
            # Render page to image at 2x resolution for better OCR
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            images.append(img_data)

        pdf_document.close()
        return images

    async def get_result(self, task_id: str, user_id: str) -> Optional[dict]:
        """
        Get OCR result for a task.

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)

        Returns:
            Result dict if found and authorized, None otherwise
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository
        from app.repositories.ocr_result_repository import OCRResultRepository

        task_repo = OCRTaskRepository()
        result_repo = OCRResultRepository()

        task = await task_repo.find_by_id(task_id)
        if not task or task["user_id"] != user_id:
            return None

        results = await result_repo.find_by_task(task_id)

        return {
            "task_id": task_id,
            "status": task["status"],
            "results": results,
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }

    async def update_result(
        self, task_id: str, user_id: str, update_data: OCRResultUpdate
    ) -> Optional[dict]:
        """
        Update OCR result.

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)
            update_data: Update data

        Returns:
            Updated result dict if found and authorized, None otherwise
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository
        from app.repositories.ocr_result_repository import OCRResultRepository

        task_repo = OCRTaskRepository()
        result_repo = OCRResultRepository()

        task = await task_repo.find_by_id(task_id)
        if not task or task["user_id"] != user_id:
            return None

        update_dict = {}
        if update_data.extracted_text is not None:
            update_dict["extracted_text"] = update_data.extracted_text
        if update_data.structured_data is not None:
            update_dict["structured_data"] = update_data.structured_data

        if update_dict:
            await result_repo.update_by_page(
                task_id, update_data.page_number, update_dict
            )

        return await self.get_result(task_id, user_id)

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete OCR task and its results.

        Args:
            task_id: Task ID
            user_id: User ID (for authorization)

        Returns:
            True if successful, False if not found or not authorized
        """
        from app.repositories.ocr_task_repository import OCRTaskRepository
        from app.repositories.ocr_result_repository import OCRResultRepository
        from app.services.file_service import FileService

        task_repo = OCRTaskRepository()
        result_repo = OCRResultRepository()
        file_service = FileService()

        task = await task_repo.find_by_id(task_id)
        if not task or task["user_id"] != user_id:
            return False

        # Delete file from MinIO
        await file_service.delete_file(task["minio_bucket"], task["minio_object_key"])

        # Delete results
        await result_repo.delete_by_task(task_id)

        # Delete task
        await task_repo.delete(task_id)

        return True
