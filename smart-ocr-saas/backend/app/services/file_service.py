"""
File upload/download service using MinIO.
"""
import uuid
from typing import Optional
from datetime import datetime

from fastapi import UploadFile

from app.config import settings


class FileService:
    """Service for file operations with MinIO."""

    def __init__(self):
        """Initialize MinIO client."""
        self._client = None

    def _get_client(self):
        """Get or create MinIO client."""
        if self._client is None:
            from minio import Minio

            self._client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )

            # Ensure bucket exists
            if not self._client.bucket_exists(settings.MINIO_BUCKET):
                self._client.make_bucket(settings.MINIO_BUCKET)

        return self._client

    async def upload_file(
        self,
        file: UploadFile,
        file_content: bytes,
        user_id: str,
    ) -> dict:
        """
        Upload file to MinIO and create OCR task.

        Args:
            file: Uploaded file
            file_content: File content bytes
            user_id: User ID

        Returns:
            Created OCR task dict
        """
        import io
        from app.repositories.ocr_task_repository import OCRTaskRepository

        client = self._get_client()
        task_repo = OCRTaskRepository()

        # Generate unique object key
        task_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        object_key = f"{user_id}/{task_id}/original.{file_ext}"

        # Determine file type
        content_type = file.content_type or ""
        if content_type.startswith("image/"):
            file_type = "image"
            page_count = 1
        elif content_type == "application/pdf":
            file_type = "pdf"
            # Count PDF pages
            page_count = await self._count_pdf_pages(file_content)
        else:
            file_type = "image"
            page_count = 1

        # Upload to MinIO
        client.put_object(
            settings.MINIO_BUCKET,
            object_key,
            io.BytesIO(file_content),
            len(file_content),
            content_type=content_type,
        )

        # Create OCR task record
        task = await task_repo.create({
            "_id": task_id,
            "user_id": user_id,
            "original_filename": file.filename,
            "file_type": file_type,
            "file_size": len(file_content),
            "minio_bucket": settings.MINIO_BUCKET,
            "minio_object_key": object_key,
            "page_count": page_count,
            "status": "uploaded",
            "progress": 0,
            "error_message": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })

        return task

    async def _count_pdf_pages(self, pdf_content: bytes) -> int:
        """
        Count pages in PDF file.

        Args:
            pdf_content: PDF file content

        Returns:
            Page count (limited by MAX_PDF_PAGES)
        """
        try:
            import fitz  # PyMuPDF

            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page_count = len(pdf_document)
            pdf_document.close()

            return min(page_count, settings.MAX_PDF_PAGES)
        except Exception:
            return 1

    async def download_file(self, bucket: str, object_key: str) -> bytes:
        """
        Download file from MinIO.

        Args:
            bucket: Bucket name
            object_key: Object key

        Returns:
            File content bytes
        """
        client = self._get_client()

        response = client.get_object(bucket, object_key)
        content = response.read()
        response.close()
        response.release_conn()

        return content

    async def delete_file(self, bucket: str, object_key: str) -> bool:
        """
        Delete file from MinIO.

        Args:
            bucket: Bucket name
            object_key: Object key

        Returns:
            True if successful
        """
        try:
            client = self._get_client()
            client.remove_object(bucket, object_key)
            return True
        except Exception:
            return False
