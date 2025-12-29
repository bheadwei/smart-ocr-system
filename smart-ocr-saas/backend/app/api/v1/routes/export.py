"""
Export routes for downloading OCR results.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.services.export_service import ExportService
from app.services.ocr_service import OCRService
from app.core.dependencies import (
    get_export_service,
    get_ocr_service,
    get_current_user,
)

router = APIRouter()


@router.get("/{task_id}")
async def export_result(
    task_id: str,
    format: str = "json",
    export_service: ExportService = Depends(get_export_service),
    ocr_service: OCRService = Depends(get_ocr_service),
    current_user: dict = Depends(get_current_user),
):
    """
    匯出 OCR 辨識結果。

    支援格式: json, csv, xlsx
    """
    # Validate format
    if format not in ["json", "csv", "xlsx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支援的匯出格式: {format}",
        )

    # Check task exists and user has access
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

    if task["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任務尚未完成，無法匯出",
        )

    # Generate export
    content, media_type, filename = await export_service.export(task_id, format)

    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )
