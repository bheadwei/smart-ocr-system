"""
WebSocket routes for real-time OCR progress updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.websocket_service import WebSocketManager

router = APIRouter()

# Global WebSocket manager instance
ws_manager = WebSocketManager()


@router.websocket("/ocr-progress")
async def websocket_ocr_progress(
    websocket: WebSocket,
    task_id: str = Query(...),
):
    """
    WebSocket 連線用於接收 OCR 處理進度更新。

    連線方式: ws://host/api/v1/ws/ocr-progress?task_id=xxx
    """
    await ws_manager.connect(task_id, websocket)

    try:
        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()
            # Client can send ping messages to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(task_id, websocket)


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    return ws_manager
