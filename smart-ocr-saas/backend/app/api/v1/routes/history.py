"""
History routes for managing OCR task history.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.ocr import OCRTaskListResponse
from app.services.ocr_service import OCRService
from app.core.dependencies import get_ocr_service, get_current_user

router = APIRouter()


@router.get("", response_model=OCRTaskListResponse)
async def list_history(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = None,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    取得辨識歷史紀錄列表。
    """
    tasks = await ocr_service.list_tasks(
        user_id=current_user["id"],
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )
    total = await ocr_service.count_tasks(
        user_id=current_user["id"],
        status_filter=status_filter,
    )

    return OCRTaskListResponse(tasks=tasks, total=total)


@router.delete("/{task_id}")
async def delete_history_item(
    task_id: str,
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    刪除歷史紀錄項目。
    """
    success = await ocr_service.delete_task(task_id, current_user["id"])

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="紀錄不存在",
        )

    return {"message": "刪除成功"}
