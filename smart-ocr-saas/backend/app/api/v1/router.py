"""
API v1 Router - Aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.v1.routes import auth, admin, ocr, export, history, websocket

api_router = APIRouter()

# Auth routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Admin routes
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"],
)

# OCR routes
api_router.include_router(
    ocr.router,
    prefix="/ocr",
    tags=["OCR"],
)

# Export routes
api_router.include_router(
    export.router,
    prefix="/export",
    tags=["Export"],
)

# History routes
api_router.include_router(
    history.router,
    prefix="/history",
    tags=["History"],
)

# WebSocket routes
api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"],
)
