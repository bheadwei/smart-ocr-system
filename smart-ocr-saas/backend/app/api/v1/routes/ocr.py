"""
OCR processing routes.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.models.ocr import (
    OCRTaskResponse,
    OCRResultResponse,
    OCRResultUpdate,
)
from app.services.ocr_service import OCRService
from app.services.file_service import FileService
from app.core.dependencies import (
    get_ocr_service,
    get_file_service,
    get_current_user,
)
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=OCRTaskResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
    current_user: dict = Depends(get_current_user),
):
    """
    上傳檔案 (圖片或 PDF)。
    """
    # Validate file type
    content_type = file.content_type
    allowed_types = settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_DOCUMENT_TYPES

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"不支援的檔案格式: {content_type}",
        )

    # Validate file size
    contents = await file.read()
    file_size = len(contents)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"檔案大小超過限制 ({settings.MAX_FILE_SIZE_MB}MB)",
        )

    # Reset file position
    await file.seek(0)

    # Upload and create task
    task = await file_service.upload_file(
        file=file,
        file_content=contents,
        user_id=current_user["id"],
    )

    return task


@router.post("/process/{task_id}", response_model=OCRResultResponse)
async def process_ocr(
    task_id: str,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    執行 OCR 辨識處理。
    """
    task = await ocr_service.get_task(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任務不存在",
        )

    if task["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="無權限存取此任務",
        )

    if task["status"] == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="任務正在處理中",
        )

    # Start OCR processing
    result = await ocr_service.process(task_id)
    return result


@router.get("/result/{task_id}", response_model=OCRResultResponse)
async def get_ocr_result(
    task_id: str,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    取得 OCR 辨識結果。
    """
    result = await ocr_service.get_result(task_id, current_user["id"])

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="結果不存在",
        )

    return result


@router.put("/result/{task_id}", response_model=OCRResultResponse)
async def update_ocr_result(
    task_id: str,
    update_data: OCRResultUpdate,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    編輯 OCR 辨識結果。
    """
    result = await ocr_service.update_result(task_id, current_user["id"], update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="結果不存在",
        )

    return result


@router.delete("/result/{task_id}")
async def delete_ocr_result(
    task_id: str,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    刪除 OCR 辨識結果。
    """
    success = await ocr_service.delete_task(task_id, current_user["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任務不存在",
        )

    return {"message": "刪除成功"}
